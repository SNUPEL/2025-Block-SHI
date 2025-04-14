import numpy as np

np.bool = np.bool_
from docplex.cp.model import *
from preprocess_data import *
from define_variable import *
from add_constraint_area_limitation import *
from add_constraint_block_intersection import *
from add_constraint_crane_sequence import *
from add_constraint_simultaneous_block import *
from add_constraint_lug_direction import *
from add_constraint_crane_usage import *
from add_objective_preference import *
from add_objective_sum_delay import *
from add_objective_sum_unassinged_block import *
from solve_model import *
from postprocess_solution import *





class CPmodel:
    def __init__(self, config):
        self.config = config
        self.df_raw_data_dict = dict()
        self.work_area_list = dict()
        self.crane_dict = dict()
        self.block_dict = dict()
        self.calendar = dict()
        self.df_result = pd.DataFrame()


    def get_data(self):
        try:
            self.df_raw_data_dict = pd.read_excel(self.config['data_file_path'], sheet_name=None, skiprows=[1])
            print("Data loaded successfully.")
        except FileNotFoundError:
            print(f"Error: The file at {self.config['data_file_path']} was not found.")

    def preprocess_data(self):
        preprocess_data(self)

    def run_model(self):

        # 탐색을 위한 데이터 준비
        self.obj = 0

        ## < 최적화 모델 구성> ##
        # CP 모델 생성
        self.cpmodel=CpoModel()

        # 변수 정의 #
        define_variable(self)

        # 제약 조건 #
        # 정반 별 블록 사이즈 제한
        add_constraint_area_limitation(self)
        # 블록 간섭 제약
        add_constraint_block_intersection(self)
        # 정반 러그 방향 제한 제약
        add_constraint_lug_direction(self)
        # 크레인 단독 운용
        add_constraint_crane_usage(self)
        # 특정 블록 동시 작업 제약
        add_constraint_simultaneous_block(self)

        # 목적 함수 #
        # 정반 그룹 선호도 최대화
        add_objective_preference(self)

        # 지연 최소화 목적함수
        add_objective_sum_delay(self)

        # 미배치 블록 최소화 목적함수
        add_objective_sum_unassinged_block(self)

        ## <모델 탐색 파트> ##
        self.solution_cpmodel= solve_model(self,
                                               model=self.cpmodel,
                                               objective_function=self.obj,
                                               direction="maximize",
                                               time_limit=self.config['time_limit'],
                                               method='single_solution')

        ## <모델 후처리> ##
        postprocess_solution(self)

    # def get_final_result(self):
    #         df_result = self.df_result









