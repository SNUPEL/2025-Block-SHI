def add_constraint_area_limitation(self):
    '''
    정반그룹 별 최대 size 제한
    :param self:
    :return:
    '''

    # # 1번 방법
    # for block_key, block in self.block_dict.items():
    #     block_id = f"{block.ship_type}_{block.project_number}_{block.block_number}"
    #     # 모든 정반과 회전 각도에 대해 변수 탐색
    #     for surface_group_key, work_area in self.work_area_dict.items():
    #         # 정반 ID를 스트링으로 변환 (리스트일 경우 튜플로 변환)
    #         surface_id = work_area.surface_id_list
    #         if isinstance(surface_id, list):
    #             surface_id = tuple(surface_id)
    #         # 회전 각도별로 변수 생성
    #         for rotate in [0, 90]:
    #             # 변수 키 생성
    #             var_key = (block_id, surface_group_key, surface_id, rotate)
    #             # var_key 예시 : ('15000 TEU_PN1231_A110L', (1, (1, 2, 3, 4)), (1, 2, 3, 4), 0)
    #             # self.cpmodel.size_of(self.block_time_var_by_id_group_surf_rotate_dict[var_key])
    #             if self.block_time_var_by_id_group_surf_rotate_dict[var_key].name.split('_')[-3][1] == '1':
    #                 # if bigger than 10 or 8 or 2 or 30
    #                     # than presence_of(self.block_time_var_by_id_group_surf_rotate_dict[var_key]) == 0
    #                 self.cpmodel.add(block.length <=10)
    #                 self.cpmodel.add(block.breadth <=11)
    #                 self.cpmodel.add(block.height <=8)
    #                 self.cpmodel.add(block.weight <=8)
    #             elif self.block_time_var_by_id_group_surf_rotate_dict[var_key].name.split('_')[-3][1] == '2':
    #                 self.cpmodel.add(block.length <=8)
    #                 self.cpmodel.add(block.breadth <=11)
    #                 self.cpmodel.add(block.height <=11)
    #                 self.cpmodel.add(block.weight <=11)
    #             elif self.block_time_var_by_id_group_surf_rotate_dict[var_key].name.split('_')[-3][1] == '3':
    #                 self.cpmodel.add(block.length <=2)
    #                 self.cpmodel.add(block.breadth <=4)
    #                 self.cpmodel.add(block.height <=3)
    #                 self.cpmodel.add(block.weight <=3)
                # # 5번은 지금 당장 안쓰기에 주석 처리 해놓음
                # elif self.block_time_var_by_id_group_surf_rotate_dict[var_key].name.split('_')[-3][1] == '5':
                #     self.cpmodel.add(block.length <=30)
                #     self.cpmodel.add(block.breadth <=38)
                #     self.cpmodel.add(block.height <=38)
                #     self.cpmodel.add(block.weight <=38)

    # 2번 방법
    # self.cpmodel.presence_of(block_id,(1,(1,2,3,4)),surface_id,rotate): 1번 정반그룹에 배치되었는지의 여부 (1 if True, 0 if False)

    ML = 100
    MB = 100
    MH = 100
    MW = 100
    # ML = MAX_BLOCK_LENGTH
    # MB = MAX_BLOCK_BREADTH
    # MH = MAX_BLOCK_HEIGHT
    # MW = MAX_BLOCK_WEIGHT

    length_limit = [10, 11, 8]
    breadth_limit = [8, 11, 11]
    height_limit = [2, 4, 3]
    weight_limit = [30, 38, 38]
    for block_key, block in self.block_dict.items():
        block_id = f"{block.ship_type}_{block.project_number}_{block.block_number}"
        # 모든 정반과 회전 각도에 대해 변수 탐색
        # 회전 각도별로 변수 생성
        for rotate in [0, 90]:
            # var_key 예시 : ('15000 TEU_PN1231_A110L', (1, (1, 2, 3, 4)), (1, 2, 3, 4), 0)
            for i, group in enumerate(range(1,4)):
                var_key = (block_id, (group, (1, 2, 3, 4)), (1, 2, 3, 4), rotate)
                self.cpmodel.add(block.length<=length_limit[i]+ML*(1-self.cpmodel.presence_of(self.block_time_var_by_id_group_surf_rotate_dict[var_key])))
                self.cpmodel.add(block.breadth<=breadth_limit[i]+MB*(1-self.cpmodel.presence_of(self.block_time_var_by_id_group_surf_rotate_dict[var_key])))
                self.cpmodel.add(block.height<=height_limit[i]+MH*(1-self.cpmodel.presence_of(self.block_time_var_by_id_group_surf_rotate_dict[var_key])))
                self.cpmodel.add(block.weight<=weight_limit[i]+MW*(1-self.cpmodel.presence_of(self.block_time_var_by_id_group_surf_rotate_dict[var_key])))
                # print(f"Block {block_id.split('_')[-1]}에 대해 Group {group}에 속한 경우 length가 {length_limit[i]} 이하여야 한다는 제약이 추가되었습니다.")
                # print(f"Block {block_id.split('_')[-1]}에 대해 Group {group}에 속한 경우 breadth가 {breadth_limit[i]} 이하여야 한다는 제약이 추가되었습니다.")
                # print(f"Block {block_id.split('_')[-1]}에 대해 Group {group}에 속한 경우 height가 {height_limit[i]} 이하여야 한다는 제약이 추가되었습니다.")
                # print(f"Block {block_id.split('_')[-1]}에 대해 Group {group}에 속한 경우 weight가 {weight_limit[i]} 이하여야 한다는 제약이 추가되었습니다.")


        # self.cpmodel.add_constraint(block.length<=10+ML*(1-x1))
        # self.cpmodel.add_constraint(block.length<=11+ML*(1-x2))
        # self.cpmodel.add_constraint(block.length<=8+ML*(1-x3))
        # self.cpmodel.add_constraint(block.length<=8+ML*(1-x5))
        #
        # self.cpmodel.add_constraint(block.breadth<=8+MB*(1-x1))
        # self.cpmodel.add_constraint(block.breadth<=11+MB*(1-x2))
        # self.cpmodel.add_constraint(block.breadth<=11+MB*(1-x3))
        # self.cpmodel.add_constraint(block.breadth<=11+MB*(1-x5))
        #
        # self.cpmodel.add_constraint(block.height<=2+MH*(1-x1))
        # self.cpmodel.add_constraint(block.height<=4+MH*(1-x2))
        # self.cpmodel.add_constraint(block.height<=3+MH*(1-x3))
        # self.cpmodel.add_constraint(block.height<=3+MH*(1-x5))
        #
        # self.cpmodel.add_constraint(block.weight<=30+MW*(1-x1))
        # self.cpmodel.add_constraint(block.weight<=38+MW*(1-x2))
        # self.cpmodel.add_constraint(block.weight<=38+MW*(1-x3))
        # self.cpmodel.add_constraint(block.weight<=38+MW*(1-x5))