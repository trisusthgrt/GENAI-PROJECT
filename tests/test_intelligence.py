# Intelligence Module Tests
"""
Comprehensive test suite for AI intelligence modules including requirement synthesis,
backend architecture generation, and frontend design generation.
"""

import pytest
import asyncio
from unittest.mock import patch, Mock, AsyncMock, MagicMock


class TestRequirementSynthesizer:
    """Test suite for RequirementSynthesizer class."""
    
    @patch('intelligence.requirement_synthesizer.OpenAIChatCompletionClient')
    @patch('intelligence.requirement_synthesizer.RoundRobinGroupChat')
    def test_initialize_agent_ecosystem(self, mock_group_chat, mock_client):
        """Test initialization of agent ecosystem."""
        from intelligence.requirement_synthesizer import RequirementSynthesizer
        
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        mock_group_instance = Mock()
        mock_group_chat.return_value = mock_group_instance
        
        # Test initialization
        frontend_agent, backend_agent, team = RequirementSynthesizer.initialize_agent_ecosystem()
        
        # Verify that OpenAI client was initialized
        mock_client.assert_called()
        
        # Verify that group chat was created with correct participants
        mock_group_chat.assert_called_once()
        call_args = mock_group_chat.call_args
        assert 'participants' in call_args.kwargs
        assert len(call_args.kwargs['participants']) == 3  # frontend, backend, reviewer
        assert call_args.kwargs['max_turns'] == 3
    
    @patch('intelligence.requirement_synthesizer.RequirementSynthesizer.initialize_agent_ecosystem')
    @pytest.mark.asyncio
    async def test_process_requirements_success(self, mock_init_ecosystem):
        """Test successful requirements processing."""
        from intelligence.requirement_synthesizer import RequirementSynthesizer
        
        # Mock agents and team
        mock_frontend_agent = Mock()
        mock_backend_agent = Mock()
        mock_team = Mock()
        
        mock_init_ecosystem.return_value = (mock_frontend_agent, mock_backend_agent, mock_team)
        
        # Mock team execution result
        mock_result = Mock()
        mock_result.messages = [
            Mock(source="Frontend_Architecture_Specialist", content="Frontend spec content"),
            Mock(source="Backend_Architecture_Specialist", content="Backend spec content"),
            Mock(source="Technical_Quality_Analyst", content="Review completed")
        ]
        
        mock_team.run = AsyncMock(return_value=mock_result)
        
        # Test the processing
        requirements = "Create an e-commerce platform with user management"
        frontend_spec, backend_spec = await RequirementSynthesizer.process_requirements(requirements)
        
        assert frontend_spec == "Frontend spec content"
        assert backend_spec == "Backend spec content"
        
        # Verify team was called with correct task
        mock_team.run.assert_called_once()
        call_args = mock_team.run.call_args
        assert "e-commerce platform" in call_args.kwargs['task']
    
    @patch('intelligence.requirement_synthesizer.RequirementSynthesizer.initialize_agent_ecosystem')
    @pytest.mark.asyncio
    async def test_process_requirements_partial_response(self, mock_init_ecosystem):
        """Test requirements processing with partial agent responses."""
        from intelligence.requirement_synthesizer import RequirementSynthesizer
        
        mock_frontend_agent = Mock()
        mock_backend_agent = Mock()
        mock_team = Mock()
        
        mock_init_ecosystem.return_value = (mock_frontend_agent, mock_backend_agent, mock_team)
        
        # Mock result with only frontend response
        mock_result = Mock()
        mock_result.messages = [
            Mock(source="Frontend_Architecture_Specialist", content="Frontend spec only"),
            Mock(source="Technical_Quality_Analyst", content="Review completed")
        ]
        
        mock_team.run = AsyncMock(return_value=mock_result)
        
        requirements = "Create a simple frontend application"
        frontend_spec, backend_spec = await RequirementSynthesizer.process_requirements(requirements)
        
        assert frontend_spec == "Frontend spec only"
        assert backend_spec == ""  # Should be empty when no backend agent responds
    
    @patch('intelligence.requirement_synthesizer.RequirementSynthesizer.initialize_agent_ecosystem')
    @pytest.mark.asyncio
    async def test_process_requirements_team_failure(self, mock_init_ecosystem):
        """Test requirements processing with team execution failure."""
        from intelligence.requirement_synthesizer import RequirementSynthesizer
        
        mock_frontend_agent = Mock()
        mock_backend_agent = Mock()
        mock_team = Mock()
        
        mock_init_ecosystem.return_value = (mock_frontend_agent, mock_backend_agent, mock_team)
        
        # Mock team execution failure
        mock_team.run = AsyncMock(side_effect=Exception("AI processing failed"))
        
        requirements = "Create an application"
        
        with pytest.raises(Exception) as exc_info:
            await RequirementSynthesizer.process_requirements(requirements)
        
        assert "AI processing failed" in str(exc_info.value)
    
    def test_process_requirements_synchronous(self):
        """Test synchronous wrapper for requirements processing."""
        from intelligence.requirement_synthesizer import RequirementSynthesizer
        
        with patch.object(RequirementSynthesizer, 'process_requirements') as mock_async:
            mock_async.return_value = ("Frontend", "Backend")
            
            # Mock asyncio.run to avoid actual async execution in test
            with patch('asyncio.run') as mock_run:
                mock_run.return_value = ("Frontend", "Backend")
                
                result = RequirementSynthesizer.process_requirements_synchronous("Test requirements")
                
                assert result == ("Frontend", "Backend")
                mock_run.assert_called_once()


