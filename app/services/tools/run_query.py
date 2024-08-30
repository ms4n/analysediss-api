import pandas as pd


def run_query_tool(df, query):
    try:
        # First, try to execute the query using df.query()
        try:
            result = df.query(query)
            return result
        except Exception as e:
            # If df.query() fails, try to execute the query as a pandas operation
            result = eval(f"df.{query}")
            return result
    except Exception as e:
        return f"Error executing query: {str(e)}"
