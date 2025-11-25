import pytest
import json
from unittest.mock import AsyncMock, MagicMock
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agent import TutorCoordinatorAgent, TutorContent


class TestTutorContent:
    def test_load_content(self):
        """Test that tutor content loads correctly."""
        content = TutorContent()
        concepts = content.get_all_concepts()
        
        assert len(concepts) >= 4  # Should have at least 4 concepts
        
        # Check that required concepts exist
        concept_ids = [c['id'] for c in concepts]
        assert 'variables' in concept_ids
        assert 'loops' in concept_ids
        assert 'functions' in concept_ids
        assert 'conditionals' in concept_ids
    
    def test_get_concept(self):
        """Test getting a specific concept."""
        content = TutorContent()
        
        variables_concept = content.get_concept('variables')
        assert variables_concept is not None
        assert variables_concept['id'] == 'variables'
        assert variables_concept['title'] == 'Variables'
        assert 'summary' in variables_concept
        assert 'sample_question' in variables_concept
        
        # Test non-existent concept
        invalid_concept = content.get_concept('invalid')
        assert invalid_concept is None


class TestTutorCoordinatorAgent:
    @pytest.fixture
    def agent(self):
        """Create a tutor coordinator agent for testing."""
        agent = TutorCoordinatorAgent()
        agent._room = MagicMock()
        agent._room.local_participant.publish_data = AsyncMock()
        return agent
    
    @pytest.mark.asyncio
    async def test_explain_learning_modes(self, agent):
        """Test that the agent can explain learning modes."""
        context = MagicMock()
        
        result = await agent.explain_learning_modes(context)
        
        assert "LEARN Mode" in result
        assert "QUIZ Mode" in result
        assert "TEACH_BACK Mode" in result
        assert "Matthew" in result
        assert "Alicia" in result
        assert "Ken" in result
    
    @pytest.mark.asyncio
    async def test_switch_to_learn_mode(self, agent):
        """Test switching to learn mode."""
        context = MagicMock()
        
        result = await agent.switch_to_learn_mode(context)
        
        assert agent.current_mode == "learn"
        assert "LEARN mode" in result
        assert "Matthew" in result
        assert "variables" in result
    
    @pytest.mark.asyncio
    async def test_explain_concept(self, agent):
        """Test explaining a concept in learn mode."""
        context = MagicMock()
        
        result = await agent.explain_concept(context, "variables")
        
        assert agent.current_mode == "learn"
        assert agent.current_concept is not None
        assert agent.current_concept['id'] == "variables"
        assert "Variables" in result
        assert "container" in result.lower() or "store" in result.lower()
    
    @pytest.mark.asyncio
    async def test_ask_question_about_concept(self, agent):
        """Test asking a quiz question."""
        context = MagicMock()
        
        result = await agent.ask_question_about_concept(context, "loops")
        
        assert agent.current_mode == "quiz"
        assert agent.current_concept is not None
        assert agent.current_concept['id'] == "loops"
        assert "question" in result.lower()
        assert "loops" in result.lower()
    
    @pytest.mark.asyncio
    async def test_request_explanation(self, agent):
        """Test requesting user explanation in teach-back mode."""
        context = MagicMock()
        
        result = await agent.request_explanation(context, "functions")
        
        assert agent.current_mode == "teach_back"
        assert agent.current_concept is not None
        assert agent.current_concept['id'] == "functions"
        assert "explain" in result.lower()
        assert "functions" in result.lower()
    
    @pytest.mark.asyncio
    async def test_evaluate_answer_good(self, agent):
        """Test evaluating a good answer."""
        context = MagicMock()
        
        # Set up a concept first
        await agent.ask_question_about_concept(context, "variables")
        
        # Provide a good answer with key terms
        good_answer = "Variables are containers that store data values so you can reuse them later in your program"
        result = await agent.evaluate_answer(context, good_answer)
        
        assert "excellent" in result.lower() or "good" in result.lower()
    
    @pytest.mark.asyncio
    async def test_provide_feedback_good(self, agent):
        """Test providing feedback on a good explanation."""
        context = MagicMock()
        
        # Set up teach-back mode
        await agent.request_explanation(context, "loops")
        
        # Provide a good explanation
        good_explanation = "Loops are used to repeat code multiple times. For loops repeat a specific number of times while while loops continue as long as a condition is true"
        result = await agent.provide_feedback(context, good_explanation)
        
        assert "excellent" in result.lower() or "good" in result.lower()
    
    @pytest.mark.asyncio
    async def test_list_available_concepts(self, agent):
        """Test listing available concepts."""
        context = MagicMock()
        
        result = await agent.list_available_concepts(context)
        
        assert "variables" in result.lower()
        assert "loops" in result.lower()
        assert "functions" in result.lower()
        assert "conditionals" in result.lower()
    
    @pytest.mark.asyncio
    async def test_invalid_concept_handling(self, agent):
        """Test handling of invalid concept IDs."""
        context = MagicMock()
        
        result = await agent.explain_concept(context, "invalid_concept")
        
        assert "don't have information" in result.lower()
        assert "available concepts" in result.lower()


if __name__ == "__main__":
    pytest.main([__file__])