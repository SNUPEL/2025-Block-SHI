import re


def add_objective_allocation(self):
    """
    """

    # 계층적 목적함수 파라미터
    score_position = self.config['score_position']  # 1단계: 같은 정반 내 위치 근접
    score_same_workarea = self.config['score_same_workarea']  # 2단계: 같은 정반 그룹
    score_both_allocation = self.config['score_both_allocation']  # 3단계: 둘 다 배치

    objective_exprs = []
    objective_exprs1 = []
    objective_exprs2 = []
    objective_exprs3 = []

    # L/R 블록 쌍 찾기
    lr_block_pairs = []
    for i, block_key1 in enumerate(self.block_keys):
        block1 = self.block_dict[block_key1]
        ship_type1, project_number1, block_number1 = block_key1
        base_number1 = block_number1[:-1]  # 마지막 문자 제외
        block_id1 = f"{ship_type1}_{project_number1}_{block_number1}"

        for j in range(i + 1, len(self.block_keys)):
            block_key2 = self.block_keys[j]
            block2 = self.block_dict[block_key2]
            ship_type2, project_number2, block_number2 = block_key2
            base_number2 = block_number2[:-1]  # 마지막 문자 제외
            block_id2 = f"{ship_type2}_{project_number2}_{block_number2}"

            # L/R 블록 쌍 조건: 같은 선종, 호선, base_number이고 다른 마지막 문자
            if (ship_type1 == ship_type2 and project_number1 == project_number2 and
                    base_number1 == base_number2 and block_number1 != block_number2):
                lr_block_pairs.append({
                    'block_id1': block_id1,  # 'A110L'
                    'block_id2': block_id2,  # 'A110R'
                    'block1': block1,  # A110L: 블록 정보
                    'block2': block2  # A110R: 블록 정보
                })

    # 각 L/R 쌍에 대해 목적함수 계산
    for pair in lr_block_pairs:
        block_id1 = pair['block_id1']
        block_id2 = pair['block_id2']

        # 각 블록의 배치 가능한 변수들 수집
        placements1 = []
        placements2 = []

        for surface_group_key, work_area in self.work_area_dict.items():
            surface_id = work_area.surface_id_list
            if isinstance(surface_id, list):
                surface_id = tuple(surface_id)

            for rotate in self.rotation_list:
                # 블록1의 STORE 변수 찾기
                var_key1 = (block_id1, surface_group_key, surface_id, 'STORE', rotate)
                if var_key1 in self.block_schedule_var_by_id_group_surf_work_rotate_dict:
                    store_var1 = self.block_schedule_var_by_id_group_surf_work_rotate_dict[var_key1]

                    # 위치 변수도 찾기
                    pos_key1 = (block_id1, surface_group_key, surface_id, rotate)
                    x_var1 = self.block_x_var_by_id_group_surf_rotate_dict.get(pos_key1)
                    y_var1 = self.block_y_var_by_id_group_surf_rotate_dict.get(pos_key1)

                    placements1.append({
                        'store_var': store_var1,
                        'x_var': x_var1,
                        'y_var': y_var1,
                        'surface_group_key': surface_group_key,
                        'surface_id': surface_id,
                        'rotate': rotate
                    })

                # 블록2의 STORE 변수 찾기
                var_key2 = (block_id2, surface_group_key, surface_id, 'STORE', rotate)
                if var_key2 in self.block_schedule_var_by_id_group_surf_work_rotate_dict:
                    store_var2 = self.block_schedule_var_by_id_group_surf_work_rotate_dict[var_key2]

                    # 위치 변수도 찾기
                    pos_key2 = (block_id2, surface_group_key, surface_id, rotate)
                    x_var2 = self.block_x_var_by_id_group_surf_rotate_dict.get(pos_key2)
                    y_var2 = self.block_y_var_by_id_group_surf_rotate_dict.get(pos_key2)

                    placements2.append({
                        'store_var': store_var2,
                        'x_var': x_var2,
                        'y_var': y_var2,
                        'surface_group_key': surface_group_key,
                        'surface_id': surface_id,
                        'rotate': rotate
                    })

        ### 목적함수 계산 ###
        # 1단계: 같은 정반에 배치될 때 위치 차이 최소화
        for workarea_1 in placements1:
            for workarea_2 in placements2:
                # 같은 정반, 같은 회전인 경우
                if (workarea_1['surface_group_key'] == workarea_2['surface_group_key'] and
                        workarea_1['surface_id'] == workarea_2['surface_id'] and
                        workarea_1['rotate'] == workarea_2['rotate']):

                    # 두 블록이 모두 이 정반에 배치되는 경우 체크
                    both_placed = (self.cpmodel.presence_of(workarea_1['store_var']) *
                                   self.cpmodel.presence_of(workarea_2['store_var']))

                    # x축, y축 위치 변수가 존재하는 경우만 거리 계산
                    if (workarea_1['x_var'] is not None and workarea_1['y_var'] is not None and
                            workarea_2['x_var'] is not None and workarea_2['y_var'] is not None):

                        # x축 위치 차이 계산
                        x1_start = self.cpmodel.start_of(workarea_1['x_var'])
                        x2_start = self.cpmodel.start_of(workarea_2['x_var'])
                        x_diff = self.cpmodel.abs(x1_start - x2_start)

                        # y축 위치 차이 계산
                        y1_start = self.cpmodel.start_of(workarea_1['y_var'])
                        y2_start = self.cpmodel.start_of(workarea_2['y_var'])
                        y_diff = self.cpmodel.abs(y1_start - y2_start)

                        # 맨하탄 거리 계산
                        distance = x_diff + y_diff

                        # 거리를 최소화하기 위해 음수로 변환 (거리가 작을수록 좋음)
                        distance_penalty = distance

                        # 같은 정반 배치 점수 + 위치 근접성 점수
                        total_score = score_position * distance_penalty
                        objective_exprs.append(total_score * both_placed)
                        objective_exprs1.append(total_score * both_placed)

                    else:
                        # 위치 변수가 없는 경우 기본 점수만 부여
                        objective_exprs.append(score_position * 0)
                        objective_exprs1.append(score_position * 0)
                        pass

        # 2단계: 같은 정반 그룹에 배치
        # 두 블록이 배치 가능한 모든 정반 list
        all_group_keys = []
        for workarea in placements1 + placements2:
            """
            예를 들어, 220L블록이 2, 4-1, 4-2, 4-3, 4-4에 배치 가능하고, 220R블록이 4-1, 4-2, 4-3, 4-4에 배치 가능하면 -> 공통인 것들만 추출
            """
            if workarea['surface_group_key'] not in all_group_keys:
                all_group_keys.append(workarea['surface_group_key'])

        # 각 정반 그룹에 따른 변수 list
        for group_key in all_group_keys:
            group_vars1 = []
            for workarea_1 in placements1:
                if workarea_1['surface_group_key'] == group_key:
                    group_vars1.append(workarea_1['store_var'])

            group_vars2 = []
            for workarea_2 in placements2:
                if workarea_2['surface_group_key'] == group_key:
                    group_vars2.append(workarea_2['store_var'])

            # 동일 정반 배치 가능 여부 계산
            if len(group_vars1) > 0 and len(group_vars2) > 0:
                # 블록1 배치 여부 계산
                block1_presence_list = []
                for var in group_vars1:
                    block1_presence_list.append(self.cpmodel.presence_of(var))
                block1_in_group = self.cpmodel.sum(block1_presence_list)

                # 블록2 배치 여부 계산
                block2_presence_list = []
                for var in group_vars2:
                    block2_presence_list.append(self.cpmodel.presence_of(var))
                block2_in_group = self.cpmodel.sum(block2_presence_list)

                # Pointing 계산(둘 다 배치: (1,1), 둘 중 하나만 배치: (1,0), 둘다 배치 X: (0,0))
                both_in_group = self.cpmodel.min(block1_in_group, block2_in_group)

                # penalty 계산(둘 다 배치: 0, 둘 중 하나만 배치: 0, 둘 다 미배치: 0
                penalty_2 = score_same_workarea * (1 - both_in_group)
                objective_exprs.append(penalty_2)
                objective_exprs2.append(penalty_2)

        # 3단계: 서로 다른 그룹이라도 둘 다 배치
        if len(placements1) > 0 and len(placements2) > 0:
            # 블록1 배치 여부 계산
            block1_all_presence = []
            for variable_1 in placements1:
                block1_all_presence.append(self.cpmodel.presence_of(variable_1['store_var']))
            block1_placed = self.cpmodel.sum(block1_all_presence)

            # 블록2 배치 여부 계산
            block2_all_presence = []
            for variable_2 in placements2:
                block2_all_presence.append(self.cpmodel.presence_of(variable_2['store_var']))
            block2_placed = self.cpmodel.sum(block2_all_presence)

            # Pointing 계산(둘 다 배치: (1,1), 둘 중 하나만 배치: (1,0), 둘다 배치 X: (0,0))
            both_placed = self.cpmodel.min(block1_placed, block2_placed)

            penalty_3 = score_both_allocation * (1 - both_placed)
            objective_exprs.append(penalty_3)
            objective_exprs3.append(penalty_3)

    # 전체 목적함수 합산
    if objective_exprs:
        self.obj_sum_allocation = self.cpmodel.sum(objective_exprs)
        self.obj_sum_allocation1 = self.cpmodel.sum(objective_exprs1)
        self.obj_sum_allocation2 = self.cpmodel.sum(objective_exprs2)
        self.obj_sum_allocation3 = self.cpmodel.sum(objective_exprs3)
    else:
        self.obj_sum_allocation = 0
