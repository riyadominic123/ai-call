from TTS.api import TTS
import os

# Define the path for saving audio files
AUDIO_OUTPUT_DIR = "audio_output"

# Ensure the output directory exists
if not os.path.exists(AUDIO_OUTPUT_DIR):
    os.makedirs(AUDIO_OUTPUT_DIR)

# Load the TTS model
# You might need to specify a model name, e.g., "tts_models/en/ljspeech/tacotron2-DDC"
# For simplicity, we'll use a default or a common one if available.
try:
    # This will download the model if not already present
    tts_model = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False, gpu=False)
except Exception as e:
    print(f"Error loading TTS model: {e}")
    tts_model = None

def synthesize_speech(text: str, output_filename: str) -> str:
    """
    Synthesizes speech from text and saves it to an audio file.
    Returns the path to the saved audio file.
    """
    if tts_model is None:
        return "TTS model not loaded. Cannot synthesize speech."

    output_path = os.path.join(AUDIO_OUTPUT_DIR, output_filename)
    try:
        tts_model.tts_to_file(text=text, file_path=output_path)
        return output_path
    except Exception as e:
        return f"Error synthesizing speech: {e}"

if __name__ == "__main__":
    # Simple test for speech synthesis
    print("TTS module created. Testing synthesize_speech...")
    test_text = "Hello, this is a test of the text-to-speech module."
    test_output_file = "test_output.wav"
    audio_file_path = synthesize_speech(test_text, test_output_file)

    if audio_file_path and "Error" not in audio_file_path:
        print(f"Speech synthesized and saved to: {audio_file_path}")
    else:
        print(f"Failed to synthesize speech: {audio_file_path}")
