import pandas as pd
import json


def run_query_tool(df, query):
    try:
        # First, try to execute the query using df.query()
        try:
            result = df.query(query)
        except Exception as e:
            # If df.query() fails, try to execute the query as a pandas operation
            result = eval(f"df.{query}")

        # Convert the result to a JSON-serializable format
        if isinstance(result, pd.DataFrame):
            return result.to_dict(orient='records')
        elif isinstance(result, pd.Series):
            return result.to_dict()
        elif isinstance(result, (pd.Int64Dtype, pd.Int64Index)):
            return int(result)
        elif isinstance(result, (float, int, str, bool)):
            return result
        else:
            return json.loads(json.dumps(result, default=str))

    except Exception as e:
        return f"Error executing query: {str(e)}"
