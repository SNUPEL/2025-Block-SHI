import numpy as np

np.bool = np.bool_
# from docplex.cp.model import *
from preprocess_data import *


class CPmodel:
    def __init__(self, config):
        self.config = config
        self.df_raw_data_dict = dict()
        self.work_area_list = list()
        self.crane_dict = dict()

    def get_data(self):
        try:
            self.df_raw_data_dict = pd.read_excel(self.config['data_file_path'], sheet_name=None, skiprows=[1])
            print("Data loaded successfully.")
        except FileNotFoundError:
            print(f"Error: The file at {self.config['data_file_path']} was not found.")

    def preprocess_data(self):
        preprocess_data(self)
