def add_constraint_lug_direction(self):

    for block_key, block in self.block_dict.items():
        block_id = f"{block.ship_type}_{block.project_number}_{block.block_number}"

        # 모든 정반과 회전 각도에 대해 변수 탐색
        for surface_group_key, work_area in self.work_area_dict.items():
            # 정반 ID를 스트링으로 변환 (리스트일 경우 튜플로 변환)
            surface_id = work_area.surface_id_list
            if isinstance(surface_id, list):
                surface_id = tuple(surface_id)

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
