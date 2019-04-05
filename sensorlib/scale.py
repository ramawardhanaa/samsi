import RPi.GPIO as GPIO
from sensorlib.hx711 import HX711
from helper.config import Config
from numpy import median
import time


class Scale:
    def __init__(self):
        self.config = Config()  # config init
        self.config_data = self.config.get_config_data()
        self.hx = HX711(5, 6)  # initialize scale
        self.is_calibrated = self.config_data['SCALE'].getboolean("calibrated")  # check config if scale is calibrated
        self.ratio = 0  # scale ratio for calibration
        self.offset = 0
        self.value = 0
        self.result = 0
        self.data = 0
        if self.is_calibrated:
            self.hx.set_offset(float(self.config_data["SCALE"]['offset']))
            self.config_ratio = self.config_data["SCALE"]['ratio']  # get scale ratio of config
            self.hx.set_scale(float(self.config_ratio))

    def setup(self):
        try:
            self.offset = self.hx.read_average()
            self.hx.set_offset(self.offset)
            return True
        except Exception as e:
           return False

    def has_error(self):
        value_list = []
        try:
            for x in range(15):
                self.hx.power_up()
                value_list.append(self.hx.get_grams())
                self.hx.power_down()
                time.sleep(0.1)

            print(value_list)
            median_val = median(value_list)
            print(median_val)
            if value_list[3] == median_val:
                return True
            else:
                return False

        except:
            return True

    def calibrate(self, weight):
        try:
            self.value = int(weight)
            measured_weight = (self.hx.read_average() - self.hx.get_offset())
            self.ratio = int(measured_weight) / self.value
            self.hx.set_scale(self.ratio)
            self.config.set_scale(ratio=self.ratio, offset=self.hx.get_offset(), calibrated=1)
            return True
        except ValueError:
            return False

    def get_data(self):
        try:
            self.hx.power_up()
            val = self.hx.get_grams()
            measure_weight = round((val / 1000), 2)
            self.hx.power_down()
            return measure_weight
        except Exception as e:
            pass

    def calibrated(self):
        self.is_calibrated = self.config_data['SCALE'].getboolean("calibrated")

        return self.is_calibrated

    def reset(self):
        self.config.set_scale()

    def tare(self):
        pass

    @staticmethod
    def clean():
        GPIO.cleanup()
