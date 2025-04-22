import pandas as pd
from matplotlib import pyplot as plt
from postprocessing.plot import *
import matplotlib.pyplot as plt
import imageio
import io
import numpy as np

class ScheduleChecker:
    def __init__(self, filename):
        self.filename = filename
        self.raw_schedule = pd.read_excel(filename)
        print("Schedule loaded successfully!")

        self.scheduled = self.raw_schedule[self.raw_schedule['착수일'].notna()]
        dates = pd.concat([self.scheduled['착수일'].dt.date, self.scheduled['완료일'].dt.date]).dropna().unique()
        time_horizon = sorted(dates)
        self.min_date = time_horizon[0]
        self.max_date = time_horizon[-1]
        print(f"time horizon: {self.min_date} ~ {self.max_date}")

        # 전체 연속 날짜 리스트로 생성 (중간 날짜 포함)
        self.time_horizon = pd.date_range(start=self.min_date, end=self.max_date).date.tolist()
        self.summary = {}


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
        self.create_GIF()

    def check_obj_unscheduled(self):
        # 전체 블록 : self.raw_schedule.shape[0]
        unscheduled = self.raw_schedule.shape[0] - self.scheduled.shape[0]
        print(f"(1) 총 {self.raw_schedule.shape[0]}개의 블록 중 {unscheduled}개의 미배치 블록이 발생했습니다.")
        self.summary['1. 미배치 블록 개수'] = unscheduled
        pass

    def check_obj_adjustments(self):
        pass

    def check_obj_preference(self):
        pass

    def check_cnstr_size(self):
        pass

    def check_cnstr_interference(self):
        pass

    def check_cnstr_pair(self):
        pass

    def check_cnstr_crane(self):
        pass

    def create_GIF(self):
        image_list = []
        for t in self.time_horizon:
            timestamp_t = pd.Timestamp(t)
            presence = self.scheduled[
                (self.scheduled['착수일'] <= timestamp_t) &
                (self.scheduled['완료일'] >= timestamp_t)
                ]

            fig, axes = plt.subplots(nrows=2, ncols=2)
            axes = axes.flatten()
            plot_workarea_group(fig, axes)

            for idx, row in presence.iterrows():
                plot_block_and_margin(fig, axes, groupidx=row['그룹ID'], workareaidx = row['정반명'],
                                      x=row['블록위치X']*0.1, y=row['블록위치Y']*0.1,
                                      dx=row['길이'], dy=row['폭'], rotate=row['회전']>0, show_margin=True)

            for ax in axes:
                ax.set_aspect('equal')

            fig.suptitle(t)
            # 4. fig를 메모리 상의 이미지로 저장
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            image = imageio.v2.imread(buf)
            image_list.append(image)
            plt.close(fig)  # 메모리 누수 방지

        # 5. GIF 저장

        height, width, _ = image_list[0].shape
        black_frame = np.zeros((height, width, 4), dtype=np.uint8)

        # 2. 검은 화면 삽입
        image_list.append(black_frame)

        # 3. GIF 저장 (마지막 프레임만 길게 보여줌)
        durations = [0.5] * len(image_list)  # 마지막 검은 프레임을 1.5초 보여줌
        imageio.mimsave("output.gif", image_list, duration=durations, loop=0)  # duration은 프레임 간 시간(초)
        # 저장된 이미지들로 GIF 생성
        pass


if __name__ == "__main__":
    filename = "../results/block_allocation_result_3.xlsx"
    checker = ScheduleChecker(filename)
