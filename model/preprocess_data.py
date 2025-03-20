from class_definition import *
import pandas as pd
import numpy as np


def get_work_area_list(df_work_area_group, df_work_area):
    work_area_list = []
    for _, row in df_work_area_group.iterrows():
        if row['사용여부'] == 'Y':
            filtered_df_work_area = df_work_area[
                (df_work_area['그룹ID'] == row['그룹ID']) & (df_work_area['정반사용여부'] == 'Y')].copy()

            filtered_df_work_area['그룹내정반위치Y'] = filtered_df_work_area['그룹내정반위치Y'] + filtered_df_work_area[
                '마진거리1'].fillna(0)
            filtered_df_work_area['그룹내정반위치X'] = filtered_df_work_area['그룹내정반위치X'] - filtered_df_work_area[
                '마진거리4'].fillna(0)

            filtered_df_work_area['그룹내정반위치X'] = filtered_df_work_area['그룹내정반위치X'] - min(
                filtered_df_work_area['그룹내정반위치X'])
            filtered_df_work_area['그룹내정반위치Y'] = -1 * filtered_df_work_area['그룹내정반위치Y']

            filtered_df_work_area['정반폭'] = (filtered_df_work_area['정반폭'] + filtered_df_work_area['마진거리1'].fillna(0)
                                            + filtered_df_work_area['마진거리3'].fillna(0))
            filtered_df_work_area['정반길이'] = (filtered_df_work_area['정반길이'] + filtered_df_work_area['마진거리2'].fillna(0)
                                             + filtered_df_work_area['마진거리4'].fillna(0))

            # 정반끼리 조금 떨어져 있는 경우는 고려하지 않음
            if row['정반연결축'] == 'B':
                filtered_df_work_area_group_by_axis = filtered_df_work_area.groupby('그룹내정반위치Y')
            elif row['정반연결축'] == 'L':
                filtered_df_work_area_group_by_axis = filtered_df_work_area.groupby('그룹내정반위치X')
            elif row['정반연결축'] == 'LB':
                filtered_df_work_area_group_by_axis = [(None, filtered_df_work_area)]
            elif pd.isna(row['정반연결축']):
                for idx, rect in filtered_df_work_area.iterrows():
                    length = rect['정반길이']
                    breadth = rect['정반폭']
                    direction = [rect['TP운송방향1'] == 'Y', rect['TP운송방향2'] == 'Y', rect['TP운송방향3'] == 'Y',
                                 rect['TP운송방향4'] == 'Y']
                    temp_work_area = WorkArea(group_id=row['그룹ID'], surface_id_list=rect['정반ID'], priority=row['우선순위'],
                                              indoor_outdoor_condition=row['옥내외'], lug_condition=row['우선순위'],
                                              L_limit_of_block=row['사이즈제한LTH'], B_limit_of_block=row['사이즈제한BTH'],
                                              H_limit_of_block=row['사이즈제한HGT'], W_limit_of_block=row['사이즈제한WGT'],
                                              TP_condition=row['TP운송여부'], TP_direction=direction, L=length, B=breadth)
                    temp_work_area.work_unit_dict[rect['정반ID']] = WorkUnit(unit_id=rect['정반ID'], x=rect['그룹내정반위치X'],
                                                                           y=rect['그룹내정반위치Y'], dx=length, dy=breadth)
                    work_area_list.append(temp_work_area)
                filtered_df_work_area_group_by_axis = None
            else:
                print('Unexpected input error encountered.')
                continue
            # 각 그룹별로 결합된 직사각형의 크기를 계산
            if filtered_df_work_area_group_by_axis is not None:
                for group_key, group in filtered_df_work_area_group_by_axis:
                    temp_row = group.loc[group['정반ID'].idxmin()]
                    direction = [temp_row['TP운송방향1'] == 'Y', temp_row['TP운송방향2'] == 'Y', temp_row['TP운송방향3'] == 'Y',
                                 temp_row['TP운송방향4'] == 'Y']

                    x_vals = set()
                    y_vals = set()
                    for _, r in group.iterrows():
                        x_vals.add(r['그룹내정반위치X'])
                        x_vals.add(r['그룹내정반위치X'] + r['정반길이'])
                        y_vals.add(r['그룹내정반위치Y'])
                        y_vals.add(r['그룹내정반위치Y'] + r['정반폭'])
                    x_vals = sorted(x_vals)
                    y_vals = sorted(y_vals)
                    grid = np.zeros((len(y_vals) - 1, len(x_vals) - 1), dtype=bool)
                    for _, r in group.iterrows():
                        left = r['그룹내정반위치X']
                        bottom = r['그룹내정반위치Y']
                        right = left + r['정반길이']
                        top = bottom + r['정반폭']
                        # 경계 좌표 리스트에서 인덱스 찾기
                        ix1 = x_vals.index(left)
                        ix2 = x_vals.index(right)
                        iy1 = y_vals.index(bottom)
                        iy2 = y_vals.index(top)
                        grid[iy1:iy2, ix1:ix2] = True

                    combined_length = x_vals[-1] - x_vals[0]
                    combined_breadth = y_vals[-1] - y_vals[0]
                    temp_work_area\
                        = WorkArea(group_id=row['그룹ID'], surface_id_list=list(group['정반ID']), priority=row['우선순위'],
                                   indoor_outdoor_condition=row['옥내외'], lug_condition=row['우선순위'],
                                   L_limit_of_block=row['사이즈제한LTH'], B_limit_of_block=row['사이즈제한BTH'],
                                   H_limit_of_block=row['사이즈제한HGT'], W_limit_of_block=row['사이즈제한WGT'],
                                   TP_condition=row['TP운송여부'], TP_direction=direction,
                                   L=combined_length, B=combined_breadth)

                    print(
                        f"work_area {temp_work_area.group_id}-{temp_work_area.surface_id_list}:"
                        f" L={temp_work_area.L}, B={temp_work_area.B}")

                    for _, rect in group.iterrows():
                        temp_work_area.work_unit_dict[rect['정반ID']]\
                            = WorkUnit(unit_id=rect['정반ID'], x=rect['그룹내정반위치X'], y=rect['그룹내정반위치Y'],
                                       dx=rect['정반길이'], dy=rect['정반폭'])

                    if not np.all(grid):
                        false_indices = np.argwhere(~grid)
                        min_y_idx = false_indices[:, 0].min()
                        max_y_idx = false_indices[:, 0].max()
                        min_x_idx = false_indices[:, 1].min()
                        max_x_idx = false_indices[:, 1].max()

                        missing_lower_left_x = x_vals[min_x_idx] - x_vals[0]
                        missing_lower_left_y = y_vals[min_y_idx] - y_vals[0]
                        missing_length = x_vals[max_x_idx + 1] - x_vals[min_x_idx]
                        missing_breadth = y_vals[max_y_idx + 1] - y_vals[min_y_idx]

                        # 향후 고정 블록으로 구현
                        temp_work_area.add_unavailable_area(missing_lower_left_x, missing_lower_left_y,
                                                            missing_length, missing_breadth)

                        print(
                            f"work_area {temp_work_area.group_id}-{temp_work_area.surface_id_list}"
                            f" has an empty area at ({temp_work_area.unavailable_area_x},"
                            f" {temp_work_area.unavailable_area_y})"
                            f" with L={temp_work_area.unavailable_area_L}, B={temp_work_area.unavailable_area_B}")

                    work_area_list.append(temp_work_area)
        else:
            continue
    print('Work area definition is complete')
    return work_area_list


