import logging
import json
import os
from typing import Dict, List, Optional

from livekit.agents import Agent, function_tool, RunContext

logger = logging.getLogger("fraud_agent")


# Fraud Case State
class FraudCaseState:
    def __init__(self):
        self.user_name: Optional[str] = None
        self.security_identifier: Optional[str] = None
        self.card_ending: Optional[str] = None
        self.transaction_amount: Optional[str] = None
        self.transaction_name: Optional[str] = None
        self.transaction_time: Optional[str] = None
        self.transaction_category: Optional[str] = None
        self.transaction_source: Optional[str] = None
        self.transaction_location: Optional[str] = None
        self.security_question: Optional[str] = None
        self.security_answer: Optional[str] = None
        self.status: str = "pending_review"
        self.outcome: Optional[str] = None
        self.verification_passed: bool = False
        self.user_confirmed_transaction: Optional[bool] = None
    
    def to_dict(self) -> Dict:
        return {
            "userName": self.user_name,
            "securityIdentifier": self.security_identifier,
            "cardEnding": self.card_ending,
            "transactionAmount": self.transaction_amount,
            "transactionName": self.transaction_name,
            "transactionTime": self.transaction_time,
            "transactionCategory": self.transaction_category,
            "transactionSource": self.transaction_source,
            "transactionLocation": self.transaction_location,
            "securityQuestion": self.security_question,
            "securityAnswer": self.security_answer,
            "status": self.status,
            "outcome": self.outcome
        }


