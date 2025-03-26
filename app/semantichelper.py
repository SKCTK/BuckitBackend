import asyncio
import os
from functools import reduce
from typing import TYPE_CHECKING

from database import get_db

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion, OpenAIChatPromptExecutionSettings
from semantic_kernel.contents import ChatHistory
from semantic_kernel.contents.chat_message_content import ChatMessageContent
from semantic_kernel.contents.function_call_content import FunctionCallContent
from semantic_kernel.contents.streaming_chat_message_content import StreamingChatMessageContent
from semantic_kernel.contents.utils.author_role import AuthorRole
from semantic_kernel.filters.auto_function_invocation.auto_function_invocation_context import (
    AutoFunctionInvocationContext,
)
from semantic_kernel.filters.filter_types import FilterTypes
from semantic_kernel.functions import KernelArguments

from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
from semantic_kernel.connectors.ai.open_ai import AzureChatPromptExecutionSettings
from rootdialog import BucketPlugin

if TYPE_CHECKING:
    from semantic_kernel.functions import KernelFunction

system_message = """
You are a chat bot. Your name is XXX and...

Sample of a math teacher:

...you have one goal: figure out what people need.
Your full name, should you need to know it, is
Splendid Speckled XXX. You communicate
effectively, but you tend to answer with long
flowery prose. You are also a math wizard,
especially for adding and subtracting.
You also excel at joke telling, where your tone is often sarcastic.
Once you have the answer I am looking for,
you will return a full answer to me as soon as possible.
"""

kernel = Kernel()

chat_completion = AzureChatCompletion(
            deployment_name="deployment_name",
            api_key="api_key",
            base_url="base_url",
    )
kernel.add_service(chat_completion)


execution_settings = AzureChatPromptExecutionSettings()
execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto()


# adding plugins to the kernel
kernel.add_plugin(BucketPlugin(db=get_db),plugin_name="ChatBot")


chat_function = kernel.add_function(
    prompt="{{$chat_history}}{{$user_input}}",
    plugin_name="ChatBot",
    function_name="Chat",
)

history = ChatHistory()

history.add_system_message(system_message)
history.add_user_message("Hi there, who are you?")
history.add_assistant_message("I am XXX, a chat bot. I'm trying to figure out what people need.")

# To control auto function calling you can do it two ways:
# 1. Configure the attribute `auto_invoke_kernel_functions` as False
# 2. Configure the `maximum_auto_invoke_attempts` as 0.
# These can be done directly on the FunctionChoiceBehavior.Auto/Required/None object or via the JSON/yaml config.
execution_settings = AzureChatPromptExecutionSettings()
execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto()


arguments = KernelArguments()


# We will hook up a filter to show which function is being called.
# A filter is a piece of custom code that runs at certain points in the process
# this sample has a filter that is called during Auto Function Invocation
# this filter will be called for each function call in the response.
# You can name the function itself with arbitrary names, but the signature needs to be:
# `context, next`
# You are then free to run code before the call to the next filter or the function itself.
# if you want to terminate the function calling sequence. set context.terminate to True
@kernel.filter(FilterTypes.AUTO_FUNCTION_INVOCATION)
async def auto_function_invocation_filter(context: AutoFunctionInvocationContext, next):
    """A filter that will be called for each function call in the response."""
    print("\nAuto function invocation filter")
    print(f"Function: {context.function.fully_qualified_name}")

    # if we don't call next, it will skip this function, and go to the next one
    await next(context)


