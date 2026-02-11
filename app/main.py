from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import FileResponse, Response
import os
import shutil
import uuid
import asyncio
import httpx
from twilio.twiml.voice_response import VoiceResponse, Play
from loguru import logger

from app.stt import transcribe_audio
from app.agent import get_rag_response, warm_up_ollama
from app.tts import synthesize_speech_async
from app.config import AUDIO_UPLOAD_DIR, AUDIO_OUTPUT_DIR, BASE_DIR, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, NGROK_URL

# Configure Loguru logger
LOG_FILE_PATH = os.path.join(BASE_DIR, "logs", "agent.log")
logger.add(LOG_FILE_PATH, rotation="500 MB", compression="zip", level="INFO")

app = FastAPI()

# Global dict to track if first reply was given for each call
first_reply_given = {}

# Global dict to store processing results for async pattern
call_results = {}


@app.on_event("startup")
async def startup_event():
    """Warm up models and pre-generate intro audio on server start."""
    warm_up_ollama()
    # Pre-generate intro and goodbye audio with Edge-TTS voice
    intro_text = "Hi there! Calling from Paradise Holidays, your travel assistant calling to collect feedback. How is your trip going so far?"
    await synthesize_speech_async(intro_text, "intro.mp3")
    goodbye_text = "Thank you for your time. Have a great day!"
    await synthesize_speech_async(goodbye_text, "goodbye.mp3")
    logger.info("Intro and goodbye audio pre-generated with Edge-TTS voice.")


async def process_recording(call_sid: str, recording_url: str):
    """
    Background task: downloads recording, transcribes, generates LLM reply, synthesizes audio.
    Stores the result in call_results[call_sid] when done.
    """
    try:
        logger.info(f"[BG] Starting processing for call {call_sid}")

        # Download the recorded audio from Twilio
        async with httpx.AsyncClient(auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)) as client:
            audio_content = await client.get(recording_url)
            audio_content.raise_for_status()

        # Save the downloaded audio temporarily
        unique_filename = f"{call_sid}_recorded.wav"
        recorded_audio_path = os.path.join(AUDIO_UPLOAD_DIR, unique_filename)
        with open(recorded_audio_path, "wb") as f:
            f.write(audio_content.content)
        logger.info(f"[BG] Recorded audio saved to: {recorded_audio_path}")

        # 1. Transcribe audio
        transcribed_text = transcribe_audio(recorded_audio_path)
        os.remove(recorded_audio_path)
        logger.info(f"[BG] Transcribed text for {call_sid}: {transcribed_text}")

        if "Error" in transcribed_text:
            call_results[call_sid] = {"status": "error", "error": "transcription_failed"}
            return

        # 2. Generate LLM reply using RAG
        llm_reply = get_rag_response(transcribed_text)
        if "Error" in llm_reply:
            call_results[call_sid] = {"status": "error", "error": "llm_failed"}
            return
        logger.info(f"[BG] LLM Reply for {call_sid}: {llm_reply}")

        # 3. Synthesize speech from LLM reply
        if not first_reply_given.get(call_sid):
            max_tts_length = 200
            first_reply_given[call_sid] = True
        else:
            max_tts_length = 100
        short_reply = llm_reply[:max_tts_length]
        output_audio_filename = f"reply_{call_sid}.mp3"
        synthesized_audio_path = await synthesize_speech_async(short_reply, output_audio_filename)

        if "Error" in synthesized_audio_path:
            call_results[call_sid] = {"status": "error", "error": "tts_failed"}
            return

        logger.info(f"[BG] Audio ready for {call_sid}: {synthesized_audio_path}")

        # Store result
        audio_url = f"{NGROK_URL}/audio/{output_audio_filename}"
        call_results[call_sid] = {
            "status": "done",
            "audio_url": audio_url,
            "text": llm_reply
        }

    except Exception as e:
        logger.error(f"[BG] Error processing call {call_sid}: {e}")
        call_results[call_sid] = {"status": "error", "error": str(e)}


