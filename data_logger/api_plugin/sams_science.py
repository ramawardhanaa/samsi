import requests
import configparser
from main.logging_activity import Log


class SamsApi:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.token_config = configparser.ConfigParser()
        self.log = Log()
        self.config_file = '/boot/credentials.ini'
        self.token_config_file = '/home/pi/sams/data_logger/config/config.ini'
        self.config.read(self.config_file)
        self.secret_data = self.config['DEFAULT']
        self.client_id = self.secret_data['client_id']
        self.client_secret = self.secret_data['client_secret']
        self.audience = self.secret_data['audience']
        self.data_url = self.secret_data['data_url']
        self.token_url = self.secret_data['token_url']
        self.grant_type = self.secret_data['grant_type']
        self.access_header = {'content-type': "application/json"}
        self.header = {}
        self.auth = {}

        self.token_payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "audience": self.audience,
            "grant_type": self.grant_type
        }

    def get_access_token(self):
        try:
            self.auth = requests.post(self.token_url, json=self.token_payload,
                                      headers=self.access_header).json()
            print(self.token_url)
            print(self.token_payload)
            

            token = self.auth['token_type'] + ' ' + self.auth['access_token']
            print(token)
            self.write_token(token)
            return token
        except Exception as e:
            self.log.write_log("failed to take access token: {0}".format(e))
            return False

    def send_data(self, payload, has_token=True):
        try:
            if has_token:
                token = self.read_token()
            else:
                token = self.get_access_token()

            self.header = {
                'content-type': 'application/json',
                'Authorization': token
            }

            resp = requests.post(
                self.data_url, json=payload,
                headers=self.header)
            print(resp.status_code)
            return resp.status_code

        except Exception as e:
            self.log.write_log("failed to send data: {0}".format(e))
            return False

    def call(self, payload):
        print(payload)
        api_call = self.send_data(payload)
        
        if api_call == 401:
            second_call = self.send_data(payload, has_token=False)
            if second_call == 200:
                return second_call
            else:
                self.log.write_log("send to api failed! Status code: {0}".format(second_call))
                return False
        elif api_call == 200:
            return api_call
        else:
            self.log.write_log("send to api failed! Status code: {0}".format(api_call))
            return api_call

    def read_token(self):
        try:
            self.token_config.read(self.token_config_file)
            token_config_data = self.token_config['DEFAULT']
            token = token_config_data['token']

            return token
        except Exception as e:
            self.log.write_log("read token failed: {}".format(e))

    def write_token(self, token):
        try:
            self.token_config.set("DEFAULT", "token", token)
            with open(self.token_config_file, 'w+') as configfile:
                self.token_config.write(configfile)
        except Exception as e:
            self.log.write_log("write token failed: {}".format(e))
