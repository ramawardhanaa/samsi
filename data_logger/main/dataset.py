import time
import sounddevice as sd
import scipy.io.wavfile
from sensorlib.scale import Scale
from sensorlib.dht22 import DHT22
from sensorlib.ds1820 import DS18B20
from config.config import Config
from api_plugin.sams_science import SamsApi
from main.logging_activity import Log
from numpy import median
import datetime
from scipy import signal
import numpy as np


class Dataset:
    def __init__(self):
        self.config = Config()
        self.config_data = self.config.get_config_data()
        try:
            self.dht22 = DHT22(int(self.config_data['DHT22']['pin']))
        except Exception as e:
            self.log.write_log("Failed to initialize DHT22: {}".format(e))
        try:
            self.scale = Scale()
        except Exception as e:
            self.log.write_log("Failed to initialize scale: {}".format(e))

        try:
            self.DS18B20 = DS18B20()
        except Exception as e:
            self.log.write_log("Failed to initialize DS18B20: {}".format(e))

        self.api = SamsApi()
        self.log = Log()

        self.median_interval = int(self.config_data['INTERVAL']['median'])
        self.wait_time = int(self.config_data['INTERVAL']['wait_time_seconds'])

        self.dataset = []
        self.temp = []
        self.hum = []
        self.weight = []
        self.ds_temp = []

        self.median_temp = 0
        self.median_hum = 0
        self.median_weight = 0
        self.median_ds_temp = 0

        self.duration = int(self.config_data['AUDIO']['duration'])

    @staticmethod
    def get_time():
        now = datetime.datetime.utcnow()
        return now.strftime('%Y-%m-%dT%H:%M:%S') + now.strftime('.%f')[:0] + 'Z'

    def error(self, device, error):
        if not device == "audio":
            self.dataset.append(
                {
                    "sourceId": "{0}-{1}".format(device, self.api.client_id),
                    "value": [
                        {
                            "ts": self.get_time(),
                            "value": 0
                        },
                    ]
                }
            )
        else:
            self.dataset.append(
                {
                    "sourceId": "{0}-{1}".format("audio", self.api.client_id),
                    "value": [
                        {
                            "ts": self.get_time(),
                            "value": [0, 0]
                        },
                    ]
                }
            )
        self.log.write_log("something went wrong by collecting the {0} dataset! Error: {1}".format(device, error))

    def get_fft_data(self):
        n_window = pow(2, 12)
        n_overlap = n_window / 2
        n_fft = n_window
        fs = 16000

        try:
            audiodata = sd.rec(self.duration * fs, samplerate=fs, channels=1, dtype='float64')
            sd.wait()
            data = audiodata.transpose()
            [F, pxx] = scipy.signal.welch(data, fs=fs, window='hanning', nperseg=n_window, noverlap=n_overlap,
                                          nfft=n_fft,
                                          detrend=False, return_onesided=True, scaling='density')
            temp_data = np.array(pxx).astype(float)
            data = temp_data.tolist()

            self.dataset.append(
                {
                    "sourceId": "audio-{0}".format(self.api.client_id),
                    "values": [
                        {
                            "ts": self.get_time(),
                            "values": data[0]
                        },
                    ]
                }
            )

        except Exception as e:
            self.error("audio", e)
            print("error")


        return True

    def get_ds18b20_data(self):
        sensor_counter = self.DS18B20.device_count()
        print(sensor_counter)
        try:
            if sensor_counter != 0:
                for x in range(sensor_counter):
                    self.median_ds_temp = []
                    for i in range(self.median_interval):
                        value = self.DS18B20.tempC(x)
                        print("temp")
                        print(value)
                        if value == 998 or value == 85.0:
                            self.log.write_log(
                                "DS18B20 does not work properly...")
                        else:
                            self.ds_temp.append(self.DS18B20.tempC(x))
                            time.sleep(self.wait_time)

                    if len(self.ds_temp) != 0:
                        self.median_ds_temp = median(self.ds_temp)
                        del self.ds_temp[:]
                        self.dataset.append(
                            {
                                "sourceId": "dsb18b20-{0}-{1}".format(x, self.api.client_id),
                                "values": [
                                    {
                                        "ts": self.get_time(),
                                        "value": float(self.median_ds_temp)
                                    },
                                ]
                            }
                        )
                        self.median_ds_temp = ""

        except Exception as e:
            self.error("ds18b20", e)

    def get_dht22_data(self):
        try:
            print("mausk")
            for i in range(self.median_interval):
                dhtdata = self.dht22.get_data()
                print(dhtdata)
                self.temp.append(dhtdata['temp'])
                self.hum.append(dhtdata['hum'])
                time.sleep(self.wait_time)

            self.median_temp = median(self.temp)
            self.median_hum = median(self.hum)

            self.dataset.append(
                {
                    "sourceId": "dht22-temperature-{0}".format(self.api.client_id),
                    "values": [
                        {
                            "ts": self.get_time(),
                            "value": float(self.median_temp)
                        },
                    ]
                }
            )
            self.dataset.append(
                {
                    "sourceId": "dht22-humidity-{0}".format(self.api.client_id),
                    "values": [
                        {
                            "ts": self.get_time(),
                            "value": float(self.median_hum)
                        },
                    ]
                }
            )

            del self.temp[:]
            del self.hum[:]

        except Exception as e:
            self.error("dht22", e)
            print(self.error("dht22",e))

    def get_scale_data(self):
        try:
            for i in range(self.median_interval):
                self.weight.append(self.scale.get_data())
                print(self.weight)
                print("weight")
                time.sleep(self.wait_time)

            self.median_weight = median(self.weight)

            del self.weight[:]
            self.dataset.append(
                {
                    "sourceId": "scale-{0}".format(self.api.client_id),
                    "values": [
                        {
                            "ts": self.get_time(),
                            "value": float(self.median_weight)
                        }
                    ]
                }
            )
        except Exception as e:
            self.error("scale", e)

    def get_dataset(self):
        try:
            self.dataset[:] = []  # empty the dataset before take new data
            #self.dataset.append({"sourceId": "dht22-temperature-YSc3h664jkqsnftrUN2uhfNxKloTFK4y","values": [{"ts": "2019-04-05T21:52:42Z","value": 5}]})
            #self.get_fft_data()
            print("fft")
            #self.get_scale_data()
            print("berat")
            #self.get_dht22_data()
            print("lembab")
            #self.get_ds18b20_data()
            print("suhu")
            return self.dataset
        except Exception as e:
            self.log.write_log("Dataset error: {}".format(e))
            return False

