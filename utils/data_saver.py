import os 
from datetime import datetime 
import pandas as pd

class DataSaver:
    def __init__(self, max_rows=3000, data_dir='datasets/dummy_data/', signal_type='non-arc'):
        self.row_count = 0
        self.max_rows = max_rows
        self.temp_filename = "temp.csv"
        self.def_dir = 'datasets/dummy_data/'
        self.buffer = []
        self.data_dir = data_dir
        self.signal_type = signal_type
        print(data_dir)

    def get_filename(self):
        datetime_obj = datetime.now()
        formatted_datetime = datetime_obj.strftime("%Y-%m-%d_%H-%M-%S")
        return formatted_datetime + f"_{self.signal_type}.csv"
    
    def save_data(self, data_collection):
        self.buffer.extend(data_collection)
        self.row_count += len(data_collection)
        filename = None
        if self.row_count >= self.max_rows:
            filename = self.get_filename()

            if os.path.exists(self.data_dir) and os.path.isdir(self.data_dir):
                save_dir = os.path.join(self.data_dir, filename)
            else:
                save_dir = self.def_dir + filename
            # save_dir = self.data_dir + filename
            pd.DataFrame(self.buffer).to_csv(save_dir, index=False, header=False, sep=' ')
            self.buffer = []
            self.row_count = 0

            print(save_dir)
        return filename, self.def_dir
