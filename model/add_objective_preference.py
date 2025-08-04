import re


def add_objective_preference(self):
    """

    """
    penalty_exprs = []

    block_info = []
    for block_key in self.block_keys:
        block = self.block_dict[block_key]
        block_id = f"{block.ship_type}_{block.project_number}_{block.block_number}"

        # 블록 정보에서 블록 착수일 빼옴
        block_stdt = block.allocation_index
        block_fndt = block.TO_index

        # 블록이 배치될 수 있는 모든 조합
        placements = []
        for surface_group_key, work_area in self.work_area_dict.items():
            surface_id = work_area.surface_id_list
            surface_id = tuple(surface_id) if isinstance(surface_id, list) else surface_id

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
            'block_stdt': block_stdt,
            'block_fndt': block_fndt,
            'placements': placements
        })

    # 2. 목적함수 구현: 패널티 구현
    for i, block1 in enumerate(block_info):
        for block2 in block_info[i + 1:]:
            if block1['block_stdt'] == block2['block_stdt']:
                continue

            if block1['block_fndt'] in range(block2['block_stdt'], block2['block_fndt'] + 1, 1):
                if block1['block_stdt'] < block2['block_stdt']:
                    early_block = block1
                    late_block = block2
                elif block1['block_stdt'] > block2['block_stdt']:
                    early_block = block2
                    late_block = block1
                else:
                    continue

            elif block2['block_fndt'] in range(block1['block_stdt'], block1['block_fndt'] + 1, 1):
                if block2['block_stdt'] < block1['block_stdt']:
                    early_block = block2
                    late_block = block1
                elif block2['block_stdt'] > block1['block_stdt']:
                    early_block = block1
                    late_block = block2
                else:
                    continue

            else:
                continue

            for placement_early in early_block['placements']:
                for placement_late in late_block['placements']:
                    if placement_early['priority'] >= placement_late['priority']:
                        # 두 블록이 모두 해당 위치에 배치될 경우의 표현식
                        penalty_expr = self.cpmodel.presence_of(
                            placement_early['var']) * self.cpmodel.presence_of(
                            placement_late['var'])
                        penalty_exprs.append(penalty_expr)

    penalty_sum = self.cpmodel.sum(penalty_exprs)
    self.obj_sum_preference = penalty_sum
