def add_constraint_lug_direction(self):
    """
    블록 방향 L을 정반 방향 L에 넣으려면 돌림 필요 X
    블록 방향 L을 정반 방향 B에 넣으려면 돌림 90도 필요
    :param self:
    :return:
    """

    for block_key, block in self.block_dict.items():
        block_id = f"{block.ship_type}_{block.project_number}_{block.block_number}"

        # 모든 정반과 회전 각도에 대해 변수 탐색
        for surface_group_key, work_area in self.work_area_dict.items():
            # 정반 ID를 스트링으로 변환 (리스트일 경우 튜플로 변환)
            surface_id = work_area.surface_id_list
            if isinstance(surface_id, list):
                surface_id = tuple(surface_id)

            # 정반그룹 4번의 경우 TP 방향에 따른 회전 제약 적용
            if surface_group_key[0] == 4:
                # TP 방향 분석
                tp_directions = work_area.TP_direction

                # TP 운송방향이 없는 경우는 처리하지 않음 (제약 없음)
                if not any(tp_directions):
                    continue

                # 방향 조합 분석
                direction_L = any([tp_directions[1], tp_directions[3]])  # 방향 2 또는 4가 활성화 (L)
                direction_B = any([tp_directions[0], tp_directions[2]])  # 방향 1 또는 3이 활성화 (B)

                # 인접 방향 확인 또는 3개 이상 방향 활성화 확인
                has_adjacent = (
                        (tp_directions[0] and tp_directions[1]) or
                        (tp_directions[0] and tp_directions[3]) or
                        (tp_directions[2] and tp_directions[1]) or
                        (tp_directions[2] and tp_directions[3])
                )
                has_flexible_direction = has_adjacent or sum(tp_directions) >= 3

                # 회전 각도별로 변수 생성
                for rotate in [0, 90]:
                    # 변수 키 생성
                    var_key = (block_id, surface_group_key, surface_id, rotate)

                    # 변수가 존재하는지 확인 추가
                    if var_key not in self.block_time_var_by_id_group_surf_rotate_dict:
                        continue

                    # 인접 방향이 활성화된 경우 또는 3개 이상 방향이 활성화된 경우 회전 제약 없음
                    if has_flexible_direction:
                        continue

                    # 블록 방향에 따른 제약
                    if block.lug_direction == 'L':  # 블록 방향이 L일 때
                        if rotate == 90 and direction_B:  # B방향 운송만 가능한데 90도 회전하려는 경우
                            self.cpmodel.add(0 == self.cpmodel.presence_of(
                                self.block_time_var_by_id_group_surf_rotate_dict[var_key]))
                        elif rotate == 0 and direction_L:  # L방향 운송만 가능한데 0도 회전하려는 경우
                            self.cpmodel.add(0 == self.cpmodel.presence_of(
                                self.block_time_var_by_id_group_surf_rotate_dict[var_key]))
                    elif block.lug_direction == 'B':  # 블록 방향이 B일 때
                        if rotate == 0 and direction_B:  # B방향 운송만 가능한데 0도 회전하려는 경우
                            self.cpmodel.add(0 == self.cpmodel.presence_of(
                                self.block_time_var_by_id_group_surf_rotate_dict[var_key]))
                        elif rotate == 90 and direction_L:  # L방향 운송만 가능한데 90도 회전하려는 경우
                            self.cpmodel.add(0 == self.cpmodel.presence_of(
                                self.block_time_var_by_id_group_surf_rotate_dict[var_key]))
            else:
                # 정반그룹 4번이 아닌 경우 기존 로직 적용
                for rotate in [0, 90]:
                    # 변수 키 생성
                    var_key = (block_id, surface_group_key, surface_id, rotate)

                    # 변수가 존재하는지 확인 추가
                    if var_key not in self.block_time_var_by_id_group_surf_rotate_dict:
                        continue

                    # 원래 코드와 동일한 로직 적용
                    if work_area.lug_condition == 'L':
                        if block.lug_direction == 'L':  # 정반은 L, 블록은 L일 때는 rotate가 90이면 안됨
                            if rotate == 90:
                                self.cpmodel.add(0 == self.cpmodel.presence_of(
                                    self.block_time_var_by_id_group_surf_rotate_dict[var_key]))
                        elif block.lug_direction == 'B':  # 정반은 L, 블록은 B일 때는 rotate가 0이면 안됨
                            if rotate == 0:
                                self.cpmodel.add(0 == self.cpmodel.presence_of(
                                    self.block_time_var_by_id_group_surf_rotate_dict[var_key]))







