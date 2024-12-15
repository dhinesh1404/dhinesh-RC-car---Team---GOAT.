import lgpio
import time
import sys
import termios
import tty

# Pin setup
SERVO_PIN = 18          # GPIO pin for servo motor

# Initialize lgpio for the servo motor
h = lgpio.gpiochip_open(0)
lgpio.gpio_claim_output(h, SERVO_PIN)

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
    # Calculate duty cycle for servo motor
    duty_cycle = (angle / 18) + 2  # Range: 2-12 for 0-180 degrees
    duty_cycle = max(2, min(duty_cycle, 12))  # Clamp the duty cycle to the valid range for the servo (2-12)
    
    # Convert duty cycle to a percentage of the PWM period
    lgpio.tx_pwm(h, SERVO_PIN, 50, duty_cycle)  # 50Hz frequency, duty cycle in percentage
    time.sleep(0.3)

# Smoothly move the servo by 10% increments (10 degrees)
def smooth_move_servo(start_angle, target_angle):
    # Calculate the step size (10 degrees)
    step_size = 10  # 10 degrees
    direction = 1 if target_angle > start_angle else -1  # Determine direction to move (up or down)

    # Move smoothly by stepping through each intermediate angle
    for angle in range(start_angle, target_angle, direction * step_size):
        set_servo_angle(angle)
        print(f"Moving to {angle} degrees")
        time.sleep(0.3)  # Small delay to make the movement smooth

    # Finally, move to the target angle
    set_servo_angle(target_angle)
    print(f"Arrived at {target_angle} degrees")

# Main loop to control servo motor direction with keyboard input
try:
    print("Controls: A - Turn Left, D - Turn Right, W - Center, Q - Quit")
    current_angle = 90  # Start with the servo at 90 degrees (center)
    while True:
        key = get_key()

        # Direction controls
        if key == 'a':  # Turn left
            if current_angle > 0:
                current_angle -= 10  # Decrease angle by 10 degrees
                smooth_move_servo(current_angle + 10, current_angle)  # Smooth transition from previous angle
                print("Turning Left")
        elif key == 'd':  # Turn right
            if current_angle < 180:
                current_angle += 10  # Increase angle by 10 degrees
                smooth_move_servo(current_angle - 10, current_angle)  # Smooth transition from previous angle
                print("Turning Right")
        elif key == 'w':  # Center
            current_angle = 80  # Reset to center
            smooth_move_servo(current_angle, current_angle)  # Smooth transition to center
            print("Centering Servo")
        elif key == 'q':  # Quit
            break

finally:
    lgpio.gpiochip_close(h)
    print("Program exited and GPIO cleaned up.")