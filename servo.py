#!/usr/bin/env python3
import pigpio
import atexit

SERVO_HORIZ = 13
SERVO_VERT  = 12

#########################################################
# Low-level/initialization functions                    #
#########################################################

def init_outputs():
    """
    Initialize the GPIO outputs
    """
    global pi
    global __initialized
    try:
        __initialized
    except NameError:
        pass # Initializing for the first time
    else:
        return # Already initialized
    pi = pigpio.pi()
    pi.set_mode(SERVO_HORIZ, pigpio.ALT0)
    pi.set_mode(SERVO_VERT,  pigpio.ALT0)
    atexit.register(disable_servos) # Disable the servos on exit
    __initialized = True


def set_pwm(pin, percent):
    """
    Set the output pin's PWM value to a certain percent (0-100) duty cycle at 50Hz.
    For servos, the inputs must be between 5 and 10 percent, or 1-2ms (although some servos accept a wider range).
    This function will generate an inverted PWM signal (i.e. only LOW for the specified duty cycle) to work properly with the inverting level shifters.
    """
    # This function accomodates for the inverting level shifters
    pi.hardware_PWM(pin, 50, int((100 - percent) * 10000)) # 10000 * 100 = 1 million

def set_servo_us(pin, us):
    """
    Sets the PWM duty cycle of the pin based on the desired pulse width, in microseconds.
    For servos, this should range between 1000 and 2000.
    """
    # Each cycle is 20ms == 20,000us
    # set_pwm wants a percentage, so multiply by 100
    # duty cycle = (us / 20,000) * 100
    duty_cycle = (float(us) / 200)
    set_pwm(pin, duty_cycle)

#########################################################
# High-level user functions                             #
#########################################################

# For HS-485HB
SERVO_MIN_US = 560
SERVO_MAX_US = 2400

def set_servo_angle(pin, pos):
    """
    Set the servo's position based on a value from 0 (minimum angle) to 1 (maximum angle).
    """
    normalized = pos
    # Constrain between 0 and 1
    if normalized > 1: normalized = 1
    elif normalized < 0: normalized = 0

    # Scale 0--1 to SERVO_MIN_US--SERVO_MAX_US
    us = SERVO_MIN_US + normalized * (SERVO_MAX_US - SERVO_MIN_US)
    set_servo_us(pin, us)

def disable_servo(pin):
    """
    Attempt to disable the specified servo by turning off the PWM signal.
    Note that this method does NOT work for digital servos--they will
      continue to run until they are powered off.
    """
    set_pwm(pin, 0) # Turning off PWM should stop the servo unless something is really, really wrong

def disable_servos():
    """
    Attempt to disable all of the servos. Does NOT work for digital servos,
      since they need to be powered off to stop running.
    """
    disable_servo(SERVO_HORIZ)
    disable_servo(SERVO_VERT)
