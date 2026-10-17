from typing import Any

from task.tools.users.base import BaseUserServiceTool
from task.tools.users.models.user_info import UserCreate


class CreateUserTool(BaseUserServiceTool):
    @property
    def name(self) -> str:
        # TODO: Provide tool name as `add_user`
        return "add_user"

    @property
    def description(self) -> str:
        # TODO: Provide description of this tool
        return "Tool for creating a new user in the system."

    @property
    def input_schema(self) -> dict[str, Any]:
        # TODO: Provide tool params Schema. To do that you can create json schema from UserCreate pydentic model ` UserCreate.model_json_schema()`
        return UserCreate.model_json_schema()

    def execute(self, arguments: dict[str, Any]) -> str:
        # TODO:
        # 1. Validate arguments with `UserCreate.model_validate`
        # 2. Call user_client add user and return its results
        # 3. Optional: You can wrap it with `try-except` and return error as string `f"Error while creating a new user: {str(e)}"`
        try:
            user_create = UserCreate.model_validate(arguments)
            created_user = self._user_client.add_user(user_create)
            return f"User created successfully: {created_user}"
        except Exception as e:
            return f"Error while creating a new user: {str(e)}"
