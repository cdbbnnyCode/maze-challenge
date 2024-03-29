#!/usr/bin/env python3

import servo
import json

# X_MIN = 0.0100
# Y_MIN = 0.3200
# X_MAX = 0.1100
# Y_MAX = 0.5600

def init():
    global X_MIN, X_MAX, Y_MIN, Y_MAX, orientation
    with open('calibration.json', 'r') as f:
        conf = json.load(f)
        X_MIN = conf['xmin']
        Y_MIN = conf['ymin']
        X_MAX = conf['xmax']
        Y_MAX = conf['ymax']
    try:
        with open('/tmp/orientation.json', 'r') as f:
            conf = json.load(f)
            orientation = conf
#            if '+' in conf['down']: # Should be - ; swap otherwise
#                temp = X_MIN
#                X_MIN = X_MAX
#                X_MAX = temp
#            if '+' in conf['left']: # Should also be -
#                temp = Y_MIN
#                Y_MIN = Y_MAX
#                Y_MAX = temp
#            if 'y' in conf['down']: # should be -x
#                tmin = X_MIN
#                X_MIN = Y_MIN
#                Y_MIN = tmin
#                tmax = X_MAX
#                X_MAX = Y_MAX
#                Y_MAX = tmax
    except:
        pass

def get_servo_pos(axis, val):
    """
    Convert values from the interpreted program into calibrated servo positions.
    The axis parameter is used to choose the correct calibration values.
    This function also constrains the input value between -1 and 1.
    """
    # Input is -1..1
    if val < -1: val = -1
    elif val > 1: val = 1
    val = (float(val) + 1) / 2 # Adjust input range to 0..1
    if axis == 'X':
        return X_MIN + val * (X_MAX - X_MIN)
    elif axis == 'Y':
        return Y_MIN + val * (Y_MAX - Y_MIN)
    else:
        print("Warning: (Programmer Error) Undefined axis %s" % axis)
        return 0

def end():
    """
    Disable the servo outputs at the end of the program.
    """
    servo.disable_servos()

def reorient(x, y):
    rx = x
    ry = y
    if orientation['down'] == '+x':   rx = -x
    elif orientation['down'] == '+y': ry = -x
    elif orientation['down'] == '-y': ry =  x
    if orientation['left'] == '+y':   ry = -y
    elif orientation['left'] == '+x': rx = -y
    elif orientation['left'] == '-x': rx =  y
    print("%s: (%.1f,%.1f) -> (%.1f,%.1f)" % (orientation, x, y, rx, ry))
    return (rx, ry)

def read_command(line):
    """
    Read and execute a line of user code. Does not delay at the end of the line!
    Returns 0 on success, and 1 if a syntax error occurred.
    """
    x = 0
    y = 0
    line = line.upper()
    i = 0
    while i < len(line):
        c = line[i]
        cmd_col = i # Save where we were before we look ahead
        # Look ahead for an amount
        amount = 1
        amt_str = ''
        while i < len(line)-1 and line[i+1] in '-.0123456789':
            i += 1
            amt_str += line[i]
        if amt_str != '':
            try:
                amount = float(amt_str)
            except ValueError:
                print("Syntax error: '%s' is not a number!" % amt_str)
                return 1
        
        if c not in 'UDLR':
            print("Syntax Error (col %d): Expected U, D, L, or R; got '%s'" % (cmd_col + 1, c))
            return 1
        if c == 'U':
            x = amount
        elif c == 'D':
            x = -amount
        elif c == 'L':
            y = -amount
        elif c == 'R':
            y = amount
        
        i += 1
    x, y = reorient(x, y)
    print("X: %.4f, Y: %.4f" % (x, y))
    servo.set_servo_angle(servo.SERVO_VERT, get_servo_pos('X', x))
    servo.set_servo_angle(servo.SERVO_HORIZ, get_servo_pos('Y', y))
    return 0
    
            
