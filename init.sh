#!/bin/bash

# Initialize pigpiod, capture error message if it is already running
echo "Starting pigpiod daemon..."
error=$(sudo pigpiod 2>&1 | wc -l)
if [ $error -gt 0 ]; then
  echo "pigpiod daemon already running!"
else
  echo "Done!"
fi
