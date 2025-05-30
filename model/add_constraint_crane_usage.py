def add_constraint_crane_usage(self):

    crane_usage = self.cpmodel.step_at(0, 0)

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
        crane_usage += self.cpmodel.pulse(schedule_var, crane_time)

    # 크레인 일별 크레인 가용 시간(시간 * 2)
    self.cpmodel.add(crane_usage <= 2 * self.config['crane_usage_time'])
