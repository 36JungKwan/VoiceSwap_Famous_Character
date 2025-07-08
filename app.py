import sys
import os
import torch
import sounddevice as sd
import soundfile as sf
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QComboBox,
    QVBoxLayout, QHBoxLayout, QMainWindow, QDesktopWidget, QSlider
)
from PyQt5.QtCore import Qt, QUrl, QTimer, QPropertyAnimation, QRect
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtGui import QFont, QPalette, QColor
import whisper
from TTS.api import TTS

# ================= CONFIG =================
AUDIO_PATH = "recorded_voice/recorded.wav"
OUTPUT_PATH = "output_voice/output.wav"
DURATION = 5
SAMPLE_RATE = 16000
WHISPER_MODEL = "small"
TTS_MODEL = "tts_models/multilingual/multi-dataset/your_tts"

# Nhân vật nổi tiếng: câu nói & video bị mute
CELEBRITY_DATA = {
    "Barack Obama": {
        "quote": "Yes we can.",
        "video": "video_clips/obama.mp4",
        "ref": "ref_voices/Obama.wav",
        "mute_start": 23000,
        "mute_end": 24000
    },
    "Donald Trump": {
        "quote": "You're fired!",
        "video": "video_clips/trump.mp4",
        "ref": "ref_voices/Trump.wav",
        "mute_start": 9500,
        "mute_end": 11000
    },
    "Tony Stark": {
        "quote": "I am Iron Man.",
        "video": "video_clips/tony.mp4",
        "ref": "ref_voices/Tony_Stark.wav",
        "mute_start": 17000,
        "mute_end": 19000
    },
    "Captain America": {
        "quote": "I can do this all day.",
        "video": "video_clips/captain.mp4",
        "ref": "ref_voices/Captain_America.wav",
        "mute_start": 20000,
        "mute_end": 47000
    },
    "Yoda": {
        "quote": "May the force be with you.",
        "video": "video_clips/yoda.mp4",
        "ref": "ref_voices/Yoda.wav",
        "mute_start": 00000,
        "mute_end": 19000
    },
    "Darth Vader": {
        "quote": "Luke, I am your father.",
        "video": "video_clips/vader.mp4",
        "ref": "ref_voices/Vader.wav",
        "mute_start": 12500,
        "mute_end": 17000
    },
    "Batman": {
        "quote": "I’m Batman.",
        "video": "video_clips/batman.mp4",
        "ref": "ref_voices/Batman.wav",
        "mute_start": 17000,
        "mute_end": 19000
    }
}

# ================= GHI ÂM =================
def record_audio(path, duration=5, sr=16000):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    print("🎤 Đang ghi âm...")
    audio = sd.rec(int(duration * sr), samplerate=sr, channels=1, dtype='float32')
    sd.wait()
    sf.write(path, audio, sr)
    print("✅ Ghi âm xong")

# ================= STT =================
def transcribe(path):
    model = whisper.load_model(WHISPER_MODEL)
    result = model.transcribe(path, language="en")
    print("📝 Văn bản chuyển từ giọng nói:", result["text"])
    return result["text"]

# ================= TTS =================
tts = TTS(model_name=TTS_MODEL, progress_bar=False, gpu=torch.cuda.is_available())

def synthesize(text, ref_path, output_path):
    wav = tts.tts(
        text=text,
        speaker_wav=ref_path,
        language="en"
    )
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    sf.write(output_path, wav, 16000)

