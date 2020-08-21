#!/usr/bin/env python3
########################################################################
# Filename    : SenseLED.py
# Description : Controlling an led by infrared Motion sensor.
# Author      : freenove
# modification: 2018/08/03
########################################################################
import RPi.GPIO as GPIO
from time import sleep 

sensorPin = 29    # define the sensorPin

def setup_PIR():
	print ('Program is starting...')
	GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location
	GPIO.setup(sensorPin, GPIO.IN)    # Set sensorPin's mode is input

def process_PIR_data():
    if GPIO.input(sensorPin)==GPIO.HIGH:
        return True
    else :
        return False
	    
	    
def destroy():
	GPIO.cleanup()                     # Release resource

"""
if __name__ == '__main__':     # Program start from here
	setup()
	try:
		loop()
	except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
		destroy()
"""
