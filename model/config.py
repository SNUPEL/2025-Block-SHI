import pandas as pd
import os
import time


def create_config():
    config = dict()

    config['data_file_path'] = 'data_간단.xlsx'

    config['data_start_date'] = None
    config['data_duration'] = 14
    config['time_limit'] = 3600

    return config
