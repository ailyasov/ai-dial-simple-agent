import json
from typing import Any

import requests

from task.models.message import Message
from task.models.role import Role
from task.tools.base import BaseTool


class DialClient:
    def __init__(
        self,
        endpoint: str,
        deployment_name: str,
        api_key: str,
        tools: list[BaseTool] | None = None,
    ):
        # TODO:
        # 1. If not api_key then raise error
        # 2. Add `self._endpoint` with formatted `endpoint` with model (model=deployment_name):
        #   - f"{endpoint}/openai/deployments/{deployment_name}/chat/completions"
        # 3. Add `self._api_key`
        # 4. Prepare tools dict where key will be tool name and value will
        # 5. Prepare tools list with tool schemas
        # 6. Optional: print endpoint and tools schemas
        self._endpoint = (
            endpoint + f"/openai/deployments/{deployment_name}/chat/completions"
        )
        if not api_key:
            raise ValueError("API key is required")
        self._api_key = api_key
        self._tools_dict = {tool.name: tool for tool in tools} if tools else {}
        self._tools = [tool.schema for tool in tools] if tools else []

    def get_completion(
        self, messages: list[Message], print_request: bool = True
    ) -> Message:
        # TODO:
        # 1. create `headers` dict with:
        #   - "api-key": self._api_key
        #   - "Content-Type": "application/json"
        # 2. create `request_data` dict with:
        #   - "messages": [msg.to_dict() for msg in messages]
        #   - "tools": self._tools
        # 3. Optional: print request (message history)
        # 4. Make POST request (requests) with:
        #   - url=self._endpoint
        #   - headers=headers
        #   - json=request_data
        # 5. If response status code is 200:
        #   - get response as json
        #   - get "choices" from response json
        #   - get first choice
        #   - Optional: print choice
        #   - Get `message` from `choice` and assign to `message_data` variable
        #   - Get `content` from `message` and assign to `content` variable
        #   - Get `tool_calls` from `message` and assign to `tool_calls` variable
        #   - Create `ai_response` Message (with AI role, `content` and `tool_calls`)
        #   - If `choice` `finish_reason` is `tool_calls`:
        #       Yes:
        #           - append `ai_response` to `messages`
        #           - call `_process_tool_calls` with `tool_calls` and assign result to `tool_messages` variable
        #           - add `tool_messages` to `messages` (use `extend` method)
        #           - make recursive call (return `get_completion` with `messages` and `print_request`)
        #       No: return `ai_response` (final assistant response)
        # Otherwise raise exception
        headers = {"api-key": self._api_key, "Content-Type": "application/json"}

        request_data = {
            "messages": [msg.to_dict() for msg in messages],
            "tools": self._tools,
        }

        if print_request:
            print(self._endpoint)
            print(
                "REQUEST:",
                json.dumps({"messages": [msg.to_dict() for msg in messages]}, indent=2),
            )

        response = requests.post(
            url=self._endpoint, headers=headers, json=request_data, timeout=30
        )
        if response.status_code != 200:
            raise Exception(f"HTTP {response.status_code}: {response.text}")
        data = response.json()
        choices = data.get("choices")
        if not choices:
            raise Exception("No choices in response found")
        message = choices[0].get("message")
        if not message:
            raise Exception("No message in response found")
        content = message.get("content", "")

        tool_calls = message.get("tool_calls", [])
        ai_response = Message(role=Role.AI, content=content, tool_calls=tool_calls)
        if choices[0].get("finish_reason") == "tool_calls":
            messages.append(ai_response)
            tool_messages = self._process_tool_calls(tool_calls)
            messages.extend(tool_messages)
            return self.get_completion(messages, print_request)

        return ai_response

    def _process_tool_calls(self, tool_calls: list[dict[str, Any]]) -> list[Message]:
        """Process tool calls and add results to messages."""
        tool_messages = []
        for tool_call in tool_calls:
            # TODO:
            # 1. Get `id` from `tool_call` and assign to `tool_call_id` variable
            # 2. Get `function` from `tool_call` and assign to `function` variable
            # 3. Get `name` from `function` and assign to `function_name` variable
            # 4. Get `arguments` from `function` as json (json.loads) and assign to `arguments` variable
            # 5. Call `_call_tool` with `function_name` and `arguments`, and assign to `tool_execution_result` variable
            # 6. Append to `tool_messages` Message with:
            #       - role=Role.TOOL
            #       - name=function_name
            #       - tool_call_id=tool_call_id
            #       - content=tool_execution_result
            # 7. print(f"FUNCTION '{function_name}'\n{tool_execution_result}\n{'-'*50}")
            # 8. Return `tool_messages`
            # -----
            # FYI: It is important to provide `tool_call_id` in TOOL Message. By `tool_call_id` LLM make a  relation
            #      between Assistant message `tool_calls[i][id]` and message in history.
            #      In case if no Tool message presented in history (no message at all or with different tool_call_id),
            #      then LLM with answer with Error (that not find tool message with specified id).
            tool_call_id = tool_call.get("id")
            error_message = []
            if not tool_call_id:
                error_message.append("Tool call ID is missing in the tool call data")
            function = tool_call.get("function", {})
            if not function:
                error_message.append("Function data is missing in the tool call data")
            function_name = function.get("name")
            if not function_name:
                error_message.append("Function name is missing in the tool call data")
            try:
                raw = function.get("arguments")
                arguments = json.loads(raw) if raw is not None else {}
                if not isinstance(arguments, dict):
                    arguments = {}
            except json.JSONDecodeError as e:
                error_message.append(f"Error decoding arguments JSON: {e!s}")
            if error_message:
                tool_execution_result = " | ".join(error_message)
            else:
                tool_execution_result = self._call_tool(function_name, arguments)
                MAX_TOOL_CHARS = 20000  # about 5K tokens, far under the 128K window
                if len(tool_execution_result) > MAX_TOOL_CHARS:
                    tool_execution_result = (
                        tool_execution_result[:MAX_TOOL_CHARS]
                        + "\n... [result truncated]"
                    )
            tool_messages.append(
                Message(
                    role=Role.TOOL,
                    name=function_name,
                    tool_call_id=tool_call_id,
                    content=tool_execution_result,
                )
            )
            print(f"FUNCTION '{function_name}'\n{tool_execution_result}\n{'-' * 50}")

        return tool_messages

    def _call_tool(self, function_name: str, arguments: dict[str, Any]) -> str:
        # TODO:
        # Get tool from `_tools_dict`, id present then return executed result, otherwise return `f"Unknown function: {function_name}"`
        tool = self._tools_dict.get(function_name)
        if tool:
            try:
                return tool.execute(arguments)
            except Exception as e:
                return f"Error executing tool '{function_name}': {e}"

        return f"Unknown function: {function_name}"
