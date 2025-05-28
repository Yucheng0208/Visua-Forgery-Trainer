from flask import Flask, render_template, request, Response
import cv2
import yt_dlp
import numpy as np

app = Flask(__name__)

VIDEO_SOURCES = {
    #"YouTube Live A": "https://www.youtube.com/embed/Ndo_8RuefH4?si=qgaWkMBZWD5-X6kU&amp",
    "CCTV #1": "https://www.youtube.com/embed/xwAWSh35uuw?si=Rv2FPTao_XJZLh0Z&amp",
    "CCTV #2": "https://www.youtube.com/embed/XSD5ptYisw8?si=tDpZPxhEZyT9DGNg&amp",
    "Cam": 0,
    "Glasses": "webcam_glasses",
    "Remote Cam": "remote_lenna",
    "Server File": "sample.mp4"
}

selected_source = None
overlay_image_path = "Lenna.jpg"

glasses_img = cv2.imread('glasses.png', cv2.IMREAD_UNCHANGED)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')


def resolve_youtube_stream(youtube_url):
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'forceurl': True,
        'format': 'best[ext=mp4]/best'
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=False)
        return info['url']


def overlay_glasses_on_face(frame, face_box, glasses_img):
    x, y, w, h = face_box
    glasses_width = int(w * 0.9)
    aspect_ratio = glasses_img.shape[0] / glasses_img.shape[1]
    glasses_height = int(glasses_width * aspect_ratio)
    x1 = x + int((w - glasses_width) / 2) + int(w * 0.05)
    y1 = y + int(h * 0.10)
    x2 = x1 + glasses_width
    y2 = y1 + glasses_height
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)
    resized_glasses = cv2.resize(glasses_img, (x2 - x1, y2 - y1), interpolation=cv2.INTER_AREA)
    alpha = resized_glasses[:, :, 3] / 255.0
    for c in range(3):
        frame[y1:y2, x1:x2, c] = (
            resized_glasses[:, :, c] * alpha +
            frame[y1:y2, x1:x2, c] * (1 - alpha)
        )
    return frame


def generate_frames(source, overlay_mode=False):
   
    if isinstance(source, str) and "youtube.com" in source:
        source = resolve_youtube_stream(source)

    if source == "webcam_glasses":
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Cannot open camera")
            return
        while True:
            success, frame = cap.read()
            if not success:
                break
            if overlay_mode:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray)
                for face_box in faces:
                    frame = overlay_glasses_on_face(frame, face_box, glasses_img)
            _, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        return

    if source == "remote_lenna":
        cap = cv2.VideoCapture("http://IP:8080/video")
        if not cap.isOpened():
            print("Cannot open remote camera")
            return
        overlay = cv2.imread(overlay_image_path, cv2.IMREAD_UNCHANGED)
        while True:
            success, frame = cap.read()
            if not success:
                break
            if overlay_mode and overlay is not None:
                
                target_width = frame.shape[1] // 7
                aspect_ratio = overlay.shape[0] / overlay.shape[1]
                target_height = int(target_width * aspect_ratio) 
                resized_overlay = cv2.resize(overlay, (target_width, target_height), interpolation=cv2.INTER_AREA)
                oh, ow = resized_overlay.shape[:2]
                if frame.shape[0] >= oh and frame.shape[1] >= ow:
                    roi = frame[-oh:, :ow]
                    if resized_overlay.shape[2] == 4:
                        alpha = resized_overlay[:, :, 3] / 255.0
                        for c in range(3):
                            roi[:, :, c] = roi[:, :, c] * (1 - alpha) + resized_overlay[:, :, c] * alpha
                    else:
                        roi[:] = resized_overlay[:, :, :3]
                    frame[-oh:, :ow] = roi
            _, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        return

    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        print("Cannot open source")
        return
    overlay = cv2.imread(overlay_image_path, cv2.IMREAD_UNCHANGED)
    while True:
        success, frame = cap.read()
        if not success:
            break
        if overlay_mode and overlay is not None:
            target_width = frame.shape[1] // 2
            aspect_ratio = overlay.shape[0] / overlay.shape[1]
            target_height = int(target_width * aspect_ratio)
            resized_overlay = cv2.resize(overlay, (target_width, target_height), interpolation=cv2.INTER_AREA)
            oh, ow = resized_overlay.shape[:2]
            if frame.shape[0] >= oh and frame.shape[1] >= ow:
                roi = frame[-oh:, :ow]
                if resized_overlay.shape[2] == 4:
                    alpha = resized_overlay[:, :, 3] / 255.0
                    for c in range(3):
                        roi[:, :, c] = roi[:, :, c] * (1 - alpha) + resized_overlay[:, :, c] * alpha
                else:
                    roi[:] = resized_overlay[:, :, :3]
                frame[-oh:, :ow] = roi
        _, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')


@app.route("/", methods=["GET", "POST"])
def index():
    global selected_source
    if request.method == "POST":
        selected_source = request.form.get("stream_source")
    return render_template("index.html", sources=VIDEO_SOURCES, selected=selected_source)


@app.route("/video_feed")
def video_feed():
    from flask import request
    mode = request.args.get("mode", "original")
    overlay_mode = mode == "overlay"
    if selected_source is None:
        return "No stream selected", 400
    source = VIDEO_SOURCES[selected_source]
    return Response(generate_frames(source, overlay_mode),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    app.run(debug=True)
