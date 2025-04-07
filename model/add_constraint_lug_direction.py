def add_constraint_lug_direction(self):
    """
    블록 방향 L을 정반 방향 L에 넣으려면 돌림 필요 X
    블록 방향 L을 정반 방향 B에 넣으려면 돌림 90도 필요
    :param self:
    :return:
    """
    # Idea
    # if WorkArea.lug_condition == 'L':
    #     if Block.lug_direction == 'L':
    #         self.cpmodel.add(0 == self.cpmodel.presence_of(rotation=90도 일때의 interval variable))
    #     elif Block.lug_direction == 'B':
    #         self.cpmodel.add(0 == self.cpmodel.presence_of(rotation=0도 일때의 interval variable))
    # else:
    #     상관없음


    for block_key, block in self.block_dict.items():
        block_id = f"{block.ship_type}_{block.project_number}_{block.block_number}"
        # 모든 정반과 회전 각도에 대해 변수 탐색
        for surface_group_key, work_area in self.work_area_dict.items():
            # 정반 ID를 스트링으로 변환 (리스트일 경우 튜플로 변환)
            surface_id = work_area.surface_id_list
            if isinstance(surface_id, list):
                surface_id = tuple(surface_id)
            # 회전 각도별로 변수 생성
            for rotate in [0, 90]:
                # 변수 키 생성
                var_key = (block_id, surface_group_key, surface_id, rotate)
                if work_area.lug_condition == 'L':
                    if block.lug_direction == 'L': # 정반은 L, 블록은 L일 때는 rotate가 90이면 안됨
                        if rotate == 90:
                            self.cpmodel.add(0 == self.cpmodel.presence_of(self.block_time_var_by_id_group_surf_rotate_dict[var_key]))
                            print(f"Block {block_id}이 Work Area {work_area.group_id}에 갈 경우, work_area.lug_condition={work_area.lug_condition}, block.lug_direction={block.lug_direction} 이므로 rotate={rotate} 이면 안 된다는 제약이 추가되었습니다.")
                        else:
                            pass
                    elif block.lug_direction == 'B': # 정반은 L, 블록은 B일 때는 rotate가 0이면 안됨
                        if rotate == 0:
                            self.cpmodel.add(0 == self.cpmodel.presence_of(self.block_time_var_by_id_group_surf_rotate_dict[var_key]))
                            print(f"Block {block_id}이 Work Area {work_area.group_id}에 갈 경우, work_area.lug_condition = {work_area.lug_condition}, block.lug_direction={block.lug_direction} 이므로 rotate={rotate} 이면 안 된다는 제약이 추가되었습니다.")
                        else:
                            pass
                else: # 블록 정반 조건이 L이 아닌 경우는 따로 없기에 만들지 않음
                    pass




