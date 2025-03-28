
import asyncio
from typing import Annotated, List

from semantic_kernel.agents import AzureAssistantAgent
from semantic_kernel.functions import kernel_function
from app.model.schemas import BucketBase


# Define a sample plugin for the sample
class BucketPlugin:

    """Semantic Kernel Plugin for interacting with user buckets."""
    @kernel_function(description="Get all buckets for a specific user with pagination.")
    def get_user_buckets(
        self, user_id: Annotated[int, "User ID to retrieve buckets for."],
        skip: Annotated[int, "Number of records to skip."] = 0,
        limit: Annotated[int, "Max number of records to return."] = 100
    ) -> Annotated[List[dict], "List of user buckets."]:
        """Fetch all buckets for a user, returning a list of dictionaries."""
        user_buckets = self.db.query(BucketBase.Bucket).filter(BucketBase.user_id == user_id)
        user_buckets = user_buckets.order_by(BucketBase.id.desc()).offset(skip).limit(limit).all()

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
        bucket = self.db.query(BucketBase).filter(BucketBase.id == bucket_id).first()
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
]


async def main():
    # 1. Create the client using Azure OpenAI resources and configuration
    client, model = AzureAssistantAgent.setup_resources()

    # 2. Create the assistant on the Azure OpenAI service
    definition = await client.beta.assistants.create(
        model=model,
        instructions="Answer questions about ...",
        name="Host",
    )

    # 3. Create a Semantic Kernel agent for the Azure OpenAI assistant
    agent = AzureAssistantAgent(
        client=client,
        definition=definition,
        plugins=[BucketPlugin()],  # The plugins can be passed in as a list to the constructor
    )
    # Note: plugins can also be configured on the Kernel and passed in as a parameter to the OpenAIAssistantAgent

    # 4. Create a new thread on the Azure OpenAI assistant service
    thread = await agent.client.beta.threads.create()

    try:
        for user_input in USER_INPUTS:
            # 5. Add the user input to the chat thread
            await agent.add_chat_message(
                thread_id=thread.id,
                message=user_input,
            )
            print(f"# User: '{user_input}'")
            # 6. Invoke the agent for the current thread and print the response
            async for content in agent.invoke(thread_id=thread.id):
                print(f"# Agent: {content.content}")
    finally:
        # 7. Clean up the resources
        await agent.client.beta.threads.delete(thread.id)
        await agent.client.beta.assistants.delete(assistant_id=agent.id)

    """
    You should see output similar to the following:

    # User: 'Hello'
    # Agent: Hello! How can I assist you today?
    # User: 
    #...
    # Agent: 
    # User: 'Thank you'
    # Agent: You're welcome! If you have any more questions or need further assistance, feel free to ask. 
        Enjoy your day!
     """


if __name__ == "__main__":
    asyncio.run(main())





