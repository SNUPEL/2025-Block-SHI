def add_objective_sum_delay(self):
    """
    """
    delay_penalties = []
    for block_key in self.block_keys:
        block = self.block_dict[block_key]
        block_id = f"{block.ship_type}_{block.project_number}_{block.block_number}"
        possible_date = block.PE_index + self.possible_delay_day
        for surface_group_key, work_area in self.work_area_dict.items():
            surface_id = work_area.surface_id_list
            if isinstance(surface_id, list):
                surface_id = tuple(surface_id)
            for rotate in self.rotation_list:
                var_key = (block_id, surface_group_key, surface_id, 'PE', rotate)
                if var_key in self.block_schedule_var_by_id_group_surf_work_rotate_dict:
                    pe_schedule = self.block_schedule_var_by_id_group_surf_work_rotate_dict[var_key]
                    end_time = self.cpmodel.end_of(pe_schedule)
                    delay_expr = self.cpmodel.max(self.cpmodel.diff(end_time, possible_date), 0)
                    delay_penalties.append(delay_expr)
    if delay_penalties:
        total_delay = self.cpmodel.sum(delay_penalties)
    else:
        total_delay = 0

    self.obj_sum_delay = total_delay