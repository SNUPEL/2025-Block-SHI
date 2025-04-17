def add_objective_sum_unassinged_block(self):
    """
    미배치 블록의 수를 최소화하는 목적함수 추가
    :param self:
    :return:
    """

    # 미배치 블록 목적함수
    unassigned_blocks = []

    # 각 블록의 STORE 작업 변수가 optional=True이므로
    # 해당 변수가 존재하지 않으면 블록이 미배치된 것으로 간주
    for block_key in self.block_keys:
        block = self.block_dict[block_key]
        block_id = f"{block.ship_type}_{block.project_number}_{block.block_number}"

        # 1 - presence_of는 블록이 배치되지 않으면 1, 배치되면 0을 반환
        unassigned_block = 1 - self.cpmodel.presence_of(self.block_schedule_var_by_id_work_dict[(block_id, 'STORE')])
        unassigned_blocks.append(unassigned_block)
    if unassigned_blocks:
        total_unassigned_blocks = self.cpmodel.sum(unassigned_blocks)
    else:
        total_unassigned_blocks = 0

    self.obj_sum_unassinged_block = total_unassigned_blocks

