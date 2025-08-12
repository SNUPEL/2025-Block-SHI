from config import *
from CPmodel import *

if __name__ == '__main__':
    from postprocessing.visualize import ScheduleChecker
    start_time = time.time()

    config = create_config()
    model = CPmodel(config)
    model.get_data()
    model.preprocess_data()
    model.run_model()



    schedule_path = config['folderpath'] + "/block_allocation_result.xlsx"
    block_path = config['data_file_path']

    checker = ScheduleChecker(schedule_path, block_path,
                              # save_path = "../data/",
                              save_path = config['folderpath']+'/',
                              save_gif=True)