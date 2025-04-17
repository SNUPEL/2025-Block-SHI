def add_constraint_simultaneous_block(self):
    """
    L/R 블록 동일 정반 배치 제약 조건
    """
    # 모든 블록 쌍을 검사
    for i, block_key1 in enumerate(self.block_keys):
        block1 = self.block_dict[block_key1]
        ship_type1, project_number1, block_number1 = block_key1
        base_number1 = block_number1[:-1]  # 마지막 문자 제외한 블록 번호
        block_id1 = f"{ship_type1}_{project_number1}_{block_number1}"

        for j in range(i + 1, len(self.block_keys)):
            block_key2 = self.block_keys[j]
            block2 = self.block_dict[block_key2]
            ship_type2, project_number2, block_number2 = block_key2
            base_number2 = block_number2[:-1]  # 마지막 문자 제외한 블록 번호
            block_id2 = f"{ship_type2}_{project_number2}_{block_number2}"

            # 같은 선종, 호선이고 블록 번호의 마지막 문자만 다른 경우
            if (ship_type1 == ship_type2 and
                    project_number1 == project_number2 and
                    base_number1 == base_number2 and
                    block_number1 != block_number2 and
                    block1.allocation_index == block2.allocation_index):

                # 두 블록이 모두 정반에 배치될 수 있어야 함
                for surface_group_key, work_area in self.work_area_dict.items():
                    for rotate in self.rotation_list:
                        # 두 블록의 해당 정반, 회전에 대한 STORE 변수 찾기
                        interval_key1 = None
                        interval_key2 = None

                        # 첫 번째 블록의 변수 찾기
                        for interval in self.block_schedule_var_by_id_group_surf_work_rotate_dict:
                            if (interval[0] == block_id1 and interval[1] == surface_group_key and
                                    interval[3] == 'STORE' and interval[4] == rotate):
                                interval_key1 = interval
                                break

                        # 두 번째 블록의 변수 찾기
                        for interval in self.block_schedule_var_by_id_group_surf_work_rotate_dict:
                            if (interval[0] == block_id2 and interval[1] == surface_group_key and
                                    interval[3] == 'STORE' and interval[4] == rotate):
                                interval_key2 = interval
                                break

                        # 두 블록 모두 해당 정반에 배치될 수 있는 경우 제약조건 추가
                        if interval_key1 and interval_key2:
                            self.cpmodel.add(
                                self.cpmodel.presence_of(
                                    self.block_schedule_var_by_id_group_surf_work_rotate_dict[interval_key1]
                                ) ==
                                self.cpmodel.presence_of(
                                    self.block_schedule_var_by_id_group_surf_work_rotate_dict[interval_key2]
                                )
                            )
