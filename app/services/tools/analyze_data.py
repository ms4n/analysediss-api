import pandas as pd
import json


def analyze_data_tool(file_path):
    try:
        df = pd.read_csv(file_path)
        summary = {
            "columns": df.columns.tolist(),
            "shape": df.shape,
            "dtypes": df.dtypes.astype(str).to_dict(),
            "head": df.head().to_dict(orient='records'),
            "description": df.describe().to_dict()
        }
        return json.dumps(summary)
    except Exception as e:
        return f"Error loading CSV: {str(e)}"
