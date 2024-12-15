import lgpio
import time
import curses

# Define GPIO pins
SERVO_PIN = 18
DC_IN1 = 23
DC_IN2 = 24
DC_ENA = 25

# Setup GPIO
gpio = lgpio.gpiochip_open(0)  # Open GPIO chip 0 (usually the first chip on the Raspberry Pi)
lgpio.gpio_claim(gpio, SERVO_PIN, lgpio.OUTPUT)
lgpio.gpio_claim(gpio, DC_IN1, lgpio.OUTPUT)
lgpio.gpio_claim(gpio, DC_IN2, lgpio.OUTPUT)
lgpio.gpio_claim(gpio, DC_ENA, lgpio.OUTPUT)

# Set servo pulse width to center (adjust as needed)
def set_servo_angle(angle):
    pulse_width = int((angle / 180) * 2000 + 1000)  # 1000 to 2000 for 0 to 180 degrees
    lgpio.gpio_pwm(gpio, SERVO_PIN, pulse_width)
    time.sleep(0.5)

# DC Motor forward
def motor_forward():
    lgpio.gpio_write(gpio, DC_IN1, 1)
    lgpio.gpio_write(gpio, DC_IN2, 0)
    lgpio.gpio_pwm(gpio, DC_ENA, 255)  # Set speed (0-255)
    time.sleep(2)

# DC Motor backward
def motor_backward():
    lgpio.gpio_write(gpio, DC_IN1, 0)
    lgpio.gpio_write(gpio, DC_IN2, 1)
    lgpio.gpio_pwm(gpio, DC_ENA, 255)  # Set speed (0-255)
    time.sleep(2)

# DC Motor stop
def motor_stop():
    lgpio.gpio_write(gpio, DC_IN1, 0)
    lgpio.gpio_write(gpio, DC_IN2, 0)
    lgpio.gpio_pwm(gpio, DC_ENA, 0)  # Stop the motor
    time.sleep(1)

# Main control loop
def main(stdscr):
    # Clear screen and set up the window
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(100)

    # Initial servo position
    servo_angle = 90
    set_servo_angle(servo_angle)

    while True:
        key = stdscr.getch()

        if key == ord('q'):  # Quit
            break
        elif key == curses.KEY_UP:  # Move forward
            motor_forward()
        elif key == curses.KEY_DOWN:  # Move backward
            motor_backward()
        elif key == curses.KEY_LEFT:  # Turn left
            servo_angle = max(0, servo_angle - 10)  # Left steering
            set_servo_angle(servo_angle)
        elif key == curses.KEY_RIGHT:  # Turn right
            servo_angle = min(180, servo_angle + 10)  # Right steering
            set_servo_angle(servo_angle)

        motor_stop()  # Stop the motor after each movement

    # Cleanup
    lgpio.gpio_unclaim(gpio, SERVO_PIN)
    lgpio.gpio_unclaim(gpio, DC_IN1)
    lgpio.gpio_unclaim(gpio, DC_IN2)
    lgpio.gpio_unclaim(gpio, DC_ENA)
    print("Test complete")

# Initialize the curses library and run the main function
curses.wrapper(main)
