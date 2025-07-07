def add_constraint_crane_usage(self):

    for crane_keys, crane in self.crane_dict.items():
        for value in crane.unavailable_time_list:
            name, day, time = value[0], value[1], value[2]
            time = int(time * 2)
            self.crane_usage_step += self.cpmodel.pulse((day, day + 1), time)

    for (block_id, surface_group_key, surface_id, work,
         rotate), schedule_var in self.block_schedule_var_by_id_group_surf_work_rotate_dict.items():

        work_area = self.work_area_dict[surface_group_key]

        operation_info = work_area.crane_operation_dict.get(work, (0, []))
        crane_time = int(operation_info[0])

        block_found = None
        for block in self.block_dict.values():
            current_block_id = f"{block.ship_type}_{block.project_number}_{block.block_number}"
            if current_block_id == block_id:
                block_found = block
                break
        if block_found is None:
            continue

        # 중량이 45 초과이고 작업이 'TO' 또는 'PE'인 경우 누적되지 않도록 구현
        if block_found.weight > 45 and work in ['TO', 'PE']:
            continue

        # 크레인 사용량 누적
        self.crane_usage_step += self.cpmodel.pulse(schedule_var, crane_time)

    self.cpmodel.add(self.crane_usage_step <= 2 * self.config['crane_usage_time'])

