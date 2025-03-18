from config import *
from CPmodel import *

if __name__ == '__main__':
    start_time = time.time()

    config = create_config()
    model = CPmodel(config)
    model.get_data()
    model.preprocess_data()
