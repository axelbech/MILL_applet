import pytz

class Config:
    SAMPLING_TIME = 60 # minutes
    LOCAL_TIMEZONE = pytz.timezone('Europe/Oslo')
    BACKUP_COPIES = 5
    BACKUP_INTERVAL = 24 # hours
    DEFAULT_PARAMS = {
        'tibber': {
            'sampling_time': 60, # minutes
            'rt_sampling_time': 20
        },
        'sensibo': {
            'sampling_time': 5, # minutes
        },
        'mill': {
            'sampling_time': 10 # minutes
        },
        'MET': {
            'lat': 63.3998,
            'lon': 10.3355,
            'altitude': 200,
            'location_name': 'ugla',
            'personal_id': 'sebastien.gros@ntnu.no ericth@stud.ntnu.no POWIOT project'
        },
        'open_weather_map': {
            'lat': "63.4",
            'lon': "10.335",
            'sampling_time': 60, # minutes
        },
        'backup': {
            'run_backups': True,
        },
        'running_in_webserver': True
    }