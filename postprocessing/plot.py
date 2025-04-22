from shapely.geometry import Polygon
import pandas as pd

def generate_polygon_from_anchor(x1: float, y1: float, dx: float, dy: float, groupidx=0) -> Polygon:
    """
    주어진 좌상단 점 (x1, y1)과 가로 길이 dx, 세로 길이 dy를 기반으로 사각형 Polygon을 생성합니다.

    :param x1: 좌상단 x 좌표
    :param y1: 좌상단 y 좌표
    :param dx: 사각형의 가로 길이
    :param dy: 사각형의 세로 길이
    :return: shapely.geometry.Polygon 객체
    """

    x2, y2 = x1 + dx, y1 - dy  # 우하단 점 계산 (y 좌표는 아래 방향이 -)

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
            x += 11
        elif workareaidx == '(5, 6, 7)':
            x += 33.5
        elif workareaidx == '(8, 9, 10)':
            x += 43.5
        elif workareaidx == '(11, 12, 13)':
            x += 66
        else:
            raise Exception("Invalid work area index for GROUP 4")
    if rotate:
        dx, dy = dy, dx
    block_polygon = generate_polygon_from_anchor(x, y, dx, dy, groupidx=groupidx)
    margin_polygon = generate_polygon_from_anchor(x-1.5, y+1.5, dx+3.0, dy+3.0, groupidx=groupidx)
    # 면 색 지정
    axes[groupidx-1].fill(*block_polygon.exterior.xy, color='grey')
    axes[groupidx-1].plot(*block_polygon.exterior.xy, color='black')
    axes[groupidx-1].fill(*margin_polygon.exterior.xy, color='yellow', alpha=0.2)
    axes[groupidx-1].plot(*margin_polygon.exterior.xy, color='black', alpha=0.2)

def plot_workarea_group(fig, axes):
    group = {1:[], 2:[], 3:[], 4:[]}
    data = pd.read_excel("../data/data_rev0.2.xlsx", sheet_name='WORKAREA', skiprows=[1])
    # available = data
    available = data[data['정반사용여부'] == 'Y']
    for index, row in available.iterrows():
        group[row['그룹ID']].append(generate_polygon_from_anchor(row['그룹내정반위치X'], row['그룹내정반위치Y'], row['정반길이'], row['정반폭'], groupidx=row['그룹ID']))

    for idx, workarea_list in group.items():
        for workarea in workarea_list:
            axes[idx-1].plot(*workarea.exterior.xy, color='grey')

    axes[0].set_xlim([-35, 15])
    axes[0].set_ylim([-10, 10])
    axes[1].set_xlim([-35, 15])
    axes[1].set_ylim([-10, 10])
    axes[2].set_xlim([-10, 10])
    axes[2].set_ylim([-30, 5])
    axes[3].set_xlim([-5, 80])
    axes[3].set_ylim([-30, 5])

if __name__ == "__main__":
    import matplotlib.pyplot as plt



    fig, axes = plt.subplots(nrows=2, ncols=2)
    axes = axes.flatten()
    plot_workarea_group(fig, axes)
    plot_block_and_margin(fig, axes, groupidx=2, workareaidx=None, x=6.1, y=4.3, dx=3.8, dy=5.6, rotate=True, show_margin=True)
    plot_block_and_margin(fig, axes, groupidx=2, workareaidx=None, x=0.0, y=0.0, dx=3.8, dy=5.6, rotate=True, show_margin=True)

    for ax in axes:
        ax.set_aspect('equal')
    plt.show()
