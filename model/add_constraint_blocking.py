def add_constraint_blocking(self):
    """
    정반그룹 4번에 배치된 블록들에 대하여 먼저 입고/나중에 출고되는 블록이 더 안쪽에 배치되는 것을 조건으로 이중배치를 허용하는 제약 구현
    """
    schedule_var_list_by_group_dict = {}

    # for block_key, block in self.block_dict.items():
    #     block_id = f"{block.ship_type}_{block.project_number}_{block.block_number}"

    # 모든 블록 쌍에 대해 반복
    for i, block_key1 in enumerate(self.block_keys):
        block1 = self.block_dict[block_key1]
        block_id1 = f"{block1.ship_type}_{block1.project_number}_{block1.block_number}"
        for j, block_key2 in enumerate(self.block_keys[i + 1:], i + 1):
            if i == j:  # 같은 블록은 비교하지 않음
                continue
            block2 = self.block_dict[block_key2]
            block_id2 = f"{block2.ship_type}_{block2.project_number}_{block2.block_number}"

            # TP 사용그룹에 대해서만 고려
            TP_group_dict = {key: val for key, val in self.work_area_dict.items() if val.TP_condition == 'Y'}
            for group_key, group_val in TP_group_dict.items():
                # 정반 ID를 스트링으로 변환 (리스트일 경우 튜플로 변환)
                surface_id = group_val.surface_id_list
                if isinstance(surface_id, list):
                    surface_id = tuple(surface_id)

                if sum(self.work_area_dict[group_key].TP_direction) == 1:
                    # 정해진 TP 방향이 하나만 있음
                    # 모든 회전 조합에 대해 고려
                    for rotate1 in [0, 90]:
                        for rotate2 in [0, 90]:
                            block1_var_key = (block_id1, group_key, surface_id, rotate1)
                            block2_var_key = (block_id2, group_key, surface_id, rotate2)

                            # 두 블록 변수가 모두 존재하는지 확인
                            if (block1_var_key not in self.block_x_var_by_id_group_surf_rotate_dict or
                                    block2_var_key not in self.block_x_var_by_id_group_surf_rotate_dict):
                                continue

                            # 첫 번째 블록의 위치 변수
                            block1_x_var = self.block_x_var_by_id_group_surf_rotate_dict[block1_var_key]
                            block1_y_var = self.block_y_var_by_id_group_surf_rotate_dict[block1_var_key]
                            block1_time_var = self.block_time_var_by_id_group_surf_rotate_dict[block1_var_key]

                            # 두 번째 블록의 위치 변수
                            block2_x_var = self.block_x_var_by_id_group_surf_rotate_dict[block2_var_key]
                            block2_y_var = self.block_y_var_by_id_group_surf_rotate_dict[block2_var_key]
                            block2_time_var = self.block_time_var_by_id_group_surf_rotate_dict[block2_var_key]

                            # presence_both = (self.cpmodel.presence_of(block1_time_var) *
                            #                  self.cpmodel.presence_of(block2_time_var)) == 1

                            y_overlap = ((self.cpmodel.start_of(block1_y_var) < self.cpmodel.end_of(block2_y_var)) &
                                         (self.cpmodel.start_of(block2_y_var) < self.cpmodel.end_of(block1_y_var)))

                            if self.work_area_dict[group_key].TP_direction.index(True) == 1:
                                '''(4, (2, 3, 4)) 번 정반그룹의 경우'''
                                self.cpmodel.add(
                                    (self.cpmodel.presence_of(block1_time_var) == 0) |
                                    (self.cpmodel.presence_of(block2_time_var) == 0) |
                                    (y_overlap == 0) |
                                    (
                                            (self.cpmodel.start_of(block1_x_var) < self.cpmodel.start_of(
                                                block2_x_var))  &
                                            (self.cpmodel.start_of(block2_time_var) >= self.cpmodel.start_of(
                                                block1_time_var))  &
                                            (self.cpmodel.end_of(block1_time_var) >= self.cpmodel.end_of(
                                                block2_time_var))
                                    )
                                    |
                                    (
                                            (self.cpmodel.start_of(block1_x_var) > self.cpmodel.start_of(
                                                block2_x_var)) &
                                            (self.cpmodel.start_of(block2_time_var) <= self.cpmodel.start_of(
                                                block1_time_var)) &
                                            (self.cpmodel.end_of(block1_time_var) <= self.cpmodel.end_of(
                                                block2_time_var))
                                    )
                                )


                            elif self.work_area_dict[group_key].TP_direction.index(True) == 3:
                                '''(4, (5, 6, 7)) 번 정반그룹의 경우'''
                                self.cpmodel.add(
                                    (self.cpmodel.presence_of(block1_time_var) == 0) |
                                    (self.cpmodel.presence_of(block2_time_var) == 0) |
                                    (y_overlap == 0) |
                                    (
                                            (self.cpmodel.start_of(block1_x_var) > self.cpmodel.start_of(
                                                block2_x_var)) &
                                            (self.cpmodel.start_of(block2_time_var) >= self.cpmodel.start_of(
                                                block1_time_var)) &
                                            (self.cpmodel.end_of(block1_time_var) >= self.cpmodel.end_of(
                                                block2_time_var))
                                    )
                                    |
                                    (
                                            (self.cpmodel.start_of(block1_x_var) < self.cpmodel.start_of(
                                                block2_x_var)) &
                                            (self.cpmodel.start_of(block2_time_var) <= self.cpmodel.start_of(
                                                block1_time_var)) &
                                            (self.cpmodel.end_of(block1_time_var) <= self.cpmodel.end_of(
                                                block2_time_var))
                                    )
                                )
                    else: # TP direction 이 0이나 2번 index 에서 True
                        '''TP 운송 방향이 위 혹은 아래인 경우 <- 현재 문제에서 개발 대상 아님'''
                        pass
                elif sum(self.work_area_dict[group_key].TP_direction) == 2:
                    '''(4,(1,)) 의 경우 <- 아직 개발 대상 아님'''
                    pass
        pass