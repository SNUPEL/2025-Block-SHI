from class_definition import *
import matplotlib.pyplot as plt
import time

def save_result(self, sol, solution_index):
    results = []
    crane_results = []
    raw_results = []
    results.append({
        '선종': 'NEW_SKND',
        '호선': 'PROJ_NO',
        '블록': 'BLK_NO',
        '착수일': 'STDT',
        '완료일': 'FNDT',
        '공기': 'DUR',
        'OUT일정': 'OUT_DATE',
        'TO일정': 'TO_DATE',
        'PE일정': 'PE_DATE',
        '블록길이': 'LTH',
        '블록폭': 'BTH',
        '블록높이': 'HGT',
        '블록중량': 'WGT',
        '옥내외': 'BLK_IODR',
        '러그방향': 'LUG_DRCT',
        '배치확정여부': 'ARNG_CNFM_YN',
        '그룹ID': 'GRP_ID',
        '블록위치X': 'BLK_LOC_X',
        '블록위치Y': 'BLK_LOC_Y'
    })
    crane_results.append({
        '선종': 'NEW_SKND',
        '호선': 'PROJ_NO',
        '블록': 'BLK_NO',
        '착수일': 'STDT',
        '완료일': 'FNDT',
        '공기': 'DUR',
        'OUT일정': 'OUT_DATE',
        'TO일정': 'TO_DATE',
        'PE일정': 'PE_DATE',
        '블록길이': 'LTH',
        '블록폭': 'BTH',
        '블록높이': 'HGT',
        '블록중량': 'WGT',
        '옥내외': 'BLK_IODR',
        '러그방향': 'LUG_DRCT',
        '배치확정여부': 'ARNG_CNFM_YN',
        '그룹ID': 'GRP_ID',
        '블록위치X': 'BLK_LOC_X',
        '블록위치Y': 'BLK_LOC_Y',
        '회전': 'ROT',
        '변환 블록길이': 'ADJ_LTH',
        '변환 블록폭': 'ADJ_BTH',
        'IN_크레인_소요시간': 'IN_CRANE_TIME',
        'TO_크레인_소요시간': 'TO_CRANE_TIME',
        'PE_크레인_소요시간': 'PE_CRANE_TIME',
        'IN_크레인ID': 'IN_CRANE_ID',
        'TO_크레인ID': 'TO_CRANE_ID',
        'PE_크레인ID': 'PE_ID',
    })
    raw_results.append({
        '선종': 'NEW_SKND',
        '호선': 'PROJ_NO',
        '블록': 'BLK_NO',
        '착수일': 'STDT',
        '완료일': 'FNDT',
        '공기': 'DUR',
        'OUT일정': 'OUT_DATE',
        'TO일정': 'TO_DATE',
        'PE일정': 'PE_DATE',
        '블록길이': 'LTH',
        '블록폭': 'BTH',
        '블록높이': 'HGT',
        '블록중량': 'WGT',
        '옥내외': 'BLK_IODR',
        '러그방향': 'LUG_DRCT',
        '배치확정여부': 'ARNG_CNFM_YN',
        '그룹ID': 'GRP_ID',
        '블록위치X': 'BLK_LOC_X',
        '블록위치Y': 'BLK_LOC_Y',
        '회전': 'ROT',
        '변환 블록길이': 'ADJ_LTH',
        '변환 블록폭': 'ADJ_BTH',
        'IN_크레인_소요시간': 'IN_CRANE_TIME',
        'TO_크레인_소요시간': 'TO_CRANE_TIME',
        'PE_크레인_소요시간': 'PE_CRANE_TIME',
        'IN_크레인ID': 'IN_CRANE_ID',
        'TO_크레인ID': 'TO_CRANE_ID',
        'PE_크레인ID': 'PE_ID',
    })

    # 각 블록에 대한 결과 수집
    for block_key, block in self.all_block_dict.items():
        block_id = f"{block.ship_type}_{block.project_number}_{block.block_number}"

        if block_key in self.block_dict.keys():

            # 각 블록에 대한 결과 수집
            # for block_key in self.block_keys:
            #    block = self.block_dict[block_key]
            #    block_id = f"{block.ship_type}_{block.project_number}_{block.block_number}"

            # 선택된 정반과 회전 찾기
            selected_group = None
            selected_surface = None
            selected_rotation = None

            # STORE 작업 변수로 선택된 정반과 회전 확인
            for var_key, var in self.block_schedule_var_by_id_group_surf_work_rotate_dict.items():
                if block_id in var_key and 'STORE' in var_key:
                    if sol.get_var_solution(var).is_present():
                        _, selected_group, selected_surface, _, selected_rotation = var_key
                        break

            if selected_group is not None:
                # 날짜 변환
                in_var_key = (block_id, selected_group, selected_surface, 'IN', selected_rotation)
                store_var_key = (block_id, selected_group, selected_surface, 'STORE', selected_rotation)
                to_var_key = (block_id, selected_group, selected_surface, 'TO', selected_rotation)
                pe_var_key = (block_id, selected_group, selected_surface, 'PE', selected_rotation)

                # 변수 솔루션 추출
                in_sol = sol.get_var_solution(
                    self.block_schedule_var_by_id_group_surf_work_rotate_dict[in_var_key]
                )
                store_sol = sol.get_var_solution(
                    self.block_schedule_var_by_id_group_surf_work_rotate_dict[store_var_key]
                )
                to_sol = sol.get_var_solution(
                    self.block_schedule_var_by_id_group_surf_work_rotate_dict[to_var_key]
                )
                pe_sol = sol.get_var_solution(
                    self.block_schedule_var_by_id_group_surf_work_rotate_dict[pe_var_key]
                )

                # 위치 변수
                pos_var_key = (block_id, selected_group, selected_surface, selected_rotation)
                x_sol = sol.get_var_solution(
                    self.block_x_var_by_id_group_surf_rotate_dict[pos_var_key]
                )
                y_sol = sol.get_var_solution(
                    self.block_y_var_by_id_group_surf_rotate_dict[pos_var_key]
                )
                time_sol = sol.get_var_solution(
                    self.block_time_var_by_id_group_surf_rotate_dict[pos_var_key]
                )

                # 인덱스를 날짜로 변환 (범위 체크 추가)
                # def get_date_from_index(index):
                #     if index in self.postprocess_calendar_dict:
                #         return self.postprocess_calendar_dict[index]
                #     else:
                #         # 범위를 벗어난 경우, 가장 가까운 유효한 날짜 반환
                #         valid_indices = sorted(self.postprocess_calendar_dict.keys())
                #         if index < valid_indices[0]:
                #             return self.postprocess_calendar_dict[valid_indices[0]]
                #         else:
                #             return self.postprocess_calendar_dict[valid_indices[-1]]

                IN_date = self.postprocess_calendar_dict[in_sol.get_start()]
                OUT_date = self.postprocess_calendar_dict[to_sol.get_start()]
                TO_date = self.postprocess_calendar_dict[to_sol.get_start()]
                PE_date = self.postprocess_calendar_dict[pe_sol.get_start()]
                # IN_date = in_sol.get_start()
                # OUT_date = time_sol.get_end()
                # TO_date = to_sol.get_end()
                # PE_date = pe_sol.get_end()

                IN_crane_time = None
                TO_crane_time = None
                PE_crane_time = None
                IN_crane_id = None
                TO_crane_id = None
                PE_crane_id = None

                crane_operation_dict = self.work_area_dict[selected_group].crane_operation_dict
                for key, value in crane_operation_dict.items():
                    total_key = (block_id, selected_group, selected_surface, key, selected_rotation)

                    if key == 'IN':
                        IN_crane_time = value[0] / 2
                        IN_crane_id = value[1]

                    elif key == 'TO':
                        TO_crane_time = value[0] / 2
                        TO_crane_id = value[1]

                    elif key == 'PE':
                        PE_crane_time = value[0] / 2
                        PE_crane_id = value[1]

                # if selected_rotation == 90:
                #     breadth = block.adjusted_length
                #     length = block.adjusted_breadth
                # else:
                #     length = block.adjusted_length
                #     breadth = block.adjusted_breadth
                breadth = int(x_sol.get_end() - x_sol.get_start())
                length = int(y_sol.get_end() - y_sol.get_start())

                # if selected_group[0] == 4:
                #     if length <= breadth and length <= 55:
                #         length = 55
                #     else:
                #         pass

                # 결과 행 추가
                results.append({
                    '선종': block.ship_type,
                    '호선': block.project_number,
                    '블록': block.block_number,
                    '착수일': IN_date,
                    '완료일': OUT_date,
                    '공기': block.processing_time,
                    'OUT일정': OUT_date,
                    'TO일정': TO_date,
                    'PE일정': PE_date,
                    '블록길이': length / 10,
                    '블록폭': breadth / 10,
                    '블록높이': block.adjusted_height / 10,
                    '블록중량': block.weight,
                    '옥내외': block.indoor_outdoor_condition,
                    '러그방향': block.lug_direction,
                    '배치확정여부': 'Y',
                    '그룹ID': selected_group,
                    '블록위치X': x_sol.get_start() / 10,
                    '블록위치Y': y_sol.get_start() / 10
                })

                crane_results.append({
                    '선종': block.ship_type,
                    '호선': block.project_number,
                    '블록': block.block_number,
                    '착수일': IN_date,
                    '완료일': OUT_date,
                    '공기': block.processing_time,
                    'OUT일정': OUT_date,
                    'TO일정': TO_date,
                    'PE일정': PE_date,
                    '블록길이': block.length,
                    '블록폭': block.breadth,
                    '블록높이': block.height,
                    '블록중량': block.weight,
                    '옥내외': block.indoor_outdoor_condition,
                    '러그방향': block.lug_direction,
                    '배치확정여부': 'Y',
                    '그룹ID': selected_group,
                    '블록위치X': x_sol.get_start() / 10,
                    '블록위치Y': y_sol.get_start() / 10,
                    '회전': selected_rotation,
                    '변환 블록길이': length / 10,
                    '변환 블록폭': breadth / 10,
                    'IN_크레인_소요시간': IN_crane_time,
                    'TO_크레인_소요시간': TO_crane_time,
                    'PE_크레인_소요시간': PE_crane_time,
                    'IN_크레인ID': IN_crane_id,
                    'TO_크레인ID': TO_crane_id,
                    'PE_크레인ID': PE_crane_id
                })
                raw_results.append({
                    '선종': block.ship_type,
                    '호선': block.project_number,
                    '블록': block.block_number,
                    '착수일': IN_date,
                    '완료일': OUT_date,
                    '공기': block.processing_time,
                    'OUT일정': OUT_date,
                    'TO일정': TO_date,
                    'PE일정': PE_date,
                    '블록길이': block.length,
                    '블록폭': block.breadth,
                    '블록높이': block.height,
                    '블록중량': block.weight,
                    '옥내외': block.indoor_outdoor_condition,
                    '러그방향': block.lug_direction,
                    '배치확정여부': 'Y',
                    '그룹ID': selected_group,
                    '블록위치X': x_sol.get_start() / 10 + self.work_area_dict[selected_group].min_x_of_workgroup + self.work_area_dict[selected_group].min_x_of_work_area,
                    '블록위치Y': (y_sol.get_start() / 10 + self.work_area_dict[selected_group].min_y_of_workgroup) * -1
                    if self.config['workarea_y_symmetric'] else y_sol.get_start() / 10 + self.work_area_dict[selected_group].min_y_of_workgroup + self.work_area_dict[selected_group].min_y_of_work_area,
                    '회전': selected_rotation,
                    '변환 블록길이': length / 10,
                    '변환 블록폭': breadth / 10,
                    'IN_크레인_소요시간': IN_crane_time,
                    'TO_크레인_소요시간': TO_crane_time,
                    'PE_크레인_소요시간': PE_crane_time,
                    'IN_크레인ID': IN_crane_id,
                    'TO_크레인ID': TO_crane_id,
                    'PE_크레인ID': PE_crane_id
                })

            else:
                # 미배치 블록
                results.append({
                    '선종': block.ship_type,
                    '호선': block.project_number,
                    '블록': block.block_number,
                    '착수일': None,
                    '완료일': None,
                    '공기': block.processing_time,
                    'OUT일정': None,
                    'TO일정': None,
                    'PE일정': None,
                    '블록길이': block.length,
                    '블록폭': block.breadth,
                    '블록높이': block.height,
                    '블록중량': block.weight,
                    '옥내외': block.indoor_outdoor_condition,
                    '러그방향': block.lug_direction,
                    '배치확정여부': 'N',
                    '그룹ID': None,
                    '블록위치X': None,
                    '블록위치Y': None
                })

                crane_results.append({
                    '선종': block.ship_type,
                    '호선': block.project_number,
                    '블록': block.block_number,
                    '착수일': None,
                    '완료일': None,
                    '공기': block.processing_time,
                    'OUT일정': None,
                    'TO일정': None,
                    'PE일정': None,
                    '그룹ID': None,
                    '블록길이': block.length,
                    '블록폭': block.breadth,
                    '블록높이': block.height,
                    '블록중량': block.weight,
                    '옥내외': block.indoor_outdoor_condition,
                    '러그방향': block.lug_direction,
                    '배치확정여부': 'N',
                    '블록위치X': None,
                    '블록위치Y': None,
                    '회전': None,
                    '변환 블록길이': block.adjusted_length / 10,
                    '변환 블록폭': block.adjusted_breadth / 10,
                    'IN_크레인_소요시간': None,
                    'TO_크레인_소요시간': None,
                    'PE_크레인_소요시간': None,
                    'IN_크레인ID': None,
                    'TO_크레인ID': None,
                    'PE_크레인ID': None
                })

                raw_results.append({
                    '선종': block.ship_type,
                    '호선': block.project_number,
                    '블록': block.block_number,
                    '착수일': None,
                    '완료일': None,
                    '공기': block.processing_time,
                    'OUT일정': None,
                    'TO일정': None,
                    'PE일정': None,
                    '그룹ID': None,
                    '블록길이': block.length,
                    '블록폭': block.breadth,
                    '블록높이': block.height,
                    '블록중량': block.weight,
                    '옥내외': block.indoor_outdoor_condition,
                    '러그방향': block.lug_direction,
                    '배치확정여부': 'N',
                    '블록위치X': None,
                    '블록위치Y': None,
                    '회전': None,
                    '변환 블록길이': block.adjusted_length / 10,
                    '변환 블록폭': block.adjusted_breadth / 10,
                    'IN_크레인_소요시간': None,
                    'TO_크레인_소요시간': None,
                    'PE_크레인_소요시간': None,
                    'IN_크레인ID': None,
                    'TO_크레인ID': None,
                    'PE_크레인ID': None
                })

                # DataFrame 생성 및 엑셀 저장
                # self.df_result = pd.DataFrame(results)
                # self.df_crane_result = pd.DataFrame(crane_results)
                # output_path = f"{self.config['folderpath']}/block_allocation_result.xlsx"
                # with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                #    self.df_result.to_excel(writer, index=False, sheet_name='배치결과')
                #    self.df_crane_result.to_excel(writer, index=False, sheet_name='크레인 정보')
                # self.df_result.to_excel(output_path, index=False)
        else:
            results.append({
                '선종': block.ship_type,
                '호선': block.project_number,
                '블록': block.block_number,
                '착수일': block.allocation_start_date,
                '완료일': block.allocation_end_date,
                '공기': block.processing_time,
                'OUT일정': block.allocation_end_date,
                'TO일정': block.TO_date,
                'PE일정': block.PE_date,
                '블록길이': block.length,
                '블록폭': block.breadth,
                '블록높이': block.height,
                '블록중량': block.weight,
                '옥내외': block.indoor_outdoor_condition,
                '러그방향': block.lug_direction,
                '배치확정여부': None,
                '그룹ID': None,
                '블록위치X': None,
                '블록위치Y': None
            })

            crane_results.append({
                '선종': block.ship_type,
                '호선': block.project_number,
                '블록': block.block_number,
                '착수일': block.allocation_start_date,
                '완료일': block.allocation_end_date,
                '공기': block.processing_time,
                'OUT일정': block.allocation_end_date,
                'TO일정': block.TO_date,
                'PE일정': block.PE_date,
                '블록길이': block.length,
                '블록폭': block.breadth,
                '블록높이': block.height,
                '블록중량': block.weight,
                '옥내외': block.indoor_outdoor_condition,
                '러그방향': block.lug_direction,
                '배치확정여부': None,
                '그룹ID': None,
                '블록위치X': None,
                '블록위치Y': None,
                '회전': None,
                '변환 블록길이': None,
                '변환 블록폭': None,
                'IN_크레인_소요시간': None,
                'TO_크레인_소요시간': None,
                'PE_크레인_소요시간': None,
                'IN_크레인ID': None,
                'TO_크레인ID': None,
                'PE_크레인ID': None
            })
            raw_results.append({
                '선종': block.ship_type,
                '호선': block.project_number,
                '블록': block.block_number,
                '착수일': block.allocation_start_date,
                '완료일': block.allocation_end_date,
                '공기': block.processing_time,
                'OUT일정': block.allocation_end_date,
                'TO일정': block.TO_date,
                'PE일정': block.PE_date,
                '블록길이': block.length,
                '블록폭': block.breadth,
                '블록높이': block.height,
                '블록중량': block.weight,
                '옥내외': block.indoor_outdoor_condition,
                '러그방향': block.lug_direction,
                '배치확정여부': None,
                '그룹ID': None,
                '블록위치X': None,
                '블록위치Y': None,
                '회전': None,
                '변환 블록길이': None,
                '변환 블록폭': None,
                'IN_크레인_소요시간': None,
                'TO_크레인_소요시간': None,
                'PE_크레인_소요시간': None,
                'IN_크레인ID': None,
                'TO_크레인ID': None,
                'PE_크레인ID': None
            })

    # DataFrame 생성 및 엑셀 저장
    self.df_result = pd.DataFrame(results)
    self.df_crane_result = pd.DataFrame(crane_results)
    self.df_raw_result = pd.DataFrame(raw_results)
    output_path = f"{self.config['folderpath']}/block_allocation_result.xlsx"
    output_path2 = f"{self.config['folderpath']}/block_allocation_result_sol_{str(solution_index)}.xlsx"
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        self.df_result.to_excel(writer, index=False, sheet_name='배치결과')
        self.df_crane_result.to_excel(writer, index=False, sheet_name='크레인 정보')
        self.df_raw_result.to_excel(writer, index=False, sheet_name='기존 좌표 변환')
    with pd.ExcelWriter(output_path2, engine='openpyxl') as writer:
        self.df_result.to_excel(writer, index=False, sheet_name='배치결과')
        self.df_crane_result.to_excel(writer, index=False, sheet_name='크레인 정보')
        self.df_raw_result.to_excel(writer, index=False, sheet_name='기존 좌표 변환')
        # self.df_result.to_excel(output_path, index=False)

        # postprocess_solution_crane

    results_crane = []
    results_crane_worktime = []

    day_time_tracker = {}

    for index, day in self.postprocess_calendar_dict.items():
        crane_worktime = 0
        if day not in day_time_tracker:
            day_time_tracker[day] = {'hour': 9, 'minute': 0}

        # 하루치 작업 중 해당하는 작업들만 선별
        day_results = [r for r in crane_results if
                       r.get('TO일정') == day or r.get('PE일정') == day or r.get('착수일') == day]

        # TO → PE → IN 순서대로 작업 정렬
        for work_type in ['TO', 'PE', 'IN']:
            for result in day_results:
                # 각 작업에 해당하는 날짜 및 시간 소요 정보 설정
                if work_type == 'TO' and result.get('TO일정') == day:
                    work_time = result.get('TO_크레인_소요시간') or 0
                    crane_id = result.get('TO_크레인ID')
                elif work_type == 'PE' and result.get('PE일정') == day:
                    work_time = result.get('PE_크레인_소요시간') or 0
                    crane_id = result.get('PE_크레인ID')
                elif work_type == 'IN' and result.get('착수일') == day:
                    work_time = result.get('IN_크레인_소요시간') or 0
                    crane_id = result.get('IN_크레인ID')
                else:
                    continue

                if result['블록중량'] > 45 and work_type in ['TO', 'PE']:
                    continue

                current_hour = day_time_tracker[day]['hour']
                current_minute = day_time_tracker[day]['minute']
                work_time_minutes = int(work_time * 60)

                end_minute = current_minute + work_time_minutes
                end_hour = current_hour + end_minute // 60
                end_minute = end_minute % 60

                datetime_str = f"{str(day).split(' ')[0]} {current_hour:02d}:{current_minute:02d}:00"

                operated_block_dict = {
                    'date': datetime_str,
                    '선종': result['선종'],
                    '호선': result['호선'],
                    '블록': result['블록'],
                    '그룹ID': result['그룹ID'],
                    'work': work_type,
                    '크레인ID': crane_id,
                    '크레인_소요시간': work_time,
                }
                results_crane.append(operated_block_dict)

                crane_worktime += work_time
                day_time_tracker[day] = {'hour': end_hour, 'minute': end_minute}

        crane_worktime_dict = {
            'date': day,
            '일별_크레인_소요시간': crane_worktime,
        }

        results_crane_worktime.append(crane_worktime_dict)

        # for index, day in self.postprocess_calendar_dict.items():
        #     crane_worktime = 0
        #     # 날짜별 시작 시간 초기화 (8시 시작 가정)
        #     if day not in day_time_tracker:
        #         day_time_tracker[day] = {'hour': 9, 'minute': 0}
        #
        #     for result in crane_results:
        #         if result['착수일'] == day:
        #             # 현재 시간 가져오기
        #             current_hour = day_time_tracker[day]['hour']
        #             current_minute = day_time_tracker[day]['minute']
        #
        #             # 작업 시간 (분 단위로 변환)
        #             work_time_minutes = int((result['IN_크레인_소요시간'] or 0) * 60)
        #
        #             # 작업 종료 시간 계산
        #             end_minute = current_minute + work_time_minutes
        #             end_hour = current_hour + end_minute // 60
        #             end_minute = end_minute % 60
        #
        #             datetime_str = f"{str(day).split(' ')[0]} {current_hour:02d}:{current_minute:02d}:00"
        #
        #             operated_block_dict = {
        #                 'date': datetime_str,
        #                 '선종': result['선종'],
        #                 '호선': result['호선'],
        #                 '블록': result['블록'],
        #                 '그룹ID': result['그룹ID'],
        #                 'work': 'IN',
        #                 '크레인ID': result['IN_크레인ID'],
        #                 '크레인_소요시간': result['IN_크레인_소요시간']
        #             }
        #             results_crane.append(operated_block_dict)
        #
        #             crane_worktime += int(result['IN_크레인_소요시간'] or 0)
        #
        #             day_time_tracker[day] = {'hour': end_hour, 'minute': end_minute}
        #
        #         elif result['TO일정'] == day:
        #             current_hour = day_time_tracker[day]['hour']
        #             current_minute = day_time_tracker[day]['minute']
        #
        #             work_time_minutes = int((result['TO_크레인_소요시간'] or 0) * 60)
        #
        #             end_minute = current_minute + work_time_minutes
        #             end_hour = current_hour + end_minute // 60
        #             end_minute = end_minute % 60
        #
        #             datetime_str = f"{str(day).split(' ')[0]} {current_hour:02d}:{current_minute:02d}:00"
        #
        #             operated_block_dict = {
        #                 'date': datetime_str,
        #                 '선종': result['선종'],
        #                 '호선': result['호선'],
        #                 '블록': result['블록'],
        #                 '그룹ID': result['그룹ID'],
        #                 'work': 'TO',
        #                 '크레인ID': result['TO_크레인ID'],
        #                 '크레인_소요시간': result['TO_크레인_소요시간']
        #             }
        #             results_crane.append(operated_block_dict)
        #
        #             crane_worktime += int(result['TO_크레인_소요시간'] or 0)
        #
        #             day_time_tracker[day] = {'hour': end_hour, 'minute': end_minute}
        #
        #         elif result['PE일정'] == day:
        #             current_hour = day_time_tracker[day]['hour']
        #             current_minute = day_time_tracker[day]['minute']
        #
        #             work_time_minutes = int((result['PE_크레인_소요시간'] or 0) * 60)
        #
        #             end_minute = current_minute + work_time_minutes
        #             end_hour = current_hour + end_minute // 60
        #             end_minute = end_minute % 60
        #
        #             datetime_str = f"{str(day).split(' ')[0]} {current_hour:02d}:{current_minute:02d}:00"
        #
        #             operated_block_dict = {
        #                 'date': datetime_str,
        #                 '선종': result['선종'],
        #                 '호선': result['호선'],
        #                 '블록': result['블록'],
        #                 '그룹ID': result['그룹ID'],
        #                 'work': 'PE',
        #                 '크레인ID': result['PE_크레인ID'],
        #                 '크레인_소요시간': result['PE_크레인_소요시간']
        #             }
        #             results_crane.append(operated_block_dict)
        #
        #             crane_worktime += int(result['PE_크레인_소요시간'] or 0)
        #
        #             day_time_tracker[day] = {'hour': end_hour, 'minute': end_minute}


    # self.df_result = pd.DataFrame(results_crane)
    # self.df_result.dropna(subset=['크레인ID'], inplace=True)  # 그룹 4에서 in은 크레인 없어서 출력 제외
    # self.df_result_2 = pd.DataFrame(results_crane_worktime)
    #
    # # 크레인별로 작업 시간순 정렬
    # _24_hour_mask = self.df_result['date'].astype(str).str.contains(r' 24:00:00', na=False, regex=True)
    # if _24_hour_mask.any():
    #     self.df_result.loc[_24_hour_mask, 'date'] = \
    #         self.df_result.loc[_24_hour_mask, 'date'].astype(str).str.replace(' 24:00:00', ' 00:00:00')
    #
    # expected_format = '%Y-%m-%d %H:%M:%S'
    # self.df_result['date'] = pd.to_datetime(self.df_result['date'], format=expected_format, errors='coerce')
    # if _24_hour_mask.any():
    #     self.df_result.loc[_24_hour_mask, 'date'] = \
    #         self.df_result.loc[_24_hour_mask, 'date'] + pd.Timedelta(days=1)
    #
    # self.df_result = self.df_result.sort_values(['date', 'work'])
    #
    # output_path = f"{self.config['folderpath']}/crane_result.xlsx"
    # output_path2 = f"{self.config['folderpath']}/crane_result_sol_{str(solution_index)}.xlsx"
    #
    # with pd.ExcelWriter(output_path, engine='openpyxl', mode='w') as writer:
    #     self.df_result.to_excel(writer, sheet_name='crane_result_main', index=False)
    #     self.df_result_2.to_excel(writer, sheet_name='result_crane_worktime', index=False)
    #
    # with pd.ExcelWriter(output_path2, engine='openpyxl', mode='w') as writer:
    #     self.df_result.to_excel(writer, sheet_name='crane_result_main', index=False)
    #     self.df_result_2.to_excel(writer, sheet_name='result_crane_worktime', index=False)
    #
    # if len(self.df_result) == 0:
    #     return True
    #
    # df = self.df_result.copy()
    # df['weekday'] = df['date'].dt.day_name()
    # df['week'] = df['date'].dt.isocalendar().week
    #
    # weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    # df = df[df['weekday'].isin(weekday_order)]
    # df['weekday'] = pd.Categorical(df['weekday'], categories=weekday_order, ordered=True)
    #
    # df['크레인_소요시간'] = df['크레인_소요시간'].fillna(0).astype(int)
    # df['time_info'] = df['date'].dt.strftime('%H:%M')
    # df['summary'] = df['work'] + ' (' + df['time_info'] + '): ' + df['크레인_소요시간'].astype(str) + 'h'
    #
    # summary_total_df = df.groupby(['week', 'weekday'], observed=False).agg(
    #     {'summary': lambda x: '\n'.join(x), '크레인_소요시간': 'sum'}).reset_index()
    #
    # summary_total_df['cell_text'] = summary_total_df['summary'] + '\nTotal: ' + summary_total_df[
    #     '크레인_소요시간'].astype(
    #     str) + 'h'
    #
    # calendar_df = summary_total_df.pivot(index='week', columns='weekday', values='cell_text').fillna('')
    #
    # calendar_df.columns.name = None
    #
    # fig, ax = plt.subplots(figsize=(16, len(calendar_df) * 1.2))
    # ax.axis('off')
    #
    # table = ax.table(
    #     cellText=calendar_df.values,
    #     rowLabels=[f"Week {w}" for w in calendar_df.index],
    #     colLabels=calendar_df.columns.tolist(),
    #     colWidths=[0.2] * len(calendar_df.columns),
    #     loc='center',
    #     cellLoc='center'
    # )
    #
    # table.auto_set_font_size(False)
    # table.set_fontsize(10)
    # table.scale(1.5, 3.0)
    #
    # plt.title('Crane Operation Calendar', fontsize=14, pad=20)
    # plt.tight_layout()
    # plt.savefig(f"{self.config['folderpath']}/crane_result.png")
    # plt.close()


