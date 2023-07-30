import pickle
import os

def save_pickle(file_name, data):
    with open(file_name, 'wb') as handle:
        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)

def fetch_pickle(file_name):
    if not os.path.exists(file_name):
        raise FileNotFoundError(f"There is no experiment run for dataset")
    with open(file_name, 'rb') as handle:
        return pickle.load(handle)
