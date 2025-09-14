from numpy.distutils.system_info import x11_info
from shapely.geometry import Polygon
import pandas as pd
import pandas as pd
from shapely.geometry import Polygon
import math

class Area:
    def __init__(self, row):
        self.group_id = row['그룹ID']
        self.bed_id = row['정반ID']
        self.bed_length = row['정반길이'] * 10
        self.bed_width = row['정반폭'] * 10
        self.rel_x = row['그룹내정반위치X'] * 10
        self.rel_y = row['그룹내정반위치Y'] * 10
        self.bed_usage = row['정반사용여부']
        self.tp_dir1 = row['TP운송방향1']
        self.tp_dir2 = row['TP운송방향2']
        self.tp_dir3 = row['TP운송방향3']
        self.tp_dir4 = row['TP운송방향4']
        self.margin1 = row['마진거리1'] * 10
        self.margin2 = row['마진거리2'] * 10
        self.margin3 = row['마진거리3'] * 10
        self.margin4 = row['마진거리4'] * 10

        # 향후 외부에서 설정할 translation 값
        self.x_translation = 0
        self.y_translation = 0

        self._set_translation_by_group()

        self.absolute_x = self.rel_x + self.x_translation
        self.absolute_y = self.rel_y + self.y_translation
        self._set_polygon()

        self.origin_x = self.absolute_x
        self.origin_y = self.absolute_y - self.bed_width
        self.margin_poly_dict = {}

        self._create_margin_polygons()

    def _set_translation_by_group(self):
        """그룹 ID에 따라 translation 값 설정"""
        if self.group_id == 1:
            self.x_translation += 300
            self.y_translation += 625
        elif self.group_id == 2:
            self.x_translation += 800
            self.y_translation += 625
        elif self.group_id == 3:
            self.x_translation += 78
            self.y_translation += 375
        elif self.group_id == 4:
            self.x_translation += 250
            self.y_translation += 200

    def _set_polygon(self):
        # Polygon 객체 정의
        self.polygon = Polygon([
            (self.absolute_x, self.absolute_y),
            (self.absolute_x + self.bed_length, self.absolute_y),
            (self.absolute_x + self.bed_length, self.absolute_y - self.bed_width),
            (self.absolute_x, self.absolute_y - self.bed_width),
            (self.absolute_x, self.absolute_y)
        ])


    def _is_valid_margin(self, value):
        return value not in [None, 0] and not (isinstance(value, float) and math.isnan(value))


    def _create_margin_polygons(self):
        ax, ay = self.absolute_x, self.absolute_y

        # margin1: 위쪽 (positive y)
        if self._is_valid_margin(self.margin1):
            m = self.margin1
            poly1 = Polygon([
                (ax, ay + m),
                (ax + self.bed_length, ay + m),
                (ax + self.bed_length, ay),
                (ax, ay),
                (ax, ay + m)
            ])
            self.margin_poly_dict[1] = poly1

        # margin2: 오른쪽 (positive x)
        if self._is_valid_margin(self.margin2):
            m = self.margin2
            poly2 = Polygon([
                (ax + self.bed_length, ay),
                (ax + self.bed_length + m, ay),
                (ax + self.bed_length + m, ay - self.bed_width),
                (ax + self.bed_length, ay - self.bed_width),
                (ax + self.bed_length, ay)
            ])
            self.margin_poly_dict[2] = poly2

        # margin3: 아래쪽 (negative y)
        if self._is_valid_margin(self.margin3):
            m = self.margin3
            poly3 = Polygon([
                (ax, ay - self.bed_width),
                (ax + self.bed_length, ay - self.bed_width),
                (ax + self.bed_length, ay - self.bed_width - m),
                (ax, ay - self.bed_width - m),
                (ax, ay - self.bed_width)
            ])
            self.margin_poly_dict[3] = poly3
            self.origin_y -= m

        # margin4: 왼쪽 (negative x)
        if self._is_valid_margin(self.margin4):
            m = self.margin4
            poly4 = Polygon([
                (ax - m, ay),
                (ax, ay),
                (ax, ay - self.bed_width),
                (ax - m, ay - self.bed_width),
                (ax - m, ay)
            ])
            self.margin_poly_dict[4] = poly4
            self.origin_x -= m


