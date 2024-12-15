import cv2

# Open the camera (0 is usually the default camera)
cap = cv2.VideoCapture(0)

# Check if the camera opened correctly
if not cap.isOpened():
    print("Error: Camera not detected.")
    exit()

print("Press 'q' to exit.")

try:
    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to grab frame.")
            break
        
        # Display the resulting frame
        cv2.imshow('Camera Test', frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    # Release the camera and close all OpenCV windows
    cap.release()
    cv2.destroyAllWindows()
