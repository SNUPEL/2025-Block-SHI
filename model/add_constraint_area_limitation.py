import pandas as pd


def add_constraint_area_limitation(self):

    cols = ['블록길이', '블록폭', '블록높이', '블록중량']

    # 1. 열 선택
    sizeinfo = self.df_raw_data_dict['BLK'][cols]

    # 2. 열마다 숫자로 변환 (DataFrame 전체에 적용)
    sizeinfo = sizeinfo.apply(pd.to_numeric, errors='coerce')

    # 3. 최대값 계산
    ML = sizeinfo['블록길이'].max()
    MB = sizeinfo['블록폭'].max()
    MH = sizeinfo['블록높이'].max()
    MW = sizeinfo['블록중량'].max()

    # 1. 데이터프레임에서 '사용여부'가 'Y'인 행만 필터
    groupinfo = self.df_raw_data_dict['WORKAREA_GROUP']
    groupinfo = groupinfo[(groupinfo['사용여부'] == 'Y') & (pd.to_numeric(groupinfo['사이즈제한LTH'], errors='coerce') != 0)]

    # 2. '사이즈제한LTH' 열만 리스트로 추출 (숫자형 변환 포함)
    length_limit = pd.to_numeric(groupinfo['사이즈제한LTH'], errors='coerce').tolist()
    breadth_limit = pd.to_numeric(groupinfo['사이즈제한BTH'], errors='coerce').tolist()
    height_limit = pd.to_numeric(groupinfo['사이즈제한HGT'], errors='coerce').tolist()
    weight_limit = pd.to_numeric(groupinfo['사이즈제한WGT'], errors='coerce').tolist()

    for block_key, block in self.block_dict.items():
        block_id = f"{block.ship_type}_{block.project_number}_{block.block_number}"
        # 모든 정반과 회전 각도에 대해 변수 탐색
        # 회전 각도별로 변수 생성
        for rotate in [0, 90]:
            # var_key 예시 : ('15000 TEU_PN1231_A110L', (1, (1, 2, 3, 4)), (1, 2, 3, 4), 0)
            for i, group in enumerate(range(1, 4)):
                var_key = (block_id, (group, (1, 2, 3, 4)), (1, 2, 3, 4), rotate)
                # 정반크기로 존재하지 않는 경우 제외하도록 추가
                if var_key not in self.block_time_var_by_id_group_surf_rotate_dict:
                    continue
                var_key = (block_id, (group, (1, 2, 3, 4)), (1, 2, 3, 4), rotate)
                self.cpmodel.add(block.length <= length_limit[i]+ML*(1-self.cpmodel.presence_of(self.block_time_var_by_id_group_surf_rotate_dict[var_key])))
                self.cpmodel.add(block.breadth <= breadth_limit[i]+MB*(1-self.cpmodel.presence_of(self.block_time_var_by_id_group_surf_rotate_dict[var_key])))
                self.cpmodel.add(block.height <= height_limit[i]+MH*(1-self.cpmodel.presence_of(self.block_time_var_by_id_group_surf_rotate_dict[var_key])))
                self.cpmodel.add(block.weight <= weight_limit[i]+MW*(1-self.cpmodel.presence_of(self.block_time_var_by_id_group_surf_rotate_dict[var_key])))
