import lgpio
import time
import sys
import termios
import tty
import cv2  # OpenCV library for camera handling

# Pin setup for Servo Motor
SERVO_PIN = 18          # GPIO pin for servo motor

# Pin setup for DC Motor
DC_MOTOR_IN1 = 23    # GPIO pin for DC motor direction 1 (IN1)
DC_MOTOR_IN2 = 24    # GPIO pin for DC motor direction 2 (IN2)
DC_MOTOR_ENA = 25    # GPIO pin for DC motor speed (ENA, PWM control)

# Initialize lgpio for the Servo Motor and DC Motor
h = lgpio.gpiochip_open(0)
lgpio.gpio_claim_output(h, SERVO_PIN)
lgpio.gpio_claim_output(h, DC_MOTOR_IN1)
lgpio.gpio_claim_output(h, DC_MOTOR_IN2)
lgpio.gpio_claim_output(h, DC_MOTOR_ENA)

# Initialize OpenCV camera capture
cap = cv2.VideoCapture(0)  # 0 for default camera
if not cap.isOpened():
    print("Error: Could not open video stream")
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

# Function to control Servo motor angle
def set_servo_angle(angle):
    duty_cycle = (5 + (angle / 180) * 5)  # Scale 0-180� to 5%-10% duty cycle
    lgpio.tx_pwm(h, SERVO_PIN, 50, duty_cycle)  # 50Hz frequency
    time.sleep(0.3)

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

# Main loop to control both motors with keyboard input and display camera feed
try:
    print("Controls:")
    print("Servo Controls: Q - Turn Left, E - Turn Right, R - Center")
    print("DC Motor Controls: I - Forward, K - Backward, + - Increase Speed, - - Decrease Speed, X - Stop Motor, C - Quit")

    # Initial conditions
    current_servo_angle = 70  # Initial servo angle (centered)
    current_speed = 30  # Initial speed (0 to 100)
    current_direction = "stop"  # Initial direction for DC motor

    while True:
        key = get_key()
        print(f"Key pressed: {repr(key)}")  # Debugging key press

        # Servo controls
        if key == 'q':  # Turn servo left
            if current_servo_angle > 30:
                current_servo_angle -= 10
                set_servo_angle(current_servo_angle)
                print(f"Servo turning left to {current_servo_angle} degrees")
        elif key == 'e':  # Turn servo right
            if current_servo_angle < 100:
                current_servo_angle += 10
                set_servo_angle(current_servo_angle)
                print(f"Servo turning right to {current_servo_angle} degrees")
        elif key == 'r':  # Center the servo
            current_servo_angle = 70
            set_servo_angle(current_servo_angle)
            print("Servo centered")

        # DC motor controls
        elif key == 'i':  # Move DC motor forward
            current_direction = "forward"
            dc_motor_control(current_direction, current_speed)
        elif key == 'k':  # Move DC motor backward
            current_direction = "backward"
            dc_motor_control(current_direction, current_speed)
        elif key == 'x':  # Stop DC motor
            current_direction = "stop"
            dc_motor_control(current_direction, 0)
        elif key == '+':  # Increase DC motor speed
            if current_speed < 50:
                current_speed += 10
            print(f"DC Motor speed increased to {current_speed}")
            dc_motor_control(current_direction, current_speed)
        elif key == '-':  # Decrease DC motor speed
            if current_speed > 0:
                current_speed -= 10
            print(f"DC Motor speed decreased to {current_speed}")
            dc_motor_control(current_direction, current_speed)

        # Quit condition
        elif key == 'c':  # Quit
            break
        
        # Capture frame from camera
        ret, frame = cap.read()
        if ret:
            # Display the captured frame in a window
            cv2.imshow("Camera Feed", frame)
        else:
            print("Error: Failed to capture frame")

        # Wait for key press to update the display and control motors
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    # Clean up
    dc_motor_control("stop", 0)
    lgpio.gpiochip_close(h)
    cap.release()  # Release the camera
    cv2.destroyAllWindows()  # Close all OpenCV windows
    print("Program exited and GPIO cleaned up.")
