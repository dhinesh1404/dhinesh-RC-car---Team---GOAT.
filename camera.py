import cv2

# Open the camera (0 is usually the default camera for USB cameras)
camera_index = 0
cap = cv2.VideoCapture(camera_index)

# Check if the camera opened successfully
if not cap.isOpened():
    print("Error: Could not open the camera.")
else:
    print("Press 'q' to exit the video feed.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        # Display the video frame
        cv2.imshow("Live Video Feed", frame)

        # Exit when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the camera and close all OpenCV windows
    cap.release()
    cv2.destroyAllWindows()
