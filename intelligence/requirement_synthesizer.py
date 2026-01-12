# Advanced Requirement Analysis and Technical Specification Synthesis
"""
Intelligent requirement processing system that transforms high-level software
requirements into detailed technical specifications using advanced AI agents.
"""

import asyncio
import os
import logging
from dotenv import load_dotenv
from typing import Tuple, Dict, Any

from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.ui import Console
from autogen_agentchat import EVENT_LOGGER_NAME, TRACE_LOGGER_NAME

# Configure advanced logging for AI agent interactions
logging.basicConfig(level=logging.WARNING)

trace_logger = logging.getLogger(TRACE_LOGGER_NAME)
trace_logger.addHandler(logging.StreamHandler())
trace_logger.setLevel(logging.DEBUG)

event_logger = logging.getLogger(EVENT_LOGGER_NAME)
event_logger.addHandler(logging.StreamHandler())
event_logger.setLevel(logging.DEBUG)

# Load environment configuration
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable must be configured for AI agent operation.")

class RequirementSynthesizer:
    """
    Advanced AI-powered requirement analysis and specification generation system.
    Orchestrates multiple specialized agents to transform SRS into detailed technical documents.
    """
    
    @classmethod
    def initialize_agent_ecosystem(cls):
        """
        Initialize and configure the multi-agent system for requirement processing.
        Creates specialized agents with distinct expertise domains.
        """
        # Configure AI model client with optimal settings
        model_client = OpenAIChatCompletionClient(
            model="gpt-4o", 
            api_key=openai_api_key,
            temperature=0.7,
            max_tokens=4000
        )

        # Project management and orchestration agent
        project_orchestrator = UserProxyAgent(
            name="Technical_Project_Manager",
            description="Strategic project orchestrator responsible for coordinating requirement analysis and ensuring comprehensive coverage.",
            input_func=input,
        )

        # Frontend architecture specialist
        frontend_specification_architect = AssistantAgent(
            name="Frontend_Architecture_Specialist",
            model_client=model_client,
            system_message="""You are an elite Frontend Architecture Specialist with deep expertise in modern web development.
            Your mission is to analyze Software Requirements Specifications and create comprehensive Frontend Technical Design Documents.
            
            Focus Areas:
            - User Interface Architecture and Component Design
            - User Experience Flow Optimization
            - Client-Side State Management Strategies
            - Frontend API Integration Patterns
            - Responsive Design and Accessibility Standards
            - Modern Frontend Technology Stack Selection
            
            Document Structure Requirements:
            1. Executive Summary of Frontend Architecture
            2. User Interface Component Hierarchy
            3. User Experience Journey Mapping
            4. Frontend Technology Stack Specifications
            5. Client-Side API Integration Design
            6. Performance Optimization Strategies
            7. Security and Authentication Patterns
            
            Exclude all backend-specific implementation details. Focus exclusively on frontend concerns.
            """
        )

        # Backend architecture specialist
        backend_specification_architect = AssistantAgent(
            name="Backend_Architecture_Specialist",
            model_client=model_client,
            system_message="""You are a senior Backend Architecture Specialist with extensive expertise in scalable system design.
            Your responsibility is to transform Software Requirements into detailed Backend Technical Design Documents.
            
            Core Competencies:
            - Distributed System Architecture Design
            - RESTful API Design and Documentation
            - Database Schema Architecture and Optimization
            - Business Logic Implementation Strategies
            - Security and Authentication Architecture
            - Scalability and Performance Engineering
            - Integration and Microservices Design
            
            Document Structure Requirements:
            1. Executive Summary of Backend Architecture
            2. API Endpoint Specifications and Documentation
            3. Database Schema Design and Relationships
            4. Business Logic Implementation Framework
            5. Security Architecture and Authentication Systems
            6. Performance and Scalability Considerations
            7. Third-Party Integration Specifications
            
            Focus exclusively on server-side architecture. Avoid frontend-specific details.
            """
        )

        # Technical review and quality assurance specialist
        technical_reviewer = AssistantAgent(
            name="Technical_Quality_Analyst",
            model_client=model_client,
            system_message="""You are a Technical Quality Analyst specializing in software architecture review and validation.
            Your role is to ensure consistency, completeness, and technical excellence across all specification documents.
            
            Review Responsibilities:
            - Cross-reference Frontend and Backend specifications for consistency
            - Validate that all original SRS requirements are addressed
            - Identify potential integration challenges between frontend and backend
            - Ensure technical feasibility and best practice compliance
            - Verify comprehensive coverage of functional and non-functional requirements
            
            Completion Criteria:
            - All SRS requirements are mapped to technical specifications
            - Frontend and Backend designs are architecturally compatible
            - No technical inconsistencies or gaps identified
            - Documents are ready for development team implementation
            
            Upon successful validation, respond with 'TECHNICAL_REVIEW_COMPLETE' to signal completion.
            """
        )

        # Configure collaborative agent ecosystem
        specification_generation_team = RoundRobinGroupChat(
            participants=[
                frontend_specification_architect,
                backend_specification_architect,
                technical_reviewer
            ],
            max_turns=3  # Optimized for thorough but efficient processing
        )

        return (frontend_specification_architect, backend_specification_architect, specification_generation_team)

    @classmethod
    async def process_requirements(cls, software_requirements: str) -> Tuple[str, str]:
        """
        Primary interface for transforming software requirements into technical specifications.
        
        Args:
            software_requirements: Raw SRS document content
            
        Returns:
            Tuple containing (frontend_specification, backend_specification)
        """
        frontend_architect, backend_architect, agent_team = cls.initialize_agent_ecosystem()
        
        # Construct comprehensive processing task
        analysis_task = (
            "Transform the following Software Requirements Specification into comprehensive "
            "Frontend and Backend Technical Design Documents. Ensure complete coverage of "
            "all functional and non-functional requirements with detailed technical specifications: "
            f"\n\n{software_requirements}"
        )

        trace_logger.info("Initiating multi-agent requirement analysis with task: %s", analysis_task)
        
        # Execute collaborative requirement processing
        analysis_result = await agent_team.run(task=analysis_task)
        
        trace_logger.info("Multi-agent requirement analysis completed successfully.")

        # Extract specialized specifications from agent responses
        frontend_technical_spec = ""
        backend_technical_spec = ""
        
        for message in analysis_result.messages:
            message_source = getattr(message, "source", None)
            
            if message_source == "Frontend_Architecture_Specialist":
                frontend_technical_spec = message.content
                event_logger.debug("Frontend technical specification generated successfully.")
                
            elif message_source == "Backend_Architecture_Specialist":
                backend_technical_spec = message.content
                event_logger.debug("Backend technical specification generated successfully.")

        return frontend_technical_spec, backend_technical_spec

    @classmethod
    def process_requirements_synchronous(cls, software_requirements: str) -> Tuple[str, str]:
        """
        Synchronous interface for requirement processing when async execution is not available.
        
        Args:
            software_requirements: Raw SRS document content
            
        Returns:
            Tuple containing (frontend_specification, backend_specification)
        """
        frontend_spec, backend_spec = asyncio.run(cls.process_requirements(software_requirements))
        return frontend_spec, backend_spec

# Legacy compatibility functions for existing integrations
async def generate_srd_docs(requirements_content: str) -> Tuple[str, str]:
    """Legacy compatibility wrapper for requirement processing."""
    return await RequirementSynthesizer.process_requirements(requirements_content)

def generate_srd_docs_sync(requirements_content: str) -> Tuple[str, str]:
    """Legacy synchronous compatibility wrapper."""
    return RequirementSynthesizer.process_requirements_synchronous(requirements_content)
