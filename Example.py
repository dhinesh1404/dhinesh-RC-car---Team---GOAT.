import cv2
import numpy as np
import lgpio
import time

# --- GPIO Pin Setup ---
DC_MOTOR_IN1 = 23    # GPIO pin for DC motor direction 1
DC_MOTOR_IN2 = 24    # GPIO pin for DC motor direction 2
DC_MOTOR_ENA = 25    # GPIO pin for DC motor speed (ENA, PWM control)
SERVO_PIN = 18       # GPIO pin for servo motor

# --- Initialize GPIO ---
h = lgpio.gpiochip_open(0)
lgpio.gpio_claim_output(h, DC_MOTOR_IN1)
lgpio.gpio_claim_output(h, DC_MOTOR_IN2)
lgpio.gpio_claim_output(h, DC_MOTOR_ENA)
lgpio.gpio_claim_output(h, SERVO_PIN)

# --- DC Motor Control ---
def dc_motor_control(direction, speed):
    if direction == "forward":
        lgpio.gpio_write(h, DC_MOTOR_IN1, 1)
        lgpio.gpio_write(h, DC_MOTOR_IN2, 0)
    elif direction == "backward":
        lgpio.gpio_write(h, DC_MOTOR_IN1, 0)
        lgpio.gpio_write(h, DC_MOTOR_IN2, 1)
    elif direction == "stop":
        lgpio.gpio_write(h, DC_MOTOR_IN1, 0)
        lgpio.gpio_write(h, DC_MOTOR_IN2, 0)

    lgpio.tx_pwm(h, DC_MOTOR_ENA, 1000, speed)  # Speed: duty cycle (0-100)

# --- Servo Control ---
def servo_control(angle):
    # Convert angle to PWM duty cycle (500-2500 ?s for 0-180 degrees)
    duty_cycle = 500 + (angle / 180) * 2000
    lgpio.tx_servo(h, SERVO_PIN, int(duty_cycle))

# --- Image Processing for White Line Detection ---
def process_frame(frame):
    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian Blur
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Apply Thresholding to detect white lines
    _, binary = cv2.threshold(blurred, 200, 255, cv2.THRESH_BINARY)  # White is high intensity (close to 255)
    
    # Display the thresholded image for debugging
    cv2.imshow("Thresholded Image", binary)
    
    # Define Region of Interest (ROI) to focus on the lower part of the frame
    height, width = binary.shape
    roi = binary[int(height * 0.6):height, :]  # Bottom 40% of the frame
    
    # Find edges of the line (left and right)
    left_edge = np.argmax(roi, axis=1)  # Leftmost white pixel for each row
    right_edge = width - np.argmax(np.flip(roi, axis=1), axis=1) - 1  # Rightmost white pixel for each row
    
    # Remove rows without a valid line detection
    valid_rows = np.where((left_edge > 0) & (right_edge < width - 1))[0]
    if len(valid_rows) > 0:
        # Calculate the average position of the left and right edges
        avg_left = np.mean(left_edge[valid_rows])
        avg_right = np.mean(right_edge[valid_rows])
        
        # Calculate the center of the line
        center_x = (avg_left + avg_right) / 2
        return center_x, width
    else:
        return None, width

# --- Line Following Logic (Center Focused) ---
def follow_line(frame):
    center_x, frame_width = process_frame(frame)
    if center_x is not None:
        # Visualize the detected center point on the frame
        cv2.circle(frame, (int(center_x), int(frame.shape[0] * 0.8)), 5, (0, 255, 0), -1)
        
        # Calculate how far the detected line center is from the middle of the frame
        center = frame_width // 2
        error = center_x - center
        
        # Adjust servo to keep the car on the center of the line
        if error < -50:  # Line is too far left, turn left
            servo_control(30)  # Turn left
            print("Steering Left")
        elif error > 50:  # Line is too far right, turn right
            servo_control(80)  # Turn right
            print("Steering Right")
        else:  # Line is near the center, go straight
            servo_control(49)  # Keep straight
            print("Steering Center")
        
        # Move the car forward
        dc_motor_control("forward", 40)
    else:
        # Stop the motor if no line is detected
        dc_motor_control("stop", 0)
        print("Line not detected, stopping")

# --- Capture Images and Process in Real-Time ---
def main():
    cap = cv2.VideoCapture(0)  # Initialize camera
    if not cap.isOpened():
        print("Error: Could not open the camera")
        return

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to capture frame")
                break
            
            # Process the frame and follow the line
            follow_line(frame)
            
            # Display the processed frame for debugging
            cv2.imshow("Line Tracking", frame)
            
            # Exit on pressing 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        # Clean up resources
        cap.release()
        cv2.destroyAllWindows()
        dc_motor_control("stop", 0)
        servo_control(49)  # Reset servo to center
        lgpio.gpiochip_close(h)
        print("Program exited and GPIO cleaned up.")

# --- Run the Main Loop ---
if __name__ == "__main__":
    main()
