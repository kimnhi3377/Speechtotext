import time
import os
import numpy as np

import whisper
import sounddevice as sd
import scipy.io.wavfile as wav

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QDialog, QFileDialog, QTextEdit
from PyQt5 import uic
from utils import clean_speech as clean_text


class MyApp(QDialog):

    def __init__(self):
        super().__init__()
        uic.loadUi("main.ui", self)

        # CSS
        path = os.path.join(os.path.dirname(__file__), "style.qss")
        with open(path, "r", encoding="utf-8") as f:
            self.setStyleSheet(f.read())

        # Whisper
        print("Loading Whisper...")
        self.model = whisper.load_model("base")

        # DATA
        self.fs = 16000
        self.recording = False
        self.audio_buffer = []
        self.last_voice_time = 0
        self.stream = None

        self.ds_cau = []
        self.min_record_time = 2.0
        self.silence_limit = 4.0

        self.start_time = time.time()

        # LANGUAGE
        self.lang_map = {
            "Tiếng Việt": "vi",
            "Tiếng Anh": "en"
        }

        # BUTTON
        self.bt_ghi.clicked.connect(self.bat_dau)
        self.bt_dung.clicked.connect(self.dung_ghi)

        self.bt_xoa1cau.clicked.connect(self.xoa_cau_cuoi)
        self.bt_xoatatca.clicked.connect(self.xoa_tat_ca)
        self.bt_luu.clicked.connect(self.luu_file)

        # TIMER
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_silence)

    # =====================================================
    
    def bat_dau(self):

        self.start_time = time.time()

        if self.recording:
            return

        self.recording = True

        self.bt_ghi.setProperty("recording", "true")
        self.bt_ghi.style().unpolish(self.bt_ghi)
        self.bt_ghi.style().polish(self.bt_ghi)
        self.bt_ghi.update()
        self.bt_ghi.setText("🎤 Đang nghe...")
        self.audio_buffer = []
        self.last_voice_time = time.time()

        print("Bắt đầu ghi...")

        self.stream = sd.InputStream(
            samplerate=self.fs,
            channels=1,
            callback=self.callback
        )

        self.stream.start()
        self.timer.start(300)

    # =====================================================
    def callback(self, indata, frames, time_info, status):

        if not self.recording:
            return

        audio = indata.copy().astype(np.float32)
        volume = np.sqrt(np.mean(audio ** 2))

        # luôn append audio (quan trọng)
        self.audio_buffer.append(audio)

        # chỉ update thời gian khi có tiếng
        if volume > 0.01:
            self.last_voice_time = time.time()

    # =====================================================
    def check_silence(self):

        if not self.recording:
            return

        # chưa đủ thời gian tối thiểu thì không được dừng
        if time.time() - self.start_time < self.min_record_time:
            return

        if time.time() - self.last_voice_time > self.silence_limit:
            print("Im lặng -> tự dừng")
            self.dung_ghi()

    # =====================================================
    def dung_ghi(self):

        if not self.recording:
            return

        self.recording = False
        self.bt_ghi.setProperty("recording", "false")
        self.bt_ghi.style().unpolish(self.bt_ghi)
        self.bt_ghi.style().polish(self.bt_ghi)
        self.bt_ghi.update()
        self.bt_ghi.setText("Bắt đầu")


        self.timer.stop()

        print("Dừng ghi...")

        if self.stream:
            self.stream.stop()
            self.stream.close()

        if len(self.audio_buffer) == 0:
            print("Không có audio")
            return

        # ================= AUDIO =================
        audio = np.concatenate(self.audio_buffer, axis=0)

        # remove DC noise
        audio = audio - np.mean(audio)

        # normalize
        audio = audio / (np.max(np.abs(audio)) + 1e-7)

        temp_file = "temp.wav"
        wav.write(temp_file, self.fs, audio.astype(np.float32))

        # ================= LANGUAGE =================
        lang_text = self.cb_language.currentText()
        lang_code = self.lang_map.get(lang_text, "vi")

        print("🌍 Language:", lang_code)

        # ================= WHISPER =================
        try:
            result = self.model.transcribe(
                temp_file,
                language=lang_code,
                task="transcribe",
                fp16=False,
                temperature=0,
                condition_on_previous_text=False,
                no_speech_threshold=0.6,
                logprob_threshold=-1.0,
                compression_ratio_threshold=2.2,
                beam_size=5
            )

            text = result["text"].strip()

            # dùng clean_text của em
            text = clean_text(text)

            print(" RESULT:", text)

            if text:
                text = text.rstrip(".")
                self.ds_cau.append(text + ".")
                self.cap_nhat_noi_dung()

        except Exception as e:
            print("Whisper error:", e)

        if os.path.exists(temp_file):
            os.remove(temp_file)

    # =====================================================


    def cap_nhat_noi_dung(self):
        self.tedit_noidung.setPlainText(" ".join(self.ds_cau))

    def xoa_cau_cuoi(self):
        if self.ds_cau:
            self.ds_cau.pop()
            self.cap_nhat_noi_dung()

    def xoa_tat_ca(self):
        self.ds_cau.clear()
        self.tedit_noidung.clear()

    def luu_file(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Lưu file", "", "Text Files (*.txt)"
        )

        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.tedit_noidung.toPlainText())