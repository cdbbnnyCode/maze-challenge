print("Importing libraries...")
import io
print("io")
import time
print("time")
import cv2
print("cv2")
import numpy as np
print("numpy")
import picamera
print("picamera")

camera = picamera.PiCamera()
current_thresh = 0
ratio = 3
kernel_size = 3
static_img = None

def imcapture(camera):
    stream = io.BytesIO()
    camera.capture(stream, format='jpeg', use_video_port=True)
    data = np.fromstring(stream.getvalue(), dtype=np.uint8)
    image = cv2.imdecode(data, 1)
    return image

def imshow(image, title="Image"):
    cv2.imshow(title, image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def set_threshold(val):
    global current_thresh
    current_thresh = val

def on_click(ev, x, y, param, p2):
    global static_img
    if ev != cv2.EV_LBUTTONDOWN: return
    static_img = imcapture(camera)

def process(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.blur(image, (5, 5))
    cv2.imshow("Blurred", blur)
    edges = cv2.Canny(blur, current_thresh, current_thresh * ratio, kernel_size)
    return edges

cv2.namedWindow("Camera view")
cv2.createTrackbar("Threshold", "Camera view", 0, 100, set_threshold)
cv2.setMouseCallback("Camera view", on_click, 0)
set_threshold(0)

while True:
    image = imcapture(camera)
    image = process(image)
    cv2.imshow("Camera view", image)
    cv2.waitKey(5)
