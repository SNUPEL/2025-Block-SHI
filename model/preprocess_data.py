from class_definition import *
import pandas as pd
import numpy as np


def get_work_area_list(df_work_area_group, df_work_area):
    work_area_dict = dict()
    for _, row in df_work_area_group.iterrows():
        if row['사용여부'] == 'Y':
            filtered_df_work_area = df_work_area[
                (df_work_area['그룹ID'] == row['그룹ID']) & (df_work_area['정반사용여부'] == 'Y')].copy()

            filtered_df_work_area['그룹내정반위치Y'] = filtered_df_work_area['그룹내정반위치Y'] + filtered_df_work_area[
                '마진거리1'].fillna(0)
            filtered_df_work_area['그룹내정반위치X'] = filtered_df_work_area['그룹내정반위치X'] - filtered_df_work_area[
                '마진거리4'].fillna(0)

            min_x_of_work_area = min(filtered_df_work_area['그룹내정반위치X'])
            filtered_df_work_area['그룹내정반위치X'] = filtered_df_work_area['그룹내정반위치X'] - min_x_of_work_area

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
                                              indoor_outdoor_condition=row['옥내외'], lug_condition=row['러그고려'],
                                              L_limit_of_block=row['사이즈제한LTH'], B_limit_of_block=row['사이즈제한BTH'],
                                              H_limit_of_block=row['사이즈제한HGT'], W_limit_of_block=row['사이즈제한WGT'],
                                              TP_condition=row['TP운송여부'], TP_direction=direction, L=length, B=breadth,
                                              min_x_of_work_area=min_x_of_work_area)
                    temp_work_area.work_unit_dict[rect['정반ID']] = WorkUnit(unit_id=rect['정반ID'], x=rect['그룹내정반위치X'],
                                                                           y=rect['그룹내정반위치Y'], dx=length, dy=breadth)
                    work_area_dict[(row['그룹ID'], rect['정반ID'])] = temp_work_area
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
                    min_of_x_vals = min(x_vals)
                    min_of_y_vals = min(y_vals)
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
                    temp_work_area \
                        = WorkArea(group_id=row['그룹ID'], surface_id_list=list(group['정반ID']), priority=row['우선순위'],
                                   indoor_outdoor_condition=row['옥내외'], lug_condition=row['러그고려'],
                                   L_limit_of_block=row['사이즈제한LTH'], B_limit_of_block=row['사이즈제한BTH'],
                                   H_limit_of_block=row['사이즈제한HGT'], W_limit_of_block=row['사이즈제한WGT'],
                                   TP_condition=row['TP운송여부'], TP_direction=direction,
                                   L=combined_length, B=combined_breadth, min_x_of_work_area=min_x_of_work_area)

                    print(
                        f"work_area {temp_work_area.group_id}-{temp_work_area.surface_id_list}:"
                        f" L={temp_work_area.L}, B={temp_work_area.B}")

                    for _, rect in group.iterrows():
                        temp_work_area.work_unit_dict[rect['정반ID']] \
                            = WorkUnit(unit_id=rect['정반ID'],
                                       x_raw=rect['그룹내정반위치X'], y_raw=rect['그룹내정반위치Y'],
                                       x=rect['그룹내정반위치X'] - min_of_x_vals, y=rect['그룹내정반위치Y'] - min_of_y_vals,
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
                        temp_work_area.add_unavailable_area(missing_lower_left_x, missing_lower_left_y, missing_length,
                                                            missing_breadth)

                        print(
                            f"work_area {temp_work_area.group_id}-{temp_work_area.surface_id_list}"
                            f" has an empty area at ({temp_work_area.unavailable_area_x},"
                            f" {temp_work_area.unavailable_area_y})"
                            f" with L={temp_work_area.unavailable_area_L}, B={temp_work_area.unavailable_area_B}")

                    work_area_dict[(row['그룹ID'], tuple(group['정반ID']))] = temp_work_area
        else:
            continue
    return work_area_dict


def preprocess_data(self):
    sheet_name_list = list(self.df_raw_data_dict.keys())

    if 'UNAL_WORKDAY' in sheet_name_list:
        df_block = self.df_raw_result_data_dict['크레인 정보'] \
            if self.config['use_block_allocation_result'] else self.df_raw_data_dict['BLK']
        df_block[['착수일', '완료일', 'TO일정', 'PE일정']] \
            = df_block[['착수일', '완료일', 'TO일정', 'PE일정']].apply(pd.to_datetime, errors='coerce')
        allocated_blocks = df_block[(df_block['배치확정여부'] == 'Y') & (df_block['PE일정'] >= self.start_date)]
        if not allocated_blocks.empty:
            self.allocate_start_date = allocated_blocks['착수일'].min()

        # 향후 추가해 일정으로 활용
        df_calendar = self.df_raw_data_dict['UNAL_WORKDAY']
        while True:
            row = df_calendar[df_calendar['달력일자'] == self.start_date]
            if row.empty or row.iloc[0]['휴일여부'] == 0:
                break
            self.start_date += pd.Timedelta(days=1)
        df_after_start = df_calendar[df_calendar['달력일자'] >= self.start_date].copy()
        if self.config['only_workingday']:
            df_after_start = df_after_start[df_after_start['휴일여부'] == 0]
            # end_date 계산
            if len(df_after_start) < self.config['data_duration']:
                raise ValueError("달력 데이터가 부족합니다.")
            self.block_end_date = df_after_start.iloc[self.config['data_duration'] - 1]['달력일자']
        else:
            self.block_end_date = pd.to_datetime(self.config['data_end_date'])
        while True:
            row = df_calendar[df_calendar['달력일자'] == self.block_end_date]
            if row.empty or row.iloc[0]['휴일여부'] == 0:
                break
            self.block_end_date += pd.Timedelta(days=1)

        df_block_filtered = df_block[(df_block['착수일'] >= self.start_date) & (df_block['착수일'] <= self.block_end_date)]
        self.end_date = df_block_filtered['PE일정'].max() + pd.Timedelta(days=self.config['max_delay_day'] + 1)
        df_after_pe = df_calendar[df_calendar['달력일자'] >= self.end_date]
        df_after_pe = df_after_pe[df_after_pe['휴일여부'] == 0]
        if len(df_after_pe) < 4:
            raise ValueError("PE일정 이후 평일이 부족하여 end_date 계산 불가")
        self.end_date = df_after_pe.iloc[3]['달력일자']

        date = self.allocate_start_date if self.allocate_start_date else self.start_date
        idx = 0
        while True:
            # 평일이면 기록
            if df_calendar.loc[df_calendar['달력일자'] == date, '휴일여부'].iloc[0] == 0:
                self.calendar_dict[date] = idx
                self.postprocess_calendar_dict[idx] = date
                idx += 1
            # end_date면 기록 후 종료
            if date == self.end_date:
                break
            date += pd.Timedelta(days=1)
        self.model_start_index = self.calendar_dict[self.start_date]
        self.model_end_index = self.calendar_dict[self.end_date]

        # 대조를 위한 calendar date 저장
        # calendar_date_df = pd.DataFrame(self.calendar_dict, index=[0]).transpose()
        # start_date_str = str(self.start_date).split(' ')[0]
        # calendar_date_df.to_csv(f'calender_index_from_{start_date_str}.csv')

        print(self.start_date, self.end_date)
        print(self.model_start_index, self.model_end_index)
        print('Time index has been defined')
    else:
        print('Sheet names do not match')

    if 'WORKAREA_GROUP' in sheet_name_list and 'WORKAREA' in sheet_name_list:
        df_work_area_group = self.df_raw_data_dict['WORKAREA_GROUP']
        df_work_area = self.df_raw_data_dict['WORKAREA']
        self.work_area_dict = get_work_area_list(df_work_area_group, df_work_area)
        print('WorkArea class has been defined')
    else:
        print('Sheet names do not match')

    # if 'WORKAREA_CRANE_REL' in sheet_name_list and 'CRANE_WORK_TIME' in sheet_name_list:
    #     df_crane_time = pd.merge(self.df_raw_data_dict['WORKAREA_CRANE_REL'], self.df_raw_data_dict['CRANE_WORK_TIME'],
    #                              on=['작업종류', '크레인ID'], how='left')
    #     for _, work_area in self.work_area_dict.items():
    #         for key, group in df_crane_time.groupby('그룹ID').get_group(work_area.group_id).groupby('작업종류'):
    #             work_area.crane_operation_dict[key] = (int(sum(group['작업시간'] * 2)), list(group['크레인ID']))
    #     print('Crane operation dictionary has been defined')
    # else:
    #     print('Sheet names do not match')
    # TO와 OUT을 합치기 위해 수정
    if 'WORKAREA_CRANE_REL' in sheet_name_list and 'CRANE_WORK_TIME' in sheet_name_list:
        df_crane_time = pd.merge(self.df_raw_data_dict['WORKAREA_CRANE_REL'], self.df_raw_data_dict['CRANE_WORK_TIME'],
                                 on=['작업종류', '크레인ID'], how='left')

        out_to_types = ['OUT', 'TO']

        for _, work_area in self.work_area_dict.items():
            # 그룹ID로 먼저 필터링
            group_df = df_crane_time[df_crane_time['그룹ID'] == work_area.group_id]

            # 일반 작업종류 처리
            for key, group in group_df[~group_df['작업종류'].isin(out_to_types)].groupby('작업종류'):
                work_area.crane_operation_dict[key] = (int(sum(group['작업시간'] * 2)), list(group['크레인ID']))

            # PE와 TO 작업을 합쳐서 처리
            pe_to_df = group_df[group_df['작업종류'].isin(out_to_types)]
            if not pe_to_df.empty:
                # 합쳐진 작업시간 계산
                combined_time = int(sum(pe_to_df['작업시간'] * 2))
                # 두 작업에 사용된 크레인ID 리스트 (중복 제거)
                combined_cranes = list(pe_to_df['크레인ID'].unique())
                # TO 키 값으로 저장
                work_area.crane_operation_dict['TO'] = (combined_time, combined_cranes)

        print('Crane operation dictionary has been defined with PE and TO combined')
    else:
        print('Sheet names do not match')

    if 'CRANE' in sheet_name_list and 'CRANE_RESV_SCH' in sheet_name_list:
        df_crane = self.df_raw_data_dict['CRANE']
        df_unavailable_crane = self.df_raw_data_dict['CRANE_RESV_SCH']
        for _, row in df_crane.iterrows():
            self.crane_dict[row['크레인ID']] = Crane(Crane_id=row['크레인ID'], condition=row['사용여부'])
        for _, row in df_unavailable_crane.iterrows():
            if pd.to_datetime(row['예약작업날짜']) not in self.calendar_dict:
                continue
            self.crane_dict[row['크레인ID']].unavailable_time_dict[row['예약작업이름']] = \
                (self.calendar_dict[pd.to_datetime(row['예약작업날짜'])], float(row['예약작업시간']))
        # 향후 크레인 별 예약 작업 list 추가하는 코드 구현
        # 더미 변수 생성해 step function에 pulse 추가
        print('Crane class has been defined')
    else:
        print('Sheet names do not match')

    if 'BLK' in sheet_name_list:
        df_block = self.df_raw_result_data_dict['크레인 정보'] \
            if self.config['use_block_allocation_result'] else self.df_raw_data_dict['BLK']
        df_block[['착수일', '완료일', 'TO일정', 'PE일정']] \
            = df_block[['착수일', '완료일', 'TO일정', 'PE일정']].apply(pd.to_datetime, errors='coerce')
        for _, row in df_block.iterrows():
            if row['블록길이'] == 'LTH':
                continue
            temp_block = Block(ship_type=row['선종'], project_number=row['호선'], block_number=row['블록'],
                               allocation_start_date=row['착수일'], allocation_end_date=row['완료일'],
                               processing_time=row['공기'], TO_date=row['TO일정'], PE_date=row['PE일정'],
                               length=row['블록길이'], spacing_x=self.config['block_spacing_x'], breadth=row['블록폭'],
                               spacing_y=self.config['block_spacing_y'], height=row['블록높이'], weight=row['블록중량'],
                               indoor_outdoor_condition=row['옥내외'], lug_direction=row['러그방향'],
                               allocate_condtion=row['배치확정여부'])
            self.all_block_dict[(row['선종'], row['호선'], row['블록'])] = temp_block

        df_block_filtered \
            = df_block[((df_block['배치확정여부'] == 'Y') & (df_block['PE일정'] >= self.start_date)) |
                       ((df_block['착수일'] >= self.start_date) & (df_block['착수일'] <= self.block_end_date))]
        for _, row in df_block_filtered.iterrows():
            temp_block = Block(ship_type=row['선종'], project_number=row['호선'], block_number=row['블록'],
                               allocation_start_date=row['착수일'], allocation_end_date=row['완료일'],
                               processing_time=row['공기'], TO_date=row['TO일정'], PE_date=row['PE일정'],
                               length=row['블록길이'], spacing_x=self.config['block_spacing_x'], breadth=row['블록폭'],
                               spacing_y=self.config['block_spacing_y'], height=row['블록높이'], weight=row['블록중량'],
                               indoor_outdoor_condition=row['옥내외'], lug_direction=row['러그방향'],
                               allocate_condtion=row['배치확정여부'])
            if temp_block.allocate_condtion == 'Y':
                temp_block.update_allocate_condition(row['변환 블록길이'], row['변환 블록폭'], row['그룹ID'],
                                                     row['회전'], row['블록위치X'], row['블록위치Y'])

            temp_block.datetime_to_idx(self.calendar_dict)

            for key, value in self.block_dict.items():
                if row['선종'] == key[0] and row['호선'] == key[1] and row['블록'][:-1] == key[2][:-1]:
                    if abs(value.allocation_index - temp_block.allocation_index) < 3:
                        value.allocation_index = max(value.allocation_index, temp_block.allocation_index)
                        temp_block.allocation_index = max(value.allocation_index, temp_block.allocation_index)
                    value.TO_index = max(value.TO_index, temp_block.TO_index)
                    temp_block.TO_index = max(value.TO_index, temp_block.TO_index)
                    value.PE_index = max(value.PE_index, temp_block.PE_index)
                    temp_block.PE_index = max(value.PE_index, temp_block.PE_index)
                    break

            self.block_dict[(row['선종'], row['호선'], row['블록'])] = temp_block
        print('Block class has been defined')
    else:
        print('Sheet names do not match')

    if 'UNAL_WORKAREA' in sheet_name_list:
        df_unavailable_workarea = self.df_raw_data_dict['UNAL_WORKAREA']
        for _, row in df_unavailable_workarea.iterrows():
            for key, value in self.work_area_dict.items():
                if row['그룹ID'] == key[0] and row['정반ID'] in list(key[1]):
                    day1 = pd.to_datetime(row['정반불가시작일'])
                    day2 = pd.to_datetime(row['정반불가종료일'])
                    if day2 <= self.start_date or self.day1 >= self.end_date:
                        continue
                    if day1 <= self.start_date:
                        day1 = self.start_date
                    if day2 >= self.end_date:
                        day2 = self.end_date

                    while day1 not in self.calendar_dict:
                        day1 += pd.Timedelta(days=1)
                    while day2 not in self.calendar_dict:
                        day2 += pd.Timedelta(days=1)
                    value.work_unit_dict[row['정반ID']].unavailable_duration_list.append(
                        [self.calendar_dict[day1], self.calendar_dict[day2]])

    else:
        print('Sheet names do not match')
