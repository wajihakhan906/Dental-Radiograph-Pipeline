"""Speech-to-text with Faster Whisper and optional text-to-speech."""


class Transcriber:
    def __init__(self, model_size="base", device="auto", compute_type="int8"):
        from faster_whisper import WhisperModel

        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)

    def __call__(self, audio_path):
        segments, _ = self.model.transcribe(audio_path, beam_size=5, vad_filter=True)
        return " ".join(s.text.strip() for s in segments)


def speak(text, out_path="answer.wav"):
    """Offline TTS with pyttsx3; returns the audio file path (or None if TTS is unavailable)."""
    try:
        import pyttsx3
    except ImportError:
        return None
    engine = pyttsx3.init()
    engine.save_to_file(text, out_path)
    engine.runAndWait()
    return out_path
