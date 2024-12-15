import lgpio
import time
import threading
import cv2
import os
import sys
import termios
import tty

# Pin setup
DC_MOTOR_IN1 = 23
DC_MOTOR_IN2 = 24
DC_MOTOR_ENA = 25
SERVO_PIN = 18

# Initialize GPIO
h = lgpio.gpiochip_open(0)
lgpio.gpio_claim_output(h, DC_MOTOR_IN1)
lgpio.gpio_claim_output(h, DC_MOTOR_IN2)
lgpio.gpio_claim_output(h, DC_MOTOR_ENA)
lgpio.gpio_claim_output(h, SERVO_PIN)

# Initialize Camera
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open the camera")
    sys.exit()

# Thread-safe capturing control
capturing_event = threading.Event()

def get_key():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

# DC Motor Control
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
    lgpio.tx_pwm(h, DC_MOTOR_ENA, 1000, speed)

# Servo Motor Control
def servo_control(angle):
    duty_cycle = 500 + ((angle - 30) / (80 - 30)) * 2000
    lgpio.tx_servo(h, SERVO_PIN, int(duty_cycle))

# Image Capture
def capture_images():
    desktop_path = "/home/pi/Desktop/captured_images"
    os.makedirs(desktop_path, exist_ok=True)
    while capturing_event.is_set():
        ret, frame = cap.read()
        if ret:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            image_filename = os.path.join(desktop_path, f"captured_image_{timestamp}.jpg")
            cv2.imwrite(image_filename, frame)
        time.sleep(0.5)

try:
    print("Controls:")
    print("W - Forward, S - Backward, A - Servo Left, D - Servo Right")
    print("X - Stop, + - Increase Speed, - - Decrease Speed, E - Quit")
    print("C - Center Servo")

    center_angle = 49
    current_speed = 50
    current_direction = "stop"
    servo_angle = center_angle

    # Start Image Capture Thread
    capturing_event.set()
    capture_thread = threading.Thread(target=capture_images)
    capture_thread.start()

    while True:
        key = get_key()

        if key == 'i':  # Forward
            current_direction = "forward"
            dc_motor_control(current_direction, current_speed)
        elif key == 'k':  # Backward
            current_direction = "backward"
            dc_motor_control(current_direction, current_speed)
        elif key == 'x':  # Stop
            current_direction = "stop"
            dc_motor_control(current_direction, 0)
        elif key == '=':  # Increase Speed
            current_speed = min(current_speed + 5, 100)
        elif key == '-':  # Decrease Speed
            current_speed = max(current_speed - 5, 0)

        elif key == 'j':  # Servo Left
            if servo_angle > 30:
                servo_angle -= 3
                servo_control(servo_angle)
        elif key == 'l':  # Servo Right
            if servo_angle < 80:
                servo_angle += 3
                servo_control(servo_angle)
        elif key == 'c':  # Center Servo
            servo_angle = center_angle
            servo_control(servo_angle)

        elif key == 'e':  # Exit
            break

finally:
    capturing_event.clear()
    capture_thread.join()
    dc_motor_control("stop", 0)
    lgpio.tx_servo(h, SERVO_PIN, 0)
    lgpio.gpiochip_close(h)
    cap.release()
    cv2.destroyAllWindows()
