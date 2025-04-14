from docplex.cp.model import *

def add_constraint_crane_usage(self):
    """

    :param self:
    :return:
    """
    # crane_usage = step_at(0, 0)
    #
    # for key, schedule_var in self.block_schedule_var_by_id_group_surf_work_rotate_dict.items():
    #     # key 구조: (block_id, surface_group_key, surface_id, work, rotate)
    #     group_id = key[1]
    #     work = key[3]
    #
    #     # 그룹 ID 변환: 예시로, 만약 group_id가 이중 튜플이면 첫번째 튜플 요소를 사용
    #     if isinstance(group_id, tuple) and len(group_id) == 2 and isinstance(group_id[0], tuple):
    #         extracted_group_id = group_id[0]
    #     else:
    #         extracted_group_id = group_id
    #
    #     # work_area_dict의 key와 비교 (여기서는 work_area_dict의 key가 group_id라고 가정)
    #     if extracted_group_id in self.work_area_dict:
    #         work_area = self.work_area_dict[extracted_group_id]
    #         # crane_operation_dict의 key는 (work_area.group_id, work) 형태라고 가정
    #         if (work_area.group_id, work) in work_area.crane_operation_dict:
    #             op_info = work_area.crane_operation_dict[(work_area.group_id, work)]
    #             crane_time = int(op_info[0])
    #             # print(
    #             #     f"Mapping - key: {key}, schedule_var: {getattr(schedule_var, 'name', schedule_var)}, group_id: {work_area.group_id}, work: {work}, crane_time: {crane_time}")
    #             crane_usage = crane_usage + pulse(schedule_var, crane_time)
    #         else:
    #             pass
    #             # print(
    #             #     f"[Warning] No crane operation found for (group_id, work)=({work_area.group_id}, {work}) in work_area.")
    #     else:
    #         pass
    #         # print(f"[Warning] Group id {extracted_group_id} not found in work_area_dict.")
    #
    # # print("Final crane_usage expression:", crane_usage)
    # self.cpmodel.add(crane_usage <= 16)

    crane_usage = step_at(0, 0)

    for key, schedule_var in self.block_schedule_var_by_id_group_surf_work_rotate_dict.items():
        block_id = key[0]
        group_id = key[1]
        work = key[3]

        if isinstance(group_id, tuple) and len(group_id) == 2 and isinstance(group_id[0], tuple):
            extracted_group_id = group_id[0]
        else:
            extracted_group_id = group_id

        if extracted_group_id in self.work_area_dict:
            work_area = self.work_area_dict[extracted_group_id]
            if (work_area.group_id, work) in work_area.crane_operation_dict:
                op_info = work_area.crane_operation_dict[(work_area.group_id, work)]
                crane_time = int(op_info[0])

                block_found_weight = None
                for b in self.block_dict.values():
                    temp_block_id = f"{b.ship_type}_{b.project_number}_{b.block_number}"
                    if temp_block_id == block_id:
                        block_found_weight = b
                        break
                if block_found_weight is None:
                    print(f"[Warning] Block with id {block_id} not found in block_dict.")
                    continue

                # 만약 블록 중량이 45를 초과하고 작업이 'TO' 또는 'PE'인 경우, pulse를 추가하지 않음.
                if block_found_weight.weight > 45 and work in ['TO', 'PE']:
                    pass
                else:
                    crane_usage = crane_usage + pulse(schedule_var, crane_time)
            else:
                pass
        else:
            pass

    self.cpmodel.add(crane_usage <= 16)