def generate_workarea_info_from_excel(fig, ax, areas):

    # 예시 출력
    # fig, ax = plt.subplots()
    for area in areas.values():
        # print(f"Group {area.group_id} | Bed {area.bed_id} | Abs X: {area.absolute_x} | Abs Y: {area.absolute_y}")
        if area.bed_usage == 'Y':
            # 정반 본체 테두리 그리기 (검정색)
            ax.plot(*area.polygon.exterior.xy, color='grey', linewidth = 1)

            # margin polygon 있으면 채우기 (연회색)
            for poly in area.margin_poly_dict.values():
                x, y = poly.exterior.xy
                ax.fill(x, y, color='lightgrey', alpha=0.5)

            # 중심 좌표
            cx, cy = area.polygon.centroid.x, area.polygon.centroid.y

            # 중심에 bed_id 출력
            ax.text(cx, cy, str(area.bed_id), ha='center', va='center', fontsize=16, color='grey', alpha=0.3)

    # ax.set_aspect('equal')
    # plt.show()
    return areas

def generate_polygon_from_anchor(x1: float, y1: float, dx: float, dy: float) -> Polygon:
    """
    주어진 좌하단 점 (x1, y1)과 가로 길이 dx, 세로 길이 dy를 기반으로 사각형 Polygon을 생성합니다.

    :param x1: 좌상단 x 좌표
    :param y1: 좌상단 y 좌표
    :param dx: 사각형의 가로 길이
    :param dy: 사각형의 세로 길이
    :return: shapely.geometry.Polygon 객체
    """

    x2, y2 = x1 + dx, y1 + dy  # 우상단 점 계산 (y 좌표는 아래 방향이 -)

    # 사각형의 꼭짓점 정의 (시계방향 또는 반시계방향으로 닫힌 경로)
    corners = [(x1, y1), (x2, y1), (x2, y2), (x1, y2), (x1, y1)]

    return Polygon(corners)

def plot_block(fig, ax, block_polygon):
    ax.fill(*block_polygon.exterior.xy, color='grey')
    ax.plot(*block_polygon.exterior.xy, color='black')

def plot_margin(fig, ax, margin_polygon):
    ax.fill(*margin_polygon.exterior.xy, color='yellow', alpha=0.2)
    ax.plot(*margin_polygon.exterior.xy, color='black', alpha=0.2)

# def plot_block_and_margin(fig, axes, groupidx, workareaidx, x, y, dx, dy, rotate = False, show_margin = False):
#     groupidx = int(groupidx)
#     if groupidx == 4:
#         if workareaidx == '(1,)':
#             pass
#         elif workareaidx == '(2, 3, 4)':
#             x += 120
#         elif workareaidx == '(5, 6, 7)':
#             x += 335
#         elif workareaidx == '(8, 9, 10)':
#             x += 445
#         elif workareaidx == '(11, 12, 13)':
#             x += 660
#         else:
#             raise Exception("Invalid work area index for GROUP 4")
#     if rotate:
#         dx, dy = dy, dx
#     block_polygon = generate_polygon_from_anchor(x, y, dx, dy)
#     margin_polygon = generate_polygon_from_anchor(x-15, y-15, dx+30, dy+30)
#     # 면 색 지정
#     axes[groupidx-1].fill(*block_polygon.exterior.xy, color='grey')
#     axes[groupidx-1].plot(*block_polygon.exterior.xy, color='black')
#     axes[groupidx-1].fill(*margin_polygon.exterior.xy, color='yellow', alpha=0.2)
#     axes[groupidx-1].plot(*margin_polygon.exterior.xy, color='black', alpha=0.2)

