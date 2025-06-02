import numpy as np

np.bool = np.bool_
from docplex.cp.model import *
from preprocess_data import *
from define_variable import *
from add_constraint_area_limitation import *
from add_constraint_block_intersection import *
from add_constraint_simultaneous_block import *
from add_constraint_scheduled import *
from add_constraint_lug_direction import *
from add_constraint_crane_usage import *
from add_objective_allocation import *
from add_objective_preference import *
from add_objective_sum_delay import *
from add_objective_sum_unassinged_block import *
from solve_model import *
from postprocess_solution import *


class CPmodel:
    def __init__(self, config):
        self.config = config
        self.cpmodel = CpoModel()

        self.start_date = pd.to_datetime(self.config['data_start_date'])
        self.time_limit = self.config['time_limit']
        self.allocate_start_date = None
        self.block_end_date = None
        self.end_date = None
        self.model_start_index = None  # 변환시 시작 시간, 0으로 정의
        self.model_end_index = None  # 변환시 마지막 시간
        self.df_raw_data_dict = dict()
        self.df_raw_result_data_dict = dict()
        self.work_area_dict = dict()
        self.crane_dict = dict()
        self.block_dict = dict()
        self.all_block_dict = dict()
        self.calendar_dict = dict()  # 날짜 -> idx
        self.postprocess_calendar_dict = dict()  # idx -> 날짜
        self.df_result = pd.DataFrame()
        self.rotation_list = [0, 90]
        self.work_list = ['IN', 'STORE', 'TO', 'PE']
        self.block_keys = list()
        self.max_delay_day = self.config['max_delay_day']
        self.possible_delay_day = self.config['possible_delay_day']
        self.obj_weight_preference = self.config['weight_preference']
        self.obj_weight_delay = self.config['weight_delay']
        self.obj_weight_unassigned_block = self.config['weight_unassigned_block']
        self.obj_weight_allocation = self.config['weight_allocation']
        self.crane_usage = self.config['crane_usage']

        self.obj_sum_preference = 0
        self.obj_sum_delay = 0
        self.obj_sum_unassigned_block = 0
        self.obj_sum_allocation = 0
        self.obj = 0
        self.solution_cpmodel = None

        # 일정 변수
        self.block_schedule_var_by_id_work_dict = {}  # 블록 ID별, 작업별 일정 변수(대표 변수)
        self.block_schedule_var_list_by_id_work_dict = {}  # 블록 ID별, 작업별 가능한 일정 변수 리스트
        self.block_schedule_var_by_id_group_surf_work_rotate_dict = {}  # 블록 ID, 그룹, 정반, 작업, 회전별 일정 변수

        # 위치 변수
        self.block_x_var_by_id_dict = {}  # 블록 ID별 x축 위치 변수
        self.block_x_var_list_by_id_dict = {}  # 블록 ID별 가능한 x축 위치 변수 리스트
        self.block_x_var_by_id_group_surf_rotate_dict = {}  # 블록 ID, 그룹, 정반, 회전별 x축 위치 변수

        self.block_y_var_by_id_dict = {}  # 블록 ID별 y축 위치 변수
        self.block_y_var_list_by_id_dict = {}  # 블록 ID별 가능한 y축 위치 변수 리스트
        self.block_y_var_by_id_group_surf_rotate_dict = {}  # 블록 ID, 그룹, 정반, 회전별 y축 위치 변수

        self.block_time_var_by_id_dict = {}  # 블록 ID별 시간축 변수
        self.block_time_var_list_by_id_dict = {}  # 블록 ID별 가능한 시간축 변수 리스트
        self.block_time_var_by_id_group_surf_rotate_dict = {}  # 블록 ID, 그룹, 정반, 회전별 시간축 위치 변수

    def get_data(self):
        try:
            self.df_raw_data_dict = pd.read_excel(self.config['data_file_path'], sheet_name=None, skiprows=[1])
            print("Data loaded successfully.")
        except FileNotFoundError:
            print(f"Error: The file at {self.config['data_file_path']} was not found.")

        if self.config['use_block_allocation_result']:
            try:
                self.df_raw_result_data_dict = pd.read_excel(self.config['result_data_file_path'], sheet_name=None, skiprows=[1])
                print("Result data loaded successfully.")
            except FileNotFoundError:
                print(f"Error: The file at {self.config['result_data_file_path']} was not found.")

    def preprocess_data(self):
        preprocess_data(self)

    def run_model(self):

        ## < 최적화 모델 구성> ##
        # 변수 정의 #
        define_variable(self)

        # 제약 조건 #
        # 정반 별 블록 사이즈 제한
        # add_constraint_area_limitation(self)
        # 정반 러그 방향 제한 제약
        # add_constraint_lug_direction(self)
        # 크레인 단독 운용
        if self.crane_usage:
            add_constraint_crane_usage(self)
        # # 특정 블록(L/R) 동시 작업 제약
        # add_constraint_simultaneous_block(self)
        # 블록 간섭 제약
        add_constraint_block_intersection(self)
        # 기 배치된 블록 제약
        # add_constraint_scheduled(self)

        # 목적 함수 #
        # L/R 블록 배치 최대화
        if self.config['obj_allocation']:
            add_objective_allocation(self)
        else:
            self.obj_sum_allocation = 0

        # 정반 그룹 선호도 최대화
        if self.config['obj_preference']:
            add_objective_preference(self)
        else:
            self.obj_sum_preference = 0

        # 지연 최소화 목적함수
        if self.config['obj_delay']:
            add_objective_sum_delay(self)
        else:
            self.obj_sum_delay = 0

        # 미배치 블록 최소화 목적함수
        if self.config['obj_unassigned_block']:
            add_objective_sum_unassinged_block(self)
        else:
            self.obj_sum_unassigned_block = 0

        # 목적함수 계산
        self.obj = (
                    self.obj_weight_allocation + self.obj_sum_allocation
                    +
                    self.obj_weight_preference * self.obj_sum_preference
                    +
                    self.obj_weight_delay * self.obj_sum_delay
                    +
                    self.obj_weight_unassigned_block * self.obj_sum_unassigned_block
                    )

        ## <모델 탐색 파트> ##
        self.solution_cpmodel = solve_model(self,
                                            model=self.cpmodel,
                                            objective_function=self.obj,
                                            direction="minimize",
                                            time_limit=self.time_limit,
                                            method='single_solution')

        ## <모델 출력 및 후처리> ##
        postprocess_solution(self)
