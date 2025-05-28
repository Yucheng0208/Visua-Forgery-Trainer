import cv2
import numpy as np

# 載入分類器（OpenCV 內建 XML）
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# 載入含透明背景的眼鏡圖片
glasses_img = cv2.imread('glasses.png', cv2.IMREAD_UNCHANGED)
if glasses_img is None:
    raise FileNotFoundError("❌ glasses.png 未找到，請放在同一資料夾內。")

# 若圖片不是 4 channel (RGBA)，補上 Alpha 通道
if glasses_img.shape[2] != 4:
    print("⚠️ 警告：眼鏡圖不是透明背景，系統將自動補上不透明 alpha。")
    b, g, r = cv2.split(glasses_img)
    alpha = np.ones(b.shape, dtype=b.dtype) * 255
    glasses_img = cv2.merge((b, g, r, alpha))


def overlay_glasses_on_face(frame, face_box, glasses_img):
    x, y, w, h = face_box

    # 設定眼鏡寬度約為人臉寬度的 90%
    glasses_width = int(w * 0.9)
    aspect_ratio = glasses_img.shape[0] / glasses_img.shape[1]
    glasses_height = int(glasses_width * aspect_ratio)

    # 眼鏡貼在人臉上部約 10% 高度處
    x1 = x + int((w - glasses_width) / 2) + int(w * 0.05)
    y1 = y + int(h * 0.10)
    x2 = x1 + glasses_width
    y2 = y1 + glasses_height

    # 邊界檢查，避免超出畫面
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)

    # 調整眼鏡大小
    resized_glasses = cv2.resize(glasses_img, (x2 - x1, y2 - y1), interpolation=cv2.INTER_AREA)
    alpha = resized_glasses[:, :, 3] / 255.0

    for c in range(3):
        frame[y1:y2, x1:x2, c] = (
            resized_glasses[:, :, c] * alpha +
            frame[y1:y2, x1:x2, c] * (1 - alpha)
        )
    return frame


# 啟用攝影機
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("❌ 無法開啟攝影機")

print("🎥 啟動中，按下 ESC 可結束")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray)

    for face_box in faces:
        frame = overlay_glasses_on_face(frame, face_box, glasses_img)

    cv2.imshow('🕶️ Glasses on Face', frame)

    # 按 ESC 離開
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
