import pandas as pd
from matplotlib import pyplot as plt
from shapely import intersection_all
from shapely import intersection

from postprocessing.plot import *
import matplotlib.pyplot as plt
import imageio
import io
import numpy as np
from datetime import datetime

class ScheduleChecker:
    def __init__(self, schedule_path, block_path, save_gif):
        self.schedule_path = schedule_path
        self.block_path = block_path
        self.block_info = pd.read_excel(self.block_path, sheet_name='BLK', skiprows=[1])
        self.workarea_info = pd.read_excel(self.block_path, sheet_name='WORKAREA_GROUP', skiprows=[1])
        self.raw_schedule = pd.read_excel(self.schedule_path)
        print("Schedule loaded successfully!")
        self.prefix = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

        self.scheduled = self.raw_schedule[self.raw_schedule['착수일'].notna()]
        dates = pd.concat([self.scheduled['착수일'].dt.date, self.scheduled['완료일'].dt.date]).dropna().unique()
        time_horizon = sorted(dates)
        self.min_date = time_horizon[0]
        self.max_date = time_horizon[-1]
        print(f"time horizon: {self.min_date} ~ {self.max_date}")

        # 전체 연속 날짜 리스트로 생성 (중간 날짜 포함)
        self.time_horizon = pd.date_range(start=self.min_date, end=self.max_date).date.tolist()

        self.image_list = []
        self.blocks_by_time_dict = {}
        self.intersections_by_time_dict = {}
        self.summary = {}

        self._create_polygon()
        self._check_intersection_area()

        ######### I. 목적함수 확인 #########
        ### I-1. 미배치 블록 확인
        self.check_obj_unscheduled()

        ### I-2. 블록일자 조정 확인
        self.check_obj_adjustments()

        ### I-3. 정반그룹 선호도 최대화 목적함수 확인
        self.check_obj_preference()

        ######### II. 제약 확인 #########
        ### II-1. 정반 별 블록 사이즈 제약
        self.check_cnstr_size()

        ### II-2. 블록 간섭 제약
        self.check_cnstr_interference()

        ### II-3. 특정 블록 동시 작업 제약
        self.check_cnstr_pair()

        ### II-4. 크레인 단독 운용
        self.check_cnstr_crane()

        ######### III. 완료 보고서 #########

        ######### IV. GIF 만들기 #########
        if save_gif:
            self.create_GIF()

    def check_obj_unscheduled(self):
        # 전체 블록 : self.raw_schedule.shape[0]
        unscheduled = self.raw_schedule.shape[0] - self.scheduled.shape[0]
        print(f"(1) 총 {self.raw_schedule.shape[0]}개의 블록 중 {unscheduled}개의 미배치 블록이 발생했습니다.")
        self.summary['1. 미배치 블록 개수'] = unscheduled
        pass

    def check_obj_adjustments(self):
        # 누적 점수 초기화
        sum_adjustments = 0
        block_adjustments = {}
        # 날짜 컬럼 이름 목록
        date_columns = ["착수일", "완료일", "TO일정", "PE일정"]

        # scheduled DataFrame 반복
        for idx, block in self.scheduled.iterrows():
            key = (block['선종'], block['호선'], block['블록'])

            # key 조건에 맞는 block_info 검색
            reference = self.block_info[
                (self.block_info['선종'] == key[0]) &
                (self.block_info['호선'] == key[1]) &
                (self.block_info['블록'] == key[2])
                ]

            # 매칭되는 데이터가 없으면 건너뜀
            if reference.empty:
                raise Exception(f"Schedule 결과 Excel 파일의 {block['블록']}블록의 원본 블록을 찾을 수 없습니다.")

            # 첫 번째 매칭된 row 사용
            reference = reference.iloc[0]

            # 날짜 차이 계산
            diff = []
            for col in date_columns:
                ref_date = pd.to_datetime(reference[col])
                blk_date = pd.to_datetime(block[col])
                diff.append((blk_date - ref_date).days)

            # 누적 합산
            sum_adjustments += sum(diff)
            block_adjustments[key] = diff
        self.summary['2. date adjustments'] = block_adjustments
        return sum_adjustments

    def check_obj_preference(self):
        pass

    def check_cnstr_size(self):
        # length_violence = 0
        # breadth_violence = 0
        # height_violence = 0
        # weight_violence = 0

        # 1. '사용여부'가 'Y'이고 '사이즈제한LTH'가 0이 아닌 경우만 필터
        groupinfo = self.workarea_info.copy()
        groupinfo = groupinfo[
            (groupinfo['사용여부'] == 'Y') &
            (pd.to_numeric(groupinfo['사이즈제한LTH'], errors='coerce') != 0)
            ]

        # 2. 숫자형 변환
        groupinfo['사이즈제한LTH'] = pd.to_numeric(groupinfo['사이즈제한LTH'], errors='coerce')
        groupinfo['사이즈제한BTH'] = pd.to_numeric(groupinfo['사이즈제한BTH'], errors='coerce')
        groupinfo['사이즈제한HGT'] = pd.to_numeric(groupinfo['사이즈제한HGT'], errors='coerce')
        groupinfo['사이즈제한WGT'] = pd.to_numeric(groupinfo['사이즈제한WGT'], errors='coerce')

        # 3. 그룹ID를 key로 하는 제한 사전 생성
        length_limit_dict = dict(zip(groupinfo['그룹ID'], groupinfo['사이즈제한LTH']))
        breadth_limit_dict = dict(zip(groupinfo['그룹ID'], groupinfo['사이즈제한BTH']))
        height_limit_dict = dict(zip(groupinfo['그룹ID'], groupinfo['사이즈제한HGT']))
        weight_limit_dict = dict(zip(groupinfo['그룹ID'], groupinfo['사이즈제한WGT']))
        for idx, row in self.scheduled.iterrows():
            length = row['길이']
            breadth = row['폭']
            # height = row['높이']
            # weight = row['중량']

            # 회전 고려
            if row['회전']>0: # row['회전'] : numpy.float64
                length, breadth = breadth, length
            # 정반 : row['그룹ID'] (float)
            if row['그룹ID'] in length_limit_dict.keys():
                if length>length_limit_dict[row['그룹ID']]:
                    print(f"(4-1) {row['블록']} 의 길이 제약 위반 - (회전 후) 길이: {length}, 제한:{length_limit_dict[row['그룹ID']]}")
                if breadth > breadth_limit_dict[row['그룹ID']]:
                    print(f"(4-2) {row['블록']} 의 폭 제약 위반 - (회전 후) 폭: {breadth}, 제한:{breadth_limit_dict[row['그룹ID']]}")
                # if height > height_limit_dict[row['그룹ID']]:
                #     print(f"(4-3) {row['블록']} 의 높이 제약 위반 - 높이: {height}, 제한:{height_limit_dict[row['그룹ID']]}")
                # if weight > weight_limit_dict[row['그룹ID']]:
                #     print(f"(4-3) {row['블록']} 의 중량 제약 위반 - 중량: {weight}, 제한:{weight_limit_dict[row['그룹ID']]}")

        pass

    def check_cnstr_interference(self):
        pass

    def check_cnstr_pair(self):
        pass

    def check_cnstr_crane(self):
        pass

    def _create_polygon(self):
        for t in self.time_horizon:
            timestamp_t = pd.Timestamp(t)
            presence = self.scheduled[
                (self.scheduled['착수일'] <= timestamp_t) &
                (self.scheduled['완료일'] >= timestamp_t)
                ]

            self.blocks_by_time_dict[t] = []
            for idx, row in presence.iterrows():
                poly = generate_polygon(groupidx=row['그룹ID'], workareaidx=row['정반명'],
                                      x=row['블록위치X'], y=row['블록위치Y'],
                                      dx=row['길이'] * 10, dy=row['폭'] * 10, rotate=row['회전'] > 0)
                self.blocks_by_time_dict[t].append((row['그룹ID'],poly))

    def _check_intersection_area(self):
        for t in self.time_horizon:
            self.intersections_by_time_dict[t] = []
            polygons = [self.blocks_by_time_dict[t][i] for i in range(len(self.blocks_by_time_dict[t]))]
            for idx, blockA in enumerate(polygons[:-1]):
                for blockB in polygons[idx+1:]:
                    if blockA[0] == blockB[0]: # groupidx 가 같은 경우
                        intersections = intersection(blockA[1], blockB[1], grid_size=1)
                        if not intersections.is_empty:
                            self.intersections_by_time_dict[t].append((blockA[0], intersections))
            if len(self.intersections_by_time_dict[t])!=0:
                print(t.strftime("%Y-%m-%d"),"에 겹치는 블록들이 있습니다.")

    def _create_image(self, t):
        fig, axes = plt.subplots(nrows=2, ncols=2)
        axes = axes.flatten()
        plot_workarea_group(fig, axes)
        for ax in axes:
            ax.set_aspect('equal')

        for idx, (groupidx, block_polygon) in enumerate(self.blocks_by_time_dict[t]):
            plot_block_polygon(fig, axes, int(groupidx), block_polygon, with_margin=True)

        for idx, (groupidx, intersection_polygon) in enumerate(self.intersections_by_time_dict[t]):
            plot_block_polygon(fig, axes, int(groupidx), intersection_polygon, with_margin=False,color='red')

        fig.suptitle(t)
        # 4. fig를 메모리 상의 이미지로 저장
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        image = imageio.v2.imread(buf)
        self.image_list.append(image)
        plt.close(fig)  # 메모리 누수 방지

    def create_GIF(self):
        for t in self.blocks_by_time_dict.keys():
            self._create_image(t=t)

        # 5. GIF 저장
        height, width, _ = self.image_list[0].shape
        black_frame = np.zeros((height, width, 4), dtype=np.uint8)

        # 2. 검은 화면 삽입
        self.image_list.append(black_frame)

        # 3. GIF 저장 (마지막 프레임만 길게 보여줌)
        durations = [0.5] * len(self.image_list)  # 마지막 검은 프레임을 1.5초 보여줌
        imageio.mimsave(self.prefix + ".gif", self.image_list, duration=durations, loop=0)  # duration은 프레임 간 시간(초)
        # 저장된 이미지들로 GIF 생성


if __name__ == "__main__":
    schedule_path = "../results/5월_intersect.xlsx"
    block_path = "../data/data_rev0.2.xlsx"
    checker = ScheduleChecker(schedule_path, block_path, save_gif=True)
