import edge_tts
import asyncio
import os

# Define the path for saving audio files
AUDIO_OUTPUT_DIR = "audio_output"

# Ensure the output directory exists
if not os.path.exists(AUDIO_OUTPUT_DIR):
    os.makedirs(AUDIO_OUTPUT_DIR)

# Edge-TTS voice - natural sounding English voice
VOICE = "en-IN-NeerjaExpressiveNeural"


async def synthesize_speech_async(text: str, output_filename: str) -> str:
    """
    Synthesizes speech from text using Edge-TTS and saves it as MP3.
    """
    output_path = os.path.join(AUDIO_OUTPUT_DIR, output_filename)
    try:
        communicate = edge_tts.Communicate(text, VOICE)
        await communicate.save(output_path)
        return output_path
    except Exception as e:
        return f"Error synthesizing speech: {e}"


def synthesize_speech(text: str, output_filename: str) -> str:
    """
    Synchronous wrapper for Edge-TTS synthesis.
    """
    # Change extension from .wav to .mp3 since Edge-TTS outputs MP3
    if output_filename.endswith(".wav"):
        output_filename = output_filename.replace(".wav", ".mp3")
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If called from within an async context (FastAPI)
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                result = pool.submit(asyncio.run, synthesize_speech_async(text, output_filename)).result()
            return result
        else:
            return loop.run_until_complete(synthesize_speech_async(text, output_filename))
    except RuntimeError:
        return asyncio.run(synthesize_speech_async(text, output_filename))


if __name__ == "__main__":
    print("TTS module created. Testing synthesize_speech...")
    test_text = "Hello, this is a test of the Edge TTS module."
    test_output_file = "test_output.mp3"
    audio_file_path = synthesize_speech(test_text, test_output_file)

    if audio_file_path and "Error" not in audio_file_path:
        print(f"Speech synthesized and saved to: {audio_file_path}")
    else:
        print(f"Failed to synthesize speech: {audio_file_path}")
