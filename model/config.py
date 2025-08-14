import pandas as pd
import os
import time


def create_config():
    config = dict()

    config['data_file_path'] = '../data/data_rev0.2.xlsx'

    config['data_start_date'] = '2019-04-21'  # 시작일자 (착수일 기준)
    config['only_workingday'] = False  # True: workingday 기준 duration의 기간을 셈, False: data_end_date 사용
    config['data_duration'] = 40  # workingday
    config['data_end_date'] = '2019-05-11'
    config['time_limit'] = 60  # 탐색 시간
    config['search_method'] = 'single_solution'  # single_solution, multiple_solutions
    # config['search_method'] = 'multiple_solutions'  # single_solution, multiple_solutions

    # 배치 확정된 블록 사용
    config['use_block_allocation_result'] = False  # True 시 하단의 결과를 가져옴
    config['result_data_file_path'] = '../results/20250611_14h_35m_8s/block_allocation_result.xlsx'


    # 정반그룹 선호도 최소화 목적함수
    config['obj_preference'] = False  # True: 실행, False: 미실행
    config['weight_preference'] = 10  # 가중치

    # 지연 최소화 목적함수
    config['obj_delay'] = False  # True: 실행, False: 미실행
    config['weight_delay'] = 1  # 가중치

    # 미배치 최소화 목적함수
    config['obj_unassigned_block'] = True  # True: 실행, False: 미실행
    config['weight_unassigned_block'] = 10000  # 가중치

    # L/R 블록 배치 제약 조건
    config['pair_block'] = False  # True: 실행, False: 미실행

    # L/R 블록 배치 최대화 목적함수 (L/R 블록 배치 제약 허용 시 목적 함수 미실행 되도록 해야함)
    config['obj_allocation'] = True  # True: 실행, False: 미실행
    config['weight_allocation'] = 100  # 가중치
    config['score_position'] = 0  # 동일 정반 배치 시 위치 가중치
    config['score_same_workarea'] = 0  # 동일 정반 배치 가중치
    config['score_both_allocation'] = 0  # 타 정반 배치 가중치

    # 크레인 제약 활용 및 시간 설정
    config['crane_usage'] = True  # True: 실행, False: 미실행
    config['crane_usage_time'] = 8   # 크레인 일별 가용 시간 설정

    # 이격거리 조정 (블록 크기)
    config['block_spacing_x'] = 0
    config['block_spacing_y'] = 0

    # 이격거리 조정 (제약조건)
    config['min_block_spacing_distance'] = 1.5


    # 최대 허용 가능 지연
    config['max_delay_day'] = 2

    # 패널티 기준 지연 (possible delay day 이후는 지연으로 패널티를 주도록 함)
    config['possible_delay_day'] = 0

    # 결과 저장
    config['ymd'] = time.strftime('%Y%m%d')
    config['hour'] = str(time.localtime().tm_hour)
    config['minute'] = str(time.localtime().tm_min)
    config['second'] = str(time.localtime().tm_sec)
    config["folderpath"] = '../results/{0}_{1}h_{2}m_{3}s'.format(
        config['ymd'], config['hour'], config['minute'], config['second'])
    print(config["folderpath"])

    if not os.path.exists(config["folderpath"]):
        os.mkdir(config["folderpath"])

    # base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'results'))
    # config["folderpath"] = os.path.join(base_dir, '{0}_{1}h_{2}m_{3}s'.format(
    #     config['ymd'], config['hour'], config['minute'], config['second']))
    # os.makedirs(config["folderpath"], exist_ok=True)

    config_df = pd.json_normalize(config, sep='_').transpose()
    config_df.to_excel(config['folderpath'] + '/configuration.xlsx', index=True)

    return config
