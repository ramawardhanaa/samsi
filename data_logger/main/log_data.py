import json
import os
import time
from api_plugin.sams_science import SamsApi
from main.logging_activity import Log


class LogData:
    def __init__(self):
        self.path = '/home/pi/sams/data_logger/log/'
        self.api = SamsApi()
        self.status = []
        self.files = os.listdir(self.path)
        self.log = Log()

    def insert(self, json_data):
        files = os.listdir(self.path)
        if len(files) != 0:
            file = int(
                len([name for name in os.listdir(self.path) if os.path.isfile(os.path.join(self.path, name))])) + 1
        else:
            file = int(1)
        try:
            with open(self.path + str(file) + ".json", 'w') as f:
                json.dump(json_data, f)
                f.close()
        except Exception as e:
            print(e)

    def list_dir(self):
        self.files = os.listdir(self.path)
        self.files.sort()

    @staticmethod
    def read_file(path):
        with open(path) as json_file:
            data = json.load(json_file)

        return data

    def has_log_files(self):
        if not os.listdir(self.path):
            return False
        else:
            return True

    def post_log_files(self, dataset):
        try:
            self.log.write_log("log dataset...")
            self.insert(dataset)
            while self.has_log_files():
                self.list_dir()
                for x in self.files:
                    file = self.read_file(self.path + str(x))
                    self.log.write_log("try to post data")
                    if self.api.call(file) == 200:
                        self.log.write_log("status code ok! Delete file...")
                        print("pulang cuy")
                        #os.remove(self.path + str(x))
                    if self.api.call(file) == 500:
                        self.log.write_log("File corrupted! Delete file...")
                        os.remove(self.path + str(x))
                    time.sleep(5)
            return True

        except Exception as e:
            print(e)
            self.log.write_log(e)
