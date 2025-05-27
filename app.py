from flask import Flask, render_template, request, Response
import cv2
import yt_dlp

app = Flask(__name__)

VIDEO_SOURCES = {
    "YouTube Live A": "https://www.youtube.com/embed/Ndo_8RuefH4?si=qgaWkMBZWD5-X6kU&amp",
    "YouTube Live B": "https://www.youtube.com/embed/xwAWSh35uuw?si=Rv2FPTao_XJZLh0Z&amp",
    "YouTube Live C": "https://www.youtube.com/embed/XSD5ptYisw8?si=tDpZPxhEZyT9DGNg&amp",
    "Webcam": 0,
    "Local File": "sample.mp4"
}

selected_source = None
overlay_image_path = "Lenna.jpg"

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

def generate_frames(source, overlay_mode=False):
    if isinstance(source, str) and "youtube.com" in source:
        source = resolve_youtube_stream(source)

    print("Opening source:", source)
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        print("❌ Failed to open video source.")
        return

    overlay = cv2.imread(overlay_image_path, cv2.IMREAD_UNCHANGED)

    while True:
        success, frame = cap.read()
        if not success:
            break

        if overlay_mode and overlay is not None:
            oh, ow = overlay.shape[:2]
            if frame.shape[0] >= oh and frame.shape[1] >= ow:
                roi = frame[-oh:, :ow]
                if overlay.shape[2] == 4:
                    alpha = overlay[:, :, 3] / 255.0
                    for c in range(3):
                        roi[:, :, c] = roi[:, :, c] * (1 - alpha) + overlay[:, :, c] * alpha
                else:
                    roi[:] = overlay[:, :, :3]
                frame[-oh:, :ow] = roi

        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

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