# def plot_workarea_group(fig, axes):
#     group = {1:[], 2:[], 3:[], 4:[]}
#     data = pd.read_excel("../data/revised_workarea_position.xlsx")
#     # # available = data
#     available = data.dropna(axis=0)
#     #
#     # # [model.work_area_dict[(1,(1,2,3,4))].work_unit_dict[i].y for i in range(1,5)]
#     for index, row in available.iterrows():
#         group[row['그룹ID']].append(generate_polygon_from_anchor(row['X'], row['Y'], row['길이']*10, row['폭']*10))
#
#     for idx, workarea_list in group.items():
#         for workarea in workarea_list:
#             axes[idx-1].plot(*workarea.exterior.xy, color='grey')
#
#     axes[0].set_xlim([-50, 450])
#     axes[0].set_ylim([-50, 150])
#     axes[1].set_xlim([-50, 450])
#     axes[1].set_ylim([-50, 150])
#     axes[2].set_xlim([-50, 200])
#     axes[2].set_ylim([-50, 300])
#     axes[3].set_xlim([-50, 800])
#     axes[3].set_ylim([-50, 300])

# def plot_integrated_workarea_group(fig, ax):
#     workarea_polygon = []
#     # 1번 정반그룹
#     workarea_polygon.append(generate_polygon_from_anchor(0, 350, 400, 75))
#
#     # 2번 정반그룹
#     workarea_polygon.append(generate_polygon_from_anchor(500, 350, 400, 100))
#
#     # 3번 정반그룹
#     workarea_polygon.append(generate_polygon_from_anchor(0, 0, 156, 250))
#
#     # 4번 정반그룹
#     neworigin_x = 250
#     workarea_polygon.append(generate_polygon_from_anchor(-10+neworigin_x, 0, 120, 100))
#     workarea_polygon.append(generate_polygon_from_anchor(110+neworigin_x, 0, 110, 85))
#     workarea_polygon.append(generate_polygon_from_anchor(110+neworigin_x, 85, 110, 85))
#     workarea_polygon.append(generate_polygon_from_anchor(110+neworigin_x, 170, 110, 75))
#     workarea_polygon.append(generate_polygon_from_anchor(325+neworigin_x, 0, 110, 85))
#     workarea_polygon.append(generate_polygon_from_anchor(325+neworigin_x, 85, 110, 85))
#     workarea_polygon.append(generate_polygon_from_anchor(325+neworigin_x, 170, 110, 90))
#     workarea_polygon.append(generate_polygon_from_anchor(435+neworigin_x, 0, 110, 85))
#     workarea_polygon.append(generate_polygon_from_anchor(435+neworigin_x, 85, 110, 85))
#     workarea_polygon.append(generate_polygon_from_anchor(435+neworigin_x, 170, 110, 90))
#     workarea_polygon.append(generate_polygon_from_anchor(660+neworigin_x, 0, 110, 70))
#     workarea_polygon.append(generate_polygon_from_anchor(660+neworigin_x, 70, 110, 95))
#     workarea_polygon.append(generate_polygon_from_anchor(660+neworigin_x, 165, 110, 90))
#     workarea_polygon.append(generate_polygon_from_anchor(740+neworigin_x, 0, 30, 70))
#
#     for workarea in workarea_polygon[:-1]:
#         ax.plot(*workarea.exterior.xy, color='grey')
#     ax.fill(*workarea_polygon[-1].exterior.xy, color='black')
#
#     margin_polygon = []
#     margin_polygon.append(generate_polygon_from_anchor(500, 435, 400, 15))
#     margin_polygon.append(generate_polygon_from_anchor(240, 0, 10, 100))
#     margin_polygon.append(generate_polygon_from_anchor(460, 0, 10, 245))
#     margin_polygon.append(generate_polygon_from_anchor(575, 0, 10, 260))
#     margin_polygon.append(generate_polygon_from_anchor(785, 0, 10, 260))
#     margin_polygon.append(generate_polygon_from_anchor(910, 0, 10, 255))
#     # margin_polygon.append(generate_polygon_from_anchor(980, 0, 10, 70))
#     # margin_polygon.append(generate_polygon_from_anchor(1010, 70, 10, 185))
#
#     for margin in margin_polygon:
#         ax.fill(*margin.exterior.xy, color='grey', alpha=0.5)

