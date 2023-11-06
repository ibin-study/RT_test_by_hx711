#!/usr/bin/env python3

import RPi.GPIO as GPIO   # Import the GPIO library.
import time               # Import time library
from PWM_control import PWMControl

pwm = PWMControl(pin_num=32, pwm_hz=3000)
pwm.start()
pwm.esc_arming()
pwm.thrust_test(30, 80)
