import cv2
import numpy as np
import time
import logging

# Configure logging for debugging and tracking execution
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def nothing(x):
    """Empty callback function required for creating trackbars."""
    pass

def create_trackbars(window_name="Trackbars"):
    """
    Creates trackbars for dynamically adjusting HSV color ranges. 
    This allows real-time color adjustments.
    """
    cv2.namedWindow(window_name)
    # Lower Hue, Saturation, and Value
    cv2.createTrackbar("LH", window_name, 30, 255, nothing)
    cv2.createTrackbar("LS", window_name, 40, 255, nothing)
    cv2.createTrackbar("LV", window_name, 40, 255, nothing)
    # Upper Hue, Saturation, and Value
    cv2.createTrackbar("UH", window_name, 80, 255, nothing)
    cv2.createTrackbar("US", window_name, 255, 255, nothing)
    cv2.createTrackbar("UV", window_name, 255, 255, nothing)

def get_trackbar_values(window_name="Trackbars"):
    """
    Retrieves the current positions of all trackbars (LH, LS, LV, UH, US, UV).
    This function allows dynamic color filtering adjustments.
    """
    lh = cv2.getTrackbarPos("LH", window_name)
    ls = cv2.getTrackbarPos("LS", window_name)
    lv = cv2.getTrackbarPos("LV", window_name)
    uh = cv2.getTrackbarPos("UH", window_name)
    us = cv2.getTrackbarPos("US", window_name)
    uv = cv2.getTrackbarPos("UV", window_name)
    
    logging.debug(f"Trackbar Values: LH={lh}, LS={ls}, LV={lv}, UH={uh}, US={us}, UV={uv}")
    
    return np.array([lh, ls, lv]), np.array([uh, us, uv])

def create_mask(hsv_frame, lower_bound, upper_bound):
    """
    Creates a binary mask where the specified HSV range is highlighted.
    The mask undergoes thresholding, erosion, and dilation to refine results.
    """
    mask = cv2.inRange(hsv_frame, lower_bound, upper_bound)
    _, mask = cv2.threshold(mask, 100, 255, cv2.THRESH_BINARY)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    logging.debug(f"Mask created with bounds: {lower_bound}-{upper_bound}")
    return mask

def detect_and_draw_contours(frame, contours, color, label):
    """
    Detects contours in the frame and draws bounding rectangles around them.
    Labels contours with specified text and color.
    """
    for contour in contours:
        if cv2.contourArea(contour) > 100:  # Ignore small areas
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            cv2.putText(frame, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            logging.debug(f"Contour detected and labeled: {label}, Area: {cv2.contourArea(contour)}")

def process_frame(frame, lower_green, upper_green, lower_red, upper_red):
    """
    Handles the processing of each frame: applying masks, finding contours, 
    and drawing labeled rectangles around detected objects.
    """
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Generate masks for red and green objects
    green_mask = create_mask(hsv, lower_green, upper_green)
    red_mask = create_mask(hsv, lower_red, upper_red)
    
    # Find contours for both masks
    red_contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    green_contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Log contour counts for debugging
    logging.debug(f"Red contours: {len(red_contours)}, Green contours: {len(green_contours)}")

    # Draw contours with labels
    detect_and_draw_contours(frame, red_contours, (0, 0, 255), "Enemy")
    detect_and_draw_contours(frame, green_contours, (0, 255, 0), "Ally")

def main():
    """Main function for capturing and processing video frames."""
    try:
        # Initialize video capture from default camera
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            logging.error("Failed to open video capture.")
            return
        
        logging.info("Video capture started.")
        create_trackbars()

        prev_frame_time = 0
        frame_skip = 5  # Process every nth frame
        frame_count = 0

        # Set predefined color bounds for red
        lower_red = np.array([0, 100, 100])
        upper_red = np.array([10, 255, 255])

        while cap.isOpened():
            frame_count += 1
            ret, frame = cap.read()
            if not ret:
                logging.warning("Failed to capture frame.")
                break
            
            # Skip frames for performance optimization
            if frame_count % frame_skip != 0:
                continue

            frame = cv2.flip(frame, 1)  # Mirror the frame horizontally
            lower_green, upper_green = get_trackbar_values()

            # Process the current frame
            process_frame(frame, lower_green, upper_green, lower_red, upper_red)

            # FPS calculation and display
            new_frame_time = time.time()
            fps = 1 / (new_frame_time - prev_frame_time)
            prev_frame_time = new_frame_time
            cv2.putText(frame, f"FPS: {int(fps)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            # Show the processed frame
            cv2.imshow("Camera Feed", frame)

            # Break loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord("q"):
                logging.info("Exiting video capture loop.")
                break

    except Exception as e:
        logging.error(f"Error occurred: {e}")
    finally:
        # Release resources
        cap.release()
        cv2.destroyAllWindows()
        logging.info("Video capture ended, resources released.")

if __name__ == "__main__":
    main()
