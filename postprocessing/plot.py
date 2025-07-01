from shapely.geometry import Polygon
import pandas as pd

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

def plot_block_and_margin(fig, axes, groupidx, workareaidx, x, y, dx, dy, rotate = False, show_margin = False):
    groupidx = int(groupidx)
    if groupidx == 4:
        if workareaidx == '(1,)':
            pass
        elif workareaidx == '(2, 3, 4)':
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
    margin_polygon = generate_polygon_from_anchor(x-15, y-15, dx+30, dy+30)
    # 면 색 지정
    axes[groupidx-1].fill(*block_polygon.exterior.xy, color='grey')
    axes[groupidx-1].plot(*block_polygon.exterior.xy, color='black')
    axes[groupidx-1].fill(*margin_polygon.exterior.xy, color='yellow', alpha=0.2)
    axes[groupidx-1].plot(*margin_polygon.exterior.xy, color='black', alpha=0.2)

def plot_workarea_group(fig, axes):
    group = {1:[], 2:[], 3:[], 4:[]}
    data = pd.read_excel("../data/revised_workarea_position.xlsx")
    # # available = data
    available = data.dropna(axis=0)
    #
    # # [model.work_area_dict[(1,(1,2,3,4))].work_unit_dict[i].y for i in range(1,5)]
    for index, row in available.iterrows():
        group[row['그룹ID']].append(generate_polygon_from_anchor(row['X'], row['Y'], row['길이']*10, row['폭']*10))

    for idx, workarea_list in group.items():
        for workarea in workarea_list:
            axes[idx-1].plot(*workarea.exterior.xy, color='grey')

    axes[0].set_xlim([-50, 450])
    axes[0].set_ylim([-50, 150])
    axes[1].set_xlim([-50, 450])
    axes[1].set_ylim([-50, 150])
    axes[2].set_xlim([-50, 200])
    axes[2].set_ylim([-50, 300])
    axes[3].set_xlim([-50, 800])
    axes[3].set_ylim([-50, 300])

def plot_integrated_workarea_group(fig, ax):
    workarea_polygon = []
    # 1번 정반그룹
    workarea_polygon.append(generate_polygon_from_anchor(0, 350, 400, 75))

    # 2번 정반그룹
    workarea_polygon.append(generate_polygon_from_anchor(500, 350, 400, 100))

    # 3번 정반그룹
    workarea_polygon.append(generate_polygon_from_anchor(0, 0, 156, 250))

    # 4번 정반그룹
    neworigin_x = 250
    workarea_polygon.append(generate_polygon_from_anchor(-10+neworigin_x, 0, 120, 100))
    workarea_polygon.append(generate_polygon_from_anchor(110+neworigin_x, 0, 110, 245))
    workarea_polygon.append(generate_polygon_from_anchor(325+neworigin_x, 0, 110, 260))
    workarea_polygon.append(generate_polygon_from_anchor(435+neworigin_x, 0, 110, 260))
    workarea_polygon.append(generate_polygon_from_anchor(660+neworigin_x, 0, 110, 255))
    workarea_polygon.append(generate_polygon_from_anchor(740+neworigin_x, 0, 30, 70))

    for workarea in workarea_polygon[:-1]:
        ax.plot(*workarea.exterior.xy, color='grey')
    ax.fill(*workarea_polygon[-1].exterior.xy, color='black')

    margin_polygon = []
    margin_polygon.append(generate_polygon_from_anchor(500, 435, 400, 15))
    margin_polygon.append(generate_polygon_from_anchor(240, 0, 10, 100))
    margin_polygon.append(generate_polygon_from_anchor(460, 0, 10, 245))
    margin_polygon.append(generate_polygon_from_anchor(575, 0, 10, 260))
    margin_polygon.append(generate_polygon_from_anchor(785, 0, 10, 260))
    margin_polygon.append(generate_polygon_from_anchor(980, 0, 10, 70))
    margin_polygon.append(generate_polygon_from_anchor(1010, 70, 10, 185))

    for margin in margin_polygon:
        ax.fill(*margin.exterior.xy, color='grey', alpha=0.5)

def generate_integrated_polygon(groupidx, workareaidx, x, y, dx, dy):
    if groupidx == 1:
        y+=350
    elif groupidx == 2:
        x +=500
        y +=350
    elif groupidx == 3:
        pass
    elif groupidx == 4:
        x+=250
        if workareaidx == '(1,)':
            x += -10
        elif workareaidx == '(2, 3, 4)':
            x += 110
        elif workareaidx == '(5, 6, 7)':
            x += 325
        elif workareaidx == '(8, 9, 10)':
            x += 435
        elif workareaidx == '(11, 12, 13)':
            x += 660


    block_polygon = generate_polygon_from_anchor(x, y, dx, dy)
    return block_polygon

def generate_polygon(groupidx, workareaidx, x, y, dx, dy, rotate = False):
    groupidx = int(groupidx)
    if groupidx == 4:
        if workareaidx == '(1,)':
            pass
        elif workareaidx == '(2, 3, 4)':
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
    ax.plot(*_polygon.exterior.xy, color='black')
    if name is not None:
        # polygon의 중심
        cx, cy = _polygon.centroid.xy  # shapely.geometry.Polygon.centroid → Point
        cx, cy = cx[0], cy[0]  # (shapely는 배열(tuple) 반환)

        # 텍스트 표시
        ax.text(cx, cy, name,
                ha='center', va='center',  # 중앙 정렬
                fontsize=4,  # 필요하면 추가 옵션
                fontweight='light')

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



    # fig, axes = plt.subplots(nrows=2, ncols=2)
    # axes = axes.flatten()
    # plot_workarea_group(fig, axes)
    # plot_block_and_margin(fig, axes, groupidx=2, workareaidx=None, x=61, y=43, dx=38, dy=56, rotate=True, show_margin=True)
    # plot_block_and_margin(fig, axes, groupidx=2, workareaidx=None, x=0.0, y=0.0, dx=38, dy=56, rotate=True, show_margin=True)
    #
    # for ax in axes:
    #     ax.set_aspect('equal')
    # plt.show()
    fig, ax = plt.subplots()
    plot_integrated_workarea_group(fig, ax)
    ax.set_aspect('equal')

    plt.show()

