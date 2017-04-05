#Bibliotheken einbinden
import RPi.GPIO as GPIO
import time


def setup(gpio_trigger, gpio_echo):
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(gpio_trigger, GPIO.OUT)
    GPIO.setup(gpio_echo, GPIO.IN)

def measure_distance(gpio_trigger, gpio_echo):
    # send spike
    GPIO.output(gpio_trigger, True)
    time.sleep(0.00001)
    GPIO.output(gpio_trigger, False)

    # Measure ramp up
    error = False
    measure_start = time.time()
    pulse_start = time.time()
    while GPIO.input(gpio_echo) == 0:
        pulse_start = time.time()
        # Error when taking too long
        if (pulse_start - measure_start) * 17150 > 100:
            error = True
            break

    # Measure ramp down
    pulse_end = time.time()
    while GPIO.input(gpio_echo) == 1:
        pulse_end = time.time()
        # Error when taking too long
        if (pulse_end - measure_start) * 17150 > 300:
            error = True
            break

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    if error:
        distance = 0

    return distance

if __name__ == '__main__':
    # gpio pins
    GPIO_TRIGGER = 18
    GPIO_ECHO = 24

    setup(GPIO_TRIGGER, GPIO_ECHO)
    try:
        while True:
            distance = distance(GPIO_TRIGGER, GPIO_ECHO)
            print ("Measured distance = %.1f cm" % distance)
            time.sleep(1)

        # Beim Abbruch durch STRG+C resetten
    except KeyboardInterrupt:
        print("User stopped measurement.")
        GPIO.cleanup()