def print_tool_calls(message: ChatMessageContent) -> None:
    # A helper method to pretty print the tool calls from the message.
    # This is only triggered if auto invoke tool calls is disabled.
    items = message.items
    formatted_tool_calls = []
    for i, item in enumerate(items, start=1):
         if isinstance(item, FunctionCallContent):
            tool_call_id = item.id
            function_name = item.name
            function_arguments = item.arguments
            
            # Here we check if the function_name matches any of the BucketPlugin functions and format accordingly.
            if function_name == "get_user_buckets":
                formatted_str = (
                    f"Tool Call {i} ID: {tool_call_id}\n"
                    f"Function Name: {function_name}\n"
                    f"Arguments: User ID = {function_arguments.get('user_id')}, "
                    f"Skip = {function_arguments.get('skip', 0)}, "
                    f"Limit = {function_arguments.get('limit', 100)}"
                )
            elif function_name == "create_bucket":
                formatted_str = (
                    f"Tool Call {i} ID: {tool_call_id}\n"
                    f"Function Name: {function_name}\n"
                    f"Arguments: User ID = {function_arguments.get('user_id')}, "
                    f"Name = {function_arguments.get('name')}, "
                    f"Target Amount = {function_arguments.get('target_amount')}, "
                    f"Current Saved Amount = {function_arguments.get('current_saved_amount')}, "
                    f"Priority Score = {function_arguments.get('priority_score')}, "
                    f"Deadline = {function_arguments.get('deadline')}, "
                    f"Status = {function_arguments.get('status', 'active')}"
                )
            elif function_name == "update_bucket":
                formatted_str = (
                    f"Tool Call {i} ID: {tool_call_id}\n"
                    f"Function Name: {function_name}\n"
                    f"Arguments: Bucket ID = {function_arguments.get('bucket_id')}, "
                    f"Update Data = {function_arguments.get('bucket')}"
                )
            elif function_name == "delete_bucket":
                formatted_str = (
                    f"Tool Call {i} ID: {tool_call_id}\n"
                    f"Function Name: {function_name}\n"
                    f"Arguments: Bucket ID = {function_arguments.get('bucket_id')}"
                )
            else:
                # If it's another function, print the raw data
                formatted_str = (
                    f"Tool Call {i} ID: {tool_call_id}\n"
                    f"Function Name: {function_name}\n"
                    f"Arguments: {function_arguments}"
                )
            
            formatted_tool_calls.append(formatted_str)
    
    # Print the formatted tool calls
    print("Tool calls:\n" + "\n\n".join(formatted_tool_calls))

async def handle_streaming(
    kernel: Kernel,
    chat_function: "KernelFunction",
    arguments: KernelArguments,
) -> str | None:
    response = kernel.invoke_stream(
        chat_function,
        return_function_results=False,
        arguments=arguments,
    )

    print("XXX:> ", end="")
    streamed_chunks: list[StreamingChatMessageContent] = []
    result_content: list[StreamingChatMessageContent] = []
    async for message in response:
        if (
            not execution_settings.function_choice_behavior.auto_invoke_kernel_functions
            and isinstance(message[0], StreamingChatMessageContent)
            and message[0].role == AuthorRole.ASSISTANT
        ):
            streamed_chunks.append(message[0])
        elif isinstance(message[0], StreamingChatMessageContent) and message[0].role == AuthorRole.ASSISTANT:
            result_content.append(message[0])
            print(str(message[0]), end="")

    if streamed_chunks:
        streaming_chat_message = reduce(lambda first, second: first + second, streamed_chunks)
        if hasattr(streaming_chat_message, "content"):
            print(streaming_chat_message.content)
        print("Auto tool calls is disabled, printing returned tool calls...")
        print_tool_calls(streaming_chat_message)

    print("\n")
    if result_content:
        return "".join([str(content) for content in result_content])
    return None


async def chat() -> bool:
    try:
        user_input = input("User:> ")
    except KeyboardInterrupt:
        print("\n\nExiting chat...")
        return False
    except EOFError:
        print("\n\nExiting chat...")
        return False

    if user_input == "exit":
        print("\n\nExiting chat...")
        return False
    arguments["user_input"] = user_input
    arguments["chat_history"] = history

    stream = False
    if stream:
        result = await handle_streaming(kernel, chat_function, arguments=arguments)
    else:
        result = await kernel.invoke("ChatBot", arguments=arguments)

        # If tools are used, and auto invoke tool calls is False, the response will be of type
        # ChatMessageContent with information about the tool calls, which need to be sent
        # back to the model to get the final response.
        function_calls = [item for item in result.value[-1].items if isinstance(item, FunctionCallContent)]
        if not execution_settings.function_choice_behavior.auto_invoke_kernel_functions and len(function_calls) > 0:
            print_tool_calls(result.value[0])
            return True

        print(f"XXX:> {result}")

    history.add_user_message(user_input)
    history.add_assistant_message(str(result))
    return True


async def main() -> None:
    chatting = True
    print(
        "Welcome to the chat bot!\
        \n  Type 'exit' to exit.\
        \n  Try..."
    )
    while chatting:
        chatting = await chat()


if __name__ == "__main__":
    asyncio.run(main())

