#!/usr/bin/env python3

import RPi.GPIO as GPIO   # Import the GPIO library.
import time               # Import time library

class PWMControl:
    def __init__(self, pin_num: int, pwm_hz: int):
        GPIO.setmode(GPIO.BOARD)    # Set Pi to use pin number when referencing GPIO pins.
                                    # Can use GPIO.setmode(GPIO.BCM) instead to use 
                                    # Broadcom SOC channel names.
        
        GPIO.setup(pin_num, GPIO.OUT)
        self.pwm = GPIO.PWM(pin_num, pwm_hz)   # Initialize PWM on PWMpin and assign Hz
        self.duty_cycle = 0

    def start(self):
        self.pwm.start(0)
        print("\nPress Ctl C to quit \n") 

    def esc_arming(self):
        time.sleep(0.5)
        self.pwm.ChangeDutyCycle(1)
        time.sleep(1)
        # self.pwm.ChangeDutyCycle(0)
        time.sleep(0.5)
        print("\nESC Arming OK\n")

    def stop(self):
        self.duty_cycle = 0
        self.pwm.stop()
    
    def stop_end(self):
        self.duty_cycle = 0
        self.pwm.stop()
        GPIO.cleanup()

    def control_by_key(self):
        try:
            while True:         # Loop until Ctl C is pressed to stop.
                command = input("pwm Duty Cucle Control [1:+5, 2:-5, 4:+1, 5:-1, 0:set 0] : ")
                if command == "1":
                    self.duty_cycle += 5
                elif command == "2":
                    self.duty_cycle -= 5
                elif command == "4":
                    self.duty_cycle += 1
                elif command == "5":
                    self.duty_cycle -= 1
                elif command == "0":
                    self.duty_cycle = 0
                else:
                    print("Error! Type Right Command! [1:+5, 2:-5, 4:+1, 5:-1, 0:set 0]")
                self.pwm.ChangeDutyCycle(self.duty_cycle)
                time.sleep(0.1)             # wait .1 seconds
                print("\nDuty Cycle(%) : {}\n".format(self.duty_cycle))


        except KeyboardInterrupt:
            print("\nCtl C pressed - ending program")
            self.duty_cycle = 0
            self.stop_end()
        
    def thrust_test(self, low_thrust: int, high_thrust: int):
        self.duty_cycle = 0
        try:
            print("Test Start!\n")
            time.sleep(1)
            for i in range(low_thrust, high_thrust):
                self.duty_cycle = i
                self.pwm.ChangeDutyCycle(self.duty_cycle)
                print("Duty Cycle(%) : {}\n".format(self.duty_cycle))
                time.sleep(0.2)
            time.sleep(1)
            input("Reached High Thrust... Press Enter to stop motor...\n")
            self.stop_end()
            print("Test Done!!")

        except KeyboardInterrupt:
            print("\nCtl C pressed - ending program")
            self.duty_cycle = 0
            self.stop_end()
    
    def delay_time_test(self, cw_max: int, ccw_max: int):
        self.duty_cycle = 0
        try:
            print("Test Start!\n")
            time.sleep(1)
            self.duty_cycle = cw_max
            self.pwm.ChangeDutyCycle(self.duty_cycle)
            print("Duty Cycle(%) : {}\n".format(self.duty_cycle))
            
            for i in range(3):
                print(i+1)
                time.sleep(1)
            
            self.duty_cycle = ccw_max
            self.pwm.ChangeDutyCycle(self.duty_cycle)
            print("\nDuty Cycle(%) : {}\n".format(self.duty_cycle))
            time.sleep(1)

            input("Reverse Thrust Ok... Press Enter to stop motor...\n")
            self.stop_end()
            print("Test Done!!")

        except KeyboardInterrupt:
            print("\nCtl C pressed - ending program")
            self.duty_cycle = 0
            self.stop_end()

if __name__ =="__main__":
    pc = PWMControl(pin_num=32, pwm_hz=3000)
    pc.start()
    pc.esc_arming()
    pc.control_by_key()