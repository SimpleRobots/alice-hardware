import RPi.GPIO as GPIO

PWM_FREQ = 40
LEFT_PWM = 11
RIGHT_PWM = 3

LEFT_DIR_1 = 13
LEFT_DIR_2 = 15

RIGHT_DIR_1 = 5
RIGHT_DIR_2 = 7

MAX_SPEED_LEFT = 0.1142 * 2
MAX_SPEED_RIGHT = 0.1142 * 2
MAX_ALLOWED_POWER = 0.5
WHEELBASE = 0.2


class Driver(object):
    def __init__(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(LEFT_PWM, GPIO.OUT)
        GPIO.setup(RIGHT_PWM, GPIO.OUT)
        GPIO.setup(LEFT_DIR_1, GPIO.OUT)
        GPIO.setup(LEFT_DIR_2, GPIO.OUT)
        GPIO.setup(RIGHT_DIR_1, GPIO.OUT)
        GPIO.setup(RIGHT_DIR_2, GPIO.OUT)

        self.left_pwm = GPIO.PWM(LEFT_PWM, PWM_FREQ)
        self.right_pwm = GPIO.PWM(RIGHT_PWM, PWM_FREQ)

        self.left_pwm.start(0)
        self.right_pwm.start(0)

    def set_speed(self, v_left, v_right):
        # Cap the max speed, so that you do not set values larger than allowed
        v_left = max(min(v_left, MAX_SPEED_LEFT), -MAX_SPEED_LEFT)
        v_right = max(min(v_right, MAX_SPEED_RIGHT), -MAX_SPEED_RIGHT)

        # Transform speed to PWM
        v_left /= MAX_SPEED_LEFT / MAX_ALLOWED_POWER
        v_right /= MAX_SPEED_RIGHT / MAX_ALLOWED_POWER

        # Controll the motor direction correctly
        if v_left >= 0:
            GPIO.output(LEFT_DIR_1, GPIO.HIGH)
            GPIO.output(LEFT_DIR_2, GPIO.LOW)
        else:
            GPIO.output(LEFT_DIR_1, GPIO.LOW)
            GPIO.output(LEFT_DIR_2, GPIO.HIGH)
            v_left = -v_left

        if v_right >= 0:
            GPIO.output(RIGHT_DIR_1, GPIO.HIGH)
            GPIO.output(RIGHT_DIR_2, GPIO.LOW)
        else:
            GPIO.output(RIGHT_DIR_1, GPIO.LOW)
            GPIO.output(RIGHT_DIR_2, GPIO.HIGH)
            v_right = -v_right

        # Actually set the duty for the motor
        self.left_pwm.ChangeDutyCycle(v_left)
        self.right_pwm.ChangeDutyCycle(v_right)

    def kill(self):
        # When killing reseting the pwm so the motors deinitialize
        self.left_pwm.stop()
        self.right_pwm.stop()
        GPIO.cleanup()
