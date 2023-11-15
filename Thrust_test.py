#!/usr/bin/env python3

import time               # Import time library
import rospy
import sys
from PWM_control import PWMControl
from std_msgs.msg import String


class ThrustTest:
    def __init__(self, pin_num: int, pwm_hz: int):

        self.pc = PWMControl(pin_num, pwm_hz)                
        self.thrust_pub = rospy.Publisher("test_status", String, queue_size=5)
        rospy.init_node("Thrust_test_pub", anonymous=True)
        self.status_msg = "NotReady"
        self.thrust_pub.publish(self.status_msg)
        # for j in range(10):
        #     self.thrust_pub.publish(self.status_msg)
        #     time.sleep(0.1)

        self.pc.start()
        self.pc.esc_arming()
    
    def test_start(self, low_thrust: int, high_thrust: int):
        input("Thrust Test ready... If you want start Test, Press Enter...")
        self.status_msg = "TestStart"
        self.thrust_pub.publish(self.status_msg)
        # for j in range(10):
        #     self.thrust_pub.publish(self.status_msg)
        #     time.sleep(0.1)
        time.sleep(0.5)

        self.pc.thrust_test(low_thrust, high_thrust)

    def test_end(self):
        self.status_msg = "TestEnd"
        self.thrust_pub.publish(self.status_msg)
        # for j in range(10):
        #     self.thrust_pub.publish(self.status_msg)
        #     time.sleep(0.1)
        sys.exit()
        

if __name__ == "__main__":
    th_test = ThrustTest(pin_num=32, pwm_hz=3000)
    th_test.test_start(low_thrust=30, high_thrust=79)
    th_test.test_end()