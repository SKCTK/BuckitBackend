
import asyncio
from typing import Annotated,List

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from semantic_kernel.functions import kernel_function
from model.models import Bucket  
from azure.identity.aio import DefaultAzureCredential
from semantic_kernel.contents import AuthorRole
from semantic_kernel.functions import kernel_function
from azure import AzureAIAgent, AzureAIAgentSettings


class BucketPlugin:
    """Semantic Kernel Plugin for interacting with user buckets."""

    def __init__(self, db: Session):
        self.db = db

    @kernel_function(description="Get all buckets for a specific user with pagination.")
    def get_user_buckets(
        self, user_id: Annotated[int, "User ID to retrieve buckets for."],
        skip: Annotated[int, "Number of records to skip."] = 0,
        limit: Annotated[int, "Max number of records to return."] = 100
    ) -> Annotated[List[dict], "List of user buckets."]:
        """Fetch all buckets for a user, returning a list of dictionaries."""
        user_buckets = self.db.query(Bucket.Bucket).filter(Bucket.Bucket.user_id == user_id)
        user_buckets = user_buckets.order_by(Bucket.Bucket.id.desc()).offset(skip).limit(limit).all()

        return [
            {
                "id": bucket.id,
                "name": bucket.name,
                "target_amount": bucket.target_amount,
                "current_saved_amount": bucket.current_saved_amount,
                "priority_score": bucket.priority_score,
                "deadline": bucket.deadline.isoformat() if bucket.deadline else None,
                "status": bucket.status,
            }
            for bucket in user_buckets
        ]

    @kernel_function(description="Get a specific bucket by ID.")
    def get_bucket(
        self, bucket_id: Annotated[int, "ID of the bucket to retrieve."]
    ) -> Annotated[dict, "Bucket details."]:
        """Fetch a bucket by ID and return its details as a dictionary."""
        bucket = self.db.query(Bucket.Bucket).filter(Bucket.Bucket.id == bucket_id).first()
        if not bucket:
            return {"message": "Bucket not found."}  # Avoiding raise
        
        return {
            "id": bucket.id,
            "name": bucket.name,
            "target_amount": bucket.target_amount,
            "current_saved_amount": bucket.current_saved_amount,
            "priority_score": bucket.priority_score,
            "deadline": bucket.deadline.isoformat() if bucket.deadline else None,
            "status": bucket.status,
        }

# Simulate a conversation with the agent
USER_INPUTS = [
    "Hello",
    "What is the special soup?",
    "How much does that cost?",
    "Thank you",
]


async def main() -> None:
    ai_agent_settings = AzureAIAgentSettings.create()

    async with (
        DefaultAzureCredential() as creds,
        AzureAIAgent.create_client(credential=creds) as client,
    ):
        # 1. Create an agent on the Azure AI agent service
        agent_definition = await client.agents.create_agent(
            model=ai_agent_settings.model_deployment_name,
            name="Host",
            instructions="Answer questions about the menu.",
        )

        # 2. Create a Semantic Kernel agent for the Azure AI agent
        agent = AzureAIAgent(
            client=client,
            definition=agent_definition,
            # Optionally configure polling options
            # polling_options=RunPollingOptions(run_polling_interval=timedelta(seconds=1)),
        )

        # 3. Add a plugin to the agent via the kernel
        agent.kernel.add_plugin(BucketPlugin(), plugin_name="menu")

        # 4. Create a new thread on the Azure AI agent service
        thread = await client.agents.create_thread()

        try:
            for user_input in USER_INPUTS:
                # 5. Add the user input as a chat message
                await agent.add_chat_message(thread_id=thread.id, message=user_input)
                print(f"# User: {user_input}")
                # 6. Invoke the agent for the specified thread for response
                async for content in agent.invoke(
                    thread_id=thread.id,
                    temperature=0.2,  # override the agent-level temperature setting with a run-time value
                ):
                    if content.role != AuthorRole.TOOL:
                        print(f"# Agent: {content.content}")
        finally:
            # 7. Cleanup: Delete the thread and agent
            await client.agents.delete_thread(thread.id)
            await client.agents.delete_agent(agent.id)

        """
        Sample Output:
        # User: Hello
        # Agent: Hello! How can I assist you today?
        # ...
        """


if __name__ == "__main__":
    asyncio.run(main())