@app.post("/twilio_voice")
async def twilio_voice(request: Request):
    logger.info("Received Twilio voice webhook request.")
    form_data = await request.form()
    call_sid = form_data.get("CallSid")
    recording_url = form_data.get("RecordingUrl")

    response = VoiceResponse()

    if recording_url:
        logger.info(f"Recording URL received for {call_sid}. Starting background processing.")

        # Kick off processing in the background
        asyncio.create_task(process_recording(call_sid, recording_url))

        # Respond IMMEDIATELY to Twilio — silent pause then check for results
        response.pause(length=2)
        response.redirect(f"{NGROK_URL}/twilio_result/{call_sid}", method="POST")
    else:
        logger.info(f"No recording URL for {call_sid}. Starting conversation.")
        intro_audio_url = f"{NGROK_URL}/audio/intro.mp3"
        response.play(intro_audio_url)
        response.record(action="/twilio_voice", maxLength="15", timeout="5", transcribe=True)

    return Response(content=str(response), media_type="application/xml")


@app.post("/twilio_result/{call_sid}")
async def twilio_result(call_sid: str, request: Request):
    """
    Polling endpoint — Twilio redirects here to check if processing is done.
    If done: plays the audio response.
    If not done: pauses briefly and redirects back (retry loop).
    """
    response = VoiceResponse()
    result = call_results.get(call_sid)

    if result and result["status"] == "done":
        logger.info(f"Result ready for {call_sid}. Playing audio: {result['audio_url']}")
        # Clean up
        del call_results[call_sid]
        # Play the response and end the call
        response.play(result["audio_url"])
        response.hangup()

    elif result and result["status"] == "error":
        logger.error(f"Processing failed for {call_sid}: {result['error']}")
        del call_results[call_sid]
        response.say("I apologize, but I encountered an error processing your feedback.")

    else:
        # Still processing — wait and check again
        logger.info(f"Still processing {call_sid}. Waiting...")
        response.pause(length=2)
        response.redirect(f"{NGROK_URL}/twilio_result/{call_sid}", method="POST")

    return Response(content=str(response), media_type="application/xml")


@app.post("/process_audio/")
async def process_audio(audio_file: UploadFile = File(...)):
    logger.info(f"Received audio processing request for file: {audio_file.filename}")
    if not audio_file.filename.endswith(('.wav', '.mp3', '.ogg')):
        logger.error(f"Invalid file format received: {audio_file.filename}")
        raise HTTPException(status_code=400, detail="Invalid file format. Only WAV, MP3, OGG are supported.")

    unique_filename = f"{uuid.uuid4()}_{audio_file.filename}"
    audio_path = os.path.join(AUDIO_UPLOAD_DIR, unique_filename)
    with open(audio_path, "wb") as buffer:
        shutil.copyfileobj(audio_file.file, buffer)
    logger.info(f"Audio file saved temporarily to: {audio_path}")

    transcribed_text = transcribe_audio(audio_path)
    if "Error" in transcribed_text:
        logger.error(f"STT Error for {audio_file.filename}: {transcribed_text}")
        raise HTTPException(status_code=500, detail=f"STT Error: {transcribed_text}")
    logger.info(f"Transcribed text: {transcribed_text}")

    llm_reply = get_rag_response(transcribed_text)
    if "Error" in llm_reply:
        logger.error(f"RAG Error for \"{transcribed_text}\": {llm_reply}")
        raise HTTPException(status_code=500, detail=f"RAG Error: {llm_reply}")
    logger.info(f"LLM Reply (from RAG): {llm_reply}")

    output_audio_filename = f"reply_{uuid.uuid4()}.mp3"
    synthesized_audio_path = await synthesize_speech_async(llm_reply, output_audio_filename)
    if "Error" in synthesized_audio_path:
        logger.error(f"TTS Error for \"{llm_reply}\": {synthesized_audio_path}")
        raise HTTPException(status_code=500, detail=f"TTS Error: {synthesized_audio_path}")
    logger.info(f"Synthesized audio saved to: {synthesized_audio_path}")

    os.remove(audio_path)
    logger.info(f"Cleaned up temporary audio file: {audio_path}")

    return {"transcribed_text": transcribed_text, "llm_reply": llm_reply, "reply_audio_path": synthesized_audio_path}


@app.get("/audio/{filename}")
async def get_audio(filename: str):
    """
    Serves synthesized audio files.
    """
    file_path = os.path.join(AUDIO_OUTPUT_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Audio file not found.")
    return FileResponse(file_path, media_type="audio/mpeg")


if __name__ == "__main__":
    import uvicorn
    print(f"FastAPI app created. To run, use: uvicorn app.main:app --reload --port 8000")