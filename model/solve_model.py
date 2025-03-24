def solve_model(self, model, objective_function, direction, time_limit, method):
    '''
    입력 모델 및 목적함수 기반 최적해 탐색 함수
    :param model: 탐색 대상 모델
    :param objective_function: 탐색 대상 모델의 목적함수
    :param direction: 탐색 방향 - "minimize" or "maximize"
    :param time_limit: 탐색 종료 조건 시간 (초)
    :param method: 단일 또는 복수해 선택 - "multiple_solutions" or "single_solution"
    :return: 탐색 해
    '''
    if direction == "minimize":
        model.add(model.minimize(objective_function))
    else:
        model.add(model.maximize(objective_function))

    if method == "multiple_solutions":
        return model.start_search(TimeLimit=time_limit)
    elif method == "single_solution":
        return model.solve(TimeLimit=time_limit)