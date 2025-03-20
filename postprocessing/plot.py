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
    from shapely.plotting import plot_polygon
    # 예제 사용
    rect = generate_polygon_from_anchor(0, 0, 10, 7.5, index=0)
    rect1 = generate_polygon_from_anchor(-10, 0, 10, 7.5, index=0)
    rect2 = generate_polygon_from_anchor(-20, 0, 10, 7.5, index=0)
    rect3 = generate_polygon_from_anchor(-30, 0, 10, 7.5, index=0)
    rect8 = generate_polygon_from_anchor(-10, -7.5, 10, 7.5, index=0)
    rect9 = generate_polygon_from_anchor(-20, -7.5, 10, 7.5, index=0)
    rect10 = generate_polygon_from_anchor(-30, -7.5, 10, 7.5, index=0)
    rect4 = generate_polygon_from_anchor(0, 0, 10, 8.5, index=1)
    rect5 = generate_polygon_from_anchor(-10, 0, 10, 8.5, index=1)
    rect6 = generate_polygon_from_anchor(-20, 0, 10, 8.5, index=1)
    rect7 = generate_polygon_from_anchor(-30, 0, 10, 8.5, index=1)

    plt.figure()
    # plt.plot(rect.exterior.coords.xy, label='WorkArea1')
    # rect = generate_polygon_from_anchor(0, 0, 10, 7.5)

    # plot_polygon(rect)
    # plot_polygon(rect1)
    # plot_polygon(rect2)
    # plot_polygon(rect3)
    # plot_polygon(rect4)
    # plot_polygon(rect5)
    # plot_polygon(rect6)
    # plot_polygon(rect7)
    # plot_polygon(rect8)
    # plot_polygon(rect9)
    # plot_polygon(rect10)
    plt.show()
