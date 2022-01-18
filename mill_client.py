import json
from datetime import datetime, timedelta

import requests


_SERVER = "https://api.millheat.com/"

class MillClientAPI(object):
    def __init__(self, access_key, secret_token, username, password):
        self._access_key = access_key
        self._secret_token = secret_token
        self._username = username
        self._password = password
        self._authorization_code = None
        self._access_token = None
        self._refresh_token = None
        self._home_id = None
        
        self.expiry_time = datetime.now()

    # def _get(self, path, ** params):
    #     params['apiKey'] = self._api_key
    #     response = requests.get(_SERVER + path, params = params, timeout=30)
    #     response.raise_for_status()
    #     return response.json()
    
    def _post(self, path, params={}, headers={}, data={}):
        response = requests.post(_SERVER + path,
                                 params=params, headers=headers, data=data)
        response.raise_for_status()
        return response.json()

    # def _patch(self, path, data, ** params):
    #     params['apiKey'] = self._api_key
    #     response = requests.patch(_SERVER + path, params = params, data = data)
    #     response.raise_for_status()
    #     return response.json()
    
    def _set_authorization_code(self):
        result = self._post("share/applyAuthCode", 
                   headers={"access_key": self._access_key, "secret_token": self._secret_token})
        self._authorization_code = result["data"]["authorization_code"]
        
    def _set_access_token(self):
        if not self._authorization_code:
            self._set_authorization_code
        if not self._access_token:
            params = {"username": self._username, "password": self._password}
            headers = {"authorization_code": self._authorization_code}
            result = self._post(
                "share/applyAccessToken", params=params, headers=headers)
            self._access_token = result["data"]["access_token"]
            self._refresh_token = result["data"]["refresh_token"]
            self.expiry_time = datetime.now() + timedelta(hours=1)
        elif self._refresh_token:
            self.update_access_token()
        
            
    def _set_home_id(self): # Assumes a single home for a user
        headers = {"access_token": self._access_token}
        result = self._post("uds/selectHomeList", headers=headers)
        self._home_id = result["data"]["homeList"][0]["homeId"]
        
    def update_access_token(self):
        params = {"refreshtoken": self._refresh_token}
        result = self._post("share/refreshtoken", params=params)
        self._access_token = result["data"]["access_token"]
        self._refresh_token = result["data"]["refresh_token"]
        self.expiry_time = datetime.now() + timedelta(hours=1)
        
    def connect(self):
        self._set_authorization_code()
        self._set_access_token()
        self._set_home_id()
        
    def devices(self):
        device_info_list = self._get_device_info_list()
        devices = [device["deviceName"] for device in device_info_list]
        return devices
            
    def _get_device_info_list(self):
        params = {"homeId": self._home_id}
        headers = {"access_token": self._access_token}
        result = self._post("uds/getIndependentDevices2020", params=params, headers=headers)
        return result["data"]["deviceInfoList"]
    
    def get_independent_devices(self):
        device_info_list = self._get_device_info_list()
        data = {}
        for sensor in device_info_list:
            #currentTemp, eco2, tvoc, humidity
            s = str(sensor["reportTime"])
            timestamp = datetime.fromtimestamp(float(s[:10]+'.'+s[10:]))
            data[sensor["deviceName"]] = {
                        "time": timestamp,
                        "currentTemp": sensor["currentTemp"],
                        "humidity": sensor["humidity"],
                        "tvoc": sensor["tvoc"],
                        "eco2": sensor["eco2"]}
        return data
            
    # def get_independent_device(self, device_name):
    #     device_info_list = self._get_independent_devices()
    #     device = [item for item in device_info_list if item["deviceName"] == device_name][0]
    #     #currentTemp, eco2, tvoc, humidity
    #     s = str(device["reportTime"])
    #     timestamp = datetime.fromtimestamp(float(s[:10]+'.'+s[10:]))
    #     return {device_name: {
    #                 "time": timestamp,
    #                 "currentTemp": device["currentTemp"],
    #                 "humidity": device["humidity"],
    #                 "tvoc": device["tvoc"],
    #                 "eco2": device["eco2"]}
    #     }
    
        
    
if __name__ == "__main__":
    access_key="cfa23c9e68aa4a74975bf0a6ef0eb4a3"
    secret_token="ec0729c262e44c36ae4e5788accd565a"
    username="sebastien.gros@ntnu.no"
    password="_Tinypinguin7"
    
    mill = MillClientAPI(access_key,secret_token,username,password)
    mill.connect()
    # print(mill.get_independent_device(device_name="Trailer"))
    # print(mill._get_device_info_list())
    # print(mill.get_independent_devices())
    print(mill.devices())
