from task._constants import API_KEY, DIAL_URL
from task.client import DialClient
from task.models.conversation import Conversation
from task.models.message import Message
from task.models.role import Role
from task.prompts import SYSTEM_PROMPT
from task.tools.users.create_user_tool import CreateUserTool
from task.tools.users.delete_user_tool import DeleteUserTool
from task.tools.users.get_user_by_id_tool import GetUserByIdTool
from task.tools.users.search_users_tool import SearchUsersTool
from task.tools.users.update_user_tool import UpdateUserTool
from task.tools.users.user_client import UserClient
from task.tools.web_search import WebSearchTool


def main():
    # TODO:
    # 1. Create UserClient
    # 2. Create DialClient with all tools (WebSearchTool, GetUserByIdTool, SearchUsersTool, CreateUserTool, UpdateUserTool, DeleteUserTool)
    # 3. Create Conversation and add there first System message with SYSTEM_PROMPT (you need to write it in task.prompts#SYSTEM_PROMPT)
    # 4. Run infinite loop and in loop and:
    #    - get user input from terminal (`input("> ").strip()`)
    #    - Add User message to Conversation
    #    - Call DialClient with conversation history
    #    - Add Assistant message to Conversation and print its content
    user_client = UserClient()

    dial_client = DialClient(
        endpoint=DIAL_URL,
        deployment_name="gpt-4o",
        api_key=API_KEY,
        tools=[
            WebSearchTool(api_key=API_KEY, endpoint=DIAL_URL),
            GetUserByIdTool(user_client=user_client),
            SearchUsersTool(user_client=user_client),
            CreateUserTool(user_client=user_client),
            UpdateUserTool(user_client=user_client),
            DeleteUserTool(user_client=user_client),
        ],
    )

    message_history = [
        Message(role=Role.SYSTEM, content=SYSTEM_PROMPT),
    ]

    conversation = Conversation(messages=message_history)

    while True:
        user_input = input("> ").strip()
        if not user_input:
            continue

        conversation.add_message(Message(role=Role.USER, content=user_input))

        response_message = dial_client.get_completion(
            messages=conversation.get_messages(), print_request=True
        )
        conversation.add_message(
            Message(role=Role.AI, content=response_message.content)
        )

        print(f"Assistant: {response_message.content}")


if __name__ == "__main__":
    main()

# TODO:
# Request sample:
# Add Andrej Karpathy as a new user
