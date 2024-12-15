import lgpio
import time
import sys
import termios
import tty

# Pin setup
DC_MOTOR_IN1 = 23    # GPIO pin for DC motor direction 1 (IN1)
DC_MOTOR_IN2 = 24    # GPIO pin for DC motor direction 2 (IN2)
DC_MOTOR_ENA = 25    # GPIO pin for DC motor speed (ENA, PWM control)

# Initialize lgpio for the DC motor
h = lgpio.gpiochip_open(0)
lgpio.gpio_claim_output(h, DC_MOTOR_IN1)
lgpio.gpio_claim_output(h, DC_MOTOR_IN2)
lgpio.gpio_claim_output(h, DC_MOTOR_ENA)

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

# Main loop to control motor direction and speed with keyboard input
try:
    print("Controls: W - Forward, S - Backward, + - Increase Speed, - - Decrease Speed, X - Stop Motor, E - Quit")
    
    current_speed = 50  # Initial speed (0 to 100)
    current_direction = "stop"  # Initial direction

    while True:
        key = get_key()

        # Direction controls
        if key == 'w':  # Move forward
            current_direction = "forward"
            dc_motor_control(current_direction, current_speed)
        elif key == 's':  # Move backward
            current_direction = "backward"
            dc_motor_control(current_direction, current_speed)
        elif key == 'x':  # Stop motor but not quit program
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
        elif key == 'e':  # Quit
            break

finally:
    # Clean up
    dc_motor_control("stop", 0)
    lgpio.gpiochip_close(h)
    print("Program exited and GPIO cleaned up.")