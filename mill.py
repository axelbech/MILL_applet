from datetime import datetime, timedelta
from uuid import uuid1
from pathlib import Path
import logging
import time
import pickle

from mill_client import MillClientAPI
from config import Config
import helpers


global _sentinel
_sentinel = object()


class MillSensor():
    def __init__(self, access_key, secret_token, username, password, sampling_time=None):
        self._session_id = str(int(time.time())) + '-' + str(uuid1())[:8]
        self._sampling_time = sampling_time if sampling_time else Config.DEFAULT_PARAMS["mill"]["sampling_time"]
        self._sensor_name = "mill"
        self._mc = MillClientAPI(access_key, secret_token, username, password)

    def connect_and_get_devices(self):
        try:
            self._mc.connect()
            return self._mc.devices()
        except Exception as e:
            time_now_string = datetime.now(tz=Config.LOCAL_TIMEZONE).strftime('%Y-%m-%d--%H:%M:%S')
            print(f"{time_now_string} - Mill API could not be accessed.")
            print(str(e))
            return None
        
        # Called by the mill thread when the thread starts
    def start_mining_loop(self, main_q, stop_q, scheduled_time, sampling_time):
        time_now_string = datetime.now(tz=Config.LOCAL_TIMEZONE).strftime('%Y-%m-%d--%H:%M:%S')
        print(f"{time_now_string} - {self._sensor_name} started mining | sampling time: {sampling_time} min | next scheduled measurement: {scheduled_time}")

        self._devices = self.connect_and_get_devices()

        while True:
            try:
                message = stop_q.get(block=False)
                if message is _sentinel:
                    stop_q.put(_sentinel)
                    time_now_string = datetime.now(tz=Config.LOCAL_TIMEZONE).strftime('%Y-%m-%d--%H:%M:%S')
                    print(f"{time_now_string} - Stopped: " + self._sensor_name)
                    break
            except:
                pass

            helpers.sleep_until(scheduled_time)
            if not self._devices:
                self._devices = self.connect_and_get_devices()
            if self._mc.expiry_time - datetime.now() < 0:
                self._mc.update_access_token() # Update token if it is expired
            data = self._get_latest_measurement(devices=self._devices)
            if data:
                message = ("mill", data, self._session_id)
                main_q.put(message) # send data to handler_thread
            else:
                time_now_string = datetime.now(tz=Config.LOCAL_TIMEZONE).strftime('%Y-%m-%d--%H:%M:%S')
                print(f"{time_now_string} - Mill: Could not get any devices. Continuing to next interval without getting measurement.")

            scheduled_time += timedelta(minutes=sampling_time)
            
    def _get_latest_measurement(self):
        data = {}
        try:
            data = self._mc.get_independent_devices()
        except Exception as e:
            time_now_string = datetime.now(tz=Config.LOCAL_TIMEZONE).strftime('%Y-%m-%d--%H:%M:%S')
            logging.error("Mill get_latest_measurement: Could not get measurements")
            print(f"{time_now_string} - Mill get_latest_measurement: Could not get measurements")
            print(str(e))
            return False

        return data
    
def save_mill_data_to_file(filename, data_point):
    try:
        file = Path(filename)
        if file.is_file():
            with open(filename, 'rb') as f:
                file_data = pickle.load(f)
                for device in data_point:
                    for data_field in file_data[device]:
                        file_data[device][data_field].append(data_point[device][data_field])
            with open(filename, 'wb') as f:
                pickle.dump(file_data, f)
        else:
            if data_point:
                with open(filename, 'wb') as f:
                    data_point_modified = {}
                    for device in data_point: 
                        data_point_modified[device] = {}
                        for data_field in data_point[device]:
                            data_point_modified[device][data_field] = [data_point[device][data_field]]
                    pickle.dump(data_point_modified, f)
    except Exception as e:
        print("something went wrong writing mill data to file: ", filename)
        print(e)
        return False
    return True

# Used by the main handler thread to store the mill data to files
def save_mill_data_to_all_periodic_files(data_point, session_id, time_now):
    # Try to get the actual time for the datapoint, else use the current time from the argument
    for pump in data_point:
        try:
            time_now = data_point[0]['time']
            break
        except:
            continue
    # Create a list of file names to use when saving the data
    fname_list = helpers.get_sensor_data_file_names('mill', session_id, time_now)
    success_flags = []

    for fname in fname_list:
        if not save_mill_data_to_file(fname, data_point):
            success_flags.append(False)

    if False in success_flags:
        print("One or more of the mill file saves failed.")
        return False
    return True

if __name__ == "__main__":
    access_key="cfa23c9e68aa4a74975bf0a6ef0eb4a3"
    secret_token="ec0729c262e44c36ae4e5788accd565a"
    username="sebastien.gros@ntnu.no"
    password="_Tinypinguin7"
    
    mill = MillSensor(access_key,secret_token,username,password)
    print(mill.connect_and_get_devices())
    # print(mill._get_latest_measurement())
    for i in range(200):
        latest_measurement = mill._get_latest_measurement()
        print(latest_measurement)
        now = datetime.now()
        # save_mill_data_to_file("data/daily/mill.pkl", latest_measurement)
        save_mill_data_to_all_periodic_files(latest_measurement, mill._session_id, now)
        time.sleep(30)
        