def add_constraint_area_limitation(self):
    '''
    정반그룹 별 최대 size 제한
    :param self:
    :return:
    '''
    ML = 100
    MB = 100
    MH = 100
    MW = 100
    # ML = MAX_BLOCK_LENGTH
    # MB = MAX_BLOCK_BREADTH
    # MH = MAX_BLOCK_HEIGHT
    # MW = MAX_BLOCK_WEIGHT
    for block_key, block in self.block_dict.items():
        # x1 : 1번 정반그룹에 배치되었는지의 여부 (1 if True, 0 if False)
        # 회전 다 고려해서 합이 1 인 어떤 변수 ??
        # self.block_x_var_by_id_group_surf_rotate_dict[var_key][1]
        for 모든 var_key에 대해서
            if self.block_time_var_by_id_group_surf_rotate_dict[var_key][1]=="GROUP1":
                block = self.block_time_var_by_id_group_surf_rotate_dict[var_key][0]
                self.cpmodel.add(block_dict[block].length <=10)

        # self.cpmodel.add(block.length<=10+ML*(1-self.cpmodel.presence_of(0,"GROUP1",_,_) )
        self.cpmodel.add_constraint(block.length<=10+ML*(1-x1))
        self.cpmodel.add_constraint(block.length<=11+ML*(1-x2))
        self.cpmodel.add_constraint(block.length<=8+ML*(1-x3))
        self.cpmodel.add_constraint(block.length<=8+ML*(1-x5))

        self.cpmodel.add_constraint(block.breadth<=8+MB*(1-x1))
        self.cpmodel.add_constraint(block.breadth<=11+MB*(1-x2))
        self.cpmodel.add_constraint(block.breadth<=11+MB*(1-x3))
        self.cpmodel.add_constraint(block.breadth<=11+MB*(1-x5))

        self.cpmodel.add_constraint(block.height<=2+MH*(1-x1))
        self.cpmodel.add_constraint(block.height<=4+MH*(1-x2))
        self.cpmodel.add_constraint(block.height<=3+MH*(1-x3))
        self.cpmodel.add_constraint(block.height<=3+MH*(1-x5))

        self.cpmodel.add_constraint(block.weight<=30+MW*(1-x1))
        self.cpmodel.add_constraint(block.weight<=38+MW*(1-x2))
        self.cpmodel.add_constraint(block.weight<=38+MW*(1-x3))
        self.cpmodel.add_constraint(block.weight<=38+MW*(1-x5))