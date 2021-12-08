import logging
import os
from datetime import datetime, timezone, timedelta
import time
from math import ceil
import pickle

from config import Config

logging.basicConfig(filename='log__data_collector.log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.WARNING)

def write_to_env_file(params):
    tibber = params['tibber']
    tibber_api_key = tibber.get('api_key', None)
    tibber_sampling_time = tibber.get('sampling_time', Config.DEFAULT_PARAMS['tibber']['sampling_time'])

    tibber_rt_sampling_time = tibber.get('rt_sampling_time', Config.DEFAULT_PARAMS['tibber']['rt_sampling_time'])

    sensibo = params['sensibo']
    sensibo_api_key = sensibo.get('api_key', None)
    sensibo_sampling_time = sensibo.get('sampling_time', Config.DEFAULT_PARAMS['sensibo']['sampling_time'])

    weather = params['open_weather_map']
    weather_api_key = weather.get('api_key', None)
    weather_sampling_time = weather.get('sampling_time', Config.DEFAULT_PARAMS['open_weather_map']['sampling_time'])
    weather_lat = weather.get('lat', Config.DEFAULT_PARAMS['open_weather_map']['lat'])
    weather_lon = weather.get('lon', Config.DEFAULT_PARAMS['open_weather_map']['lon'])

    met = params['MET']
    met_lat = met.get('lat', Config.DEFAULT_PARAMS['MET']['lat'])
    met_lon = met.get('lon', Config.DEFAULT_PARAMS['MET']['lon'])
    met_altitude = met.get('altitude', Config.DEFAULT_PARAMS['MET']['altitude'])
    met_location = met.get('location_name', Config.DEFAULT_PARAMS['MET']['location_name'])
    met_personal_id = met.get('personal_id', Config.DEFAULT_PARAMS['MET']['personal_id'])

    with open('.env', 'w') as f:
        f.write('TIBBER_API_KEY=' + str(tibber_api_key) + os.linesep)
        f.write('TIBBER_SAMPLING_TIME=' + str(tibber_sampling_time) + os.linesep)
        f.write('TIBBER_RT_SAMPLING_TIME=' + str(tibber_rt_sampling_time) + os.linesep)
        f.write('SENSIBO_API_KEY=' + str(sensibo_api_key) + os.linesep)
        f.write('SENSIBO_SAMPLING_TIME=' + str(sensibo_sampling_time) + os.linesep)
        f.write('OPEN_WEATHER_MAP_API_KEY=' + str(weather_api_key) + os.linesep)
        f.write('OPEN_WEATHER_MAP_SAMPLING_TIME=' + str(weather_sampling_time) + os.linesep)
        f.write('OPEN_WEATHER_MAP_LAT=' + str(weather_lat) + os.linesep)
        f.write('OPEN_WEATHER_MAP_LON=' + str(weather_lon) + os.linesep)
        f.write('MET_LAT=' + str(met_lat) + os.linesep)
        f.write('MET_LON=' + str(met_lon) + os.linesep)
        f.write('MET_ALTITUDE=' + str(met_altitude) + os.linesep)
        f.write('MET_LOCATION=' + str(met_location) + os.linesep)
        f.write('MET_PERSONAL_ID=' + str(met_personal_id) + os.linesep)

    return

def find_files(basedir, extfilter='', only_filename=False):
    files_ = []
    for (path, dirs, files) in os.walk(basedir):
        for f in files:
            if f.endswith(extfilter):
                if only_filename:
                    files_.append(f)
                else:
                    files_.append(os.path.join(path, f))
    return files_

def get_sensor_data_file_names(sensor_name, session_id, time_now):
    basedir = os.getcwd()+os.sep+'data'+os.sep

    folder_daily = basedir+sensor_name+os.sep+'daily'+os.sep
    filename_daily = folder_daily + sensor_name + '_' + \
        time_now.strftime('%Y-%m-%d') + '__' + session_id + ".pkl"

    # The following was removed after discovering performance issues when storing 
    # data to weekly, monthly and yearly files. See report. 

    # folder_weekly = basedir+sensor_name+os.sep+'weekly'+os.sep
    # filename_weekly = folder_weekly + sensor_name + '_' + \
    #     time_now.strftime('%Y-week-%V') + '__' + session_id + ".pkl"

    # folder_monthly = basedir+sensor_name+os.sep+'monthly'+os.sep
    # filename_monthly = folder_monthly + sensor_name + '_' + \
    #     time_now.strftime('%Y-month-%m') + '__' + session_id + ".pkl"

    # folder_yearly = basedir+sensor_name+os.sep+'yearly'+os.sep
    # filename_yearly = folder_yearly + sensor_name + '_' + \
    #     time_now.strftime('%Y') + '__' + session_id + ".pkl"
    
    # return [filename_daily, filename_weekly, filename_monthly, filename_yearly]
    return [filename_daily]

def sleep_until(scheduled_time):
    time_now = datetime.now(tz=Config.LOCAL_TIMEZONE)
    time_until_scheduled_time = (scheduled_time - time_now).total_seconds()
    
    if time_until_scheduled_time > 0:
        time.sleep(time_until_scheduled_time)
    return

def generate_data_folder_structure(folder_name):
    try:
        os.makedirs('data/'+folder_name+'/daily', exist_ok=True)
        os.makedirs('data/'+folder_name+'/weekly', exist_ok=True)
        os.makedirs('data/'+folder_name+'/monthly', exist_ok=True)
        os.makedirs('data/'+folder_name+'/yearly', exist_ok=True)
    except Exception as e:
        logging.error("ERROR: " + str(e))
        print("ERROR (_generate_data_folder_structure): " + str(e))
        return False
    return True

def generate_all_data_folders(sensor_list):
    try:
        for sensor in sensor_list:
            generate_data_folder_structure(sensor)    
    except Exception as e:
        print(str(e))
        return False
    return True

def get_first_scheduled_time(*, sampling_time_minutes):
    time_now = datetime.now(tz=Config.LOCAL_TIMEZONE)
    dt = sampling_time_minutes
    if int(dt*ceil(time_now.minute/dt)) < 60:
        scheduled_time = time_now.replace(
            second=0, microsecond=0, minute=int(dt*ceil(time_now.minute/dt)))
    else:
        scheduled_time = time_now.replace(
            second=0, microsecond=0, minute=0, hour=time_now.hour+1)
    return scheduled_time

def print_save_message(sender, time_now, save_ok):
    time_now_string = datetime.now(tz=Config.LOCAL_TIMEZONE).strftime('%Y-%m-%d--%H:%M:%S')
    if save_ok:
        if sender == 'backup':
            print(f"{time_now_string} - {sender}:       ----->        Successfully backed up /data into /backups.")
        else:
            print(f"{time_now_string} - {sender}:       ----->        Successfully saved new data.")
    else:
        print(f"{time_now_string} - {sender}:       ----->        FAILED to save new data or backup data")
    return

def is_api_data_request(sender):
    return sender == "data_request"

def get_data_and_append(file, data_obj):
    # File name format: tibber_2021-03-03__1614780738-76771924.pkl
    with open(file, 'rb') as f:
        try:
            file_data = pickle.load(f)
        except EOFError:
            logging.warning("Get_data_and_append:131: trying to load empty file")
            return data_obj
        except pickle.UnpicklingError:
            logging.warning("Get_data_and_append:131: trying to load corrupted file")
            return data_obj
        except Exception as e:
            logging.warning("Get_data_and_append:131: error when loading file: " + str(e))
            return data_obj
        date = f.name.split('_')[1]
        session_id = f.name.split('__')[1].split('.')[0]
        if date not in data_obj:
            data_obj[date] = {}
        data_obj[date][session_id] = file_data
    return data_obj

def request_get_data_since(params):
    # params = {
    #   'sensor'
    #   'type'
    #   'date_or_time'
    # }
    now = datetime.now()

    if params['type'] == 'timestamp':
        timestamp = params['date_or_time']
        try:
            since_date = datetime.strptime(timestamp, '%a, %d %b %Y %H:%M:%S GMT')
        except Exception as e:
            return False, str(e)
    elif params['type'] == 'hours':
        try:
            hours = int(params['date_or_time'])
        except Exception as e:
            return False, str(e)
        since_date = now - timedelta(hours=hours)
    elif params['type'] == 'minutes':
        try:
            minutes = int(params['date_or_time'])
            hours = 0
            days = 0
        except Exception as e:
            return False, str(e)
        since_date = now - timedelta(minutes=minutes)                
    else: # Bad Type
        return False, "Bad type. Choose either: timestamp, hour, or minute"

    now = datetime.now()

    inner_folder = "daily"
    try:
        directory = 'data' + os.sep + params['sensor'] + os.sep + inner_folder
    except:
        return data, "key_error"

    # Get a list of all daily files for this sensor
    files = find_files(directory, 'pkl')
    sorted_files = sorted(files, reverse=True)
  
    # Filter the list to only include relevant files
    since_date_epoch = int(since_date.timestamp())
    filtered_files = []
    for filename in sorted_files:
        file_epoch = int(filename.split('__')[1].split('-')[0])
        if since_date_epoch < file_epoch:
            filtered_files.insert(0,filename)
            continue
        else:
            filtered_files.insert(0,filename)
            break

    # Create a data object from the files
    data = {}
    sensor = params['sensor']
    no_data = True
    for file in filtered_files:
        with open(file, 'rb') as f:
            try:
                file_data = pickle.load(f)
            except EOFError:
                logging.warning("Get_data_since request: trying to load empty file")
                continue
            except pickle.UnpicklingError:
                logging.warning("Get_data_and_append:131: trying to load corrupted file")
                continue
            except Exception as e:
                logging.warning("Get_data_and_append:131: error when loading file: " + str(e))
                continue
            if sensor == 'tibber':
                for home in file_data:
                    if home not in data:
                        data[home] = {}
                        data[home]['time'] = []
                        data[home]['sampling_time'] = []
                        data[home]['consumption'] = []
                        data[home]['cost'] = []
                        data[home]['total_cost'] = []
                    for i, timestamp in enumerate(file_data[home]['time']):
                        timestamp = timestamp.astimezone(timezone.utc).replace(tzinfo=None)
                        if timestamp <= since_date:
                            continue
                        else:
                            no_data = False
                            if data[home]['time'] and data[home]['time'][-1] == file_data[home]['time'][i]:
                                continue
                            else:
                                data[home]['time'].extend(file_data[home]['time'][i:])
                                data[home]['sampling_time'].extend(file_data[home]['sampling_time'][i:])
                                data[home]['consumption'].extend(file_data[home]['consumption'][i:])
                                data[home]['cost'].extend(file_data[home]['cost'][i:])
                                data[home]['total_cost'].extend(file_data[home]['total_cost'][i:])
                                break
            elif sensor == 'sensibo':
                for pump in file_data:
                    if pump not in data:
                        data[pump] = {}
                        data[pump]['time'] = []
                        data[pump]['sampling_time'] = []
                        data[pump]['states'] = {}
                        data[pump]['measurements'] = {}
                        for state in file_data[pump]['states'].keys():
                            data[pump]['states'][state] = []
                        for measurement in file_data[pump]['measurements'].keys():
                            data[pump]['measurements'][measurement] = []
                    for i, timestamp in enumerate(file_data[pump]['time']):
                        timestamp = timestamp.astimezone(timezone.utc).replace(tzinfo=None)
                        if timestamp <= since_date:
                            continue
                        else:
                            no_data = False
                            if data[pump]['time'] and data[pump]['time'][-1] == file_data[pump]['time'][i]:
                                continue
                            else:
                                data[pump]['time'].extend(file_data[pump]['time'][i:])
                                data[pump]['sampling_time'].extend(file_data[pump]['sampling_time'][i:])
                                for state in file_data[pump]['states'].keys():
                                    data[pump]['states'][state].extend(file_data[pump]['states'][state][i:])
                                for measurement in file_data[pump]['measurements'].keys():
                                    data[pump]['measurements'][measurement].extend(file_data[pump]['measurements'][measurement][i:])
                                break
            elif sensor == 'tibber-realtime-home-pumps' or sensor == 'tibber-realtime-home-up':
                if 'time' not in data:
                    data['time'] = []
                    data['sampling_time'] = []
                    data['power'] = []
                    data['accumulatedCost'] = []
                    data['accumulatedConsumption'] = []
                for i, timestamp in enumerate(file_data['time']):
                    timestamp = timestamp.astimezone(timezone.utc).replace(tzinfo=None)
                    if timestamp <= since_date:
                        continue
                    else:
                        no_data = False
                        if data['time'] and data['time'][-1] == file_data['time'][i]:
                            continue
                        else:
                            data['time'].extend(file_data['time'][i:])
                            data['sampling_time'].extend(file_data['sampling_time'][i:])
                            data['power'].extend(file_data['power'][i:])
                            data['accumulatedCost'].extend(file_data['accumulatedCost'][i:])
                            data['accumulatedConsumption'].extend(file_data['accumulatedConsumption'][i:])
                            break
            elif sensor == 'MET':
                if 'time' not in data:
                    data['time'] = []
                    data['sampling_time'] = []
                    data['temperature'] = []
                for i, timestamp in enumerate(file_data['time']):
                    timestamp = timestamp.astimezone(timezone.utc).replace(tzinfo=None)
                    if timestamp <= since_date:
                        continue
                    else:
                        no_data = False
                        if data['time'] and data['time'][-1] == file_data['time'][i]:
                            continue
                        else:
                            data['time'].extend(file_data['time'][i:])
                            data['sampling_time'].extend(file_data['sampling_time'][i:])
                            data['temperature'].extend(file_data['temperature'][i:])
                            break
            elif sensor == 'open_weather_map':
                if 'time' not in data:
                    data['time'] = []
                    data['sampling_time'] = []
                    data['temperature'] = []
                for i, timestamp in enumerate(file_data['time']):
                    timestamp = timestamp.astimezone(timezone.utc).replace(tzinfo=None)
                    if timestamp <= since_date:
                        continue
                    else:
                        no_data = False
                        if data['time'] and data['time'][-1] == file_data['time'][i]:
                            continue
                        else:
                            data['time'].extend(file_data['time'][i:])
                            data['sampling_time'].extend(file_data['sampling_time'][i:])
                            data['temperature'].extend(file_data['temperature'][i:])
                            break
            else:
                return False, "No sensor with that name."
    if no_data:
        return {}, "sensor"
    else:
        return data, sensor

def get_data_for_request(params):
    # params = {
    #     'sensor': 'tibber', # 'sensibo' 'weather' 'all'(?)
    #     'format': 'daily', # 'weekly' 'monthly' 'yearly'
    #     'date': 'latest', # 'all' 'first' '2020-09-02'(daily) '2020-week-01'(weekly) '2020-month-01'(monthly) '2020'(yearly)
    # }
    data = {}
    
    try:
        directory = 'data' + os.sep + params['sensor'] + os.sep + params['format']
    except:
        return data, "key_error"
    
    files = find_files(directory, 'pkl')
    if not files:
        return data, f"No files in '{params['format']}'' folder"
    sorted_files = sorted(files)
    
    if params['date'] == 'all':
        for file in sorted_files:
            data = get_data_and_append(file, data)

    elif params['date'] == 'latest':
        latest_file = sorted_files[-1]
        data = get_data_and_append(latest_file, data)

    elif params['date'] == 'first':
        first_file = sorted_files[0]
        data = get_data_and_append(first_file, data)

    else: # it is a date format 
        requested_date = params['date']
        for filename in sorted_files:
            if requested_date in filename:
                data = get_data_and_append(filename, data)

    sensor = params['sensor']
    return data, sensor