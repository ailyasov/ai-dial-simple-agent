import re
from typing import Any

import requests

from task.tools.base import BaseTool


class WebSearchTool(BaseTool):
    def __init__(self, api_key: str, endpoint: str):
        self.__api_key = api_key
        self.__endpoint = (
            f"{endpoint}/openai/deployments/gemini-2.5-pro/chat/completions"
        )

    # https://dialx.ai/dial_api#operation/sendChatCompletionRequest (-> tools -> function)
    # Sample of tool config:
    # {
    #     "type": "function",
    #     "function": {
    #         "name": "web_search_tool",
    #         "description": "Tool for WEB searching.",
    #         "parameters": {
    #             "type": "object",
    #             "properties": {
    #                 "request": {
    #                     "type": "string",
    #                     "description": "The search query or question to search for on the web"
    #                 }
    #             },
    #             "required": [
    #                 "request"
    #             ]
    #         }
    #     }
    # }

    @property
    def name(self) -> str:
        # TODO: Provide tool name as `web_search_tool`
        return "web_search_tool"

    @property
    def description(self) -> str:
        # TODO: Provide description of this tool
        return "Tool for WEB searching."

    @property
    def input_schema(self) -> dict[str, Any]:
        # TODO: Provide tool params Schema (it applies `request` string to search by)
        return {
            "type": "object",
            "properties": {
                "request": {
                    "type": "string",
                    "description": "The search query or question to search for on the web",
                }
            },
            "required": ["request"],
        }

    def execute(self, arguments: dict[str, Any]) -> str:
        # TODO:
        # 1. Create `headers` dict: "api-key": self.__api_key, "Content-Type": "application/json"
        # 2. Create `request_data` dict with:
        #    - "messages": [{"role": "user", "content": str(arguments["request"])}]
        #    - "tools": [{"type": "static_function", "static_function": {"name": "google_search", "description": "Grounding with Google Search","configuration": {}}}]
        # 3. Make POST call with `requests` lib: `url=self.__endpoint, headers=headers, json=request_dat`
        # 4. Check if response status is 200 and if yes then return message content, otherwise return `f"Error: {response.status_code} {response.text}"`
        headers = {"api-key": self.__api_key, "Content-Type": "application/json"}
        request_data = {
            "messages": [{"role": "user", "content": str(arguments["request"])}],
            "tools": [
                {
                    "type": "static_function",
                    "static_function": {
                        "name": "google_search",
                        "description": "Grounding with Google Search",
                        "configuration": {},
                    },
                }
            ],
        }

        response = requests.post(
            url=self.__endpoint, headers=headers, json=request_data, timeout=30
        )
        if response.status_code == 200:
            response_json = response.json()
            if "choices" in response_json and len(response_json["choices"]) > 0:
                return response_json["choices"][0]["message"]["content"]
            else:
                return "Error: No choices found in the response."
        else:
            return f"Error: {response.status_code} {response.text}"
