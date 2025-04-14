from docplex.cp.model import *
import pandas as pd


def define_variable(self):
    # 블록 변수 딕셔너리 초기화
    self.block_keys = []
    for block_key, block in self.block_dict.items():
        self.block_keys.append((block.ship_type, block.project_number, block.block_number))

    # 작업 리스트 정의
    work_list = ['in', 'store', 'out', 'TO', 'PE']

    # 회전 각도 리스트 정의
    rotation_list = [0, 90]

    # 일정 변수 (수정된 구조)
    self.block_schedule_var_by_id_work_dict = {}  # 블록 ID별, 작업별 일정 변수(대표 변수)
    self.block_schedule_var_list_by_id_work_dict = {}  # 블록 ID별, 작업별 가능한 일정 변수 리스트
    self.block_schedule_var_by_id_group_surf_work_rotate_dict = {}  # 블록 ID, 그룹, 정반, 작업, 회전별 일정 변수

    # 위치 변수 (기존 구조 유지)
    self.block_x_var_by_id_dict = {}  # 블록 ID별 x축 위치 변수
    self.block_x_var_list_by_id_dict = {}  # 블록 ID별 가능한 x축 위치 변수 리스트
    self.block_x_var_by_id_group_surf_rotate_dict = {}  # 블록 ID, 그룹, 정반, 회전별 x축 위치 변수

    self.block_y_var_by_id_dict = {}  # 블록 ID별 y축 위치 변수
    self.block_y_var_list_by_id_dict = {}  # 블록 ID별 가능한 y축 위치 변수 리스트
    self.block_y_var_by_id_group_surf_rotate_dict = {}  # 블록 ID, 그룹, 정반, 회전별 y축 위치 변수

    self.block_time_var_by_id_dict = {}  # 블록 ID별 시간축 변수
    self.block_time_var_list_by_id_dict = {}  # 블록 ID별 가능한 시간축 변수 리스트
    self.block_time_var_by_id_group_surf_rotate_dict = {}  # 블록 ID, 그룹, 정반, 회전별 시간축 위치 변수

    # 각 블록에 대해 변수 생성
    for block_key in self.block_keys:
        block = self.block_dict[block_key]
        block_id = f"{block.ship_type}_{block.project_number}_{block.block_number}"

        # 각 작업별 일정 변수 초기화
        for work in work_list:
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

            # 회전 옵션 결정 (work_area가 4인 경우 회전 없이 0도만 고려)
            if surface_group_key[0] == 4 if isinstance(surface_group_key, tuple) else surface_group_key == 4:
                rotation_options = [0]  # 회전 없이 0도만 고려
            else:
                rotation_options = rotation_list  # 다른 정반은 모든 회전 고려

            # 각 작업별 일정 변수 생성 (회전 각도별 변수 생성)
            for work in work_list:
                var_key_work = (block_id, surface_group_key, surface_id, work)

                # 각 회전 각도별 변수 생성 (work_area 4는 회전 없음)
                for rotate in rotation_options:
                    var_key_work_rotate = (block_id, surface_group_key, surface_id, work, rotate)

                    # 회전에 따라 블록 크기 조정 (위치 변수용)
                    if rotate == 0:
                        block_length = block.length
                        block_breadth = block.breadth
                    else:  # 90도 회전
                        block_length = block.breadth
                        block_breadth = block.length

                    # 각 작업별 일정 변수 생성
                    if work == 'in':
                        # 반입 일정
                        self.block_schedule_var_by_id_group_surf_work_rotate_dict[
                            var_key_work_rotate] = self.cpmodel.interval_var(
                            start=(0, 10),
                            size=1,
                            optional=True,
                            name=f"{work}_{block_id}_{surface_group_key}_{surface_id}_{rotate}"
                        )
                    elif work == 'store':
                        # 적치 일정
                        self.block_schedule_var_by_id_group_surf_work_rotate_dict[
                            var_key_work_rotate] = self.cpmodel.interval_var(
                            start=(0, 10),
                            size=1,
                            optional=True,
                            name=f"{work}_{block_id}_{surface_group_key}_{surface_id}_{rotate}"
                        )
                    elif work == 'out':
                        # 반출 일정
                        self.block_schedule_var_by_id_group_surf_work_rotate_dict[
                            var_key_work_rotate] = self.cpmodel.interval_var(
                            start=(0, 10),
                            size=1,
                            optional=True,
                            name=f"{work}_{block_id}_{surface_group_key}_{surface_id}_{rotate}"
                        )
                    elif work == 'TO':
                        # T/O 일정
                        self.block_schedule_var_by_id_group_surf_work_rotate_dict[
                            var_key_work_rotate] = self.cpmodel.interval_var(
                            start=(0, 10),
                            size=1,
                            optional=True,
                            name=f"{work}_{block_id}_{surface_group_key}_{surface_id}_{rotate}"
                        )
                    elif work == 'PE':
                        # PE 일정
                        self.block_schedule_var_by_id_group_surf_work_rotate_dict[
                            var_key_work_rotate] = self.cpmodel.interval_var(
                            start=(0, 10),
                            size=1,
                            optional=True,
                            name=f"{work}_{block_id}_{surface_group_key}_{surface_id}_{rotate}"
                        )

                    # 일정 변수 리스트에 추가
                    self.block_schedule_var_list_by_id_work_dict[(block_id, work)].append(
                        self.block_schedule_var_by_id_group_surf_work_rotate_dict[var_key_work_rotate]
                    )

                    # 위치 변수도 여기서 생성 (회전마다 한 번씩)
                    if work == 'store':  # store 작업에 대해서만 위치 변수 생성
                        var_key = (block_id, surface_group_key, surface_id, rotate)

                        # X축 위치 변수
                        self.block_x_var_by_id_group_surf_rotate_dict[var_key] = self.cpmodel.interval_var(
                            start=(0, int(work_area.L - block_length)),  # 정반 내에서 가능한 x 범위
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
                            size=int(block.processing_time),  # 블록 적치 시간
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
                                                         (block_id, surface_group_key, surface_id, 'store', rotate)])
                        )

                        # 시간축 변수와 store 작업 변수 간의 시간 동기화
                        self.cpmodel.add(
                            self.cpmodel.start_of(self.block_time_var_by_id_group_surf_rotate_dict[var_key]) ==
                            self.cpmodel.start_of(self.block_schedule_var_by_id_group_surf_work_rotate_dict[
                                                      (block_id, surface_group_key, surface_id, 'store', rotate)])
                        )

            # 같은 정반, 회전에 대한 작업 변수들 간의 관계 설정 (하나가 선택되면 모두 선택)
            for rotate in rotation_options:  # 여기도 rotation_options 사용
                for i in range(len(work_list) - 1):
                    self.cpmodel.add(
                        self.cpmodel.presence_of(self.block_schedule_var_by_id_group_surf_work_rotate_dict[
                                                     (
                                                         block_id, surface_group_key, surface_id, work_list[i],
                                                         rotate)]) ==
                        self.cpmodel.presence_of(self.block_schedule_var_by_id_group_surf_work_rotate_dict[
                                                     (block_id, surface_group_key, surface_id, work_list[i + 1],
                                                      rotate)])
                    )

        # 각 블록은 최대 하나의 정반과 회전 각도 조합에만 배치 가능
        for work in work_list:
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

            # 회전 옵션 결정 (work_area가 4인 경우 회전 없이 0도만 고려)
            if surface_group_key[0] == 4 if isinstance(surface_group_key, tuple) else surface_group_key == 4:
                rotation_options = [0]  # 회전 없이 0도만 고려
            else:
                rotation_options = rotation_list  # 다른 정반은 모든 회전 고려

            for rotate in rotation_options:  # 여기도 rotation_options 사용
                # in 끝나면 바로 store 시작
                self.cpmodel.add(
                    self.cpmodel.end_before_start(
                        self.block_schedule_var_by_id_group_surf_work_rotate_dict[
                            (block_id, surface_group_key, surface_id, 'in', rotate)],
                        self.block_schedule_var_by_id_group_surf_work_rotate_dict[
                            (block_id, surface_group_key, surface_id, 'store', rotate)]
                    )
                )

                # store 끝나면 바로 out 시작
                self.cpmodel.add(
                    self.cpmodel.end_before_start(
                        self.block_schedule_var_by_id_group_surf_work_rotate_dict[
                            (block_id, surface_group_key, surface_id, 'store', rotate)],
                        self.block_schedule_var_by_id_group_surf_work_rotate_dict[
                            (block_id, surface_group_key, surface_id, 'out', rotate)]
                    )
                )

                # out 끝나면 바로 TO 시작
                self.cpmodel.add(
                    self.cpmodel.end_before_start(
                        self.block_schedule_var_by_id_group_surf_work_rotate_dict[
                            (block_id, surface_group_key, surface_id, 'out', rotate)],
                        self.block_schedule_var_by_id_group_surf_work_rotate_dict[
                            (block_id, surface_group_key, surface_id, 'TO', rotate)]
                    )
                )

                # TO 끝나면 바로 PE 시작
                self.cpmodel.add(
                    self.cpmodel.end_before_start(
                        self.block_schedule_var_by_id_group_surf_work_rotate_dict[
                            (block_id, surface_group_key, surface_id, 'TO', rotate)],
                        self.block_schedule_var_by_id_group_surf_work_rotate_dict[
                            (block_id, surface_group_key, surface_id, 'PE', rotate)]
                    )
                )

    # # 변수 생성 결과 확인을 위한 print문
    # print(f"총 {len(self.block_keys)}개 블록에 대한 변수 생성 완료")
    # for block_key in self.block_keys:
    #     block = self.block_dict[block_key]
    #     block_id = f"{block.ship_type}_{block.project_number}_{block.block_number}"
    #
    #     print(f"\n블록 {block_id}:")
    #     print(f"  위치 변수:")
    #     print(f"    x축 변수 수: {len(self.block_x_var_list_by_id_dict[block_id])}")
    #     print(f"    y축 변수 수: {len(self.block_y_var_list_by_id_dict[block_id])}")
    #     print(f"    시간축 변수 수: {len(self.block_time_var_list_by_id_dict[block_id])}")
    #     print(f"  일정 변수:")
    #     for work in work_list:
    #         print(f"    {work} 작업 변수 수: {len(self.block_schedule_var_list_by_id_work_dict[(block_id, work)])}")