def find_origin(areas, groupidx, workareaidx):
    workareaidx = int(workareaidx.strip("()").split(",")[0].strip())

    if groupidx == 4:
        if workareaidx in [1]:
            x_origin, y_origin = areas[(4, 1)].origin_x, areas[(4, 1)].origin_y
        elif workareaidx in [2, 3, 4]:
            x_origin, y_origin = areas[(4, 4)].origin_x, areas[(4, 4)].origin_y
        elif workareaidx in [5, 6, 7]:
            x_origin, y_origin = areas[(4, 7)].origin_x, areas[(4, 7)].origin_y
        elif workareaidx in [8, 9, 10]:
            x_origin, y_origin = areas[(4, 10)].origin_x, areas[(4, 10)].origin_y
        elif workareaidx in [11, 12, 13]:
            x_origin, y_origin = areas[(4, 13)].origin_x, areas[(4, 13)].origin_y
    elif groupidx == 3:
        x_origin, y_origin = areas[(3,2)].origin_x, areas[(3,2)].origin_y
    elif groupidx == 2:
        x_origin, y_origin = areas[(2, 4)].origin_x, areas[(2, 4)].origin_y
    else:
        if workareaidx in [1, 2, 3, 4]:
            x_origin, y_origin = areas[(1, 4)].origin_x, areas[(1, 4)].origin_y
        else:
            x_origin, y_origin = areas[(1, 7)].origin_x, areas[(1, 7)].origin_y

    return x_origin, y_origin

def generate_integrated_polygon(areas, groupidx, workareaidx, x, y, dx, dy):

    x_origin, y_origin = find_origin(areas, groupidx, workareaidx)

    x += x_origin
    y += y_origin

    block_polygon = generate_polygon_from_anchor(x, y, dx, dy)
    return block_polygon

def generate_polygon(groupidx, workareaidx, x, y, dx, dy, rotate = False):
    groupidx = int(groupidx)
    if groupidx == 4:
        if workareaidx == '(1,)':
            pass
        elif workareaidx in ['(2, 3, 4)', '(2,)']:
            x += 120
        elif workareaidx == '(5, 6, 7)':
            x += 335
        elif workareaidx == '(8, 9, 10)':
            x += 445
        elif workareaidx == '(11, 12, 13)':
            x += 660
        else:
            raise Exception("Invalid work area index for GROUP 4")
    if rotate:
        dx, dy = dy, dx
    block_polygon = generate_polygon_from_anchor(x, y, dx, dy)
    return block_polygon

def plot_integrated_block_polygon(fig, ax, _polygon, name = None):
    ax.fill(*_polygon.exterior.xy, color='grey')
    ax.plot(*_polygon.exterior.xy, color='black', linewidth=0.5)
    if name is not None:
        # polygon의 중심
        cx, cy = _polygon.centroid.xy  # shapely.geometry.Polygon.centroid → Point
        cx, cy = cx[0], cy[0]  # (shapely는 배열(tuple) 반환)

        # 텍스트 표시
        ax.text(cx, cy, name,
                ha='center', va='center',  # 중앙 정렬
                fontsize=4,  # 필요하면 추가 옵션
                fontweight='light',
                rotation=0)

def plot_block_polygon(fig, axes, _groupidx, _polygon, with_margin=True, color=None):
    if color is not None:
        axes[_groupidx - 1].fill(*_polygon.exterior.xy, color=color)
    else:
        axes[_groupidx - 1].fill(*_polygon.exterior.xy, color='grey')
    axes[_groupidx - 1].plot(*_polygon.exterior.xy, color='black')
    if with_margin:
        margin_polygon = generate_polygon_from_anchor(_polygon.bounds[0] - 15,
                                                      _polygon.bounds[1] - 15,
                                                      _polygon.bounds[2] - _polygon.bounds[0] + 30,
                                                      _polygon.bounds[3] - _polygon.bounds[1] + 30)
        axes[_groupidx - 1].fill(*margin_polygon.exterior.xy, color='yellow', alpha=0.2)
        axes[_groupidx - 1].plot(*margin_polygon.exterior.xy, color='black', alpha=0.2)

if __name__ == "__main__":
    import matplotlib.pyplot as plt



    fig, ax = plt.subplots()
    areas = generate_workarea_info_from_excel(fig, ax)


    ax.set_aspect('equal')
    plt.show()