def postprocess_solution(self):
    if self.config['search_method'] == 'single_solution':
        if self.solution_cpmodel:
            save_result(self, self.solution_cpmodel, solution_index=0)
    else:
        all_result_list = []
        solution_index = 0
        for sol in self.solution_cpmodel:
            solution_index += 1
            result_list = []
            result_col_name = []
            result_list.append('sol_' + str(solution_index))
            result_col_name.append('solution_index')

            result_list.append(time.time() - self.search_start_time)
            result_col_name.append('search_time')

            result_list.append(sol.get_var_solution(self.total_obj_var).get_value())
            result_col_name.append('total_obj_value')

            if self.config['obj_preference']:
                result_list.append(sol.get_var_solution(self.obj_sum_preference_var).get_value())
                result_col_name.append('obj_preference_value')

            if self.config['obj_delay']:
                result_list.append(sol.get_var_solution(self.obj_sum_delay_var).get_value())
                result_col_name.append('obj_delay')

            if self.config['obj_unassigned_block']:
                result_list.append(sol.get_var_solution(self.obj_sum_unassigned_block_var).get_value())
                result_col_name.append('obj_unassigned_block')

            if self.config['obj_allocation']:
                result_list.append(sol.get_var_solution(self.obj_sum_allocation_var).get_value())
                result_col_name.append('obj_sum_allocation')
                result_list.append(sol.get_var_solution(self.obj_sum_allocation_var1).get_value())
                result_col_name.append('obj_sum_allocation1')
                result_list.append(sol.get_var_solution(self.obj_sum_allocation_var2).get_value())
                result_col_name.append('obj_sum_allocation2')
                result_list.append(sol.get_var_solution(self.obj_sum_allocation_var3).get_value())
                result_col_name.append('obj_sum_allocation3')

            all_result_list.append(result_list)
            all_result_list_df = pd.DataFrame(all_result_list, columns=result_col_name)
            all_result_list_df.to_excel(self.config['folderpath'] + '/all_objective_function_result.xlsx', index=True)

            save_result(self, sol, solution_index)
