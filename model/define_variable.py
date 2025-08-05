from docplex.cp.model import *
import pandas as pd
import config


def define_variable(self):

    self.crane_usage_step = self.cpmodel.step_at(0, 0)

    # 블록 변수 딕셔너리 초기화
    self.block_keys = []
    for block_key, block in self.block_dict.items():
        self.block_keys.append((block.ship_type, block.project_number, block.block_number))

    # 각 블록에 대해 변수 생성
    for block_key in self.block_keys:
        block = self.block_dict[block_key]
        block_id = f"{block.ship_type}_{block.project_number}_{block.block_number}"

        if self.config['obj_unassigned_block'] == True:
            # 각 작업별 대표 변수 선언
            for work in self.work_list:
                self.block_schedule_var_by_id_work_dict[(block_id, work)] = self.cpmodel.interval_var(optional=True)
                self.block_schedule_var_list_by_id_work_dict[(block_id, work)] = []

            # 위치 변수 초기화
            self.block_x_var_by_id_dict[block_id] = self.cpmodel.interval_var(optional=True)
            self.block_x_var_list_by_id_dict[block_id] = []

            self.block_y_var_by_id_dict[block_id] = self.cpmodel.interval_var(optional=True)
            self.block_y_var_list_by_id_dict[block_id] = []

            self.block_time_var_by_id_dict[block_id] = self.cpmodel.interval_var(optional=True)
            self.block_time_var_list_by_id_dict[block_id] = []
        else:
            # 각 작업별 대표 변수 선언
            for work in self.work_list:
                self.block_schedule_var_by_id_work_dict[(block_id, work)] = self.cpmodel.interval_var()
                self.block_schedule_var_list_by_id_work_dict[(block_id, work)] = []

            # 위치 변수 초기화
            self.block_x_var_by_id_dict[block_id] = self.cpmodel.interval_var()
            self.block_x_var_list_by_id_dict[block_id] = []

            self.block_y_var_by_id_dict[block_id] = self.cpmodel.interval_var()
            self.block_y_var_list_by_id_dict[block_id] = []

            self.block_time_var_by_id_dict[block_id] = self.cpmodel.interval_var()
            self.block_time_var_list_by_id_dict[block_id] = []

        # 모든 정반에 대해 변수 생성
        for surface_group_key, work_area in self.work_area_dict.items():
            # 정반 ID를 스트링으로 변환 (리스트일 경우 튜플로 변환)
            surface_id = work_area.surface_id_list
            if isinstance(surface_id, list):
                surface_id = tuple(surface_id)


            # 각 작업별 일정 변수 생성 (회전 각도별 변수 생성)
            for work in self.work_list:

                # 각 회전 각도별 변수 생성
                for rotate in self.rotation_list:
                    var_key_work_rotate = (block_id, surface_group_key, surface_id, work, rotate)

                    # 회전에 따라 블록 크기 조정 (위치 변수용)
                    if rotate == 0:
                        block_length = block.adjusted_length
                        block_breadth = block.adjusted_breadth
                    else:  # 90도 회전
                        block_length = block.adjusted_breadth
                        block_breadth = block.adjusted_length

                    # 정반에 들어갈 수 없는 블록은 변수 생성 제외
                    if block_length > work_area.L or block_breadth > work_area.B:
                        continue

                    # 특정 블록(TEU, 20, L/R) 정반 그룹 4에 배치
                    block_num_str = str(block.block_number)
                    if ("TEU" in str(block.ship_type) and
                            "20" in block_num_str and
                            (block_num_str.endswith("L") or block_num_str.endswith("R"))):
                        if surface_group_key[0] != 4:
                            continue

                    # TP 사용 시 경우 짧은 쪽이 55가 되도록 수정
                    if work_area.TP_condition == 'Y':
                        # TP 방향이 가로 세로 동시일 경우
                        if ((work_area.TP_direction[0] or work_area.TP_direction[2])
                                and (work_area.TP_direction[1] or work_area.TP_direction[3])):
                            # 작은 쪽이 55를 못 넘으면 55로 취급
                            if block_length >= block_breadth:
                                if block_breadth - self.config['block_spacing_y'] * 10 <= 55:
                                    block_breadth = 55 + self.config['block_spacing_y'] * 10
                            else:
                                if block_length - self.config['block_spacing_x'] * 10 <= 55:
                                    block_length = 55 + self.config['block_spacing_x'] * 10
                        # TP 방향이 세로 방향일 경우
                        elif work_area.TP_direction[0] or work_area.TP_direction[2]:
                            # L이 더 작아야 함
                            if block_breadth >= block_length:
                                # L이 55를 못 넘으면 55로 취급
                                if block_length - self.config['block_spacing_x'] * 10 <= 55:
                                    block_length = 55 + self.config['block_spacing_x'] * 10
                            else:
                                continue
                        # TP 방향이 가로 방향일 경우
                        elif work_area.TP_direction[1] or work_area.TP_direction[3]:
                            # B가 더 작아야 함
                            if block_length >= block_breadth:
                                # B가 55를 못 넘으면 55로 취급
                                if block_breadth - self.config['block_spacing_y'] * 10 <= 55:
                                    block_breadth = 55 + self.config['block_spacing_y'] * 10
                            else:
                                continue
                    else:
                        # TP 미 사용 시 않는 경우 중량이 45를 넘을 수 없음
                        if block.weight > 45:
                            continue

                    # 정반 사이즈 제약에 따른 변수 선언
                    if rotate == 0:
                        if block.length > work_area.L_limit_of_block or block.breadth > work_area.B_limit_of_block or \
                                block.height > work_area.H_limit_of_block or block.weight > work_area.W_limit_of_block:
                            continue
                    else:
                        if block.breadth > work_area.L_limit_of_block or block.length > work_area.B_limit_of_block or \
                                block.height > work_area.H_limit_of_block or block.weight > work_area.W_limit_of_block:
                            continue

                    # 러그 방향 제약에 따른 변수 선언
                    if work_area.lug_condition != 'N':
                        if rotate == 0 and work_area.lug_condition == block.lug_direction:
                            pass
                        elif rotate == 90 and work_area.lug_condition != block.lug_direction:
                            pass
                        else:
                            continue

                    # 각 작업별 일정 변수 생성
                    if work == 'IN':
                        # 반입 일정
                        self.block_schedule_var_by_id_group_surf_work_rotate_dict[
                            var_key_work_rotate] = self.cpmodel.interval_var(
                            start=(block.allocation_index, block.PE_index + self.max_delay_day),
                            size=1,
                            optional=True,
                            name=f"{work}_{block_id}_{surface_group_key}_{surface_id}_{rotate}"
                        )

                    elif work == 'STORE':
                        # 적치 일정
                        self.block_schedule_var_by_id_group_surf_work_rotate_dict[
                            var_key_work_rotate] = self.cpmodel.interval_var(
                            start=(block.allocation_index, block.PE_index + self.max_delay_day),
                            size=(block.TO_index - block.allocation_index - 1, block.TO_index - block.allocation_index - 1 + self.max_delay_day),
                            optional=True,
                            name=f"{work}_{block_id}_{surface_group_key}_{surface_id}_{rotate}"
                        )

                    elif work == 'TO':
                        # T/O 일정
                        self.block_schedule_var_by_id_group_surf_work_rotate_dict[
                            var_key_work_rotate] = self.cpmodel.interval_var(
                            start=(block.allocation_index, block.PE_index + self.max_delay_day),
                            size=1,
                            optional=True,
                            name=f"{work}_{block_id}_{surface_group_key}_{surface_id}_{rotate}"
                        )

                    elif work == 'PE':
                        # PE 일정
                        self.block_schedule_var_by_id_group_surf_work_rotate_dict[
                            var_key_work_rotate] = self.cpmodel.interval_var(
                            start=(block.allocation_index, block.PE_index + self.max_delay_day),
                            size=1,
                            optional=True,
                            name=f"{work}_{block_id}_{surface_group_key}_{surface_id}_{rotate}"
                        )

                    # 일정 변수 리스트에 추가
                    self.block_schedule_var_list_by_id_work_dict[(block_id, work)].append(
                        self.block_schedule_var_by_id_group_surf_work_rotate_dict[var_key_work_rotate]
                    )

                    # 위치 변수 생성 (회전마다 한 번씩)
                    if work == 'STORE':  # store 작업에 대해서만 위치 변수 생성
                        var_key = (block_id, surface_group_key, surface_id, rotate)

                        # X축 위치 변수
                        self.block_x_var_by_id_group_surf_rotate_dict[var_key] = self.cpmodel.interval_var(
                            start=(0, int(work_area.L - block_length)),  # 정반 내에서 가능한 y 범위
                            size=int(block_length),  # 블록 길이
                            optional=True,
                            name=f"x_{block_id}_{surface_group_key}_{surface_id}_{rotate}"
                        )
                        self.block_x_var_list_by_id_dict[block_id].append(
                            self.block_x_var_by_id_group_surf_rotate_dict[var_key]
                        )

                        # Y축 위치 변수
                        self.block_y_var_by_id_group_surf_rotate_dict[var_key] = self.cpmodel.interval_var(
                            start=(0, int(work_area.B - block_breadth)),  # 정반 내에서 가능한 y 범위
                            size=int(block_breadth),  # 블록 폭
                            optional=True,
                            name=f"y_{block_id}_{surface_group_key}_{surface_id}_{rotate}"
                        )
                        self.block_y_var_list_by_id_dict[block_id].append(
                            self.block_y_var_by_id_group_surf_rotate_dict[var_key]
                        )

                        # 시간축 변수 (적치 기간)
                        self.block_time_var_by_id_group_surf_rotate_dict[var_key] = self.cpmodel.interval_var(
                            # size=(block.TO_index - block.allocation_index - 1, block.TO_index - block.allocation_index - 1 + self.max_delay_day),
                            size=(block.TO_index - block.allocation_index, block.TO_index - block.allocation_index + self.max_delay_day),
                            optional=True,
                            name=f"time_{block_id}_{surface_group_key}_{surface_id}_{rotate}"
                        )
                        self.block_time_var_list_by_id_dict[block_id].append(
                            self.block_time_var_by_id_group_surf_rotate_dict[var_key]
                        )

                        # 위치 변수들 간의 연결
                        self.cpmodel.add(
                            self.cpmodel.presence_of(self.block_x_var_by_id_group_surf_rotate_dict[var_key]) ==
                            self.cpmodel.presence_of(self.block_y_var_by_id_group_surf_rotate_dict[var_key])
                        )
                        self.cpmodel.add(
                            self.cpmodel.presence_of(self.block_x_var_by_id_group_surf_rotate_dict[var_key]) ==
                            self.cpmodel.presence_of(self.block_time_var_by_id_group_surf_rotate_dict[var_key])
                        )

                        # 위치 변수와 store 일정 변수 연결
                        self.cpmodel.add(
                            self.cpmodel.presence_of(self.block_x_var_by_id_group_surf_rotate_dict[var_key]) ==
                            self.cpmodel.presence_of(self.block_schedule_var_by_id_group_surf_work_rotate_dict[
                                                         (block_id, surface_group_key, surface_id, 'STORE', rotate)])
                        )

                        # 시간축 변수와 store 작업 변수 간의 시간 동기화
                        self.cpmodel.add(
                            self.cpmodel.start_of(self.block_time_var_by_id_group_surf_rotate_dict[var_key]) ==
                            self.cpmodel.start_of(self.block_schedule_var_by_id_group_surf_work_rotate_dict[
                                                      (block_id, surface_group_key, surface_id, 'STORE', rotate)])
                        )
                        # 시간축 변수와 store 작업 변수 간의 시간 동기화
                        self.cpmodel.add(
                            self.cpmodel.size_of(self.block_time_var_by_id_group_surf_rotate_dict[var_key]) *
                            self.cpmodel.presence_of(self.block_time_var_by_id_group_surf_rotate_dict[var_key]) ==
                            (self.cpmodel.size_of(self.block_schedule_var_by_id_group_surf_work_rotate_dict[
                                                      (block_id, surface_group_key, surface_id, 'STORE', rotate)]) + 1) *
                            self.cpmodel.presence_of(self.block_schedule_var_by_id_group_surf_work_rotate_dict[
                                                      (block_id, surface_group_key, surface_id, 'STORE', rotate)])
                        )

            # 같은 정반, 회전에 대한 작업 변수들 간의 관계 설정 (하나가 선택되면 모두 선택)
            for rotate in self.rotation_list:
                for i in range(len(self.work_list) - 1):
                    key1 = (block_id, surface_group_key, surface_id, self.work_list[i], rotate)
                    key2 = (block_id, surface_group_key, surface_id, self.work_list[i + 1], rotate)
                    if key1 in self.block_schedule_var_by_id_group_surf_work_rotate_dict \
                            and key2 in self.block_schedule_var_by_id_group_surf_work_rotate_dict:
                        self.cpmodel.add(
                            self.cpmodel.presence_of(self.block_schedule_var_by_id_group_surf_work_rotate_dict[key1])
                            ==
                            self.cpmodel.presence_of(self.block_schedule_var_by_id_group_surf_work_rotate_dict[key2])
                        )

        # 각 블록은 최대 하나의 정반과 회전 각도 조합에만 배치 가능
        for work in self.work_list:
            if self.block_schedule_var_list_by_id_work_dict[(block_id, work)]:
                self.cpmodel.add(
                    self.cpmodel.alternative(
                        self.block_schedule_var_by_id_work_dict[(block_id, work)],
                        self.block_schedule_var_list_by_id_work_dict[(block_id, work)]
                    )
                )

        # 위치 변수에 대한 alternative 관계 설정
        if self.block_x_var_list_by_id_dict[block_id]:
            self.cpmodel.add(
                self.cpmodel.alternative(
                    self.block_x_var_by_id_dict[block_id],
                    self.block_x_var_list_by_id_dict[block_id]
                )
            )
            self.cpmodel.add(
                self.cpmodel.alternative(
                    self.block_y_var_by_id_dict[block_id],
                    self.block_y_var_list_by_id_dict[block_id]
                )
            )
            self.cpmodel.add(
                self.cpmodel.alternative(
                    self.block_time_var_by_id_dict[block_id],
                    self.block_time_var_list_by_id_dict[block_id]
                )
            )

    # 모든 변수 생성 후 작업 간 선후행 관계 설정
    for block_key in self.block_keys:
        block = self.block_dict[block_key]
        block_id = f"{block.ship_type}_{block.project_number}_{block.block_number}"

        for surface_group_key, work_area in self.work_area_dict.items():
            surface_id = work_area.surface_id_list
            if isinstance(surface_id, list):
                surface_id = tuple(surface_id)

            for rotate in self.rotation_list:
                # 각 단계별 키를 미리 정의
                key_in = (block_id, surface_group_key, surface_id, 'IN', rotate)
                key_store = (block_id, surface_group_key, surface_id, 'STORE', rotate)
                key_to = (block_id, surface_group_key, surface_id, 'TO', rotate)
                key_pe = (block_id, surface_group_key, surface_id, 'PE', rotate)

                # IN → STORE
                if key_in in self.block_schedule_var_by_id_group_surf_work_rotate_dict \
                        and key_store in self.block_schedule_var_by_id_group_surf_work_rotate_dict:
                    self.cpmodel.add(
                        self.cpmodel.end_at_start(
                            self.block_schedule_var_by_id_group_surf_work_rotate_dict[key_in],
                            self.block_schedule_var_by_id_group_surf_work_rotate_dict[key_store]
                        )
                    )

                # STORE → TO
                if key_store in self.block_schedule_var_by_id_group_surf_work_rotate_dict \
                        and key_to in self.block_schedule_var_by_id_group_surf_work_rotate_dict:
                    self.cpmodel.add(
                        self.cpmodel.end_at_start(
                            self.block_schedule_var_by_id_group_surf_work_rotate_dict[key_store],
                            self.block_schedule_var_by_id_group_surf_work_rotate_dict[key_to]
                        )
                    )

                # TO → PE
                if key_to in self.block_schedule_var_by_id_group_surf_work_rotate_dict \
                        and key_pe in self.block_schedule_var_by_id_group_surf_work_rotate_dict:
                    self.cpmodel.add(
                        self.cpmodel.end_at_start(
                            self.block_schedule_var_by_id_group_surf_work_rotate_dict[key_to],
                            self.block_schedule_var_by_id_group_surf_work_rotate_dict[key_pe]
                        )
                    )

    # key[1]은 workunit 번호를 의미하며 0은 전체 정반 그룹을 의미함
    for surface_group_key, work_area in self.work_area_dict.items():
        self.unavailable_work_area_x_var_by_id_dict[(surface_group_key, 0)] = self.cpmodel.interval_var(
                            start=work_area.unavailable_area_x,
                            size=work_area.unavailable_area_L,
                            optional=False,
                        )
        self.unavailable_work_area_y_var_by_id_dict[(surface_group_key, 0)] = self.cpmodel.interval_var(
            start=work_area.unavailable_area_y,
            size=work_area.unavailable_area_B,
            optional=False,
        )
        self.unavailable_work_area_time_var_by_id_dict[(surface_group_key, 0)] = self.cpmodel.interval_var(
                            start=self.model_start_index,
                            end=self.model_end_index,
                            optional=False,
                        )

        for work_unit_number, work_unit in work_area.work_unit_dict.items():
            for unavailable_duration_list in work_unit.unavailable_duration_list:
                self.unavailable_work_area_x_var_by_id_dict[(surface_group_key, work_unit_number)]\
                    = self.cpmodel.interval_var(
                    start=work_unit.x,
                    size=work_unit.dx,
                    optional=False,
                )
                self.unavailable_work_area_y_var_by_id_dict[(surface_group_key, work_unit_number)]\
                    = self.cpmodel.interval_var(
                    start=work_unit.y,
                    size=work_unit.dy,
                    optional=False,
                )
                self.unavailable_work_area_time_var_by_id_dict[(surface_group_key, work_unit_number)]\
                    = self.cpmodel.interval_var(
                    start=unavailable_duration_list[0],
                    end=unavailable_duration_list[1],
                    optional=False,
                )