import asyncio
import os
from dotenv import load_dotenv
import re

from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.ui import Console
from autogen_agentchat.base import TaskResult

from autogen_core.model_context import BufferedChatCompletionContext


load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set.")
from utils.helpers import saveFile


def agent_group_backend():
    model_client = OpenAIChatCompletionClient(model="gpt-4o", api_key=openai_api_key)

    APIDesignerAgent = AssistantAgent(
        name="APIDesignerAgent",
        model_client=model_client,
        tools=[saveFile],
        system_message=(
            "You are an expert FastAPI backend architect. "
            "Given a software requirements document (SRD), generate FastAPI route skeletons for each endpoint, "
            "including OpenAPI-compatible request and response schemas. "
            "Output each logical component in its own file (e.g., routes in routes.py, schemas in schemas.py). "
            "At the start of your response, provide a summary of the file/folder structure you are generating. "
            "For each file, use a clear header like: '### File: routes.py'. "
            "Use saveFile tool to save the files in a 'output/backend' folder"
            "Ensure each route includes try/except blocks with proper HTTP error status handling."
        )
    )

    ModelDeveloperAgent = AssistantAgent(
        name="ModelDeveloperAgent",
        model_client=model_client,
        system_message=(
            "You are a Python data modeling expert. "
            "Given a software requirements document (SRD), generate Pydantic models for all entities, "
            "including field types, constraints, and validation logic. "
            "Use saveFile tool to save the files in a 'output/backend' folder"
            "Place all models in a models.py file, and any shared schemas in schemas.py. "
            "Start your response with a summary of the file/folder structure. "
            "Use headers like: '### File: models.py'."
        )
    )

    BusinessLogicAgent = AssistantAgent(
        name="BusinessLogicAgent",
        model_client=model_client,
        system_message=(
            "You are a backend business logic expert. "
            "Given a software requirements document (SRD), implement Python functions or classes for each business rule described. "
            "Place these in a business_logic.py file. "
            "Use saveFile tool to save the files in a 'output/backend' folder"
            "Start your response with a summary of the file/folder structure. "
            "Use headers like: '### File: business_logic.py'."
        )
    )

    IntegrationAgent = AssistantAgent(
        name="IntegrationAgent",
        model_client=model_client,
        system_message=(
            "You are an API integration specialist. "
            "Given a software requirements document (SRD), generate Python code to integrate with specified third-party APIs. "
            "Include robust retry logic and circuit breaker patterns. "
            "Place integration code in an integration.py file. "
            "Use saveFile tool to save the files in a 'output/backend' folder"
            "Start your response with a summary of the file/folder structure. "
            "Use headers like: '### File: integration.py'."
        )
    )

    DatabaseMigrationAgent = AssistantAgent(
        name="DatabaseMigrationAgent",
        model_client=model_client,
        system_message=(
            "You are a database migration expert. "
            "Given a software requirements document (SRD), generate Alembic migration scripts for all schema changes. "
            "Place each migration in a separate file under alembic/versions/. "
            "Use saveFile tool to save the files in a 'output/backend' folder"
            "Start your response with a summary of the file/folder structure. "
            "Use headers like: '### File: alembic/versions/xxxx_migration_name.py'."
        )
    )

    ErrorHandlingAgent = AssistantAgent(
        name="ErrorHandlingAgent",
        model_client=model_client,
        system_message=(
            "You are an expert in Python error handling and API robustness. "
            "Review the generated backend code to ensure all try/except blocks are present, "
            "Use saveFile tool to save the files in a 'output/backend' folder"
            "and that HTTP error statuses are handled according to best practices. "
            "If you suggest changes, specify which file(s) they belong in using headers like: '### File: routes.py'."
        )
    )

    code_developer = RoundRobinGroupChat(
        participants=[
            APIDesignerAgent,
            ModelDeveloperAgent,
            BusinessLogicAgent,
            IntegrationAgent,
            DatabaseMigrationAgent,
            ErrorHandlingAgent
        ],
        max_turns=3
    )

    return code_developer



async def generate_backend_code(srdDoc : str):
    agent_grp = agent_group_backend()
    task = f"generate code based on the given SRD document {srdDoc}"

    result = await Console(agent_grp.run_stream(task=task))

    return result










# if __name__ == "__main__":
#     asyncio.run(main())

