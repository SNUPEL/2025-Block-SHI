class WorkUnit:
    def __init__(self, unit_id, x, y, dx, dy):
        self.unit_id = unit_id
        self.x = int(x * 10)
        self.y = int(y * 10)
        self.dx = int(dx * 10)
        self.dy = int(dy * 10)


class WorkArea:
    def __init__(self, group_id, surface_id_list, priority, lug_condition, indoor_outdoor_condition, L_limit_of_block,
                 B_limit_of_block, H_limit_of_block, W_limit_of_block, TP_condition, TP_direction, L, B):
        self.group_id = group_id
        self.surface_id_list = surface_id_list
        self.priority = priority
        self.indoor_outdoor_condition = indoor_outdoor_condition
        self.lug_condition = lug_condition
        self.L_limit_of_block = int(L_limit_of_block * 10)
        self.B_limit_of_block = int(B_limit_of_block * 10)
        self.H_limit_of_block = int(H_limit_of_block * 10)
        self.W_limit_of_block = int(W_limit_of_block * 10)
        self.TP_condition = TP_condition
        # [방향1, 방향2, 방향3, 방향4]에 대한 boolean
        self.TP_direction = TP_direction
        self.L = int(L * 10)
        self.B = int(B * 10)
        self.unavailable_area_x = None
        self.unavailable_area_y = None
        self.unavailable_area_L = None
        self.unavailable_area_B = None
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
        self.unavailable_time_list = list()
