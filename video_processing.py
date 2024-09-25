import cv2
import numpy as np
import logging
import time

# Configure logging for debugging
logging.basicConfig(level=logging.INFO)

def nothing(x):
    pass

def create_trackbars():
    cv2.namedWindow("Trackbars")
    cv2.createTrackbar("LH", "Trackbars", 30, 255, nothing)
    cv2.createTrackbar("LS", "Trackbars", 40, 255, nothing)
    cv2.createTrackbar("LV", "Trackbars", 40, 255, nothing)
    cv2.createTrackbar("UH", "Trackbars", 80, 255, nothing)
    cv2.createTrackbar("US", "Trackbars", 255, 255, nothing)
    cv2.createTrackbar("UV", "Trackbars", 255, 255, nothing)

def get_trackbar_values():
    lh = cv2.getTrackbarPos("LH", "Trackbars")
    ls = cv2.getTrackbarPos("LS", "Trackbars")
    lv = cv2.getTrackbarPos("LV", "Trackbars")
    uh = cv2.getTrackbarPos("UH", "Trackbars")
    us = cv2.getTrackbarPos("US", "Trackbars")
    uv = cv2.getTrackbarPos("UV", "Trackbars")
    return np.array([lh, ls, lv]), np.array([uh, us, uv])

def create_mask(hsv_frame, lower_bound, upper_bound):
    mask = cv2.inRange(hsv_frame, lower_bound, upper_bound)
    _, mask = cv2.threshold(mask, 100, 255, cv2.THRESH_BINARY)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    return mask

def detect_and_draw_contours(frame, contours, color, label):
    for contour in contours:
        if cv2.contourArea(contour) > 100:
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

def process_video(stop_flag):
    cap = cv2.VideoCapture(0)
    logging.info("Video capture initialized")

    create_trackbars()

    prev_frame_time = 0
    frame_skip = 5
    frame_count = 0

    while cap.isOpened() and not stop_flag():
        frame_count += 1
        ret, frame = cap.read()
        if not ret:
            logging.warning("Frame capture failed")
            break
        
        if frame_count % frame_skip != 0:
            continue

        frame = cv2.flip(frame, 1)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        lower_green, upper_green = get_trackbar_values()
        lower_red = np.array([0, 100, 100])
        upper_red = np.array([10, 255, 255])

        green_mask = create_mask(hsv, lower_green, upper_green)
        red_mask = create_mask(hsv, lower_red, upper_red)

        red_contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        green_contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        logging.debug(f"Red contours detected: {len(red_contours)}")
        logging.debug(f"Green contours detected: {len(green_contours)}")

        detect_and_draw_contours(frame, red_contours, (0, 0, 255), "Enemy")
        detect_and_draw_contours(frame, green_contours, (0, 255, 0), "Ally")

        new_frame_time = time.time()
        fps = 1 / (new_frame_time - prev_frame_time)
        prev_frame_time = new_frame_time

        cv2.putText(frame, f"FPS: {int(fps)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.imshow("Camera", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
