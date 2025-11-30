import logging
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

from livekit.agents import Agent, function_tool, RunContext

logger = logging.getLogger("sdr_agent")


class LeadState:
    def __init__(self):
        self.name: Optional[str] = None
        self.company: Optional[str] = None
        self.email: Optional[str] = None
        self.role: Optional[str] = None
        self.use_case: Optional[str] = None
        self.team_size: Optional[str] = None
        self.timeline: Optional[str] = None  # now / soon / later
        self.questions_asked: List[str] = []
        self.conversation_summary: str = ""
        self.call_complete: bool = False
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "company": self.company,
            "email": self.email,
            "role": self.role,
            "use_case": self.use_case,
            "team_size": self.team_size,
            "timeline": self.timeline,
            "questions_asked": self.questions_asked,
            "conversation_summary": self.conversation_summary,
            "call_complete": self.call_complete
        }
    
    def is_complete(self) -> bool:
        """Check if we have minimum required lead information."""
        return (
            self.name is not None and 
            self.email is not None and 
            self.use_case is not None
        )
    
    def get_missing_fields(self) -> List[str]:
        """Get list of missing important fields."""
        missing = []
        if not self.name:
            missing.append("name")
        if not self.email:
            missing.append("email")
        if not self.company:
            missing.append("company")
        if not self.use_case:
            missing.append("use case")
        if not self.timeline:
            missing.append("timeline")
        return missing


