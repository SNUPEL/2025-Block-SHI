import numpy as np


class Work_area:
    def __init__(self, group_id, priority, lug_condition, L_limit, B_limit, H_limit, W_limit, TP_condition):
        self.group_id = group_id
        self.priority = priority
        self.lug_condition = lug_condition
        self.L_limit = L_limit
        self.B_limit = B_limit
        self.H_limit = H_limit
        self.W_limit = W_limit
        self.TP_condition = TP_condition