class TestBackendArchitectureGenerator:
    """Test suite for BackendArchitectureGenerator class."""
    
    @patch('intelligence.backend_architect.OpenAIChatCompletionClient')
    @patch('intelligence.backend_architect.RoundRobinGroupChat')
    @patch('processors.file_operations.CodeArtifactManager.save_code_artifact')
    def test_initialize_backend_architecture_team(self, mock_save_artifact, mock_group_chat, mock_client):
        """Test initialization of backend architecture team."""
        from intelligence.backend_architect import BackendArchitectureGenerator
        
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        mock_team_instance = Mock()
        mock_group_chat.return_value = mock_team_instance
        
        # Test initialization
        team = BackendArchitectureGenerator.initialize_backend_architecture_team()
        
        # Verify OpenAI client was initialized
        mock_client.assert_called()
        
        # Verify group chat was created with correct number of agents
        mock_group_chat.assert_called_once()
        call_args = mock_group_chat.call_args
        assert 'participants' in call_args.kwargs
        # Should have 6 agents: API, Data, Business Logic, Integration, Migration, QA
        assert len(call_args.kwargs['participants']) == 6
        assert call_args.kwargs['max_turns'] == 4
    
    @patch('intelligence.backend_architect.BackendArchitectureGenerator.initialize_backend_architecture_team')
    @patch('intelligence.backend_architect.Console')
    @pytest.mark.asyncio
    async def test_synthesize_backend_structure_success(self, mock_console, mock_init_team):
        """Test successful backend structure synthesis."""
        from intelligence.backend_architect import BackendArchitectureGenerator
        
        # Mock architecture team
        mock_team = Mock()
        mock_init_team.return_value = mock_team
        
        # Mock console and team execution
        mock_result = Mock(content="Generated backend architecture")
        mock_console_instance = Mock()
        mock_console_instance.return_value = mock_result
        mock_console.return_value = mock_console_instance
        
        mock_team.run_stream = AsyncMock(return_value=Mock())
        
        # Test synthesis
        technical_spec = "Create a FastAPI backend with PostgreSQL database"
        result = await BackendArchitectureGenerator.synthesize_backend_structure(technical_spec)
        
        assert result == mock_result
        
        # Verify team was initialized and run
        mock_init_team.assert_called_once()
        mock_console.assert_called_once()
    
    @patch('intelligence.backend_architect.BackendArchitectureGenerator.initialize_backend_architecture_team')
    @pytest.mark.asyncio
    async def test_synthesize_backend_structure_failure(self, mock_init_team):
        """Test backend structure synthesis with failure."""
        from intelligence.backend_architect import BackendArchitectureGenerator
        
        # Mock team that raises exception
        mock_team = Mock()
        mock_team.run_stream = AsyncMock(side_effect=Exception("Backend generation failed"))
        mock_init_team.return_value = mock_team
        
        technical_spec = "Create a backend system"
        
        with pytest.raises(Exception) as exc_info:
            await BackendArchitectureGenerator.synthesize_backend_structure(technical_spec)
        
        assert "Backend generation failed" in str(exc_info.value)
    
    def test_legacy_compatibility_functions(self):
        """Test legacy compatibility wrapper functions."""
        from intelligence.backend_architect import generate_backend_code, agent_group_backend
        
        # Test that legacy functions exist and can be imported
        assert callable(generate_backend_code)
        assert callable(agent_group_backend)


