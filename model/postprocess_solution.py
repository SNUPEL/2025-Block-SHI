import pandas as pd


# def postprocess_solution(self):
#     if self.solution_cpmodel:
#         results = []
#
#         # 각 블록에 대한 결과 수집
#         for block_key in self.block_keys:
#             block = self.block_dict[block_key]
#             block_id = f"{block.ship_type}_{block.project_number}_{block.block_number}"
#
#             # 선택된 정반과 회전 찾기
#             selected_group = None
#             selected_surface = None
#             selected_rotation = None
#
#             # STORE 작업 변수로 선택된 정반과 회전 확인
#             for var_key, var in self.block_schedule_var_by_id_group_surf_work_rotate_dict.items():
#                 if block_id in var_key and 'STORE' in var_key:
#                     if self.solution_cpmodel.get_var_solution(var).is_present():
#                         _, selected_group, selected_surface, _, selected_rotation = var_key
#                         break
#
#             if selected_group is not None:
#                 # 날짜 변환
#                 in_var_key = (block_id, selected_group, selected_surface, 'IN', selected_rotation)
#                 store_var_key = (block_id, selected_group, selected_surface, 'STORE', selected_rotation)
#                 to_var_key = (block_id, selected_group, selected_surface, 'TO', selected_rotation)
#                 pe_var_key = (block_id, selected_group, selected_surface, 'PE', selected_rotation)
#
#                 # 변수 솔루션 추출
#                 in_sol = self.solution_cpmodel.get_var_solution(
#                     self.block_schedule_var_by_id_group_surf_work_rotate_dict[in_var_key]
#                 )
#                 store_sol = self.solution_cpmodel.get_var_solution(
#                     self.block_schedule_var_by_id_group_surf_work_rotate_dict[store_var_key]
#                 )
#                 to_sol = self.solution_cpmodel.get_var_solution(
#                     self.block_schedule_var_by_id_group_surf_work_rotate_dict[to_var_key]
#                 )
#                 pe_sol = self.solution_cpmodel.get_var_solution(
#                     self.block_schedule_var_by_id_group_surf_work_rotate_dict[pe_var_key]
#                 )
#
#                 # 위치 변수
#                 pos_var_key = (block_id, selected_group, selected_surface, selected_rotation)
#                 x_sol = self.solution_cpmodel.get_var_solution(
#                     self.block_x_var_by_id_group_surf_rotate_dict[pos_var_key]
#                 )
#                 y_sol = self.solution_cpmodel.get_var_solution(
#                     self.block_y_var_by_id_group_surf_rotate_dict[pos_var_key]
#                 )
#
#                 # 인덱스를 날짜로 변환 (범위 체크 추가)
#                 def get_date_from_index(index):
#                     if index in self.postprocess_calendar_dict:
#                         return self.postprocess_calendar_dict[index]
#                     else:
#                         print('불가능한 해가 출력되었습니다.')
#
#                 착수일 = get_date_from_index(in_sol.get_start())
#                 완료일 = get_date_from_index(store_sol.get_end())
#                 공기 = store_sol.get_end() - in_sol.get_start() + 1
#                 TO일정 = get_date_from_index(to_sol.get_start())
#                 PE일정 = get_date_from_index(pe_sol.get_start())
#
#                 # 결과 행 추가
#                 results.append({
#                     '선종': block.ship_type,
#                     '호선': block.project_number,
#                     '블록': block.block_number,
#                     '착수일': 착수일,
#                     '완료일': 완료일,
#                     '공기': 공기,
#                     'TO일정': TO일정,
#                     'PE일정': PE일정,
#                     '그룹ID': selected_group[0],
#                     '블록위치X': x_sol.get_start(),
#                     '블록위치Y': y_sol.get_start(),
#                     '회전': selected_rotation
#                 })
#             else:
#                 # 미배치 블록
#                 results.append({
#                     '선종': block.ship_type,
#                     '호선': block.project_number,
#                     '블록': block.block_number,
#                     '착수일': None,
#                     '완료일': None,
#                     '공기': None,
#                     'TO일정': None,
#                     'PE일정': None,
#                     '그룹ID': '미배치',
#                     '블록위치X': None,
#                     '블록위치Y': None,
#                     '회전': None
#                 })
#
#         # DataFrame 생성 및 엑셀 저장
#         self.df_result = pd.DataFrame(results)
#         output_path = f"{self.config['folderpath']}/block_allocation_result.xlsx"
#         self.df_result.to_excel(output_path, index=False)
#
#         print(f"Results saved to: {output_path}")
#     else:
#         print("No solution found.")
def postprocess_solution(self):
    if self.solution_cpmodel:
        results = []

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

                # 결과 행 추가
                results.append({
                    '선종': block.ship_type,
                    '호선': block.project_number,
                    '블록': block.block_number,
                    '착수일': IN_date,
                    '완료일': OUT_date,
                    'TO일정': TO_date,
                    'PE일정': PE_date,
                    '그룹ID': selected_group[0],
                    '정반명': selected_surface,
                    '블록위치X': x_sol.get_start(),
                    '블록위치Y': y_sol.get_start(),
                    '회전': selected_rotation,
                    '길이': block.length,
                    '폭': block.breadth,
                    '중량': block.weight
                })
            else:
                # 미배치 블록
                results.append({
                    '선종': block.ship_type,
                    '호선': block.project_number,
                    '블록': block.block_number,
                    '착수일': None,
                    '완료일': None,
                    'TO일정': None,
                    'PE일정': None,
                    '그룹ID': 'None',
                    '정반명': 'None',
                    '블록위치X': None,
                    '블록위치Y': None,
                    '회전': None,
                    '길이': block.length,
                    '폭': block.breadth,
                    '중량': block.weight
                })

        # DataFrame 생성 및 엑셀 저장
        self.df_result = pd.DataFrame(results)
        output_path = f"{self.config['folderpath']}/block_allocation_result.xlsx"
        self.df_result.to_excel(output_path, index=False)

        print(f"Results saved to: {output_path}")
    else:
        print("No solution found.")