import pandas as pd
import os
import time


def create_config():
    config = dict()

    config['data_file_path'] = '../data/data_rev0.2.xlsx'

    config['data_start_date'] = '2019-04-03' # 시작일자 (착수일 기준)
    config['data_duration'] = 20
    config['only_workingday'] = True  # True: workingday 기준 duration의 기간을 셈, False: 단순히 duration의 기간을 더함
    config['time_limit'] = 600 # 탐색 시간

    # 정반그룹 선호도 최소화 목적함수
    config['obj_preference'] = True # True: 실행, False: 미실행
    config['weight_preference'] = 10 # 가중치

    # 지연 최소화 목적함수
    config['obj_delay'] = True # True: 실행, False: 미실행
    config['weight_delay'] = 100000 # 가중치

    # 미배치 최소화 목적함수
    config['obj_unassigned_block'] = True # True: 실행, False: 미실행
    config['weight_unassigned_block'] = 1000000 # 가중치


    # 이격거리 조정
    config['block_spacing_x'] = 0.5
    config['block_spacing_y'] = 0.5

    # 최대 허용 가능 지연
    config['max_delay_day'] = 20
    # 최대 패널티 불가 지연
    config['possible_delay_day'] = 2

    # 결과 저장
    config['ymd'] = time.strftime('%Y%m%d')
    config['hour'] = str(time.localtime().tm_hour)
    config['minute'] = str(time.localtime().tm_min)
    config['second'] = str(time.localtime().tm_sec)
    config["folderpath"] = '../results/{0}_{1}h_{2}m_{3}s'.format(config['ymd'], config['hour'], config['minute'], config['second'])

    if not os.path.exists(config["folderpath"]):
        os.mkdir(config["folderpath"])

    config_df = pd.json_normalize(config, sep='_').transpose()
    config_df.to_excel(config['folderpath'] + '/configuration.xlsx', index=True)

    return config
