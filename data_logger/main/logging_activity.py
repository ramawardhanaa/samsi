import datetime


# for debug purpose
class Log:
    def __init__(self):
        self.name = "log"

    @staticmethod
    def get_time():
        now = datetime.datetime.now()
        return now.strftime('%Y-%m-%dT%H:%M:%S') + now.strftime('.%f')[:0] + 'Z'

    def write_log(self, message):
        file = open("/home/pi/sams/log.txt", "a+")
        file.write("{}\n{}\n".format(message, self.get_time()))
        file.close()
        return True
