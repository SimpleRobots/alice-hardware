import RPi.GPIO as GPIO

PWM_FREQ = 20
LEFT_PWM = 11
RIGHT_PWM = 3

LEFT_DIR_1 = 13
LEFT_DIR_2 = 15

RIGHT_DIR_1 = 5
RIGHT_DIR_2 = 7

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

        self.left_pwm.ChangeDutyCycle(v_left)
        self.right_pwm.ChangeDutyCycle(v_right)

    def kill(self):
        self.left_pwm.stop()
        self.right_pwm.stop()
        GPIO.cleanup()
