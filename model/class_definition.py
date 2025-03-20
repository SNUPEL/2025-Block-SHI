import numpy as np

class Work_unit:
    def __init__(self, x, y, dx, dy):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy

class Work_area:
    def __init__(self, group_id, surface_id, priority, lug_condition, indoor_outdoor_condition, L_limit_of_block,
                 B_limit_of_block, H_limit_of_block, W_limit_of_block, TP_condition, TP_direction, L, B):
        self.group_id = group_id
        self.surface_id = surface_id
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
        self.unit_list = list()

    def add_unavailable_area(self, x, y, L, B):
        self.unavailable_area_x = int(x * 10)
        self.unavailable_area_y = int(y * 10)
        self.unavailable_area_L = int(L * 10)
        self.unavailable_area_B = int(B * 10)
