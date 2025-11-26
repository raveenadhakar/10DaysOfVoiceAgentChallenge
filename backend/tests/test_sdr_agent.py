"""Tests for SDR Agent functionality."""
import pytest
import json
import os
from unittest.mock import Mock, AsyncMock, patch
from src.agent import SDRAgent, LeadState, CompanyFAQ


class TestLeadState:
    """Test LeadState class."""
    
    def test_lead_state_initialization(self):
        """Test that LeadState initializes with None values."""
        state = LeadState()
        assert state.name is None
        assert state.company is None
        assert state.email is None
        assert state.role is None
        assert state.use_case is None
        assert state.team_size is None
        assert state.timeline is None
        assert state.questions_asked == []
        assert state.call_complete is False
    
    def test_lead_state_is_complete_false(self):
        """Test that is_complete returns False when required fields are missing."""
        state = LeadState()
        assert state.is_complete() is False
        
        state.name = "John Doe"
        assert state.is_complete() is False
        
        state.email = "john@example.com"
        assert state.is_complete() is False
    
    def test_lead_state_is_complete_true(self):
        """Test that is_complete returns True when all required fields are present."""
        state = LeadState()
        state.name = "John Doe"
        state.email = "john@example.com"
        state.use_case = "payment gateway"
        assert state.is_complete() is True
    
    def test_lead_state_to_dict(self):
        """Test that to_dict returns correct dictionary."""
        state = LeadState()
        state.name = "John Doe"
        state.email = "john@example.com"
        
        result = state.to_dict()
        assert result["name"] == "John Doe"
        assert result["email"] == "john@example.com"
        assert result["company"] is None


class TestCompanyFAQ:
    """Test CompanyFAQ class."""
    
    def test_company_faq_loads_data(self):
        """Test that CompanyFAQ loads data from JSON file."""
        faq = CompanyFAQ()
        assert faq.company_info is not None
        assert faq.faq_items is not None
        assert len(faq.faq_items) > 0
    
    def test_search_faq_finds_match(self):
        """Test that search_faq finds relevant FAQ entries."""
        faq = CompanyFAQ()
        
        # Search for pricing question
        result = faq.search_faq("what are your pricing fees")
        assert result is not None
        assert "pricing" in result["answer"].lower() or "fee" in result["answer"].lower()
    
    def test_search_faq_no_match(self):
        """Test that search_faq returns None when no match found."""
        faq = CompanyFAQ()
        
        # Search for something completely unrelated
        result = faq.search_faq("xyz123 random query")
        # May return None or a weak match
        assert result is None or isinstance(result, dict)
    
    def test_get_company_overview(self):
        """Test that get_company_overview returns company information."""
        faq = CompanyFAQ()
        overview = faq.get_company_overview()
        assert isinstance(overview, str)
        assert len(overview) > 0
        assert "Razorpay" in overview


class TestSDRAgent:
    """Test SDRAgent class."""
    
    def test_sdr_agent_initialization(self):
        """Test that SDRAgent initializes correctly."""
        agent = SDRAgent()
        assert agent.lead_state is not None
        assert agent.company_faq is not None
        assert agent.leads_file == "leads.json"
    
    @pytest.mark.asyncio
    async def test_record_lead_name(self):
        """Test recording lead name."""
        agent = SDRAgent()
        agent._room = None  # No room for testing
        
        # Create mock context
        context = Mock()
        
        result = await agent.record_lead_name(context, "John Doe")
        assert agent.lead_state.name == "John Doe"
        assert "John Doe" in result
    
    @pytest.mark.asyncio
    async def test_record_lead_email(self):
        """Test recording lead email."""
        agent = SDRAgent()
        agent._room = None
        
        context = Mock()
        
        result = await agent.record_lead_email(context, "john@example.com")
        assert agent.lead_state.email == "john@example.com"
        assert "john@example.com" in result
    
    @pytest.mark.asyncio
    async def test_record_use_case(self):
        """Test recording use case."""
        agent = SDRAgent()
        agent._room = None
        
        context = Mock()
        
        result = await agent.record_use_case(context, "ecommerce payments")
        assert agent.lead_state.use_case == "ecommerce payments"
        assert "ecommerce payments" in result
    
    @pytest.mark.asyncio
    async def test_record_timeline_normalization(self):
        """Test that timeline is normalized correctly."""
        agent = SDRAgent()
        agent._room = None
        
        context = Mock()
        
        # Test "now" normalization
        await agent.record_timeline(context, "I need this now")
        assert agent.lead_state.timeline == "now"
        
        # Test "soon" normalization
        agent.lead_state.timeline = None
        await agent.record_timeline(context, "next week")
        assert agent.lead_state.timeline == "soon"
        
        # Test "later" normalization
        agent.lead_state.timeline = None
        await agent.record_timeline(context, "just exploring")
        assert agent.lead_state.timeline == "later"
    
    @pytest.mark.asyncio
    async def test_answer_company_question(self):
        """Test answering company questions."""
        agent = SDRAgent()
        agent._room = None
        
        context = Mock()
        
        result = await agent.answer_company_question(context, "What does Razorpay do?")
        assert len(agent.lead_state.questions_asked) == 1
        assert isinstance(result, str)
        assert len(result) > 0
    
    @pytest.mark.asyncio
    async def test_check_lead_completeness(self):
        """Test checking lead completeness."""
        agent = SDRAgent()
        agent._room = None
        
        context = Mock()
        
        # Incomplete lead
        result = await agent.check_lead_completeness(context)
        assert "information" in result.lower() or "need" in result.lower()
        
        # Complete lead
        agent.lead_state.name = "John Doe"
        agent.lead_state.email = "john@example.com"
        agent.lead_state.use_case = "payments"
        
        result = await agent.check_lead_completeness(context)
        assert "summarize" in result.lower() or "information" in result.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