class CompanyFAQ:
    def __init__(self, faq_file: str = "shared-data/sdr_company_faq.json"):
        self.faq_file = faq_file
        self.data = self._load_faq()
        self.company_info = self.data.get("company", {})
        self.products = self.data.get("products", [])
        self.faq_items = self.data.get("faq", [])
        self.use_cases = self.data.get("use_cases", [])
    
    def _load_faq(self) -> Dict:
        """Load FAQ data from JSON file."""
        try:
            with open(self.faq_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load FAQ data: {e}")
            return {}
    
    def search_faq(self, query: str) -> Optional[Dict]:
        """Search FAQ for relevant answer using simple keyword matching."""
        query_lower = query.lower()
        
        # Search through FAQ items
        best_match = None
        best_score = 0
        
        for item in self.faq_items:
            score = 0
            # Check keywords
            for keyword in item.get("keywords", []):
                if keyword.lower() in query_lower:
                    score += 2
            
            # Check question text
            question_words = item["question"].lower().split()
            for word in question_words:
                if len(word) > 3 and word in query_lower:
                    score += 1
            
            if score > best_score:
                best_score = score
                best_match = item
        
        return best_match if best_score > 0 else None
    
    def get_company_overview(self) -> str:
        """Get a brief company overview."""
        return f"{self.company_info.get('name', 'Our company')} - {self.company_info.get('tagline', '')}. {self.company_info.get('description', '')}"
    
    def get_products_summary(self) -> str:
        """Get a summary of products."""
        if not self.products:
            return "We offer a range of solutions for businesses."
        
        product_names = [p["name"] for p in self.products[:3]]
        return f"Our main products include {', '.join(product_names)}, and more."


class SDRAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions=f"""You are a friendly and professional Sales Development Representative (SDR) for Razorpay, India's leading payment gateway company.

            Your personality:
            - Warm, professional, and genuinely helpful
            - Curious about the prospect's needs and challenges
            - Knowledgeable about Razorpay's products and services
            - Focused on understanding before selling
            - Natural conversational style, not pushy or aggressive
            - Ask thoughtful follow-up questions

            Your primary goals:
            1. Greet visitors warmly and make them feel welcome
            2. Understand what brought them here and what they're working on
            3. Answer questions about Razorpay using the FAQ knowledge base
            4. Naturally collect lead information during the conversation:
               - Name
               - Company name
               - Email address
               - Role/position
               - Use case (what they want to use Razorpay for)
               - Team size (optional)
               - Timeline (now / soon / later)
            5. Keep the conversation focused on their needs
            6. When they're done, provide a summary and confirm details

            Important guidelines:
            - Don't ask for all information at once - collect it naturally during conversation
            - Use the FAQ tools to answer product questions accurately
            - Don't make up information not in the FAQ
            - Be helpful and consultative, not pushy
            - Listen more than you talk
            - When you sense the conversation is ending, summarize and confirm their details

            Remember: You're here to help and understand their needs, not just collect information."""
        )
        self.lead_state = LeadState()
        self.company_faq = CompanyFAQ()
        self._room = None
        self.leads_file = "shared-data/leads_sample.json"
    
    def set_room(self, room):
        """Set the room for sending data updates."""
        self._room = room
    
    async def _send_lead_update(self):
        """Send lead state update to frontend via data channel."""
        if self._room:
            try:
                lead_data = {
                    "type": "lead_update",
                    "data": self.lead_state.to_dict()
                }
                await self._room.local_participant.publish_data(
                    json.dumps(lead_data).encode('utf-8'),
                    topic="sdr_session"
                )
                logger.info(f"Sent lead update: {lead_data}")
            except Exception as e:
                logger.error(f"Failed to send lead update: {e}")
    
    @function_tool
    async def answer_company_question(self, context: RunContext, question: str):
        """Answer a question about Razorpay using the FAQ knowledge base.
        
        Args:
            question: The prospect's question about the company, products, pricing, or features
        """
        # Track the question
        self.lead_state.questions_asked.append(question)
        
        # Search FAQ
        faq_match = self.company_faq.search_faq(question)
        
        if faq_match:
            answer = faq_match["answer"]
            logger.info(f"Found FAQ answer for: {question}")
            return f"{answer} Is there anything else you'd like to know about this?"
        else:
            # Provide general company info if no specific match
            logger.info(f"No specific FAQ match for: {question}")
            return f"That's a great question! Let me share what I know. {self.company_faq.get_company_overview()} Would you like me to connect you with our team for more specific details about that?"
    
    @function_tool
    async def get_company_overview(self, context: RunContext):
        """Provide an overview of Razorpay and what we do."""
        overview = self.company_faq.get_company_overview()
        products = self.company_faq.get_products_summary()
        return f"{overview} {products} What specifically are you interested in learning about?"
    
    @function_tool
    async def record_lead_name(self, context: RunContext, name: str):
        """Record the prospect's name.
        
        Args:
            name: The prospect's full name
        """
        self.lead_state.name = name
        logger.info(f"Recorded lead name: {name}")
        await self._send_lead_update()
        return f"Great to meet you, {name}!"
    
    @function_tool
    async def record_lead_company(self, context: RunContext, company: str):
        """Record the prospect's company name.
        
        Args:
            company: The name of the prospect's company
        """
        self.lead_state.company = company
        logger.info(f"Recorded company: {company}")
        await self._send_lead_update()
        return f"Thanks! Tell me more about what {company} does."
    
    @function_tool
    async def record_lead_email(self, context: RunContext, email: str):
        """Record the prospect's email address.
        
        Args:
            email: The prospect's email address
        """
        self.lead_state.email = email
        logger.info(f"Recorded email: {email}")
        await self._send_lead_update()
        return f"Perfect, I've got your email as {email}."
    
    @function_tool
    async def record_lead_role(self, context: RunContext, role: str):
        """Record the prospect's role or position.
        
        Args:
            role: The prospect's job title or role (e.g., founder, CTO, product manager)
        """
        self.lead_state.role = role
        logger.info(f"Recorded role: {role}")
        await self._send_lead_update()
        return f"Got it, you're the {role}."
    
    @function_tool
    async def record_use_case(self, context: RunContext, use_case: str):
        """Record what the prospect wants to use Razorpay for.
        
        Args:
            use_case: Description of how they plan to use Razorpay (e.g., ecommerce payments, subscription billing)
        """
        self.lead_state.use_case = use_case
        logger.info(f"Recorded use case: {use_case}")
        await self._send_lead_update()
        return f"That's a great use case! {use_case} is something we handle really well."
    
    @function_tool
    async def record_team_size(self, context: RunContext, team_size: str):
        """Record the prospect's team size.
        
        Args:
            team_size: Size of the team (e.g., 1-10, 10-50, 50+, just me)
        """
        self.lead_state.team_size = team_size
        logger.info(f"Recorded team size: {team_size}")
        await self._send_lead_update()
        return f"Thanks for sharing that!"
    
    @function_tool
    async def record_timeline(self, context: RunContext, timeline: str):
        """Record when the prospect is looking to get started.
        
        Args:
            timeline: When they want to start (now, soon, later, exploring, urgent)
        """
        # Normalize timeline to standard values
        timeline_lower = timeline.lower()
        if any(word in timeline_lower for word in ["now", "immediate", "urgent", "asap", "today"]):
            normalized_timeline = "now"
        elif any(word in timeline_lower for word in ["soon", "week", "month", "next"]):
            normalized_timeline = "soon"
        else:
            normalized_timeline = "later"
        
        self.lead_state.timeline = normalized_timeline
        logger.info(f"Recorded timeline: {normalized_timeline} (from: {timeline})")
        await self._send_lead_update()
        
        if normalized_timeline == "now":
            return "That's great! We can get you set up very quickly. Our onboarding typically takes less than 15 minutes."
        elif normalized_timeline == "soon":
            return "Perfect! We'll make sure you have all the information you need to get started when you're ready."
        else:
            return "No problem! It's great that you're exploring options early. I'm here to answer any questions."
    
    @function_tool
    async def check_lead_completeness(self, context: RunContext):
        """Check what lead information is still needed."""
        missing = self.lead_state.get_missing_fields()
        if not missing:
            return "I have all the key information I need! Would you like me to summarize what we discussed?"
        else:
            return f"I'd love to get a bit more information: {', '.join(missing)}. This will help me provide better assistance."
    
    @function_tool
    async def complete_call_and_save_lead(self, context: RunContext):
        """Complete the call, provide a summary, and save the lead information."""
        if not self.lead_state.is_complete():
            missing = self.lead_state.get_missing_fields()
            return f"Before we wrap up, I'd like to make sure I have your {', '.join(missing)}. This will help our team follow up with you properly."
        
        # Create timestamp
        timestamp = datetime.now()
        
        # Generate conversation summary
        summary_parts = []
        if self.lead_state.name:
            summary_parts.append(f"{self.lead_state.name}")
        if self.lead_state.role and self.lead_state.company:
            summary_parts.append(f"{self.lead_state.role} at {self.lead_state.company}")
        elif self.lead_state.company:
            summary_parts.append(f"from {self.lead_state.company}")
        
        if self.lead_state.use_case:
            summary_parts.append(f"interested in {self.lead_state.use_case}")
        
        if self.lead_state.timeline:
            timeline_text = {
                "now": "looking to start immediately",
                "soon": "planning to start soon",
                "later": "exploring options for the future"
            }.get(self.lead_state.timeline, "")
            if timeline_text:
                summary_parts.append(timeline_text)
        
        self.lead_state.conversation_summary = " - ".join(summary_parts)
        
        # Prepare lead data
        lead_data = {
            **self.lead_state.to_dict(),
            "date": timestamp.strftime("%Y-%m-%d"),
            "time": timestamp.strftime("%H:%M:%S"),
            "timestamp": timestamp.isoformat(),
            "questions_count": len(self.lead_state.questions_asked)
        }
        
        # Load existing leads or create new structure
        leads_log = {"leads": []}
        try:
            if os.path.exists(self.leads_file):
                with open(self.leads_file, 'r') as f:
                    leads_log = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load existing leads: {e}")
        
        # Add new lead
        leads_log["leads"].append(lead_data)
        
        # Save to JSON file
        try:
            with open(self.leads_file, 'w') as f:
                json.dump(leads_log, f, indent=2)
            
            logger.info(f"Lead saved to {self.leads_file}")
            
            # Send completion notification
            completion_data = {
                "type": "call_complete",
                "data": lead_data
            }
            if self._room:
                await self._room.local_participant.publish_data(
                    json.dumps(completion_data).encode('utf-8'),
                    topic="sdr_session"
                )
            
            # Create verbal summary
            summary = f"Thank you so much for your time today, {self.lead_state.name}! "
            summary += f"Let me quickly recap: You're {self.lead_state.role} at {self.lead_state.company}, " if self.lead_state.role else f"You're from {self.lead_state.company}, "
            summary += f"and you're interested in using Razorpay for {self.lead_state.use_case}. "
            
            if self.lead_state.timeline == "now":
                summary += f"Since you're looking to get started right away, our team will reach out to you at {self.lead_state.email} within the next few hours to help you get set up. "
            elif self.lead_state.timeline == "soon":
                summary += f"We'll send you detailed information to {self.lead_state.email} and our team will follow up with you soon. "
            else:
                summary += f"We'll send you some helpful resources to {self.lead_state.email} and you can reach out whenever you're ready. "
            
            summary += "Is there anything else I can help you with today?"
            
            # Mark call as complete
            self.lead_state.call_complete = True
            await self._send_lead_update()
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to save lead: {e}")
            return f"Thank you for your time, {self.lead_state.name}! I've noted all your information and our team will be in touch at {self.lead_state.email}. Is there anything else I can help with?"
