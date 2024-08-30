import json
import logging
import os
import pandas as pd
from anthropic import Anthropic
from app.services.tools.analyze_data import analyze_data_tool
from app.services.tools.run_query import run_query_tool


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChatService:
    def __init__(self):
        self.anthropic = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.chat_histories = {}
        self.tools = self.load_tools()
        self.dataframes = {}  # Store dataframes for each session
        self.system_prompt = """
        You are an AI assistant specialized in data analysis. Your primary function is to help users analyze CSV data using pandas queries. You have access to two main tools:

        1. analyze_data_tool: Use this to load a CSV file and get a summary of its contents.
        2. run_query_tool: Use this to execute pandas queries on the loaded data.

        Always use the analyze_data_tool first if no data has been loaded. When the data is loaded, carefully examine the structure and content of the data provided in the tool result. Use this information to formulate appropriate pandas queries.

        **IMPORTANT**
        Always start by explicitly asking the user for the CSV file path if it hasn't been provided yet. This is crucial for initiating the data analysis process.
        **IMPORTANT**

        When formulating pandas operations or queries, use one of these two formats:

        1. For simple queries: Provide a query string suitable for df.query(). Example: 'Sales > 1000 and Region == "North"'
        2. For complex operations: Provide the part that comes after 'df.' in a pandas operation. Example: 'groupby("Date")["Sales"].sum().idxmax()'

        Ensure that your queries reference the correct column names and data types as shown in the sample data. If a user's request is unclear, ask for clarification. Provide concise explanations of your analysis and offer to elaborate if the user requests more details.

        IMPORTANT: Once a CSV file is loaded, you can directly use pandas queries to answer follow-up questions. Do not ask to load the CSV file again for subsequent queries.

        Do not reply with internal workings of the app or mention tools in the replies to the user. Focus on providing clear, data-driven insights based on the available information.
        """

    def load_tools(self):
        tools_dir = os.path.join(os.path.dirname(__file__), 'tools')
        tools = []
        for filename in os.listdir(tools_dir):
            if filename.endswith('.json'):
                with open(os.path.join(tools_dir, filename), 'r') as f:
                    tools.append(json.load(f))
        return tools

    def process_tool_call(self, session_id, tool_name, tool_input):
        if tool_name == "analyze_data_tool":
            logger.info("analyze_data_tool called")
            result = analyze_data_tool(tool_input["file_path"])
            # Store the dataframe for this session
            self.dataframes[session_id] = pd.read_csv(tool_input["file_path"])
            return result
        elif tool_name == "run_query_tool":
            logger.info("run_query_tool called")
            if session_id not in self.dataframes:
                return "Error: No data loaded. Please load a CSV file first."
            df = self.dataframes[session_id]
            return run_query_tool(df, tool_input["query"])
        else:
            raise ValueError(f"Unknown tool: {tool_name}")

    async def process_message(self, session_id: str, user_message: str):
        logging.info(
            f"Processing message for session {session_id}: {user_message}")

        if session_id not in self.chat_histories:
            self.chat_histories[session_id] = []

        messages = self.chat_histories[session_id] + \
            [{"role": "user", "content": user_message}]

        while True:
            response = self.anthropic.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=4096,
                system=self.system_prompt,
                tools=self.tools,
                messages=messages
            )

            logging.info(
                f"Response: Stop Reason: {response.stop_reason}, Content: {response.content}")

            if response.stop_reason != "tool_use":
                break

            tool_use = next(
                block for block in response.content if block.type == "tool_use")
            tool_name = tool_use.name
            tool_input = tool_use.input

            logging.info(
                f"Tool Used: {tool_name}, Tool Input: {json.dumps(tool_input, indent=2)}")

            tool_result = self.process_tool_call(
                session_id, tool_name, tool_input)

            logging.info(f"Tool Result: {json.dumps(tool_result, indent=2)}")

            messages.extend([
                {"role": "assistant", "content": response.content},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_use.id,
                            "content": str(tool_result),
                        }
                    ],
                },
            ])

        final_response = next(
            (block.text for block in response.content if hasattr(block, "text")),
            None,
        )

        logging.info(f"Final Response: {final_response}")

        self.chat_histories[session_id] = messages
        self.chat_histories[session_id].append(
            {"role": "assistant", "content": final_response})

        return final_response

    def get_chat_history(self, session_id: str):
        if session_id not in self.chat_histories:
            raise Exception("Session not found")
        return self.chat_histories[session_id]
