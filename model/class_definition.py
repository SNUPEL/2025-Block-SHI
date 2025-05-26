import pandas as pd


class WorkUnit:
    def __init__(self, unit_id, x, y, dx, dy):
        self.unit_id = unit_id
        self.x = int(x * 10)
        self.y = int(y * 10)
        self.dx = int(dx * 10)
        self.dy = int(dy * 10)
        self.unavailable_duration_list = list()


class WorkArea:
    def __init__(self, group_id, surface_id_list, priority, lug_condition, indoor_outdoor_condition, L_limit_of_block,
                 B_limit_of_block, H_limit_of_block, W_limit_of_block, TP_condition, TP_direction, L, B, min_x_of_work_area):
        self.group_id = group_id
        self.surface_id_list = surface_id_list
        self.priority = priority
        self.indoor_outdoor_condition = indoor_outdoor_condition
        self.lug_condition = lug_condition
        self.L_limit_of_block = L_limit_of_block if L_limit_of_block else 99999
        self.B_limit_of_block = B_limit_of_block if B_limit_of_block else 99999
        self.H_limit_of_block = H_limit_of_block if H_limit_of_block else 99999
        self.W_limit_of_block = W_limit_of_block if W_limit_of_block else 99999
        self.TP_condition = TP_condition
        # [방향1, 방향2, 방향3, 방향4]에 대한 boolean
        self.TP_direction = TP_direction
        self.L = int(L * 10)
        self.B = int(B * 10)
        self.min_x_of_work_area = min_x_of_work_area

        self.unavailable_area_x = None
        self.unavailable_area_y = None
        self.unavailable_area_L = None
        self.unavailable_area_B = None
        # key: 작업명, value: 시간
        self.crane_operation_dict = dict()
        self.work_unit_dict = dict()

    def add_unavailable_area(self, x, y, L, B):
        self.unavailable_area_x = int(x * 10)
        self.unavailable_area_y = int(y * 10)
        self.unavailable_area_L = int(L * 10)
        self.unavailable_area_B = int(B * 10)


class Crane:
    def __init__(self, Crane_id, condition):
        self.Crane_id = Crane_id
        self.condition = condition
        self.unavailable_time_dict = dict()


class Block:
    def __init__(self, ship_type, project_number, block_number,
                 allocation_start_date, allocation_end_date, processing_time, TO_date, PE_date,
                 length, spacing_x, breadth, spacing_y, height, weight, indoor_outdoor_condition, lug_direction, allocate_condtion):
        self.ship_type = ship_type
        self.project_number = project_number
        self.block_number = block_number
        self.allocation_start_date = allocation_start_date
        self.allocation_end_date = allocation_end_date
        self.processing_time = processing_time
        self.TO_date = TO_date
        self.PE_date = PE_date
        self.adjusted_allocation_start_date = self.allocation_start_date
        self.allocation_index = None
        self.adjusted_TO_date = self.TO_date
        self.TO_index = None
        self.adjusted_PE_date = self.PE_date
        self.PE_index = None
        self.length = length
        self.adjusted_length = int((self.length + spacing_x) * 10)
        self.breadth = breadth
        self.adjusted_breadth = int((self.breadth + spacing_y) * 10)
        self.height = height
        self.adjusted_height = int(self.height * 10)
        self.weight = weight
        self.adjusted_weight = int(self.weight * 10)
        self.indoor_outdoor_condition = indoor_outdoor_condition
        self.lug_direction = lug_direction
        self.allocate_condtion = allocate_condtion
        self.group_id = None
        self.surf_id = None
        self.rotate = None
        self.x_location = None
        self.y_location = None

    def datetime_to_idx(self, calendar):
        # working day로 delay 및 index로 변환
        while self.adjusted_allocation_start_date not in calendar.keys():
            self.adjusted_allocation_start_date += pd.Timedelta(days=1)
        self.allocation_index = calendar[self.adjusted_allocation_start_date]
        while self.adjusted_TO_date not in calendar.keys():
            self.adjusted_TO_date += pd.Timedelta(days=1)
        self.TO_index = calendar[self.adjusted_TO_date]
        while self.adjusted_PE_date not in calendar.keys():
            self.adjusted_PE_date += pd.Timedelta(days=1)
        self.PE_index = calendar[self.adjusted_PE_date]

    def get_location(self, group_id, x_location, y_location):
        # 향후 배치 확정 블록 데이터 존재 시 좌표를 정반 그룹과 위치에 맞춰 변환하는 코드 추가 구현
        self.group_id = group_id
        self.x_location = x_location
        self.y_location = y_location
