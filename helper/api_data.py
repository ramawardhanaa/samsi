from sensorlib.dht22 import DHT22
from sensorlib.ds1820 import DS18B20
from helper.config import Config
from helper.logging_activity import Log
from threading import Thread


class ApiData:
    def __init__(self):
        self.config = Config()
        self.config_data = self.config.get_config_data()
        self.dht22 = DHT22(self.config_data['DHT22']['pin'])
        self.DS18B20 = DS18B20()
        self.json_data = {}
        self.log = Log()

        self.ds18b20_temp = []
        self.dht22_data = []

    def error_message(self,device, exception_msg):
        self.log.write_log("something went wrong by collecting the {0} api data! Error: {1}".format(device, exception_msg))

    def get_data(self):
        ds18b20_thread = Thread(target=self.get_ds18b20_data)
        dht22_thread = Thread(target=self.get_dht22_data)

        ds18b20_thread.start()
        dht22_thread.start()

        ds18b20_thread.join()
        dht22_thread.join()

        return self.json_data

    def get_ds18b20_data(self):
        sensor_counter = self.DS18B20.device_count()
        try:
            if sensor_counter != 0:
                for x in range(sensor_counter):
                    self.ds18b20_temp.append(self.DS18B20.tempC(x))

            if len(self.ds18b20_temp) != 0:
                for x in range(len(self.ds18b20_temp)):
                    if not self.ds18b20_temp[x] == 85:
                        self.json_data["DS1820B-{}".format(x)] = "{0} {1}".format(self.ds18b20_temp[x], "°C")
                    elif self.ds18b20_temp[x] == 998:
                        self.json_data["DS1820B-{}".format(x)] = "{0}".format("VCC not connected")
                    else:
                        self.json_data["DS1820B-{}".format(x)] = "{0}".format("GND or DATA not connected")

        except Exception as e:
            self.error_message("ds18b20", e)

    def get_dht22_data(self):
        try:
            dht22data = self.dht22.get_data()
            self.json_data["dht22 hum"] = "{0} {1}".format(dht22data['hum'], "%")
            self.json_data["dht22 temp"] = "{0} {1}".format(dht22data['temp'], "°C")

        except Exception as e:
            self.error_message("dht22", e)
