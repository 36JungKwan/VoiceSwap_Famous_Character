# VoiceSwap with Famous Character
Ứng dụng game tương tác thử thách người chơi về khả năng bắt chước giọng nói của các nhân vật nổi tiếng. Người chơi xem đoạn video bị tắt tiếng ở một câu thoại nổi tiếng, sau đó thu âm lại giọng chính mình và hệ thống sẽ chuyển giọng bạn thành giọng nhân vật gốc để so sánh!

## 🧠 Tính năng

- 🎬 Phát video nhân vật nổi tiếng và tự động tắt tiếng đúng đoạn thoại.
- 🎤 Ghi âm giọng nói người chơi.
- 🔁 Nghe lại giọng gốc đã ghi.
- 🗣 Chuyển đổi giọng nói của bạn sang giọng nhân vật (dùng YourTTS).
- 📝 Chuyển giọng nói thành văn bản (dùng Whisper).
- ✅ So sánh và hiển thị kết quả đúng/sai.
- 🔊 Nghe lại giọng đã chuyển đổi.

## 📂 Cấu trúc thư mục

├── video_clips/

│ ├── obama.mp4

│ ├── tony.mp4

│ └── yoda.mp4

├── ref_voices/

│ ├── Obama.wav

│ ├── Tony_Stark.wav

│ └── Yoda.wav

├── recorded_voice/

│ └── recorded.wav

├── generated_voice/

│ └── output.wav

├── app.py

├── requirements.txt

└── README.md

## ▶️ Cách chạy

**Clone repo về máy**

git clone https://github.com/36JungKwan/VoiceSwap_Famous_Character

**Cài đặt thư viện cần thiết**

pip install -r requirements.txt

## 🧩 Lưu ý về phát video (Windows)

Để đảm bảo video `.mp4` chạy đúng trên `QMediaPlayer`, bạn cần cài **K-Lite Codec Pack**:

- 👉 Tải tại: https://codecguide.com/download_k-lite_codec_pack_standard.htm
- Bạn đang cài bản **Standard** để đảm bảo hỗ trợ định dạng `.mp4` (H.264).
- Vào web và nhấn vào link `Server 1` dưới mục Location trong phần Download
   
## Chạy ứng dụng:

python VoiceSwap_YourTTS.py

## 🛠 Yêu cầu phần cứng

GPU (khuyến nghị) để xử lý nhanh hơn với Whisper và YourTTS.

Microphone và loa hoạt động tốt để ghi âm & phát lại.

## ✨ Ghi chú

- Vui lòng giữ nguyên cấu trúc thư mục để video, voice reference khớp và cho ra kết quả chuyển đổi giọng đúng chất lượng.
- Thay đổi các path (đường dẫn) nếu cần
- Lần đầu chạy app sẽ khá tốn thời gian vì các thư viện sẽ tự động tải model (whisper, YourTTS) về nếu chưa có
