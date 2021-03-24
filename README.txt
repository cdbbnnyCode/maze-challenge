Marble Maze Challenge
Version 1.2
---------------------

HOW TO USE
----------
If you just started up the Pi, you NEED to run init.sh!!

$ ./init.sh

This script starts up the pigpiod daemon, which is required for the GPIO 
interfacing. If you try to run any of the other scripts before running init.sh,
you will get an error that looks like this:
	
	%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
	Can't connect to pigpio at localhost(8888)
	
	Did you start the pigpio daemon? E.g. sudo pigpiod
	
	Did you specify the correct Pi host/port in the environment
	variables PIGPIO_ADDR/PIGPIO_PORT?
	E.g. export PIGPIO_ADDR=soft, export PIGPIO_PORT=8888
	
	Did you specify the correct Pi host/port in the
	pigpio.pi() function? E.g. pigpio.pi('soft', 8888)
	%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

There is a command-line UI tool to help run the program. It uses the Nano text
editor to edit codes and saves them in the codes/ directory.

To calibrate the system (this should only need to be done once):
Run calibrate.py

$ python calibrate.py

This script opens a GUI window that guides you through the process of
centering the servos and adjusting their range. Then it shows the variables
you need to change to apply the calibration.
