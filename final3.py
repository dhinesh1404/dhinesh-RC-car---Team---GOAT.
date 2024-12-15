import lgpio
import time
import threading
import cv2  # OpenCV for camera handling
import os
import sys
import termios
import tty

# Pin setup for DC Motor
DC_MOTOR_IN1 = 23    # GPIO pin for DC motor direction 1 (IN1)
DC_MOTOR_IN2 = 24    # GPIO pin for DC motor direction 2 (IN2)
DC_MOTOR_ENA = 25    # GPIO pin for DC motor speed (ENA, PWM control)

# Pin setup for Servo Motor
SERVO_PIN = 18  # GPIO pin for servo motor PWM signal

# Initialize lgpio for the DC motor
h = lgpio.gpiochip_open(0)
lgpio.gpio_claim_output(h, DC_MOTOR_IN1)
lgpio.gpio_claim_output(h, DC_MOTOR_IN2)
lgpio.gpio_claim_output(h, DC_MOTOR_ENA)
lgpio.gpio_claim_output(h, SERVO_PIN)

# Initialize OpenCV camera
cap = cv2.VideoCapture(0)  # Use the default camera (usually 0)
if not cap.isOpened():
    print("Error: Could not open the camera")
    sys.exit()
else:
    print("Camera opened successfully.")

# Helper function to read keyboard input
def get_key():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

# Function to control DC motor direction and speed
def dc_motor_control(direction, speed):
    if direction == "forward":
        lgpio.gpio_write(h, DC_MOTOR_IN1, 1)
        lgpio.gpio_write(h, DC_MOTOR_IN2, 0)
        print("Motor moving forward")
    elif direction == "backward":
        lgpio.gpio_write(h, DC_MOTOR_IN1, 0)
        lgpio.gpio_write(h, DC_MOTOR_IN2, 1)
        print("Motor moving backward")
    elif direction == "stop":
        lgpio.gpio_write(h, DC_MOTOR_IN1, 0)
        lgpio.gpio_write(h, DC_MOTOR_IN2, 0)
        print("Motor stopped")
    
    # Set motor speed using PWM (duty cycle)
    lgpio.tx_pwm(h, DC_MOTOR_ENA, 1000, speed)  # Frequency: 1kHz, Speed: duty cycle (0-100)

# Function to control Servo Motor
def servo_control(angle):
    # Convert the angle (0-180 degrees) to PWM duty cycle
    duty_cycle = 500 + (angle / 180) * 2000  # Duty cycle in microseconds
    lgpio.tx_servo(h, SERVO_PIN, int(duty_cycle))
    print(f"Servo moved to {angle} degrees")

# Function to continuously capture and save images
def capture_images():
    desktop_path = "/home/pi/Desktop"  # Path to save images
    while capturing:  # Run until capturing is set to False
        ret, frame = cap.read()
        if ret:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            image_filename = os.path.join(desktop_path, f"captured_image_{timestamp}.jpg")
            cv2.imwrite(image_filename, frame)
            print(f"Image saved as {image_filename}")
        time.sleep(0.5)  # Capture an image every 0.5 seconds

# Main loop to control motor, servo, and image capture
try:
    print("Controls:")
    print("W - Forward, S - Backward, + - Increase Speed, - - Decrease Speed")
    print("A - Servo Left, D - Servo Right, X - Stop Motor, E - Quit")
    
    current_speed = 30  # Initial speed (0 to 100)
    current_direction = "stop"  # Initial direction
    servo_angle = 90  # Center position for servo

    # Start image capture thread
    capturing = True
    capture_thread = threading.Thread(target=capture_images)
    capture_thread.start()

    while True:
        key = get_key()

        # DC Motor Controls
        if key == 'w':  # Move forward
            current_direction = "forward"
            dc_motor_control(current_direction, current_speed)
        elif key == 's':  # Move backward
            current_direction = "backward"
            dc_motor_control(current_direction, current_speed)
        elif key == 'x':  # Stop motor
            current_direction = "stop"
            dc_motor_control(current_direction, 0)
        elif key == '+':  # Increase speed
            if current_speed < 100:
                current_speed += 10
            print(f"Speed increased to {current_speed}")
            dc_motor_control(current_direction, current_speed)
        elif key == '-':  # Decrease speed
            if current_speed > 0:
                current_speed -= 10
            print(f"Speed decreased to {current_speed}")
            dc_motor_control(current_direction, current_speed)

        # Servo Motor Controls
        elif key == 'a':  # Turn servo left
            servo_angle = max(0, servo_angle - 10)  # Decrease angle but not below 0
            servo_control(servo_angle)
        elif key == 'd':  # Turn servo right
            servo_angle = min(180, servo_angle + 10)  # Increase angle but not above 180
            servo_control(servo_angle)

        # Quit program
        elif key == 'e':
            break

finally:
    # Stop capturing images
    capturing = False
    capture_thread.join()  # Wait for the capture thread to finish

    # Clean up resources
    dc_motor_control("stop", 0)
    lgpio.tx_servo(h, SERVO_PIN, 0)  # Turn off servo
    lgpio.gpiochip_close(h)
    cap.release()  # Release the camera
    cv2.destroyAllWindows()  # Close OpenCV windows
    print("Program exited and GPIO cleaned up.")
