from docplex.cp.model import *
import pandas as pd
import config


def define_variable(self):
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
                # var_key_work = (block_id, surface_group_key, surface_id, work)

                # 각 회전 각도별 변수 생성
                for rotate in self.rotation_list:
                    var_key_work_rotate = (block_id, surface_group_key, surface_id, work, rotate)

                    # 회전에 따라 블록 크기 조정 (위치 변수용)
                    if rotate == 0:
                        block_length = block.adjusted_length / 2
                        block_breadth = block.adjusted_breadth / 2
                    else:  # 90도 회전
                        block_length = block.adjusted_breadth / 2
                        block_breadth = block.adjusted_length / 2
                    #
                    # if surface_group_key[0] == 4:
                    #
                    #     # 둘 다 11m 이하인 경우: 최소값을 11로 변경
                    #     if block_length <= 110 and block_breadth <= 110:
                    #         if block_length <= block_breadth:
                    #             block_length = 110
                    #         else:
                    #             block_breadth = 110
                    #
                    #     # 하나만 11m 초과인 경우: 최소값을 11m로 변경
                    #     elif (block_length > 110 and block_breadth <= 110) or (block_length <= 110 and block_breadth > 110):
                    #         if block_length <= block_breadth:
                    #             block_length = 110
                    #         else:
                    #             block_breadth = 110
                    #
                    # # 정반에 들어갈 수 없는 블록은 변수 생성 제외
                    # if block_length > work_area.L or block_breadth > work_area.B:
                    #
                    #     continue

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
                            size=(block.TO_index - block.allocation_index - 2, block.TO_index - block.allocation_index -2 + self.max_delay_day),
                            # size=block.TO_index - block.allocation_index - 2,
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
                            size=(block.TO_index - block.allocation_index - 2, block.TO_index - block.allocation_index -2 + self.max_delay_day),
                            # size=block.TO_index - block.allocation_index - 2,
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
                            self.cpmodel.size_of(self.block_time_var_by_id_group_surf_rotate_dict[var_key]) ==
                            self.cpmodel.size_of(self.block_schedule_var_by_id_group_surf_work_rotate_dict[
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