def preprocess_data(self):
    sheet_name_list = list(self.df_raw_data_dict.keys())
    if 'WORKAREA_GROUP' in sheet_name_list and 'WORKAREA' in sheet_name_list:
        df_work_area_group = self.df_raw_data_dict['WORKAREA_GROUP']
        df_work_area = self.df_raw_data_dict['WORKAREA']
        self.work_area_list = get_work_area_list(df_work_area_group, df_work_area)
    else:
        print('Sheet names do not match')

    if 'WORKAREA_CRANE_REL' in sheet_name_list and 'CRANE_WORK_TIME' in sheet_name_list:
        df_crane_time = pd.merge(self.df_raw_data_dict['WORKAREA_CRANE_REL'], self.df_raw_data_dict['CRANE_WORK_TIME'],
                                 on=['작업종류', '크레인ID'], how='left')
        for work_area in self.work_area_list:
            for key, group in df_crane_time.groupby('그룹ID').get_group(work_area.group_id).groupby('작업종류'):
                work_area.crane_operation_dict[key] = (sum(group['작업시간']), list(group['크레인ID']))
    else:
        print('Sheet names do not match')

    if 'CRANE' in sheet_name_list and 'CRANE_RESV_SCH' in sheet_name_list:
        for _, row in self.df_raw_data_dict['CRANE'].iterrows():
            self.crane_dict[row['크레인ID']] = Crane(Crane_id=row['크레인ID'], condition=row['사용여부'])

        # 향후 크레인 별 예약 작업 list 추가하는 코드 구현
    else:
        print('Sheet names do not match')

    # 검증용 print 문

    # for work_area in self.work_area_list:
    #     for id, unit in work_area.work_unit_dict.items():
    #         print(work_area.group_id, unit.unit_id, unit.x, unit.y, unit.dx, unit.dy)
    #     print(work_area.crane_operation_dict)
    #     print(work_area.surface_id_list)

    if 'BLK' in sheet_name_list:
        # 구현 예정
        pass
    else:
        print('Sheet names do not match')

    if 'UNAL_WORKAREA' in sheet_name_list:
        # 향후 추가해 더미블록으로 구현
        pass
    else:
        print('Sheet names do not match')
