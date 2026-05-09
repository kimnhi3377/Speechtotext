import sounddevice as sd
import numpy as np
import time
import scipy.io.wavfile as wav
import config


class AudioService:

    def __init__(self):
        self.fs = config.FS
        self.recording = False
        self.buffer = []
        self.last_voice_time = 0

    def start(self, callback):
        self.recording = True
        self.buffer = []
        self.last_voice_time = time.time()

        self.stream = sd.InputStream(
            samplerate=self.fs,
            channels=1,
            callback=callback
        )
        self.stream.start()

    def stop(self):
        self.recording = False
        self.stream.stop()
        self.stream.close()

        if len(self.buffer) == 0:
            return None

        audio = np.concatenate(self.buffer, axis=0).flatten()
        audio = audio / (np.max(np.abs(audio)) + 1e-7)

        file = f"temp_{int(time.time())}.wav"
        wav.write(file, self.fs, audio.astype(np.float32))

        return file