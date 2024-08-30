import pandas as pd

global_df = None

def load_csv(file_path):
    global global_df
    global_df = pd.read_csv(file_path)
    return global_df

def get_dataframe():
    global global_df
    return global_df
