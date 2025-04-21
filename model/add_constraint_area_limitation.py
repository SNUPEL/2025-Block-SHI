import pandas as pd
def add_constraint_area_limitation(self):
    '''
    정반그룹 별 최대 size 제한
    :param self:
    :return:
    '''

    # 2번 방법
    # self.cpmodel.presence_of(block_id,(1,(1,2,3,4)),surface_id,rotate): 1번 정반그룹에 배치되었는지의 여부 (1 if True, 0 if False)
    cols = ['블록길이', '블록폭', '블록높이', '블록중량']

    # 1. 열 선택
    sizeinfo = self.df_raw_data_dict['BLK'][cols]

    # 2. 열마다 숫자로 변환 (DataFrame 전체에 적용)
    sizeinfo = sizeinfo.apply(pd.to_numeric, errors='coerce')

    # 3. 최대값 계산
    max_length = sizeinfo['블록길이'].max()

    ML = sizeinfo['블록길이'].max()
    MB = sizeinfo['블록폭'].max()
    MH = sizeinfo['블록높이'].max()
    MW = sizeinfo['블록중량'].max()

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
                # 정반크기로 존재하지 않는 경우 제외하도록 추가
                if var_key not in self.block_time_var_by_id_group_surf_rotate_dict:
                    continue
                time_var = self.block_time_var_by_id_group_surf_rotate_dict[var_key]

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