from docplex.cp.model import *

# def add_constraint_crane_usage(self):
#     """
#
#     :param self:
#     :return:
#     """
#
#     crane_usage = self.cpmodel.step_at(0, 0)
#
#     for (block_id, surface_group_key, surface_id, work,
#          rotate), schedule_var in self.block_schedule_var_by_id_group_surf_work_rotate_dict.items():
#         work_area = self.work_area_dict[surface_group_key]
#
#         # 크레인을 활용하지 않는 경우 (0, [])를 반환
#         operation_info = work_area.crane_operation_dict.get(work, (0, []))
#         crane_time = int(operation_info[0])
#
#         # 블록 정보 구성(호선명 + 프로젝트명 + 블록명)
#         block_found = None
#         for block in self.block_dict.values():
#             current_block_id = f"{block.ship_type}_{block.project_number}_{block.block_number}"
#             if current_block_id == block_id:
#                 block_found = block
#                 break
#         if block_found is None:
#             continue
#
#         # 중량이 45 초과이고 작업이 'TO' 또는 'PE'인 경우 누적되지 않도록 구현
#         if block_found.weight > 45 and work in ['TO', 'PE']:
#             continue
#
#         crane_usage += self.cpmodel.pulse(schedule_var, crane_time)
#
#     self.cpmodel.add(crane_usage <= 16)
def add_constraint_crane_usage(self):
    """
    크레인 사용량 제약 조건 추가
    :param self:
    :return:
    """
    # 크레인 사용량 변수 초기화
    crane_usage = self.cpmodel.step_at(0, 0)

    # 현재 처리 중인 작업 유형
    current_work_type = None

    for (block_id, surface_group_key, surface_id, work,
         rotate), schedule_var in self.block_schedule_var_by_id_group_surf_work_rotate_dict.items():

        # 현재 작업 유형 설정 (첫 번째 반복에서만 설정)
        if current_work_type is None:
            current_work_type = work

        # 작업 유형이 현재 유형과 다르면 건너뜀
        if work != current_work_type:
            continue

        work_area = self.work_area_dict[surface_group_key]

        # 크레인을 활용하지 않는 경우 (0, [])를 반환
        operation_info = work_area.crane_operation_dict.get(work, (0, []))
        crane_time = int(operation_info[0])

        # 블록 정보 구성
        block_found = None
        for block in self.block_dict.values():
            current_block_id = f"{block.ship_type}_{block.project_number}_{block.block_number}"
            if current_block_id == block_id:
                block_found = block
                break
        if block_found is None:
            continue

        # 중량이 45 초과이고 작업이 'TO' 또는 'PE'인 경우 누적되지 않도록 구현
        if block_found.weight > 45 and work in ['TO', 'PE']:
            continue

        # 크레인 사용량 누적
        crane_usage += self.cpmodel.pulse(schedule_var, crane_time)

    # 크레인 사용량 제약 설정
    self.cpmodel.add(crane_usage <= 16)

