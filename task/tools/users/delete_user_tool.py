from typing import Any

from task.tools.users.base import BaseUserServiceTool


class DeleteUserTool(BaseUserServiceTool):
    @property
    def name(self) -> str:
        # TODO: Provide tool name as `delete_users`
        return "delete_users"

    @property
    def description(self) -> str:
        # TODO: Provide description of this tool
        return "Tool for deleting a user from the system by their ID."

    @property
    def input_schema(self) -> dict[str, Any]:
        # TODO:
        # Provide tool params Schema. This tool applies user `id` (number) as a parameter and it is required
        return {
            "type": "object",
            "properties": {
                "id": {
                    "type": "number",
                    "description": "The ID of the user to be deleted",
                }
            },
            "required": ["id"],
        }

    def execute(self, arguments: dict[str, Any]) -> str:
        # TODO:
        # 1. Get int `id` from arguments
        # 2. Call user_client delete_user and return its results
        # 3. Optional: You can wrap it with `try-except` and return error as string `f"Error while deleting user by id: {str(e)}"`
        try:
            user_id = arguments.get("id")
            if user_id is None:
                raise ValueError("User ID is required for deletion.")
            deleted_user = self._user_client.delete_user(int(user_id))
            return f"User deleted successfully: {deleted_user}"
        except Exception as e:
            return f"Error while deleting user by id: {str(e)}"
