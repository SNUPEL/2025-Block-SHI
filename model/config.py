import pandas as pd
import os
import time


def create_config():
    config = dict()

    config['data_file_path'] = '../data/데이터_rev.01_2025.04.04_산학용.xlsx'

    config['data_start_date'] = None
    config['data_duration'] = 14
    config['time_limit'] = 60

    return config
