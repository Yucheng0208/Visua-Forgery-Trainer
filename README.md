# 🧩 Visua-Forgery-Trainer

A dark-themed, Flask-based web application for real-time video manipulation, designed for cybersecurity and media forensics education.  
Users can select different video sources, including YouTube streams, webcam feeds, or local files, and apply overlay effects (e.g., watermarks or image patches) to visualize visual forgery techniques in action.

## 🛠️ Features

- 📺 Support for multiple video sources (YouTube Live, local files, webcam).
- 🧠 Real-time dual-stream comparison (original vs. overwritten).
- 🖼️ Transparent image overlay using `Lenna.jpg`.
- ⚙️ Flask backend and OpenCV processing with optional `yt_dlp` for YouTube URL resolution.
- 👾 Cybersecurity educational utility — train users to detect and simulate visual attacks.

## 🌐 Live Demo Interface

After running the app, open your browser at:  
`http://127.0.0.1:5000`  
You will see:
- A selection menu to choose a video stream.
- Two synchronized video frames: one original, one with overlay manipulation.


## 📦 Installation

```bash
pip install flask opencv-python yt_dlp
python app.py
```
> Ensure that `Lenna.jpg` and `sample.mp4` are placed in the project root directory.

---

## 📁 File Structure

```
Visua-Forgery-Trainer/
├── app.py            # Flask backend application
├── index.html        # Web frontend (template)
├── Lenna.jpg         # Overlay image (see source below)
├── sample.mp4        # Local test video (see source below)

```

## 📷 Sample Media Sources

### 🖼️ Image: `Lenna.jpg`

- 📥 Origin: USC SIPI Image Database
- 📄 Description: The Lenna image is a standard test image widely used in image processing research.

### 🎞️ Video: `sample.mp4`

- 📽️ Video Title: ✈️TAIWAN 西濱快速道路 | 🎦Vlog 4K | 🚀空拍 | ✅ Free Video No Copyright

- 🔗 Video Link: [YouTube](https://youtu.be/emTnMfRuE-8?si=tTn1LnP8GFSOhu4n)

- 📡 Channel: [灣灣視野 (WanWan Vision)](https://www.youtube.com/@%E7%81%A3%E7%81%A3%E8%A6%96%E9%87%8E)

## 🔒 Disclaimer

This project is intended solely for educational and ethical use. Please do not use it for unauthorized video manipulation or malicious purposes.

## 📬 Contact

Developed by [張育丞 Yu-Cheng Chang](https://github.com/yucheng0208)
Feel free to fork, contribute, or reach out for collaboration!