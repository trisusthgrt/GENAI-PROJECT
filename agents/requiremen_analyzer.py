import asyncio
import os
from dotenv import load_dotenv

from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.ui import Console

import logging

from autogen_agentchat import EVENT_LOGGER_NAME, TRACE_LOGGER_NAME

logging.basicConfig(level=logging.WARNING)

trace_logger = logging.getLogger(TRACE_LOGGER_NAME)
trace_logger.addHandler(logging.StreamHandler())
trace_logger.setLevel(logging.DEBUG)

event_logger = logging.getLogger(EVENT_LOGGER_NAME)
event_logger.addHandler(logging.StreamHandler())
event_logger.setLevel(logging.DEBUG)

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set.")

def setup_agents_and_group():
    model_client = OpenAIChatCompletionClient(model="gpt-4o", api_key=openai_api_key)

    project_manager = UserProxyAgent(
        name="Project_Manager",
        description="You are the project manager and conversation orchestrator. You initiate the task and ensure all requirements are fulfilled.",
        input_func=input,
    )

    frontend_writer = AssistantAgent(
        name="Frontend_SRD_Writer",
        model_client=model_client,
        system_message="""You are an expert Frontend Architect preferably Angular.
        Your task is to take an SRS document and create a detailed Frontend SRD.
        Focus on user interface, user experience, client-side logic, and API calls from the frontend perspective.
        Structure the document clearly with sections like 'UI Requirements', 'User Flows', 'Frontend Technologies', and 'API Interactions'.
        Do not include any backend-specific details.
        """
    )

    backend_writer = AssistantAgent(
        name="Backend_SRD_Writer",
        model_client=model_client,
        system_message="""You are an expert Backend Architect preferably FastApi.
        Your task is to take an SRS document and create a detailed Backend SRD.
        Focus on business logic, database design, API definitions, security, and scalability.
        Structure the document clearly with sections like 'API Endpoints', 'Database Schema', 'Business Logic', and 'Security Requirements'.
        Do not include any frontend-specific details.
        """
    )

    reviewer = AssistantAgent(
        name="Reviewer_Agent",
        model_client=model_client,
        system_message="""You are a technical reviewer. Your role is to analyze both the Frontend SRD and Backend SRD documents.
        Your main goal is to ensure consistency between the two documents and that all original SRS requirements have been covered.
        Point out any discrepancies or missing requirements. If everything is consistent and the documents are ready, state 'TERMINATE'.
        """
    )

    group_chat = RoundRobinGroupChat(
        participants=[frontend_writer, backend_writer, reviewer],
        max_turns=2
    )

    return frontend_writer, backend_writer, group_chat

async def generate_srd_docs(task: str):
    frontend_writer, backend_writer, group_chat = setup_agents_and_group()
    task = "generate frontend and backend Software Requirement Design (SRD) from the following SRS Document: " + task

    trace_logger.info("Starting group chat with task: %s", task)
    result = await group_chat.run(task=task)
    trace_logger.info("Group chat completed.")

    frontend_srd_text = ""
    backend_srd_text = ""
    for msg in result.messages:
        if getattr(msg, "source", None) == "Frontend_SRD_Writer":
            frontend_srd_text = msg.content
            event_logger.debug("Frontend SRD generated.")
        elif getattr(msg, "source", None) == "Backend_SRD_Writer":
            backend_srd_text = msg.content
            event_logger.debug("Backend SRD generated.")

    return frontend_srd_text, backend_srd_text

def generate_srd_docs_sync(task: str):
    frontend_srd_text, backend_srd_text = asyncio.run(generate_srd_docs(task))
    return frontend_srd_text, backend_srd_text
