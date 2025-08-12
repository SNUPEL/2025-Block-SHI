import pandas as pd
from matplotlib import pyplot as plt
from setuptools.sandbox import save_path
from shapely import intersection_all
from shapely import intersection
import cv2
from postprocessing.plot import *
import matplotlib.pyplot as plt
import imageio
import io
import numpy as np
from datetime import datetime

class ScheduleChecker:
    def __init__(self, schedule_path, block_path, save_path = '', save_gif = False):
        self.schedule_path = schedule_path
        self.block_path = block_path
        self.block_info = pd.read_excel(self.block_path, sheet_name='BLK', skiprows=[1])
        self.workarea_info = pd.read_excel(self.block_path, sheet_name='WORKAREA_GROUP', skiprows=[1])
        self.raw_schedule = pd.read_excel(self.schedule_path, sheet_name='크레인 정보', skiprows=[1])
        print("Schedule loaded successfully!")
        self.savepath = save_path
        self.prefix = save_path + datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

        self.scheduled = self.raw_schedule[self.raw_schedule['배치확정여부'].notna()]
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

        if save_gif:
            self.create_GIF()

    def _create_polygon(self):
        for t in self.time_horizon:
            timestamp_t = pd.Timestamp(t)
            presence = self.scheduled[
                (self.scheduled['착수일'] <= timestamp_t) &
                (self.scheduled['완료일'] > timestamp_t)
                ]

            self.blocks_by_time_dict[t] = []
            for idx, row in presence.iterrows():
                groupidx = int(row['그룹ID'][1:-1].split(', ')[0])
                workareaidx = '('+row['그룹ID'][1:-1].split(', (')[1]
                name = row['블록']
                # name = row['호선']+"\n"+row['블록']
                # name = row['선종']+"\n"+row['호선']+"\n"+row['블록']
                poly = generate_integrated_polygon(groupidx=groupidx,
                                                   workareaidx=workareaidx,
                                      x=row['블록위치X']*10, y=row['블록위치Y'] * 10,
                                      dx=row['변환 블록폭'] * 10, dy=row['변환 블록길이'] * 10)
                self.blocks_by_time_dict[t].append((name, poly))


    def _create_image(self, t):
        # -- 원하는 해상도와 DPI 지정 --
        W, H = 1920, 1280  # 픽셀
        DPI = 300  # 그대로 저장할 DPI

        fig, ax = plt.subplots(figsize=(W / DPI, H / DPI), dpi=DPI)  # ← 핵심

        plot_integrated_workarea_group(fig, ax)
        ax.set_aspect('equal')
        for idx, (name, block_polygon) in enumerate(self.blocks_by_time_dict[t]):
            plot_integrated_block_polygon(fig, ax, block_polygon, name=name)

        fig.suptitle(t)
        # 4. fig를 메모리 상의 이미지로 저장
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=DPI)  # dpi는 위와 동일하게 유지
        buf.seek(0)
        image = imageio.v2.imread(buf)
        self.image_list.append(image)
        plt.close(fig)  # 메모리 누수 방지
        # plt.savefig(str(t)+".png",format='png')
        # plt.close(fig)
    def create_GIF(self):
        for t in self.blocks_by_time_dict.keys():
            self._create_image(t=t)

        # 5. GIF 저장
        height, width, _ = self.image_list[0].shape
        black_frame = np.dstack([np.zeros((height, width, 3), dtype=np.uint8),
                                 np.full((height, width), 255, dtype=np.uint8)])        # 2. 검은 화면 삽입
        self.image_list.append(black_frame)

        # 3. GIF 저장 (마지막 프레임만 길게 보여줌)
        durations = [0.5] * (len(self.image_list)-1)  # 마지막 검은 프레임을 1.5초 보여줌
        durations.append(0.1)

        # imageio.imwrite('black_frame.png', black_frame)
        # imageio.mimsave(self.prefix + ".gif", self.image_list, duration=durations, loop=0)  # duration은 프레임 간 시간(초)
        # 저장된 이미지들로 GIF 생성
        # imageio.v3.imwrite(self.prefix + ".gif", self.image_list, duration=durations, loop=0)

        h, w, _ = self.image_list[0].shape
        fps = 10  # 1 fps
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # 플랫폼 호환성 ↑
        out = cv2.VideoWriter(self.prefix + ".mp4", fourcc, fps, (w, h))

        for frame in self.image_list:
            # BGRA → BGR
            if frame.shape[2] == 4:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            out.write(frame.astype(np.uint8))

        out.release()


if __name__ == "__main__":
    # OpenCV 라이브러리를 설치해야 함 (conda install openCV 사용)
    # schedule_path = "../data/blocking_ref_1.xlsx"
    schedule_path = "../results/20250812_12h_28m_8s/block_allocation_result.xlsx"
    block_path = "../data/blocking_data_2.xlsx"

    checker = ScheduleChecker(schedule_path, block_path,
                              # save_path = "../data/",
                              save_path = "../results/20250812_12h_28m_8s/",
                              save_gif=True)
