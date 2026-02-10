from faster_whisper import WhisperModel
import os

# Load the Faster Whisper model
# You might want to make the model size configurable (e.g., 'base', 'small', 'medium', 'large')
# For local development, 'base' or 'small' might be sufficient.
try:
    # Using a smaller model for faster local inference, adjust as needed
    # The model will be downloaded to ~/.cache/huggingface/hub if not present
    model = WhisperModel("base", device="cpu", compute_type="int8") # Use "cuda" if you have a GPU
except Exception as e:
    print(f"Error loading Faster Whisper model: {e}")
    model = None

def transcribe_audio(audio_path: str) -> str:
    """
    Transcribes an audio file using the Faster Whisper model.
    """
    if model is None:
        return "Faster Whisper model not loaded. Cannot transcribe audio."
    if not os.path.exists(audio_path):
        return f"Audio file not found: {audio_path}"
    try:
        segments, info = model.transcribe(audio_path, beam_size=5)
        transcribed_text = "".join([segment.text for segment in segments])
        return transcribed_text
    except Exception as e:
        return f"Error transcribing audio: {e}"

if __name__ == "__main__":
    # Simple test for transcription (requires a test audio file)
    print("STT module created. To test, you would need an audio file.")
    # Example usage (uncomment and provide a valid audio path to test):
    # test_audio_file = "path/to/your/audio.wav"
    # if os.path.exists(test_audio_file):
    #     transcription = transcribe_audio(test_audio_file)
    #     print(f"Transcription: {transcription}")
    # else:
    #     print(f"Test audio file not found at {test_audio_file}")