"""
Tests for the Fraud Alert Agent
"""
import pytest
import json
import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agent import FraudAlertAgent, FraudCaseState


class TestFraudCaseState:
    """Test the FraudCaseState class"""
    
    def test_fraud_case_state_initialization(self):
        """Test that FraudCaseState initializes with correct defaults"""
        state = FraudCaseState()
        
        assert state.user_name is None
        assert state.status == "pending_review"
        assert state.outcome is None
        assert state.verification_passed is False
        assert state.user_confirmed_transaction is None
    
    def test_fraud_case_state_to_dict(self):
        """Test that FraudCaseState converts to dictionary correctly"""
        state = FraudCaseState()
        state.user_name = "John"
        state.card_ending = "4242"
        state.status = "confirmed_safe"
        
        result = state.to_dict()
        
        assert result["userName"] == "John"
        assert result["cardEnding"] == "4242"
        assert result["status"] == "confirmed_safe"


class TestFraudAlertAgent:
    """Test the FraudAlertAgent class"""
    
    @pytest.fixture
    def agent(self):
        """Create a FraudAlertAgent instance for testing"""
        return FraudAlertAgent()
    
    @pytest.fixture
    def mock_context(self):
        """Create a mock RunContext"""
        return MagicMock()
    
    def test_agent_initialization(self, agent):
        """Test that FraudAlertAgent initializes correctly"""
        assert agent.fraud_case is not None
        assert agent.case_loaded is False
        assert agent.fraud_cases_file == "fraud_cases.json"
    
    def test_load_fraud_cases(self, agent):
        """Test loading fraud cases from JSON file"""
        cases = agent._load_fraud_cases()
        
        assert isinstance(cases, list)
        if len(cases) > 0:
            # Verify structure of first case
            case = cases[0]
            assert "userName" in case
            assert "cardEnding" in case
            assert "transactionAmount" in case
            assert "status" in case
    
    @pytest.mark.asyncio
    async def test_load_fraud_case_by_username_success(self, agent, mock_context):
        """Test successfully loading a fraud case by username"""
        # Mock the room for data updates
        agent._room = AsyncMock()
        
        result = await agent.load_fraud_case_by_username(mock_context, "John")
        
        assert agent.case_loaded is True
        assert agent.fraud_case.user_name == "John"
        assert agent.fraud_case.card_ending == "4242"
        assert "security" in result.lower()
    
    @pytest.mark.asyncio
    async def test_load_fraud_case_by_username_not_found(self, agent, mock_context):
        """Test loading a fraud case with non-existent username"""
        agent._room = AsyncMock()
        
        result = await agent.load_fraud_case_by_username(mock_context, "NonExistentUser")
        
        assert agent.case_loaded is False
        assert "don't have a fraud case" in result.lower()
    
    @pytest.mark.asyncio
    async def test_verify_customer_identity_success(self, agent, mock_context):
        """Test successful customer identity verification"""
        agent._room = AsyncMock()
        
        # First load a case
        await agent.load_fraud_case_by_username(mock_context, "John")
        
        # Then verify with correct answer
        result = await agent.verify_customer_identity(mock_context, "Smith")
        
        assert agent.fraud_case.verification_passed is True
        assert "suspicious transaction" in result.lower()
        assert agent.fraud_case.transaction_amount in result
    
    @pytest.mark.asyncio
    async def test_verify_customer_identity_failure(self, agent, mock_context):
        """Test failed customer identity verification"""
        agent._room = AsyncMock()
        
        # First load a case
        await agent.load_fraud_case_by_username(mock_context, "John")
        
        # Then verify with incorrect answer
        result = await agent.verify_customer_identity(mock_context, "WrongAnswer")
        
        assert agent.fraud_case.verification_passed is False
        assert agent.fraud_case.status == "verification_failed"
        assert "cannot proceed" in result.lower()
    
    @pytest.mark.asyncio
    async def test_record_transaction_confirmation_safe(self, agent, mock_context):
        """Test recording a transaction as safe (customer confirms)"""
        agent._room = AsyncMock()
        
        # Load case and verify identity
        await agent.load_fraud_case_by_username(mock_context, "John")
        await agent.verify_customer_identity(mock_context, "Smith")
        
        # Customer confirms transaction
        result = await agent.record_transaction_confirmation(mock_context, True)
        
        assert agent.fraud_case.status == "confirmed_safe"
        assert agent.fraud_case.user_confirmed_transaction is True
        assert "legitimate" in result.lower()
        assert "no further action" in result.lower()
    
    @pytest.mark.asyncio
    async def test_record_transaction_confirmation_fraud(self, agent, mock_context):
        """Test recording a transaction as fraudulent (customer denies)"""
        agent._room = AsyncMock()
        
        # Load case and verify identity
        await agent.load_fraud_case_by_username(mock_context, "John")
        await agent.verify_customer_identity(mock_context, "Smith")
        
        # Customer denies transaction
        result = await agent.record_transaction_confirmation(mock_context, False)
        
        assert agent.fraud_case.status == "confirmed_fraud"
        assert agent.fraud_case.user_confirmed_transaction is False
        assert "blocked" in result.lower()
        assert "dispute" in result.lower()
    
    @pytest.mark.asyncio
    async def test_record_transaction_without_verification(self, agent, mock_context):
        """Test that recording transaction requires verification first"""
        agent._room = AsyncMock()
        
        # Try to record transaction without loading case or verifying
        result = await agent.record_transaction_confirmation(mock_context, True)
        
        assert "verify your identity" in result.lower()
    
    @pytest.mark.asyncio
    async def test_get_case_status(self, agent, mock_context):
        """Test getting the current case status"""
        agent._room = AsyncMock()
        
        # Before loading case
        result = await agent.get_case_status(mock_context)
        assert "don't have a fraud case loaded" in result.lower()
        
        # After loading case - use a different user to avoid state from previous tests
        await agent.load_fraud_case_by_username(mock_context, "Sarah")
        result = await agent.get_case_status(mock_context)
        # Should have some status message
        assert len(result) > 0
        assert "case" in result.lower() or "review" in result.lower() or "transaction" in result.lower()
    
    @pytest.mark.asyncio
    async def test_end_fraud_call(self, agent, mock_context):
        """Test ending the fraud call"""
        agent._room = AsyncMock()
        
        # Test ending call without loaded case
        result = await agent.end_fraud_call(mock_context)
        assert "thank you" in result.lower()
        
        # Test ending call with confirmed safe case
        await agent.load_fraud_case_by_username(mock_context, "John")
        await agent.verify_customer_identity(mock_context, "Smith")
        await agent.record_transaction_confirmation(mock_context, True)
        
        result = await agent.end_fraud_call(mock_context)
        assert "secure" in result.lower()
        assert agent.fraud_case.user_name in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
