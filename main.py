from drive import Driver
from time import sleep

d = Driver()
sleep(1)

print("Left")
d.set_speed(100.0, 0)
sleep(3)

print("Right")
d.set_speed(0, 100.0)
sleep(3)

print("Both")
d.set_speed(100.0, 100.0)
sleep(3)

print("Back")
d.set_speed(-100.0, -100.0)
sleep(3)

d.kill()