class TestFrontendDesignGenerator:
    """Test suite for FrontendDesignGenerator class."""
    
    @patch('intelligence.frontend_designer.OpenAIChatCompletionClient')
    @patch('intelligence.frontend_designer.SelectorGroupChat')
    @patch('processors.file_operations.CodeArtifactManager.save_code_artifact')
    def test_initialize_frontend_design_team(self, mock_save_artifact, mock_selector_chat, mock_client):
        """Test initialization of frontend design team."""
        from intelligence.frontend_designer import FrontendDesignGenerator
        
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        mock_team_instance = Mock()
        mock_selector_chat.return_value = mock_team_instance
        
        # Test initialization
        team = FrontendDesignGenerator.initialize_frontend_design_team()
        
        # Verify OpenAI client was initialized
        mock_client.assert_called()
        
        # Verify selector group chat was created
        mock_selector_chat.assert_called_once()
        call_args = mock_selector_chat.call_args
        assert 'participants' in call_args.kwargs
        # Should have 5 agents: Component, Service, UI/UX, State Management, Quality
        assert len(call_args.kwargs['participants']) == 5
        assert 'selector_prompt' in call_args.kwargs
        assert 'allow_repeated_speaker' in call_args.kwargs
        assert call_args.kwargs['allow_repeated_speaker'] is True
    
    @patch('intelligence.frontend_designer.FrontendDesignGenerator.initialize_frontend_design_team')
    @patch('intelligence.frontend_designer.Console')
    @pytest.mark.asyncio
    async def test_synthesize_frontend_components_success(self, mock_console, mock_init_team):
        """Test successful frontend components synthesis."""
        from intelligence.frontend_designer import FrontendDesignGenerator
        
        # Mock design team
        mock_team = Mock()
        mock_init_team.return_value = mock_team
        
        # Mock console and team execution
        mock_result = Mock(content="Generated frontend components")
        mock_console_instance = Mock()
        mock_console_instance.return_value = mock_result
        mock_console.return_value = mock_console_instance
        
        mock_team.run_stream = AsyncMock(return_value=Mock())
        
        # Test synthesis
        interface_spec = "Create an Angular dashboard with charts and user management"
        result = await FrontendDesignGenerator.synthesize_frontend_components(interface_spec)
        
        assert result == mock_result
        
        # Verify team was initialized and run
        mock_init_team.assert_called_once()
        mock_console.assert_called_once()
    
    @patch('intelligence.frontend_designer.FrontendDesignGenerator.initialize_frontend_design_team')
    @pytest.mark.asyncio
    async def test_synthesize_frontend_components_failure(self, mock_init_team):
        """Test frontend components synthesis with failure."""
        from intelligence.frontend_designer import FrontendDesignGenerator
        
        # Mock team that raises exception
        mock_team = Mock()
        mock_team.run_stream = AsyncMock(side_effect=Exception("Frontend generation failed"))
        mock_init_team.return_value = mock_team
        
        interface_spec = "Create a frontend application"
        
        with pytest.raises(Exception) as exc_info:
            await FrontendDesignGenerator.synthesize_frontend_components(interface_spec)
        
        assert "Frontend generation failed" in str(exc_info.value)
    
    def test_legacy_compatibility_functions(self):
        """Test legacy compatibility wrapper functions."""
        from intelligence.frontend_designer import generate_frontend_code, agent_group_frontend
        
        # Test that legacy functions exist and can be imported
        assert callable(generate_frontend_code)
        assert callable(agent_group_frontend)


