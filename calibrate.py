import getch
import sys
import os
import servo
import interp
import json
import time

def get_key():
    k = getch.getch()
    if k == '\x03':
        raise KeyboardInterrupt()
    if k == '\x1B':
        getch.getch() # [
        sub = getch.getch()
        return "\\" + sub
    else:
        return k

print("Marble Maze Calibrator")
print("Version 1.1")
print("Press any key to begin")
print()
get_key()

servo.init_outputs()

###############################
# Step 1: Choose the horizontal tilt servo
print("Choose an axis")
print("Press 1 or 2 to test one, and press Enter to continue")
print("Choose the option that tilts up and down")

def test_servo(pin):
    servo.set_servo_angle(pin, 0)
    time.sleep(0.05)
    servo.set_servo_angle(pin, 1)
    time.sleep(0.05)
    servo.disable_servo(pin)

hservo = -1
while True:
    k = get_key()
    if k == '1':
        print('1', end='\r')
        hservo = 12
        test_servo(12)
    elif k == '2':
        print('2', end='\r')
        hservo = 13
        test_servo(13)
    elif k == '\r':
        print()
        break

if hservo >= 0:
    servo.SERVO_HORIZ = hservo
    servo.SERVO_VERT  = 25 - hservo

print()
print("Level the maze")
print("Use the arrow keys to adjust the position")
print("Press Enter to continue")

x_center = interp.get_servo_pos('X', 0)
y_center = interp.get_servo_pos('Y', 0)
while True:
    print("%.2f, %.2f" % (x_center, y_center), end='\r')
    servo.set_servo_angle(servo.SERVO_HORIZ, y_center)
    servo.set_servo_angle(servo.SERVO_VERT, x_center)
    k = get_key()
    sub = ""
    if len(k) > 1:
        sub = k[1]

    # \x1B arrow key codes:
    # A=Up, B=Down, C=Right, D=Left
    if sub == 'A':
        x_center += 0.01
        if x_center > 1:
            x_center = 1
    elif sub == 'B':
        x_center -= 0.01
        if x_center < 0:
            x_center = 0
    elif sub == 'C':
        y_center += 0.01
        if y_center > 1:
            y_center = 1
    elif sub == 'D':
        y_center -= 0.01
        if y_center < 0:
            y_center = 0
    elif k == '\r':
        print()
        break

print()
print("Set the maximum travel")
print("Use the arrow keys to adjust horizontal and vertical travel")
print("Use WASD to test the adjustment")
print("Press Enter to finish")

x_range = 0
y_range = 0
x_hold = 0
y_hold = 0

while True:
    print("%.2f, %.2f" % (x_range, y_range), end='\r')
    k = get_key()
    sub = ""
    if len(k) > 1:
        sub = k[1]

    # A=Up, B=Down, C=Right, D=Left
    if sub == 'A':
        x_range += 0.01
    elif sub == 'B':
        x_range -= 0.01
    elif sub == 'C':
        y_range += 0.01
    elif sub == 'D':
        y_range -= 0.01
    elif k == 'w':
        x_hold = 1
    elif k == 'a':
        y_hold = -1
    elif k == 's':
        x_hold = -1
    elif k == 'd':
        y_hold = 1
    elif k == '\r':
        print()
        break

    if x_center - x_range < 0:
        x_range = x_center
    elif x_center + x_range > 1:
        x_range = 1 - x_center
    if y_center - y_range < 0:
        y_range = y_center
    elif y_center + y_range > 1:
        y_range = 1 - y_center

    x_pos = x_center + x_hold * x_range
    y_pos = y_center + y_hold * y_range

    servo.set_servo_angle(servo.SERVO_HORIZ, y_pos)
    servo.set_servo_angle(servo.SERVO_VERT, x_pos)

interp.X_MIN = x_center - x_range
interp.Y_MIN = y_center - y_range
interp.X_MAX = x_center + x_range
interp.Y_MAX = y_center + y_range

with open('calibration.json', 'w') as f:
    conf = {'horiz': servo.SERVO_HORIZ,
            'vert': servo.SERVO_VERT,
            'xmin': interp.X_MIN,
            'xmax': interp.X_MAX,
            'ymin': interp.Y_MIN,
            'ymax': interp.Y_MAX}
    json.dump(conf, f)

