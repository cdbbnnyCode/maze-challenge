#!/usr/bin/env python3

import servo

X_MIN = 0.0100
Y_MIN = 0.3400
X_MAX = 0.1100
Y_MAX = 0.5800

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
        if amt_str is not '':
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
    print("X: %.4f, Y: %.4f" % (x, y))
    servo.set_servo_angle(servo.SERVO_VERT, get_servo_pos('X', x))
    servo.set_servo_angle(servo.SERVO_HORIZ, get_servo_pos('Y', y))
    return 0
    
            
