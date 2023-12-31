#!/usr/bin/env python3

import time
import rospy
import sys
import gpiod
import os.path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from hx711 import HX711
from record_data import RecordLoadCell
from std_msgs.msg import String


class RecordDataROS:
    def __init__(self, dout_pin: int, sck_pin: int):              
        # Calibration value to obtain accurate weight
        self.referenceUnit = 1063

        # Connect GPIOD
        self.chip = None
        self.chip = gpiod.chip("0", gpiod.chip.OPEN_BY_NUMBER)


        # Setting HX711 module
        self.hx = HX711(dout = dout_pin, pd_sck = sck_pin, chip = self.chip)
        self.hx.set_reading_format("MSB", "MSB")
        self.hx.set_reference_unit(self.referenceUnit)
        self.hx.reset()
        self.tare()

        # Initialize Variables
        self.start_time = 0.0
        self.record_time = 0.0
        self.record_val = 0.0
        self.total_data = np.array([])
        self.noise_val = []
        self.plot_time = None
        self.plot_val = None
        self.max_val = None
        self.min_val = None
        self.df = None
        self.i = 1

        # You have to redefine your own directory and file name
        self.save_address = "/home/soobin/RT_test_data/test"

        # ROS message and Declare subscriber
        self.status_msg = ""
        self.record_now = False
        self.test_status_sub = rospy.Subscriber("test_status", String, self.test_status_callback)


    def test_status_callback(self, msg):
        self.status_msg = msg.data
        
        if self.status_msg == "TestStart":
            print("Test Started!")
            self.record_now = True
        
        elif self.status_msg == "TestEnd":
            print("Test Ended!")
            self.record_now = False

    def tare(self):
        self.hx.tare()
        print("Tare done! Add weight now...")
        time.sleep(1)
    

    def get_data(self):
        while not self.record_now:
            print("Wating for start msg...")
            time.sleep(1)
            continue

        print("Start recording ...\n")
        self.start_time = time.time()

        while True:
            if self.record_now == False:
                break
            try:
                self.record_time = time.time() - self.start_time
                self.record_val = self.hx.get_weight(1)
                self.total_data = np.append(self.total_data, [round(self.record_time,4),round(self.record_val, 2)], axis = 0)
                
                print(f"Weight : {self.record_val:.2f} / Recorded Time : {self.record_time:.4f}")

            except (KeyboardInterrupt, SystemExit):
                self.data_recording()
        # time.sleep(3)
        print("Stop recording...\n")
        self.data_recording()

    def data_recording(self):
        # Reset GPIOD (By restart pin)
        print("\nCleaning...")
        self.chip.reset()
        time.sleep(0.5)
        print("\nDone!!\n")

        # To get rid of random spike value
        print("Data Postprocessing... \n\nData Length : {}".format(len(self.total_data)))
        self.total_data = np.reshape(self.total_data, (-1,2))
        print("Reshape Data : {}".format(self.total_data.shape))

        for i in range(1, len(self.total_data)-1):
            if i == 1:
                if abs(self.total_data[i-1,1] - self.total_data[i,1]) > 200:
                    self.noise_val.append(i-1)

                elif (abs(self.total_data[i-1,1] - self.total_data[i,1]) > 200 and 
                    abs(self.total_data[i,1] - self.total_data[i+1,1]) > 200) :
                    self.noise_val.append(i)
                
            elif i == len(self.total_data)-1:
                if abs(self.total_data[i,1] - self.total_data[i+1,1]) > 200 :
                    self.noise_val.append(i+1)

                elif (abs(self.total_data[i-1,1] - self.total_data[i,1]) > 200 and 
                    abs(self.total_data[i,1] - self.total_data[i+1,1]) > 200) :
                    self.noise_val.append(i)

            elif (abs(self.total_data[i-1,1] - self.total_data[i,1]) > 200 and 
                    abs(self.total_data[i,1] - self.total_data[i+1,1]) > 200) :
                self.noise_val.append(i)
                
            else:
                pass

        self.total_data = np.delete(self.total_data, self.noise_val, axis=0)

        print("Delete Noise Data : {} // Noise Data Count : {}\n".format(self.total_data.shape, len(self.noise_val)))
        
        # Save data as .csv file
        self.df = pd.DataFrame(self.total_data)
        
        while os.path.isfile(self.save_address + str(self.i) + ".csv"):
            self.i += 1
        self.df.to_csv(self.save_address + str(self.i) + ".csv", index=False)
        print("Data Saved at {}\n".format(self.save_address + str(self.i) + ".csv"))
        time.sleep(0.5)

        # Plot data and save plot figure
        print("Saving Plot figure...")
        self.plot_time = self.total_data[:, 0]
        self.plot_val = self.total_data[:, 1]
        self.max_val = np.max(self.plot_val)
        self.min_val = np.min(self.plot_val)

        plt.plot(self.plot_time, self.plot_val)
        plt.plot(self.plot_time[np.argmax(self.plot_val)], self.plot_val[np.argmax(self.plot_val)], "o", color="Red", label=self.max_val)
        plt.plot(self.plot_time[np.argmin(self.plot_val)], self.plot_val[np.argmin(self.plot_val)], "o", color="Blue", label=self.min_val)
        plt.title("Load Cell Data")
        plt.xlabel("Time")
        plt.ylabel("Value")
        plt.legend(fontsize=12)
        # plt.show()
        plt.savefig(self.save_address + str(self.i) + ".jpg")
        print("Max value : {} , Min value : {}\n".format(self.max_val, self.min_val))
        print("Figure Saved at {}\n".format(self.save_address + str(self.i) + ".jpg"))


        print("Bye!")
        sys.exit()




if __name__ == "__main__":
    try:
        while not rospy.is_shutdown():
            rospy.init_node("Test_status_listener", anonymous=True)
            data_recorder = RecordDataROS(dout_pin = 11, sck_pin = 7)
            data_recorder.get_data()
            rospy.spin()
    
    except rospy.ROSInterruptException:
        print("\nCtrl+C pressed - terminating program\n")
        data_recorder.chip.reset()
        sys.exit()

    # finally:
    #     print("\nTerminating program\n")
    #     data_recorder.chip.reset()
    #     sys.exit()   