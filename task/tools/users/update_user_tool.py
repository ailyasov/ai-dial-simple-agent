from typing import Any

from task.tools.users.base import BaseUserServiceTool
from task.tools.users.models.user_info import UserUpdate


class UpdateUserTool(BaseUserServiceTool):
    @property
    def name(self) -> str:
        # TODO: Provide tool name as `update_user`
        return "update_user"

    @property
    def description(self) -> str:
        # TODO: Provide description of this tool
        return "Tool for updating an existing user's information in the system."

    @property
    def input_schema(self) -> dict[str, Any]:
        # TODO:
        # Provide tool params Schema:
        # - id: number, required, User ID that should be updated.
        # - new_info: UserUpdate.model_json_schema()
        return {
            "type": "object",
            "properties": {
                "id": {
                    "type": "number",
                    "description": "The ID of the user to be updated",
                },
                "new_info": UserUpdate.model_json_schema(),
            },
            "required": ["id", "new_info"],
        }

    def execute(self, arguments: dict[str, Any]) -> str:
        # TODO:
        # 1. Get user `id` from `arguments`
        # 2. Get `new_info` from `arguments` and create `UserUpdate` via pydentic `UserUpdate.model_validate`
        # 3. Call user_client update_user and return its results
        # 4. Optional: You can wrap it with `try-except` and return error as string `f"Error while creating a new user: {str(e)}"`
        return self._user_client.update_user(
            user_id=arguments.get("id"),
            user_update_model=UserUpdate.model_validate(arguments.get("new_info")),
        )
