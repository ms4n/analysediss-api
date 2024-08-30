import pandas as pd


def analyze_data_tool(file_path):
    try:
        df = pd.read_csv(file_path)
        return df.head().to_string()
    except Exception as e:
        return f"Error loading CSV: {str(e)}"
