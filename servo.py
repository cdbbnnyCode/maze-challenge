#!/usr/bin/env python3

import serial
import atexit
import json

SERVO_HORIZ = 13 # These are kept the same for compatibility, even though 0 and 1 are actually used
SERVO_VERT = 12
SERIAL_PORT = '/dev/serial0'

#########################################################
# Low-level/initialization functions                    #
#########################################################

def init_outputs():
    """
    Initialize the GPIO outputs
    """
    global ser
    global __initialized
    global SERVO_HORIZ, SERVO_VERT
    try:
        __initialized
    except NameError:
        pass # Initializing for the first time
    else:
        return # Already initialized
    with open('calibration.json', 'r') as f:
        conf = json.load(f)
        SERVO_HORIZ = conf['horiz']
        SERVO_VERT = conf['vert']
#    try:
#        with open('/tmp/orientation.json', 'r') as f:
#            conf = json.load(f)
#            if 'y' in conf['down']: # Down should be the -x direction
#                SERVO_HORIZ = 25 - SERVO_HORIZ # swap
#                SERVO_VERT = 25 - SERVO_VERT # swap
#    except: # I can't remember the exception and it doesn't matter
#        pass
    ser = serial.Serial(SERIAL_PORT, 115200) # Initialize serial communication
    ser.write(b'\xFF') # Reset the state
    atexit.register(disable_servos) # Disable the servos on exit
    __initialized = True

#########################################################
# High-level user functions                             #
#########################################################

# 0-180 'degree' inputs to the Arduino
SERVO_MIN_ANGLE = 5
SERVO_MAX_ANGLE = 180

def set_servo_angle(pin, pos):
    """
    Set the servo's position based on a value from 0 (minimum angle) to 1 (maximum angle).
    """
    normalized = pos
    # Constrain between 0 and 1
    if normalized > 1: normalized = 1
    elif normalized < 0: normalized = 0

    # Scale 0--1 between minimum and maximum angle
    angle = int(SERVO_MIN_ANGLE + normalized * (SERVO_MAX_ANGLE - SERVO_MIN_ANGLE))
    # Send the command
    ser.write(b'\xFF') # Synchronization just in case
    ser.write(bytes([pin - 12, angle]))

def disable_servo(pin):
    """
    Attempt to disable the specified servo by turning off the PWM signal.
    Note that this method does NOT work for digital servos--they will
      continue to run until they are powered off.
    """
    ser.write(b'\xFF')
    ser.write(bytes([(pin - 12) + 128])) # Turning off PWM should stop the servo unless something is really, really wrong

def disable_servos():
    """
    Attempt to disable all of the servos. Does NOT work for digital servos,
      since they need to be powered off to stop running.
    """
    disable_servo(SERVO_HORIZ)
    disable_servo(SERVO_VERT)
