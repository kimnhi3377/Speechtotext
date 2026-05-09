import whisper
import config


class SpeechService:

    def __init__(self):
        print("Loading model...")
        self.model = whisper.load_model(config.MODEL_SIZE)

    def transcribe(self, file, lang):
        return self.model.transcribe(
            file,
            language=lang,
            fp16=False,
            beam_size=5,
            temperature=0,
            condition_on_previous_text=False
        )