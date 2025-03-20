from shapely.geometry import Polygon


def generate_polygon_from_anchor(x1: float, y1: float, dx: float, dy: float, index=0) -> Polygon:
    """
    주어진 좌상단 점 (x1, y1)과 가로 길이 dx, 세로 길이 dy를 기반으로 사각형 Polygon을 생성합니다.

    :param x1: 좌상단 x 좌표
    :param y1: 좌상단 y 좌표
    :param dx: 사각형의 가로 길이
    :param dy: 사각형의 세로 길이
    :return: shapely.geometry.Polygon 객체
    """
    x1 += index*50
    x2, y2 = x1 + dx, y1 - dy  # 우하단 점 계산 (y 좌표는 아래 방향이 -)

    # 사각형의 꼭짓점 정의 (시계방향 또는 반시계방향으로 닫힌 경로)
    corners = [(x1, y1), (x1 + dx, y1), (x1 + dx, y1 - dy), (x1, y1 - dy), (x1, y1)]

    return Polygon(corners)

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import random
    from shapely.plotting import plot_polygon
    # 예제 사용
    unit_dict = {'Area1':[], 'Area2':[], 'Area3':[], 'Area4':[], 'Area5':[]}
    unit_dict['Area1'].append(generate_polygon_from_anchor(0, 0, 10, 7.5, index=0))
    unit_dict['Area1'].append(generate_polygon_from_anchor(-10, 0, 10, 7.5, index=0))
    unit_dict['Area1'].append(generate_polygon_from_anchor(-20, 0, 10, 7.5, index=0))
    unit_dict['Area1'].append(generate_polygon_from_anchor(-30, 0, 10, 7.5, index=0))
    unit_dict['Area1'].append(generate_polygon_from_anchor(-10, -7.5, 10, 7.5, index=0))
    unit_dict['Area1'].append(generate_polygon_from_anchor(-20, -7.5, 10, 7.5, index=0))
    unit_dict['Area1'].append(generate_polygon_from_anchor(-30, -7.5, 10, 7.5, index=0))
    unit_dict['Area2'].append(generate_polygon_from_anchor(0, 0, 10, 8.5, index=1))
    unit_dict['Area2'].append(generate_polygon_from_anchor(-10, 0, 10, 8.5, index=1))
    unit_dict['Area2'].append(generate_polygon_from_anchor(-20, 0, 10, 8.5, index=1))
    unit_dict['Area2'].append(generate_polygon_from_anchor(-30, 0, 10, 8.5, index=1))
    unit_dict['Area3'].append(generate_polygon_from_anchor(0, 0, 7.8, 12.5, index=2))
    unit_dict['Area3'].append(generate_polygon_from_anchor(-7.8, 0, 7.8, 12.5, index=2))
    unit_dict['Area3'].append(generate_polygon_from_anchor(0, -12.5, 7.8, 12.5, index=2))
    unit_dict['Area3'].append(generate_polygon_from_anchor(-7.8, -12.5, 7.8, 12.5, index=2))
    unit_dict['Area3'].append(generate_polygon_from_anchor(0, -25, 7.8, 12.5, index=2))
    unit_dict['Area3'].append(generate_polygon_from_anchor(-7.8, -25, 7.8, 12.5, index=2))
    unit_dict['Area3'].append(generate_polygon_from_anchor(0, -37.5, 7.8, 12.5, index=2))
    unit_dict['Area3'].append(generate_polygon_from_anchor(-7.8, -37.5, 7.8, 12.5, index=2))

    plt.figure()

    plt.gca().set_aspect('equal', adjustable='box')  # 가로세로 비율 1:1 유지
    for key, units in unit_dict.items():
        _color = (random.random(), random.random(), random.random())
        for idx, unit in enumerate(units):
            unit : Polygon
            if idx == 0:
                plt.plot(*unit.boundary.xy, label=key, c=_color)
            else:
                plt.plot(*unit.boundary.xy, c=_color)
            plt.text(unit.centroid.x, unit.centroid.y, str(idx))

    plt.legend()
    plt.show()
