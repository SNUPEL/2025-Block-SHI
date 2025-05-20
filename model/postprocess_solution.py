from class_definition import *
import matplotlib.pyplot as plt



def postprocess_solution(self):
    if self.solution_cpmodel:
        results = []
        crane_results = []

        # 각 블록에 대한 결과 수집
        for block_key in self.block_keys:
            block = self.block_dict[block_key]
            block_id = f"{block.ship_type}_{block.project_number}_{block.block_number}"

            # 선택된 정반과 회전 찾기
            selected_group = None
            selected_surface = None
            selected_rotation = None

            # STORE 작업 변수로 선택된 정반과 회전 확인
            for var_key, var in self.block_schedule_var_by_id_group_surf_work_rotate_dict.items():
                if block_id in var_key and 'STORE' in var_key:
                    if self.solution_cpmodel.get_var_solution(var).is_present():
                        _, selected_group, selected_surface, _, selected_rotation = var_key
                        break

            if selected_group is not None:
                # 날짜 변환
                in_var_key = (block_id, selected_group, selected_surface, 'IN', selected_rotation)
                store_var_key = (block_id, selected_group, selected_surface, 'STORE', selected_rotation)
                to_var_key = (block_id, selected_group, selected_surface, 'TO', selected_rotation)
                pe_var_key = (block_id, selected_group, selected_surface, 'PE', selected_rotation)

                # 변수 솔루션 추출
                in_sol = self.solution_cpmodel.get_var_solution(
                    self.block_schedule_var_by_id_group_surf_work_rotate_dict[in_var_key]
                )
                store_sol = self.solution_cpmodel.get_var_solution(
                    self.block_schedule_var_by_id_group_surf_work_rotate_dict[store_var_key]
                )
                to_sol = self.solution_cpmodel.get_var_solution(
                    self.block_schedule_var_by_id_group_surf_work_rotate_dict[to_var_key]
                )
                pe_sol = self.solution_cpmodel.get_var_solution(
                    self.block_schedule_var_by_id_group_surf_work_rotate_dict[pe_var_key]
                )

                # 위치 변수
                pos_var_key = (block_id, selected_group, selected_surface, selected_rotation)
                x_sol = self.solution_cpmodel.get_var_solution(
                    self.block_x_var_by_id_group_surf_rotate_dict[pos_var_key]
                )
                y_sol = self.solution_cpmodel.get_var_solution(
                    self.block_y_var_by_id_group_surf_rotate_dict[pos_var_key]
                )
                time_sol = self.solution_cpmodel.get_var_solution(
                    self.block_time_var_by_id_group_surf_rotate_dict[pos_var_key]
                )

                # 인덱스를 날짜로 변환 (범위 체크 추가)
                def get_date_from_index(index):
                    if index in self.postprocess_calendar_dict:
                        return self.postprocess_calendar_dict[index]
                    else:
                        # 범위를 벗어난 경우, 가장 가까운 유효한 날짜 반환
                        valid_indices = sorted(self.postprocess_calendar_dict.keys())
                        if index < valid_indices[0]:
                            return self.postprocess_calendar_dict[valid_indices[0]]
                        else:
                            return self.postprocess_calendar_dict[valid_indices[-1]]

                IN_date = get_date_from_index(in_sol.get_start())
                OUT_date = get_date_from_index(time_sol.get_end())
                TO_date = get_date_from_index(to_sol.get_end())
                PE_date = get_date_from_index(pe_sol.get_end())


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

                

                # 결과 행 추가
                results.append({
                    '선종': block.ship_type,
                    '호선': block.project_number,
                    '블록': block.block_number,
                    '착수일': IN_date,
                    '완료일': OUT_date,
                    '공기': block.processing_time,
                    'TO일정': TO_date,
                    'PE일정': PE_date,
                    '블록길이': block.adjusted_length / 10,
                    '블록폭': block.adjusted_breadth / 10,
                    '블록높이': block.adjusted_height / 10,
                    '블록중량': block.weight,
                    '옥내외': None,
                    '러그방향': block.lug_direction,
                    '배치확정여부': 'Y',
                    '그룹ID': selected_group,
                    '블록위치X': x_sol.get_start() / 10,
                    '블록위치Y': y_sol.get_start() / 10,
                })

                crane_results.append({
                    '선종': block.ship_type,
                    '호선': block.project_number,
                    '블록': block.block_number,
                    '착수일': IN_date,
                    '완료일': OUT_date,
                    'TO일정': TO_date,
                    'PE일정': PE_date,
                    '그룹ID': selected_group,
                    '회전': selected_rotation,
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
                    'TO일정': None,
                    'PE일정': None,
                    '블록길이': block.adjusted_length / 10,
                    '블록폭': block.adjusted_breadth / 10,
                    '블록높이': block.adjusted_height / 10,
                    '블록중량': block.weight,
                    '옥내외': None,
                    '러그방향': block.lug_direction,
                    '배치확정여부': 'N',
                    '그룹ID': None,
                    '블록위치X': None,
                    '블록위치Y': None,
                })

                crane_results.append({
                    '선종': block.ship_type,
                    '호선': block.project_number,
                    '블록': block.block_number,
                    '착수일': None,
                    '완료일': None,
                    'TO일정': None,
                    'PE일정': None,
                    '그룹ID': None,
                    '회전': None,
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
        output_path = f"{self.config['folderpath']}/block_allocation_result.xlsx"
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            self.df_result.to_excel(writer, index=False, sheet_name='배치결과')
            self.df_crane_result.to_excel(writer, index=False, sheet_name='크레인 정보')
        # self.df_result.to_excel(output_path, index=False)

        # postprocess_solution_crane

        results_crane = []
        results_crane_worktime = []

        day_time_tracker = {}

        for index, day in self.postprocess_calendar_dict.items():
            crane_worktime = 0
            # 날짜별 시작 시간 초기화 (8시 시작 가정)
            if day not in day_time_tracker:
                day_time_tracker[day] = {'hour': 9, 'minute': 0}

            for result in crane_results:
                if result['착수일'] == day:
                    # 현재 시간 가져오기
                    current_hour = day_time_tracker[day]['hour']
                    current_minute = day_time_tracker[day]['minute']

                    # 작업 시간 (분 단위로 변환)
                    work_time_minutes = int((result['IN_크레인_소요시간'] or 0) * 60)


                    # 작업 종료 시간 계산
                    end_minute = current_minute + work_time_minutes
                    end_hour = current_hour + end_minute // 60
                    end_minute = end_minute % 60

                    datetime_str = f"{day} {current_hour:02d}:{current_minute:02d}:00"

                    operated_block_dict = {
                        'date': datetime_str,
                        '선종': result['선종'],
                        '호선': result['호선'],
                        '블록': result['블록'],
                        '그룹ID': result['그룹ID'],
                        'work': 'IN',
                        '크레인ID': result['IN_크레인ID'],
                        '크레인_소요시간': result['IN_크레인_소요시간']
                    }
                    results_crane.append(operated_block_dict)

                    crane_worktime += int(result['IN_크레인_소요시간'] or 0)

                    day_time_tracker[day] = {'hour': end_hour, 'minute': end_minute}

                elif result['TO일정'] == day:
                    current_hour = day_time_tracker[day]['hour']
                    current_minute = day_time_tracker[day]['minute']

                    work_time_minutes = int((result['TO_크레인_소요시간'] or 0) * 60)


                    end_minute = current_minute + work_time_minutes
                    end_hour = current_hour + end_minute // 60
                    end_minute = end_minute % 60

                    datetime_str = f"{day} {current_hour:02d}:{current_minute:02d}:00"

                    operated_block_dict = {
                        'date': datetime_str,
                        '선종': result['선종'],
                        '호선': result['호선'],
                        '블록': result['블록'],
                        '그룹ID': result['그룹ID'],
                        'work': 'TO',
                        '크레인ID': result['TO_크레인ID'],
                        '크레인_소요시간': result['TO_크레인_소요시간']
                    }
                    results_crane.append(operated_block_dict)

                    crane_worktime += int(result['TO_크레인_소요시간'] or 0)

                    day_time_tracker[day] = {'hour': end_hour, 'minute': end_minute}

                elif result['PE일정'] == day:
                    current_hour = day_time_tracker[day]['hour']
                    current_minute = day_time_tracker[day]['minute']

                    work_time_minutes = int((result['PE_크레인_소요시간'] or 0) * 60)

                    end_minute = current_minute + work_time_minutes
                    end_hour = current_hour + end_minute // 60
                    end_minute = end_minute % 60

                    datetime_str = f"{day} {current_hour:02d}:{current_minute:02d}:00"

                    operated_block_dict = {
                        'date': datetime_str,
                        '선종': result['선종'],
                        '호선': result['호선'],
                        '블록': result['블록'],
                        '그룹ID': result['그룹ID'],
                        'work': 'PE',
                        '크레인ID': result['PE_크레인ID'],
                        '크레인_소요시간': result['PE_크레인_소요시간']
                    }
                    results_crane.append(operated_block_dict)

                    crane_worktime += int(result['PE_크레인_소요시간'] or 0)

                    day_time_tracker[day] = {'hour': end_hour, 'minute': end_minute}

            crane_worktime_dict = {
                'date': day,
                '일별_크레인_소요시간': crane_worktime,
            }

            results_crane_worktime.append(crane_worktime_dict)

        self.df_result = pd.DataFrame(results_crane)
        self.df_result.dropna(subset=['크레인ID'], inplace=True)  # 그룹 4  에서 in은 크레인 없어서 출력 제외
        self.df_result_2 = pd.DataFrame(results_crane_worktime)
        output_path = f"{self.config['folderpath']}/crane_result.xlsx"

        # 크레인별로 작업 시간순 정렬
        self.df_result['date'] = pd.to_datetime(self.df_result['date'])
        self.df_result = self.df_result.sort_values(['date', 'work'])

        with pd.ExcelWriter(output_path, engine='openpyxl', mode='w') as writer:
            self.df_result.to_excel(writer, sheet_name='crane_result_main', index=False)
            self.df_result_2.to_excel(writer, sheet_name='result_crane_worktime', index=False)

        df = self.df_result.copy()
        df['weekday'] = df['date'].dt.day_name()
        df['week'] = df['date'].dt.isocalendar().week

        weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        df = df[df['weekday'].isin(weekday_order)]
        df['weekday'] = pd.Categorical(df['weekday'], categories=weekday_order, ordered=True)

        df['크레인_소요시간'] = df['크레인_소요시간'].fillna(0).astype(int)
        df['time_info'] = df['date'].dt.strftime('%H:%M')
        df['summary'] = df['work'] + ' (' + df['time_info'] + '): ' + df['크레인_소요시간'].astype(str) + 'h'

        summary_total_df = df.groupby(['week', 'weekday'], observed=False).agg(
            {'summary': lambda x: '\n'.join(x), '크레인_소요시간': 'sum'}).reset_index()

        summary_total_df['cell_text'] = summary_total_df['summary'] + '\nTotal: ' + summary_total_df['크레인_소요시간'].astype(
            str) + 'h'

        calendar_df = summary_total_df.pivot(index='week', columns='weekday', values='cell_text').fillna('')

        calendar_df.columns.name = None

        fig, ax = plt.subplots(figsize=(16, len(calendar_df) * 1.2))
        ax.axis('off')

        table = ax.table(
            cellText=calendar_df.values,
            rowLabels=[f"Week {w}" for w in calendar_df.index],
            colLabels=calendar_df.columns.tolist(),
            colWidths=[0.2] * len(calendar_df.columns),
            loc='center',
            cellLoc='center'
        )

        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.5, 3.0)

        plt.title('Crane Operation Calendar', fontsize=14, pad=20)
        plt.tight_layout()
        calendar_img_path = f"{self.config['folderpath']}/crane_result.png"
        plt.savefig(calendar_img_path)
        plt.close()

        print(f"Results saved to: {output_path}")