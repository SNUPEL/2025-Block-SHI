from docplex.cp.model import *
import pandas as pd

# 모델 생성
mdl = CpoModel()

# Interval variables 생성 (작업 A, B)
task_A = mdl.interval_var(name="TaskA", size=5)
task_B = mdl.interval_var(name="TaskB", size=3)

# 제약조건: 작업 A가 끝난 후 작업 B 시작
mdl.add(mdl.end_before_start(task_A, task_B))
mdl.add(mdl.start_of(task_A) == 6)

# 목적 함수: 전체 스케줄 길이 최소화
makespan = mdl.max(mdl.end_of(task_A), mdl.end_of(task_B))
mdl.add(mdl.minimize(makespan))

# 모델 풀기
res = mdl.solve(LogVerbosity='Quiet')

# 결과 출력
print("Task A:", res.get_var_solution(task_A))
print("Task B:", res.get_var_solution(task_B))
print("Makespan:", res.get_objective_value())
