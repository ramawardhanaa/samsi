#!/usr/bin/python3

from main.application import Application
from config.config import Config
from sensorlib.scale import Scale

config = Config()
config_data = config.get_config_data()
is_calibrated = config_data['SCALE'].getboolean("calibrated")
print(is_calibrated)
app = Application()
scale=Scale()

if __name__ == '__main__':
    if is_calibrated:
        app.start()
    else :
        scale.calibrate(5000)