# Fraud Alert Agent
class FraudAlertAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions="""You are a professional and reassuring fraud detection representative for SecureBank, a trusted financial institution.

            Your personality:
            - Calm, professional, and reassuring
            - Clear and direct in communication
            - Empathetic to customer concerns
            - Security-focused but not alarming
            - Patient and understanding

            Your role:
            1. Introduce yourself as calling from SecureBank's Fraud Detection Department
            2. Explain that you're calling about a suspicious transaction on their account
            3. Verify the customer's identity using their security question (NEVER ask for full card numbers, PINs, or passwords)
            4. If verification passes:
               - Read out the suspicious transaction details (merchant, amount, time, location)
               - Ask if they made this transaction
               - Based on their answer, mark the case appropriately
            5. If verification fails:
               - Politely explain you cannot proceed without proper verification
               - Suggest they contact the bank directly
            6. Provide clear next steps and reassurance

            Important guidelines:
            - NEVER ask for sensitive information like full card numbers, PINs, or passwords
            - Use only the security question from the database for verification
            - Be clear about what actions will be taken
            - Reassure customers that their account security is the priority
            - Keep the conversation focused and professional
            - If the transaction is fraudulent, explain the card will be blocked and a new one issued
            - If the transaction is legitimate, confirm no further action is needed

            Remember: You're here to protect the customer's account and provide peace of mind."""
        )
        self.fraud_case = FraudCaseState()
        self._room = None
        self.fraud_cases_file = "shared-data/fraud_cases.json"
        self.case_loaded = False
    
    def set_room(self, room):
        """Set the room for sending data updates."""
        self._room = room
    
    async def _send_fraud_update(self):
        """Send fraud case update to frontend via data channel."""
        if self._room:
            try:
                fraud_data = {
                    "type": "fraud_update",
                    "data": self.fraud_case.to_dict()
                }
                await self._room.local_participant.publish_data(
                    json.dumps(fraud_data).encode('utf-8'),
                    topic="fraud_alert"
                )
                logger.info(f"Sent fraud update: {fraud_data}")
            except Exception as e:
                logger.error(f"Failed to send fraud update: {e}")
    
    def _load_fraud_cases(self) -> List[Dict]:
        """Load fraud cases from JSON file."""
        try:
            if os.path.exists(self.fraud_cases_file):
                with open(self.fraud_cases_file, 'r') as f:
                    data = json.load(f)
                    return data.get('fraud_cases', [])
        except Exception as e:
            logger.error(f"Failed to load fraud cases: {e}")
        return []
    
    def _save_fraud_cases(self, cases: List[Dict]):
        """Save fraud cases back to JSON file."""
        try:
            with open(self.fraud_cases_file, 'w') as f:
                json.dump({"fraud_cases": cases}, f, indent=2)
            logger.info(f"Fraud cases saved to {self.fraud_cases_file}")
        except Exception as e:
            logger.error(f"Failed to save fraud cases: {e}")
    
    @function_tool
    async def load_fraud_case_by_username(self, context: RunContext, user_name: str):
        """Load a fraud case from the database by username.
        
        Args:
            user_name: The customer's name to look up their fraud case
        """
        cases = self._load_fraud_cases()
        
        # Find case matching the username (case-insensitive)
        matching_case = None
        for case in cases:
            if case.get('userName', '').lower() == user_name.lower():
                matching_case = case
                break
        
        if not matching_case:
            return f"I'm sorry, I don't have a fraud case on file for {user_name}. Could you please verify your name?"
        
        # Load case data into state
        self.fraud_case.user_name = matching_case.get('userName')
        self.fraud_case.security_identifier = matching_case.get('securityIdentifier')
        self.fraud_case.card_ending = matching_case.get('cardEnding')
        self.fraud_case.transaction_amount = matching_case.get('transactionAmount')
        self.fraud_case.transaction_name = matching_case.get('transactionName')
        self.fraud_case.transaction_time = matching_case.get('transactionTime')
        self.fraud_case.transaction_category = matching_case.get('transactionCategory')
        self.fraud_case.transaction_source = matching_case.get('transactionSource')
        self.fraud_case.transaction_location = matching_case.get('transactionLocation')
        self.fraud_case.security_question = matching_case.get('securityQuestion')
        self.fraud_case.security_answer = matching_case.get('securityAnswer')
        self.fraud_case.status = matching_case.get('status', 'pending_review')
        
        self.case_loaded = True
        
        logger.info(f"Loaded fraud case for {user_name}")
        await self._send_fraud_update()
        
        return f"Thank you, {user_name}. I have your case pulled up. For security purposes, I need to verify your identity before we proceed. {self.fraud_case.security_question}"
    
    @function_tool
    async def verify_customer_identity(self, context: RunContext, answer: str):
        """Verify the customer's identity using their security answer.
        
        Args:
            answer: The customer's answer to the security question
        """
        if not self.case_loaded:
            return "I need to load your fraud case first. Can you please provide your name?"
        
        # Check if answer matches (case-insensitive)
        if answer.lower().strip() == self.fraud_case.security_answer.lower().strip():
            self.fraud_case.verification_passed = True
            logger.info(f"Identity verification passed for {self.fraud_case.user_name}")
            await self._send_fraud_update()
            
            return f"Thank you for verifying your identity. Now, let me tell you about the suspicious transaction we detected. On {self.fraud_case.transaction_time}, we noticed a charge of {self.fraud_case.transaction_amount} to {self.fraud_case.transaction_name} from {self.fraud_case.transaction_location}. The transaction was made through {self.fraud_case.transaction_source} for {self.fraud_case.transaction_category}. Did you make this purchase?"
        else:
            self.fraud_case.verification_passed = False
            self.fraud_case.status = "verification_failed"
            self.fraud_case.outcome = "Customer failed identity verification. Advised to contact bank directly."
            logger.warning(f"Identity verification failed for {self.fraud_case.user_name}")
            
            # Save the failed verification
            self._update_case_in_database()
            await self._send_fraud_update()
            
            return "I'm sorry, but that answer doesn't match our records. For your security, I cannot proceed with this call. Please contact SecureBank directly at 1-800-SECURE-BANK or visit your nearest branch with a valid ID. Your account security is our top priority."
    
    @function_tool
    async def record_transaction_confirmation(self, context: RunContext, customer_made_transaction: bool):
        """Record whether the customer confirms they made the transaction.
        
        Args:
            customer_made_transaction: True if customer confirms they made the transaction, False if they deny it
        """
        if not self.fraud_case.verification_passed:
            return "I need to verify your identity first before we can discuss the transaction details."
        
        self.fraud_case.user_confirmed_transaction = customer_made_transaction
        
        if customer_made_transaction:
            # Customer confirms - mark as safe
            self.fraud_case.status = "confirmed_safe"
            self.fraud_case.outcome = "Customer confirmed the transaction as legitimate. No action required."
            
            logger.info(f"Transaction confirmed as safe by {self.fraud_case.user_name}")
            
            # Update database
            self._update_case_in_database()
            await self._send_fraud_update()
            
            return f"Excellent! Thank you for confirming that you made this purchase. I've marked this transaction as legitimate in our system, and no further action is needed. Your card ending in {self.fraud_case.card_ending} remains active and secure. Is there anything else I can help you with today?"
        else:
            # Customer denies - mark as fraudulent
            self.fraud_case.status = "confirmed_fraud"
            self.fraud_case.outcome = "Customer denied making the transaction. Card blocked, dispute initiated, new card being issued."
            
            logger.info(f"Transaction confirmed as fraudulent by {self.fraud_case.user_name}")
            
            # Update database
            self._update_case_in_database()
            await self._send_fraud_update()
            
            return f"I understand, and I'm sorry this happened to you. For your protection, I'm taking immediate action. I've blocked your card ending in {self.fraud_case.card_ending} to prevent any further unauthorized charges. We're initiating a dispute for the {self.fraud_case.transaction_amount} charge, and you should see that amount credited back to your account within 5-7 business days. A new card will be sent to your address on file within 3-5 business days. You will not be held responsible for this fraudulent charge. Is there anything else you'd like me to clarify?"
    
    def _update_case_in_database(self):
        """Update the fraud case in the database with current status."""
        cases = self._load_fraud_cases()
        
        # Find and update the matching case
        for i, case in enumerate(cases):
            if case.get('userName', '').lower() == self.fraud_case.user_name.lower():
                cases[i]['status'] = self.fraud_case.status
                cases[i]['outcome'] = self.fraud_case.outcome
                break
        
        # Save back to file
        self._save_fraud_cases(cases)
    
    @function_tool
    async def get_case_status(self, context: RunContext):
        """Get the current status of the fraud case."""
        if not self.case_loaded:
            return "I don't have a fraud case loaded yet. Can you please provide your name so I can look up your case?"
        
        status_messages = {
            "pending_review": f"Your case is currently under review. We detected a suspicious transaction and need to verify it with you.",
            "verification_failed": "Identity verification was not successful. Please contact the bank directly.",
            "confirmed_safe": "The transaction has been confirmed as legitimate. No action needed.",
            "confirmed_fraud": "The transaction has been confirmed as fraudulent. Your card has been blocked and a new one is being issued."
        }
        
        return status_messages.get(self.fraud_case.status, "Case status unknown.")
    
    @function_tool
    async def end_fraud_call(self, context: RunContext):
        """End the fraud alert call with a professional closing."""
        if not self.case_loaded:
            return "Thank you for your time. If you have any concerns about your account, please contact SecureBank at 1-800-SECURE-BANK. Have a great day!"
        
        if self.fraud_case.status == "confirmed_safe":
            return f"Thank you for your time, {self.fraud_case.user_name}. Your account is secure, and we'll continue monitoring for any suspicious activity. If you notice anything unusual in the future, please don't hesitate to contact us immediately. Have a wonderful day!"
        elif self.fraud_case.status == "confirmed_fraud":
            return f"Thank you for your patience, {self.fraud_case.user_name}. We've taken all necessary steps to protect your account. You'll receive email confirmation of these actions shortly. If you have any questions, our fraud department is available 24/7 at 1-800-SECURE-BANK. Stay safe!"
        elif self.fraud_case.status == "verification_failed":
            return "For your security, please visit a SecureBank branch with valid identification or call our customer service line. Thank you for understanding. Goodbye."
        else:
            return f"Thank you for your time, {self.fraud_case.user_name}. If you have any questions, please contact us at 1-800-SECURE-BANK. Have a great day!"