# ================= PyQt5 UI =================
class GuessingGameApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Famous Quote Guessing Game")
        self.setMinimumSize(1000, 700)
        self.setStyleSheet("QLabel { font-size: 20px} QWidget { background-color: #1e1e1e; color: #ffffff; } QPushButton { font-size: 20px; padding: 8px 16px; border-radius: 8px; background-color: #3c3f41; color: #ffffff } QComboBox { font-size: 20px } QPushButton:hover { background-color: #505355 }")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)

        self.combo = QComboBox()
        self.combo.addItems(CELEBRITY_DATA.keys())
        self.layout.addWidget(QLabel("🎬 Chọn nhân vật nổi tiếng:"))
        self.layout.addWidget(self.combo)

        self.video_widget = QVideoWidget()
        self.video_widget.setMinimumHeight(700)
        self.layout.addWidget(self.video_widget)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.sliderMoved.connect(self.seek_video)
        self.layout.addWidget(self.slider)

        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.time_label)

        video_controls = QHBoxLayout()
        self.play_btn = QPushButton("▶️ Phát")
        self.pause_btn = QPushButton("⏸ Dừng")
        self.mute_btn = QPushButton("🔇 Tắt tiếng đoạn thoại")
        self.rewind_btn = QPushButton("⏪ Tua -5s")
        self.forward_btn = QPushButton("⏩ Tua +5s")

        video_controls.addWidget(self.play_btn)
        video_controls.addWidget(self.pause_btn)
        video_controls.addWidget(self.mute_btn)
        video_controls.addWidget(self.rewind_btn)
        video_controls.addWidget(self.forward_btn)
        self.layout.addLayout(video_controls)

        self.mute_indicator = QLabel("🔕 [Mute]")
        self.mute_indicator.setStyleSheet("color: red; font-weight: bold;")
        self.mute_indicator.setAlignment(Qt.AlignCenter)
        self.mute_indicator.hide()
        self.layout.addWidget(self.mute_indicator)

        # ========== Voice Controls ========== #
        voice_controls = QHBoxLayout()

        self.record_btn = QPushButton("🎙 Ghi âm câu nói")
        self.record_btn.clicked.connect(self.record_audio_only)
        voice_controls.addWidget(self.record_btn)

        self.listen_recorded_btn = QPushButton("🔁 Nghe lại giọng đã thu")
        self.listen_recorded_btn.clicked.connect(self.play_recorded_audio)
        voice_controls.addWidget(self.listen_recorded_btn)

        self.result_btn = QPushButton("📢 Hiển thị kết quả")
        self.result_btn.clicked.connect(self.check_answer_and_generate)
        self.result_btn.setEnabled(False)
        voice_controls.addWidget(self.result_btn)

        self.voice_btn = QPushButton("🔊 Phát lại giọng đã chuyển")
        self.voice_btn.clicked.connect(self.play_generated_audio)
        voice_controls.addWidget(self.voice_btn)

        self.layout.addLayout(voice_controls)

        self.result_label = QLabel("👉 Kết quả sẽ hiển thị ở đây")
        self.result_label.setWordWrap(True)
        self.result_label.setStyleSheet("padding: 10px; background-color: #2b2b2b; border-radius: 8px;")
        self.result_label.setFont(QFont("Arial", 15))
        self.layout.addWidget(self.result_label)

        # ========== Video Player Logic ========== #
        self.player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.player.setVideoOutput(self.video_widget)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_slider)

        self.mute_check_timer = QTimer(self)
        self.mute_check_timer.timeout.connect(self.check_auto_mute)

        self.play_btn.clicked.connect(self.play_video)
        self.pause_btn.clicked.connect(self.toggle_pause_resume)
        self.rewind_btn.clicked.connect(self.rewind_video)
        self.mute_btn.clicked.connect(self.toggle_auto_mute)
        self.forward_btn.clicked.connect(self.forward_video)

        self.auto_mute_enabled = True
        self.muted = False
        self.current_video = None

        self.showMaximized()

        # Animation
        self.result_anim = QPropertyAnimation(self.result_label, b"geometry")
        self.showMaximized()

    def play_video(self):
        celeb = self.combo.currentText()
        video_path = CELEBRITY_DATA[celeb]["video"]
        if os.path.exists(video_path):
            self.current_video = celeb
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(video_path)))
            self.player.setMuted(False)
            self.player.play()
            self.timer.start(100)
            self.mute_check_timer.start(100)
        else:
            self.result_label.setText("❌ Video không tồn tại")

    def forward_video(self):
        self.player.setPosition(self.player.position() + 5000)

    def rewind_video(self):
        new_pos = max(0, self.player.position() - 5000)
        self.player.setPosition(new_pos)

    def toggle_pause_resume(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
            self.pause_btn.setText("▶️ Tiếp tục")
        else:
            self.player.play()
            self.pause_btn.setText("⏸ Dừng")

    def toggle_auto_mute(self):
        self.auto_mute_enabled = not self.auto_mute_enabled
        self.mute_btn.setText("🧏 Tắt tự động tắt tiếng" if self.auto_mute_enabled else "🔊 Bật tiếng toàn bộ")
        self.mute_indicator.setVisible(self.muted)

    def check_auto_mute(self):
        if not self.current_video or not self.auto_mute_enabled:
            return
        celeb = self.current_video
        mute_start = CELEBRITY_DATA[celeb]["mute_start"]
        mute_end = CELEBRITY_DATA[celeb]["mute_end"]
        pos = self.player.position()
        is_muted = mute_start <= pos <= mute_end
        self.player.setMuted(is_muted)
        self.mute_indicator.setVisible(is_muted)

    def update_slider(self):
        duration = self.player.duration()
        position = self.player.position()
        if duration > 0:
            self.slider.setValue(int(position * 100 / duration))
            self.time_label.setText(f"{position//60000:02d}:{(position//1000)%60:02d} / {duration//60000:02d}:{(duration//1000)%60:02d}")

    def seek_video(self, position):
        duration = self.player.duration()
        self.player.setPosition(int(duration * position / 100))

    def record_audio_only(self):
        celeb = self.combo.currentText()
        self.result_label.setText("🎤 Đang ghi âm...")
        self.repaint()
        record_audio(AUDIO_PATH, DURATION, SAMPLE_RATE)
        self.result_label.setText("✅ Ghi âm xong! Bấm 'Hiển thị kết quả' để tiếp tục.")
        self.result_btn.setEnabled(True)

    def play_recorded_audio(self):
        if os.path.exists(AUDIO_PATH):
            data, sr = sf.read(AUDIO_PATH)
            sd.play(data, sr)
            sd.wait()
        else:
            self.result_label.setText("❌ Chưa có bản ghi âm để phát lại")

    def check_answer_and_generate(self):
        celeb = self.combo.currentText()
        correct_quote = CELEBRITY_DATA[celeb]["quote"]
        ref_path = CELEBRITY_DATA[celeb]["ref"]

        self.result_label.setText("📝 Đang chuyển giọng nói thành văn bản...")
        self.repaint()
        spoken_text = transcribe(AUDIO_PATH)

        if correct_quote.strip().lower() == spoken_text.strip().lower():
            self.result_label.setStyleSheet("color: green;")
            self.result_label.setText(f"✅ Chính xác! Câu đúng là: \"{correct_quote}\"\nBạn đã nói: \"{spoken_text}\"")
        else:
            self.result_label.setStyleSheet("color: red;")
            self.result_label.setText(f"❌ Sai rồi! Câu đúng là: \"{correct_quote}\"\nBạn đã nói: \"{spoken_text}\"")

        synthesize(spoken_text, ref_path, OUTPUT_PATH)
        self.result_btn.setEnabled(False)

    def play_generated_audio(self):
        if os.path.exists(OUTPUT_PATH):
            data, sr = sf.read(OUTPUT_PATH)
            sd.play(data, sr)
            sd.wait()
        else:
            self.result_label.setText("❌ Chưa có giọng đã chuyển để phát lại")

# ================= RUN =================
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = GuessingGameApp()
    sys.exit(app.exec_())
