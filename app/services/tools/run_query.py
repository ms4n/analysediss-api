import pandas as pd
import json


def run_query_tool(df, query):
    try:
        # First, try to execute the query using df.query()
        try:
            result = df.query(query)
            return result.to_json(orient='records')
        except Exception as e:
            # If df.query() fails, try to execute the query as a pandas operation
            result = eval(f"df.{query}")

            # Handle different types of results
            if isinstance(result, pd.DataFrame):
                return result.to_json(orient='records')
            elif isinstance(result, pd.Series):
                return result.to_json()
            elif isinstance(result, str):
                return result
            else:
                return json.dumps(result)
    except Exception as e:
        return f"Error executing query: {str(e)}"
