import re


def add_objective_preference(self):
    """

    """
    # 역전 패널티값 누적
    penalty_exprs = []

    block_info = []
    for block_key in self.block_keys:
        block = self.block_dict[block_key]
        block_id = f"{block.ship_type}_{block.project_number}_{block.block_number}"

        # 블록 번호에서 숫자 부분 추출(A110L: 110)
        match = re.search(r'\d+', block.block_number)
        block_num = int(match.group()) if match else 0

        # 이 블록이 배치될 수 있는 모든 정반과 회전 조합
        placements = []
        for surface_group_key, work_area in self.work_area_dict.items():
            surface_id = work_area.surface_id_list
            if isinstance(surface_id, list):
                surface_id = tuple(surface_id)

            for rotate in self.rotation_list:
                var_key = (block_id, surface_group_key, surface_id, 'STORE', rotate)
                if var_key in self.block_schedule_var_by_id_group_surf_work_rotate_dict:
                    var = self.block_schedule_var_by_id_group_surf_work_rotate_dict[var_key]
                    placements.append({
                        'var_key': var_key,
                        'var': var,
                        'priority': work_area.priority,
                        'surface_group_key': surface_group_key,
                        'surface_id': surface_id,
                        'rotate': rotate
                    })

        block_info.append({
            'block_id': block_id,
            'block_num': block_num,
            'placements': placements
        })

    # 2. 목적함수 구현: 패널티 구현
    for i, block1 in enumerate(block_info):
        for block2 in block_info[i + 1:]:
            # 숫자가 같으면 비교하지 않음
            if block1['block_num'] == block2['block_num']:
                continue

            # 숫자 크기에 따라 블록 정렬
            if block1['block_num'] < block2['block_num']:
                smaller_block = block1
                larger_block = block2
            else:
                smaller_block = block2
                larger_block = block1

            for placement_smaller in smaller_block['placements']:
                for placement_larger in larger_block['placements']:
                    # 역전 조건: 숫자가 작은 블록이 우선순위가 높은 정반에, 숫자가 큰 블록이 우선순위가 낮은 정반에 배치될 경우
                    if placement_smaller['priority'] > placement_larger['priority']:
                        # 두 블록이 모두 해당 위치에 배치될 경우의 표현식
                        penalty_expr = self.cpmodel.presence_of(placement_smaller['var']) * self.cpmodel.presence_of(
                            placement_larger['var'])
                        penalty_exprs.append(penalty_expr)

    # 패널티 누적값을 목적함수로 설정 (최소화)
    if penalty_exprs:
        penalty_sum = self.cpmodel.sum(penalty_exprs)
        self.obj = penalty_sum
