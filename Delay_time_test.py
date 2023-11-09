#!/usr/bin/env python3

import time               # Import time library
import rospy
import sys
from PWM_control import PWMControl
from std_msgs.msg import String


class DelayTimeTest:
    def __init__(self, pin_num: int, pwm_hz: int):

        self.pc = PWMControl(pin_num, pwm_hz)                
        self.delay_time_pub = rospy.Publisher("test_status", String, queue_size=5)
        rospy.init_node("Thrust_test_pub", anonymous=True)
        self.status_msg = "NotReady"
        self.delay_time_pub.publish(self.status_msg)
        # for j in range(10):
        #     self.delay_time_pub.publish(self.status_msg)
        #     time.sleep(0.1)

        self.pc.start()
        self.pc.esc_arming()
    
    def test_start(self, cw_max: int, ccw_max: int):
        input("Delay time Test ready... If you want start Test, Press Enter...")
        self.status_msg = "TestStart"
        self.delay_time_pub.publish(self.status_msg)
        # for j in range(10):
        #     self.delay_time_pub.publish(self.status_msg)
        #     time.sleep(0.1)
        time.sleep(0.5)

        self.pc.delay_time_test(cw_max, ccw_max)

    def test_end(self):
        self.status_msg = "TestEnd"
        self.delay_time_pub.publish(self.status_msg)
        # for j in range(10):
        #     self.delay_time_pub.publish(self.status_msg)
        #     time.sleep(0.1)
        sys.exit()
        

if __name__ == "__main__":
    dt_test = DelayTimeTest(pin_num=32, pwm_hz=3000)
    dt_test.test_start(cw_max=30, ccw_max=79)
    dt_test.test_end()