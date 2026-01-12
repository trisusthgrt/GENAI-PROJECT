import asyncio
import os
from dotenv import load_dotenv
import re

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import SelectorGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.ui import Console
from utils.helpers import saveFile
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set.")

def agent_group_frontend():
    model_client = OpenAIChatCompletionClient(model="gpt-4o", api_key=openai_api_key)

    ComponentDesignerAgent = AssistantAgent(
        name="ComponentDesignerAgent",
        description="An agent that creates Angular component sketches, with lazy loading",
        tools= [saveFile],
        model_client=model_client,
        system_message=(
            """
            You are an Angular component architect.Given a frontend SRD, generate Angular component TypeScript skeletons for all major UI features.
            Create a folder named output/generated_frontend and then create all the files inside the created folder "generated_frontend". Maintain the proper structure and save files.
            Use lazy loading for feature modules. Generate all the codes mentioned in the SRD. 
            You have a tool saveFile use it properly to save files in the directory you generated and maintain a proper folder structure.
            Note: Do not create the files in the root folder structure. Always create the files in the respective folder structures where they belong.
            """

        )
    )

    ServiceDeveloperAgent = AssistantAgent(
        name="ServiceDeveloperAgent",
        description="An agent that provides Angular services with retry, caching logic",
        tools= [saveFile],
        model_client=model_client,
        system_message=(
            """You are an Angular service expert. 
            Create a folder named output/generated_frontend and then create all the files inside the generated_frontend and write the file in that folder
            Given a frontend SRD and component skeletons, generate Angular service code for API calls, including retry and caching logic. 
            You have a tool saveFile use it properly to save files you generate and maintain a proper folder structure.
            """
        )
    )

    UIImplementationAgent = AssistantAgent(
        name="UIImplementationAgent",
        description="An agent that ensure  responsive UI and basic accessibility",
        model_client=model_client,
        tools= [saveFile],
        system_message=(
           """ You are a UI/UX expert. Given a frontend SRD you have to implement a responsive UI design cordinate with ComponentDesignerAgent to create the codes.
            Create a folder named output/generated_frontend and then create all the files inside the generated_frontend and write the file in that folder 
            You have a tool saveFile use it properly to save files you generate and maintain a proper folder structure.
            """
        )
    )

    StateManagementAgent = AssistantAgent(
        name="StateManagementAgent",
        model_client=model_client,
        description="An agent that NgRx store/effects skeletons, optimistic updates",
        tools= [saveFile],
        system_message=(
            "You are an NgRx state management expert. "
            "Given a frontend SRD and component/service code, generate NgRx store/effects skeletons for all stateful features. "
            "Include optimistic update patterns where appropriate. "
            "You have a tool saveFile use it properly to save files you generate and maintain a proper folder structure."
            "Create a folder named output/generated_frontend and then create all the files inside the generated_frontend folder maintain the proper structure and save files."

        )
    )



    # Cross-agent validation/rollback stubs
    ValidatorAgent = AssistantAgent(
        name="ValidatorAgent",
        tools= [saveFile],
        model_client=model_client,
        system_message=(
            "You are a code reviewer. Review the previous agent's output for correctness and alignment with the SRD. "
            "If issues are found, describe them and suggest rollback. "
            "If output is valid, reply with 'VALID'."
            "You have a tool saveFile use it properly to save files you generate and maintain a proper folder structure."
            "Create a folder named output/generated_frontend and then create all the files inside the generated_frontend folder maintain the proper structure and save files."
        )
    )

    selector_prompt = """Select an agent to perform task.

    {roles}

    Current conversation context:
    {history}

    Read the above conversation, then select an agent from {participants} to perform the next task.
    Make sure the planner agent has assigned tasks before other agents start working.
    Only select one agent.
    """

    text_mention_termination = TextMentionTermination("TERMINATE")
    max_messages_termination = MaxMessageTermination(max_messages=25)
    termination = text_mention_termination | max_messages_termination

    # Group chat with validation/rollback stub logic
    code_developer = SelectorGroupChat(
        participants=[
            ComponentDesignerAgent,
            ValidatorAgent,
            ServiceDeveloperAgent,
            UIImplementationAgent,
            StateManagementAgent
        ],
        model_client= model_client,
        selector_prompt=selector_prompt,
        allow_repeated_speaker=True, 
        termination_condition=termination,
    )

    return code_developer



async def generate_frontend_code(srdDoc: str):
    agent_grp = agent_group_frontend()
   
    task = f"generate Angular codes based on the given Frontend SRD document. Implement all the features mentioned: {srdDoc}"
    result = await Console(agent_grp.run_stream(task=task))