class TestIntelligenceModuleIntegration:
    """Test suite for integration between intelligence modules."""
    
    @patch('intelligence.requirement_synthesizer.RequirementSynthesizer.process_requirements')
    @patch('intelligence.backend_architect.BackendArchitectureGenerator.synthesize_backend_structure')
    @patch('intelligence.frontend_designer.FrontendDesignGenerator.synthesize_frontend_components')
    @pytest.mark.asyncio
    async def test_full_pipeline_integration(self, mock_frontend_gen, mock_backend_gen, mock_req_synth):
        """Test full pipeline integration from requirements to code generation."""
        
        # Mock requirement synthesis
        mock_req_synth.return_value = (
            "Frontend specification content",
            "Backend specification content"
        )
        
        # Mock code generation
        mock_backend_result = Mock(content="Generated backend code")
        mock_frontend_result = Mock(content="Generated frontend code")
        
        mock_backend_gen.return_value = mock_backend_result
        mock_frontend_gen.return_value = mock_frontend_result
        
        # Simulate full pipeline
        requirements = "Create a complete e-commerce platform"
        
        # Step 1: Generate specifications
        frontend_spec, backend_spec = await mock_req_synth(requirements)
        
        # Step 2: Generate backend code
        backend_code = await mock_backend_gen(backend_spec)
        
        # Step 3: Generate frontend code
        frontend_code = await mock_frontend_gen(frontend_spec)
        
        # Verify results
        assert frontend_spec == "Frontend specification content"
        assert backend_spec == "Backend specification content"
        assert backend_code.content == "Generated backend code"
        assert frontend_code.content == "Generated frontend code"
        
        # Verify all functions were called
        mock_req_synth.assert_called_once_with(requirements)
        mock_backend_gen.assert_called_once_with(backend_spec)
        mock_frontend_gen.assert_called_once_with(frontend_spec)
    
    @patch('intelligence.requirement_synthesizer.openai_api_key', 'test-api-key')
    def test_openai_api_key_configuration(self):
        """Test that OpenAI API key is properly configured across modules."""
        from intelligence import requirement_synthesizer, backend_architect, frontend_designer
        
        # Verify API key is set in all modules
        assert requirement_synthesizer.openai_api_key == 'test-api-key'
        assert backend_architect.openai_api_key == 'test-api-key'
        assert frontend_designer.openai_api_key == 'test-api-key'
    
    def test_module_imports_and_availability(self):
        """Test that all intelligence modules can be imported successfully."""
        # Test individual module imports
        from intelligence.requirement_synthesizer import RequirementSynthesizer
        from intelligence.backend_architect import BackendArchitectureGenerator
        from intelligence.frontend_designer import FrontendDesignGenerator
        
        # Verify classes are available and callable
        assert hasattr(RequirementSynthesizer, 'process_requirements')
        assert hasattr(BackendArchitectureGenerator, 'synthesize_backend_structure')
        assert hasattr(FrontendDesignGenerator, 'synthesize_frontend_components')
        
        # Test package-level imports
        import intelligence
        assert hasattr(intelligence, 'requirement_synthesizer')
        assert hasattr(intelligence, 'backend_architect')
        assert hasattr(intelligence, 'frontend_designer')


class TestAIAgentConfiguration:
    """Test suite for AI agent configuration and setup."""
    
    @patch('intelligence.requirement_synthesizer.AssistantAgent')
    @patch('intelligence.requirement_synthesizer.UserProxyAgent')
    def test_requirement_synthesizer_agent_configuration(self, mock_user_agent, mock_assistant_agent):
        """Test proper configuration of requirement synthesizer agents."""
        from intelligence.requirement_synthesizer import RequirementSynthesizer
        
        # Mock agent instances
        mock_assistant_instance = Mock()
        mock_user_instance = Mock()
        mock_assistant_agent.return_value = mock_assistant_instance
        mock_user_agent.return_value = mock_user_instance
        
        # Initialize agent ecosystem
        with patch('intelligence.requirement_synthesizer.RoundRobinGroupChat'):
            RequirementSynthesizer.initialize_agent_ecosystem()
        
        # Verify agents were created with correct parameters
        assert mock_assistant_agent.call_count == 2  # Frontend and Backend specialists
        assert mock_user_agent.call_count == 1  # Project manager
        
        # Check that agents have appropriate system messages
        for call in mock_assistant_agent.call_args_list:
            assert 'system_message' in call.kwargs
            assert len(call.kwargs['system_message']) > 100  # Should have substantial system message
    
    @patch('intelligence.backend_architect.AssistantAgent')
    def test_backend_architect_agent_configuration(self, mock_assistant_agent):
        """Test proper configuration of backend architecture agents."""
        from intelligence.backend_architect import BackendArchitectureGenerator
        
        mock_agent_instance = Mock()
        mock_assistant_agent.return_value = mock_agent_instance
        
        # Initialize backend team
        with patch('intelligence.backend_architect.RoundRobinGroupChat'):
            BackendArchitectureGenerator.initialize_backend_architecture_team()
        
        # Verify multiple specialized agents were created
        assert mock_assistant_agent.call_count == 6  # 6 different backend specialists
        
        # Verify each agent has tools configured
        for call in mock_assistant_agent.call_args_list:
            assert 'tools' in call.kwargs
            assert len(call.kwargs['tools']) > 0  # Should have saveFile tool
    
    @patch('intelligence.frontend_designer.AssistantAgent')
    def test_frontend_designer_agent_configuration(self, mock_assistant_agent):
        """Test proper configuration of frontend design agents."""
        from intelligence.frontend_designer import FrontendDesignGenerator
        
        mock_agent_instance = Mock()
        mock_assistant_agent.return_value = mock_agent_instance
        
        # Initialize frontend team
        with patch('intelligence.frontend_designer.SelectorGroupChat'):
            FrontendDesignGenerator.initialize_frontend_design_team()
        
        # Verify multiple specialized agents were created
        assert mock_assistant_agent.call_count == 5  # 5 different frontend specialists
        
        # Verify agents have proper configuration
        for call in mock_assistant_agent.call_args_list:
            assert 'model_client' in call.kwargs
            assert 'tools' in call.kwargs or 'system_message' in call.kwargs
