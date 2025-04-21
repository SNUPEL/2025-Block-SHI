def add_constraint_block_intersection(self):
    """
        블록 간섭 금지 제약 조건
    """
    # 모든 블록 쌍에 대해 반복
    for i, block_key1 in enumerate(self.block_keys):
        block1 = self.block_dict[block_key1]
        block_id1 = f"{block1.ship_type}_{block1.project_number}_{block1.block_number}"

        for j, block_key2 in enumerate(self.block_keys[i + 1:], i + 1):
            if i == j:  # 같은 블록은 비교하지 않음
                continue

            block2 = self.block_dict[block_key2]
            block_id2 = f"{block2.ship_type}_{block2.project_number}_{block2.block_number}"

            # 모든 정반에 대해 반복
            for surface_group_key, work_area in self.work_area_dict.items():
                surface_id = work_area.surface_id_list
                if isinstance(surface_id, list):
                    surface_id = tuple(surface_id)

                # 각 회전 조합에 대해 반복
                for rotate1 in self.rotation_list:
                    for rotate2 in self.rotation_list:
                        # 첫 번째 블록 변수 키
                        var_key1 = (block_id1, surface_group_key, surface_id, rotate1)

                        # 두 번째 블록 변수 키
                        var_key2 = (block_id2, surface_group_key, surface_id, rotate2)

                        # 두 블록 변수가 모두 존재하는지 확인
                        if (var_key1 not in self.block_x_var_by_id_group_surf_rotate_dict or
                                var_key2 not in self.block_x_var_by_id_group_surf_rotate_dict):
                            continue

                        # 첫 번째 블록의 위치 변수
                        x_var1 = self.block_x_var_by_id_group_surf_rotate_dict[var_key1]
                        y_var1 = self.block_y_var_by_id_group_surf_rotate_dict[var_key1]
                        time_var1 = self.block_time_var_by_id_group_surf_rotate_dict[var_key1]

                        # 두 번째 블록의 위치 변수
                        x_var2 = self.block_x_var_by_id_group_surf_rotate_dict[var_key2]
                        y_var2 = self.block_y_var_by_id_group_surf_rotate_dict[var_key2]
                        time_var2 = self.block_time_var_by_id_group_surf_rotate_dict[var_key2]

                        self.cpmodel.add(
                            # 두 블록이 동시에 존재할 경우에만 제약 적용
                            (self.cpmodel.presence_of(x_var1) * self.cpmodel.presence_of(x_var2) == 0) |

                            # X축 비겹침: 블록1 오른쪽 끝 ≤ 블록2 왼쪽 또는 블록2 오른쪽 끝 ≤ 블록1 왼쪽
                            (((self.cpmodel.end_of(x_var1) <= self.cpmodel.start_of(x_var2)) |
                            (self.cpmodel.end_of(x_var2) <= self.cpmodel.start_of(x_var1))))

                            &

                            # Y축 비겹침: 블록1 위쪽 끝 ≤ 블록2 아래쪽 또는 블록2 위쪽 끝 ≤ 블록1 아래쪽
                            ((self.cpmodel.end_of(y_var1) <= self.cpmodel.start_of(y_var2)) |
                            (self.cpmodel.end_of(y_var2) <= self.cpmodel.start_of(y_var1)))

                            &

                            # 시간 비겹침: 블록1 적치 종료 ≤ 블록2 적치 시작 또는 블록2 적치 종료 ≤ 블록1 적치 시작
                            ((self.cpmodel.end_of(time_var1) <= self.cpmodel.start_of(time_var2)) |
                            (self.cpmodel.end_of(time_var2) <= self.cpmodel.start_of(time_var1)))
                        )
