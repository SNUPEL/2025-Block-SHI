def add_constraint_scheduled(self):
    """
    대상 기간 이전에 기 배치된 블록을 제약으로 추가
    """
    # 각 블록에 대해 변수 생성
    for block_key in self.block_keys:
        block = self.block_dict[block_key]
        block_id = f"{block.ship_type}_{block.project_number}_{block.block_number}"

        if block.allocate_condition == 'Y':

            '''1. self.block_schedule_var_by_id_group_surf_work_rotate_dict 에서 변수 찾기'''
            for key, val in self.block_schedule_var_by_id_group_surf_work_rotate_dict.items():
                # 기본 흐름
                if key[0] == block_id:
                    if key[1] == (block.group_id,block.surf_id) and key[4] == block.rotate:
                        # 1. 해당 정반으로 스케줄 변수 고정
                        self.cpmodel.add(
                            self.cpmodel.presence_of(
                                self.block_schedule_var_by_id_group_surf_work_rotate_dict[key]) == 1
                            )

                        '''2. 해당 정반에 x, y, 시간축 변수 고정'''
                        # 2-1. X축
                        self.cpmodel.add(
                            self.cpmodel.presence_of(
                                self.block_x_var_by_id_group_surf_rotate_dict[key]) == 1
                        )
                        self.cpmodel.add(
                            self.cpmodel.start_of(
                                self.block_x_var_by_id_group_surf_rotate_dict[key]) == block.x_location
                        )

                        # 2-2. Y축
                        self.cpmodel.add(
                            self.cpmodel.presence_of(
                                self.block_y_var_by_id_group_surf_rotate_dict[key]) == 1
                        )
                        self.cpmodel.add(
                            self.cpmodel.start_of(
                                self.block_y_var_by_id_group_surf_rotate_dict[key]) == block.y_location
                        )

                        # 2-1. 시간축
                        self.cpmodel.add(
                            self.cpmodel.presence_of(
                                self.block_time_var_by_id_group_surf_rotate_dict[key]) == 1
                        )
                        self.cpmodel.add(
                            self.cpmodel.start_of(
                                self.block_time_var_by_id_group_surf_rotate_dict[key]) == block.allocation_index
                        )

            pass

