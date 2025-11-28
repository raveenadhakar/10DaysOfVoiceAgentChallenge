import logging
import json
import os
import random
from datetime import datetime
from typing import Dict, List, Optional

from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    MetricsCollectedEvent,
    WorkerOptions,
    cli,
    metrics,
    tokenize,
    function_tool,
    RunContext
)
from livekit import rtc
from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("agent")

load_dotenv(".env")

# Wellness check-in state structure
class WellnessState:
    def __init__(self):
        self.mood: Optional[str] = None
        self.energy_level: Optional[str] = None
        self.stress_factors: List[str] = []
        self.daily_objectives: List[str] = []
        self.self_care_intentions: List[str] = []
        self.check_in_complete: bool = False
    
    def to_dict(self) -> Dict:
        return {
            "mood": self.mood,
            "energy_level": self.energy_level,
            "stress_factors": self.stress_factors,
            "daily_objectives": self.daily_objectives,
            "self_care_intentions": self.self_care_intentions,
            "check_in_complete": self.check_in_complete
        }
    
    def is_complete(self) -> bool:
        return (
            self.mood is not None and 
            self.energy_level is not None and 
            len(self.daily_objectives) > 0
        )
    
    def get_missing_fields(self) -> List[str]:
        missing = []
        if not self.mood:
            missing.append("mood")
        if not self.energy_level:
            missing.append("energy level")
        if not self.daily_objectives:
            missing.append("daily objectives")
        return missing


class HealthWellnessCompanion(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are Alex, a supportive and grounded health & wellness companion. You conduct daily check-ins to help people reflect on their mood, energy, and daily intentions.

            Your personality:
            - Warm, empathetic, and genuinely caring
            - Supportive but realistic and grounded
            - Non-judgmental and encouraging
            - Use gentle, conversational language
            - Focus on small, actionable steps

            IMPORTANT: You are NOT a medical professional. Avoid any diagnosis, medical advice, or clinical claims.

            Your role is to:
            1. Ask about mood and energy levels in a caring way
            2. Inquire about any stress factors (without being intrusive)
            3. Help identify 1-3 practical daily objectives
            4. Suggest simple self-care activities if appropriate
            5. Offer small, realistic advice and reflections
            6. Provide a brief recap to confirm understanding

            Keep your suggestions:
            - Small and actionable
            - Non-medical and non-diagnostic
            - Grounded in practical daily life
            - Examples: taking short breaks, going for walks, breaking tasks into smaller steps

            Always reference previous check-ins when available to show continuity and care.

            Keep responses concise and natural - you're having a supportive conversation, not giving a lecture.""",
        )
        self.wellness_state = WellnessState()
        self._room = None
        self.wellness_log_file = "wellness_log.json"

    def set_room(self, room):
        """Set the room for sending data updates."""
        self._room = room

    async def _send_wellness_update(self):
        """Send wellness state update to frontend via data channel."""
        if self._room:
            try:
                wellness_data = {
                    "type": "wellness_update",
                    "data": self.wellness_state.to_dict()
                }
                await self._room.local_participant.publish_data(
                    json.dumps(wellness_data).encode('utf-8'),
                    topic="wellness_checkin"
                )
                logger.info(f"Sent wellness update: {wellness_data}")
            except Exception as e:
                logger.error(f"Failed to send wellness update: {e}")

    def _load_previous_entries(self) -> List[Dict]:
        """Load previous wellness check-in entries from JSON file."""
        try:
            if os.path.exists(self.wellness_log_file):
                with open(self.wellness_log_file, 'r') as f:
                    data = json.load(f)
                    return data.get('entries', [])
        except Exception as e:
            logger.error(f"Failed to load previous entries: {e}")
        return []

    def _get_previous_context(self) -> str:
        """Get context from previous check-ins for conversation continuity."""
        entries = self._load_previous_entries()
        if not entries:
            return "This is our first check-in together."
        
        # Get the most recent entry
        last_entry = entries[-1]
        last_date = last_entry.get('date', 'recently')
        last_mood = last_entry.get('mood', 'unknown')
        last_energy = last_entry.get('energy_level', 'unknown')
        
        context = f"Last time we talked on {last_date}, you mentioned feeling {last_mood} with {last_energy} energy."
        
        # Add objectives context if available
        if last_entry.get('daily_objectives'):
            objectives = last_entry['daily_objectives'][:2]  # First 2 objectives
            context += f" You had goals like: {', '.join(objectives)}."
        
        return context

    @function_tool
    async def record_mood(self, context: RunContext, mood: str):
        """Record the user's current mood.
        
        Args:
            mood: Description of current mood (e.g., happy, stressed, tired, energetic, anxious, calm)
        """
        self.wellness_state.mood = mood.lower()
        logger.info(f"Recorded mood: {mood}")
        await self._send_wellness_update()
        return f"I hear that you're feeling {mood}. Thank you for sharing that with me."

    @function_tool
    async def record_energy_level(self, context: RunContext, energy_level: str):
        """Record the user's current energy level.
        
        Args:
            energy_level: Description of energy level (e.g., high, low, moderate, drained, energized)
        """
        self.wellness_state.energy_level = energy_level.lower()
        logger.info(f"Recorded energy level: {energy_level}")
        await self._send_wellness_update()
        return f"Got it, your energy is {energy_level} today."

    @function_tool
    async def add_stress_factor(self, context: RunContext, stress_factor: str):
        """Add something that's causing stress or concern.
        
        Args:
            stress_factor: Something causing stress (e.g., work deadline, family situation, health concern)
        """
        if stress_factor.lower() not in self.wellness_state.stress_factors:
            self.wellness_state.stress_factors.append(stress_factor.lower())
        logger.info(f"Added stress factor: {stress_factor}")
        await self._send_wellness_update()
        return f"I understand that {stress_factor} is weighing on you right now."

    @function_tool
    async def add_daily_objective(self, context: RunContext, objective: str):
        """Add a daily goal or objective the user wants to accomplish.
        
        Args:
            objective: A goal or task for today (e.g., finish report, exercise, call family)
        """
        if objective.lower() not in self.wellness_state.daily_objectives:
            self.wellness_state.daily_objectives.append(objective.lower())
        logger.info(f"Added daily objective: {objective}")
        await self._send_wellness_update()
        return f"That sounds like a great goal: {objective}."

    @function_tool
    async def add_self_care_intention(self, context: RunContext, intention: str):
        """Add a self-care activity or intention for the day.
        
        Args:
            intention: Self-care activity (e.g., take a walk, read a book, meditate, rest)
        """
        if intention.lower() not in self.wellness_state.self_care_intentions:
            self.wellness_state.self_care_intentions.append(intention.lower())
        logger.info(f"Added self-care intention: {intention}")
        await self._send_wellness_update()
        return f"That's wonderful - {intention} sounds like great self-care."

    @function_tool
    async def get_previous_context(self, context: RunContext):
        """Get information from previous check-ins to provide continuity."""
        previous_context = self._get_previous_context()
        return previous_context

    @function_tool
    async def check_wellness_status(self, context: RunContext):
        """Check what information is still needed to complete the wellness check-in."""
        missing = self.wellness_state.get_missing_fields()
        if not missing:
            return "We've covered the main areas! Let me give you a recap of our check-in."
        else:
            return f"I'd still like to hear about: {', '.join(missing)}"

    @function_tool
    async def complete_checkin(self, context: RunContext):
        """Complete and save the wellness check-in when all information is collected."""
        if not self.wellness_state.is_complete():
            missing = self.wellness_state.get_missing_fields()
            return f"Let's make sure we cover {', '.join(missing)} before we wrap up our check-in."
        
        # Prepare check-in data
        timestamp = datetime.now()
        checkin_data = {
            **self.wellness_state.to_dict(),
            "date": timestamp.strftime("%Y-%m-%d"),
            "time": timestamp.strftime("%H:%M:%S"),
            "timestamp": timestamp.isoformat(),
            "summary": f"Feeling {self.wellness_state.mood} with {self.wellness_state.energy_level} energy. Goals: {', '.join(self.wellness_state.daily_objectives[:3])}"
        }
        
        # Load existing entries or create new structure
        wellness_log = {"entries": []}
        try:
            if os.path.exists(self.wellness_log_file):
                with open(self.wellness_log_file, 'r') as f:
                    wellness_log = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load existing wellness log: {e}")
        
        # Add new entry
        wellness_log["entries"].append(checkin_data)
        
        # Save to JSON file
        try:
            with open(self.wellness_log_file, 'w') as f:
                json.dump(wellness_log, f, indent=2)
            
            logger.info(f"Wellness check-in saved to {self.wellness_log_file}")
            
            # Send completion notification
            completion_data = {
                "type": "checkin_complete",
                "data": checkin_data
            }
            if self._room:
                await self._room.local_participant.publish_data(
                    json.dumps(completion_data).encode('utf-8'),
                    topic="wellness_checkin"
                )
            
            # Create summary
            objectives_text = ', '.join(self.wellness_state.daily_objectives[:3])
            stress_text = f" I also noted that {', '.join(self.wellness_state.stress_factors)} is on your mind." if self.wellness_state.stress_factors else ""
            self_care_text = f" For self-care, you're planning to {', '.join(self.wellness_state.self_care_intentions)}." if self.wellness_state.self_care_intentions else ""
            
            summary = f"Thank you for sharing with me today. To recap: you're feeling {self.wellness_state.mood} with {self.wellness_state.energy_level} energy, and your main goals are {objectives_text}.{stress_text}{self_care_text} Does this sound right? I've saved our check-in and I'm here whenever you need to talk."
            
            # Mark check-in as complete but don't reset state yet (for confirmation)
            self.wellness_state.check_in_complete = True
            await self._send_wellness_update()
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to save wellness check-in: {e}")
            return "I'm sorry, there was an issue saving our check-in. But I want you to know that I heard everything you shared with me today."

    @function_tool
    async def start_new_checkin(self, context: RunContext):
        """Start a fresh wellness check-in session."""
        # Reset wellness state for new check-in
        self.wellness_state = WellnessState()
        await self._send_wellness_update()
        
        # Get previous context for continuity
        previous_context = self._get_previous_context()
        
        return f"Hello! I'm here for your daily wellness check-in. {previous_context} How are you feeling today?"


# Tutor Content Management
class TutorContent:
    def __init__(self, content_file: str = "shared-data/day4_tutor_content.json"):
        self.content_file = content_file
        self.concepts = self._load_content()
    
    def _load_content(self) -> List[Dict]:
        """Load tutor content from JSON file."""
        try:
            with open(self.content_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load tutor content: {e}")
            return []
    
    def get_concept(self, concept_id: str) -> Optional[Dict]:
        """Get a specific concept by ID."""
        for concept in self.concepts:
            if concept['id'] == concept_id:
                return concept
        return None
    
    def get_all_concepts(self) -> List[Dict]:
        """Get all available concepts."""
        return self.concepts
    
    def get_random_concept(self) -> Optional[Dict]:
        """Get a random concept for learning."""
        if self.concepts:
            return random.choice(self.concepts)
        return None


# Base Tutor Agent
class BaseTutorAgent(Agent):
    def __init__(self, mode: str, voice: str, instructions: str):
        super().__init__(instructions=instructions)
        self.mode = mode
        self.voice = voice
        self.tutor_content = TutorContent()
        self.current_concept = None
        self._room = None
    
    def set_room(self, room):
        """Set the room for sending data updates."""
        self._room = room
    
    async def _send_mode_update(self, data: Dict):
        """Send mode-specific update to frontend."""
        if self._room:
            try:
                update_data = {
                    "type": "tutor_update",
                    "mode": self.mode,
                    "data": data
                }
                await self._room.local_participant.publish_data(
                    json.dumps(update_data).encode('utf-8'),
                    topic="tutor_session"
                )
                logger.info(f"Sent tutor update for {self.mode}: {data}")
            except Exception as e:
                logger.error(f"Failed to send tutor update: {e}")


# Learn Mode Agent - Matthew voice
class LearnModeAgent(BaseTutorAgent):
    def __init__(self):
        super().__init__(
            mode="learn",
            voice="en-US-matthew",
            instructions="""You are Matthew, a knowledgeable and patient programming tutor in LEARN mode. Your role is to explain programming concepts clearly and engagingly.

            Your personality:
            - Clear, methodical, and thorough in explanations
            - Patient and encouraging
            - Uses simple analogies and real-world examples
            - Breaks down complex topics into digestible parts
            - Enthusiastic about teaching programming

            Your role:
            - Explain programming concepts from the content file
            - Use analogies and examples to make concepts clear
            - Encourage questions and curiosity
            - Keep explanations focused but comprehensive
            - Help users understand the 'why' behind concepts

            Always be ready to switch modes when the user asks to quiz or teach back."""
        )
    
    @function_tool
    async def explain_concept(self, context: RunContext, concept_id: str):
        """Explain a specific programming concept in detail.
        
        Args:
            concept_id: The ID of the concept to explain (variables, loops, functions, conditionals)
        """
        concept = self.tutor_content.get_concept(concept_id)
        if not concept:
            return f"I don't have information about '{concept_id}'. Available concepts are: {', '.join([c['id'] for c in self.tutor_content.get_all_concepts()])}"
        
        self.current_concept = concept
        await self._send_mode_update({
            "current_concept": concept,
            "action": "explaining"
        })
        
        explanation = f"Let me explain {concept['title']} for you. {concept['summary']} "
        explanation += f"This is a fundamental concept in programming that you'll use constantly. "
        explanation += f"Would you like me to go deeper into any aspect of {concept['title']}, or are you ready to test your understanding?"
        
        return explanation
    
    @function_tool
    async def list_available_concepts(self, context: RunContext):
        """List all available programming concepts that can be learned."""
        concepts = self.tutor_content.get_all_concepts()
        concept_list = ", ".join([f"{c['title']} ({c['id']})" for c in concepts])
        return f"I can teach you about these programming concepts: {concept_list}. Which one would you like to learn about?"
    
    @function_tool
    async def get_random_concept(self, context: RunContext):
        """Get a random concept to learn about."""
        concept = self.tutor_content.get_random_concept()
        if concept:
            return await self.explain_concept(context, concept['id'])
        return "I don't have any concepts available to teach right now."


# Quiz Mode Agent - Alicia voice  
class QuizModeAgent(BaseTutorAgent):
    def __init__(self):
        super().__init__(
            mode="quiz",
            voice="en-US-alicia",
            instructions="""You are Alicia, an engaging and supportive programming tutor in QUIZ mode. Your role is to test the user's understanding through questions.

            Your personality:
            - Encouraging and supportive
            - Clear in asking questions
            - Provides helpful feedback on answers
            - Celebrates correct answers enthusiastically
            - Gently corrects mistakes with explanations
            - Builds confidence while challenging understanding

            Your role:
            - Ask questions about programming concepts
            - Evaluate user responses fairly
            - Provide constructive feedback
            - Offer hints when users struggle
            - Keep the quiz engaging and educational

            Always be ready to switch modes when the user asks to learn or teach back."""
        )
        self.current_question = None
        self.correct_answer_keywords = []
    
    @function_tool
    async def ask_question_about_concept(self, context: RunContext, concept_id: str):
        """Ask a quiz question about a specific programming concept.
        
        Args:
            concept_id: The ID of the concept to quiz about (variables, loops, functions, conditionals)
        """
        concept = self.tutor_content.get_concept(concept_id)
        if not concept:
            return f"I don't have quiz questions about '{concept_id}'. Available concepts are: {', '.join([c['id'] for c in self.tutor_content.get_all_concepts()])}"
        
        self.current_concept = concept
        self.current_question = concept['sample_question']
        
        # Set up keywords for answer evaluation
        if concept_id == "variables":
            self.correct_answer_keywords = ["store", "container", "data", "value", "reuse"]
        elif concept_id == "loops":
            self.correct_answer_keywords = ["repeat", "iteration", "for", "while", "condition"]
        elif concept_id == "functions":
            self.correct_answer_keywords = ["reusable", "parameters", "return", "organize", "block"]
        elif concept_id == "conditionals":
            self.correct_answer_keywords = ["decision", "if", "condition", "true", "false"]
        
        await self._send_mode_update({
            "current_concept": concept,
            "current_question": self.current_question,
            "action": "asking_question"
        })
        
        return f"Great! Let's test your understanding of {concept['title']}. Here's your question: {self.current_question}"
    
    @function_tool
    async def evaluate_answer(self, context: RunContext, user_answer: str):
        """Evaluate the user's answer to the current quiz question.
        
        Args:
            user_answer: The user's response to the quiz question
        """
        if not self.current_question:
            return "I haven't asked a question yet. Would you like me to ask you about a specific concept?"
        
        # Simple keyword-based evaluation
        answer_lower = user_answer.lower()
        matched_keywords = [keyword for keyword in self.correct_answer_keywords if keyword in answer_lower]
        
        score = len(matched_keywords) / len(self.correct_answer_keywords) if self.correct_answer_keywords else 0
        
        await self._send_mode_update({
            "user_answer": user_answer,
            "score": score,
            "matched_keywords": matched_keywords,
            "action": "answer_evaluated"
        })
        
        if score >= 0.5:  # 50% or more keywords matched
            feedback = f"Excellent answer! You mentioned key points like {', '.join(matched_keywords)}. "
            feedback += f"You clearly understand {self.current_concept['title']}. "
            feedback += "Would you like to try another question or switch to teach-back mode to explain a concept to me?"
        elif score >= 0.25:  # 25-49% keywords matched
            feedback = f"Good start! You got some important points like {', '.join(matched_keywords)}. "
            feedback += f"Let me give you a hint: {self.current_concept['summary'][:100]}... "
            feedback += "Would you like to try answering again or move on to another concept?"
        else:  # Less than 25% keywords matched
            feedback = f"That's a good attempt! Let me help you understand {self.current_concept['title']} better. "
            feedback += f"{self.current_concept['summary']} "
            feedback += "Now that you have more context, would you like to try the question again?"
        
        return feedback
    
    @function_tool
    async def get_hint(self, context: RunContext):
        """Provide a hint for the current quiz question."""
        if not self.current_concept:
            return "I haven't asked a question yet. Would you like me to quiz you on a specific concept?"
        
        hint = f"Here's a hint for {self.current_concept['title']}: "
        hint += self.current_concept['summary'][:150] + "..."
        return hint


# Teach Back Mode Agent - Ken voice
class TeachBackModeAgent(BaseTutorAgent):
    def __init__(self):
        super().__init__(
            mode="teach_back",
            voice="en-US-ken",
            instructions="""You are Ken, an attentive and encouraging programming tutor in TEACH-BACK mode. Your role is to listen as students explain concepts back to you.

            Your personality:
            - Attentive and patient listener
            - Encouraging and supportive
            - Asks thoughtful follow-up questions
            - Provides gentle corrections when needed
            - Celebrates good explanations
            - Helps students think through concepts

            Your role:
            - Ask students to explain programming concepts
            - Listen carefully to their explanations
            - Ask clarifying questions to deepen understanding
            - Provide feedback on their explanations
            - Help them fill in gaps in their knowledge
            - Encourage them to think through examples

            Always be ready to switch modes when the user asks to learn or take a quiz."""
        )
        self.explanation_in_progress = False
    
    @function_tool
    async def request_explanation(self, context: RunContext, concept_id: str):
        """Ask the user to explain a programming concept back to you.
        
        Args:
            concept_id: The ID of the concept for the user to explain (variables, loops, functions, conditionals)
        """
        concept = self.tutor_content.get_concept(concept_id)
        if not concept:
            return f"I don't have information about '{concept_id}'. Available concepts are: {', '.join([c['id'] for c in self.tutor_content.get_all_concepts()])}"
        
        self.current_concept = concept
        self.explanation_in_progress = True
        
        await self._send_mode_update({
            "current_concept": concept,
            "action": "requesting_explanation"
        })
        
        return f"Perfect! I'd love to hear you explain {concept['title']} to me. Pretend I'm a complete beginner - can you teach me what {concept['title'].lower()} are and why they're important in programming? Take your time and explain it in your own words."
    
    @function_tool
    async def provide_feedback(self, context: RunContext, user_explanation: str):
        """Provide feedback on the user's explanation of a concept.
        
        Args:
            user_explanation: The user's explanation of the programming concept
        """
        if not self.current_concept:
            return "I haven't asked you to explain anything yet. Would you like me to ask you to explain a specific concept?"
        
        # Analyze the explanation for key concepts
        explanation_lower = user_explanation.lower()
        concept_id = self.current_concept['id']
        
        # Define key points for each concept
        key_points = {
            "variables": ["store", "data", "value", "container", "reuse", "name"],
            "loops": ["repeat", "iteration", "for", "while", "condition", "multiple"],
            "functions": ["reusable", "parameters", "return", "organize", "input", "output"],
            "conditionals": ["decision", "if", "condition", "true", "false", "branch"]
        }
        
        covered_points = []
        if concept_id in key_points:
            covered_points = [point for point in key_points[concept_id] if point in explanation_lower]
        
        coverage_score = len(covered_points) / len(key_points.get(concept_id, [])) if concept_id in key_points else 0
        
        await self._send_mode_update({
            "user_explanation": user_explanation,
            "covered_points": covered_points,
            "coverage_score": coverage_score,
            "action": "feedback_provided"
        })
        
        feedback = f"Thank you for that explanation! "
        
        if coverage_score >= 0.7:  # 70% or more key points covered
            feedback += f"You did an excellent job explaining {self.current_concept['title']}! "
            feedback += f"You covered the key concepts like {', '.join(covered_points)}. "
            feedback += "Your explanation shows you really understand this topic. "
            feedback += "Would you like to explain another concept or try a different learning mode?"
        elif coverage_score >= 0.4:  # 40-69% key points covered
            feedback += f"That's a good explanation! You mentioned important points like {', '.join(covered_points)}. "
            feedback += f"Can you also tell me about how {self.current_concept['title'].lower()} help with organizing code or making it more efficient? "
            feedback += "What examples can you think of?"
        else:  # Less than 40% key points covered
            feedback += f"I can see you're thinking about {self.current_concept['title']}! "
            feedback += f"Let me ask you this: {self.current_concept['sample_question']} "
            feedback += "Try to think about the main purpose and benefits. What problem do they solve?"
        
        return feedback
    
    @function_tool
    async def ask_follow_up_question(self, context: RunContext, topic: str):
        """Ask a follow-up question to deepen the user's explanation.
        
        Args:
            topic: The specific aspect to ask about (examples, benefits, usage, etc.)
        """
        if not self.current_concept:
            return "I haven't asked you to explain anything yet. Would you like me to ask you to explain a specific concept?"
        
        concept_title = self.current_concept['title']
        
        follow_up_questions = {
            "examples": f"Can you give me a specific example of how you would use {concept_title.lower()} in a real program?",
            "benefits": f"What are the main benefits of using {concept_title.lower()} in programming?",
            "usage": f"When would you choose to use {concept_title.lower()} in your code?",
            "comparison": f"How do {concept_title.lower()} compare to other programming concepts you know?",
            "problems": f"What problems do {concept_title.lower()} help solve in programming?"
        }
        
        question = follow_up_questions.get(topic, f"Can you tell me more about {concept_title.lower()}?")
        return f"That's interesting! {question}"


# Main Tutor Coordinator Agent
class TutorCoordinatorAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions="""You are the Teach-the-Tutor Active Recall Coach. You help users learn programming concepts through three different modes.

            Available modes and voices:
            - LEARN: You explain programming concepts clearly (Matthew's voice)
            - QUIZ: You test understanding with questions (Alicia's voice)  
            - TEACH_BACK: You listen as users explain concepts back (Ken's voice)

            Available concepts: variables, loops, functions, conditionals

            Your role:
            - Start by greeting users and explaining the three learning modes
            - Help users choose the right mode for their needs
            - Switch between modes when requested
            - In LEARN mode: explain concepts clearly with examples
            - In QUIZ mode: ask questions and evaluate answers
            - In TEACH_BACK mode: listen to explanations and provide feedback
            - Keep track of learning progress
            - Encourage active learning and recall

            Always be enthusiastic about learning and adapt your personality to the current mode."""
        )
        self.current_mode = "coordinator"
        self.tutor_content = TutorContent()
        self.current_concept = None
        self._room = None
    
    def set_room(self, room):
        """Set the room for sending updates."""
        self._room = room
    
    async def _send_mode_change(self, new_mode: str):
        """Send mode change notification to frontend."""
        if self._room:
            try:
                mode_data = {
                    "type": "mode_change",
                    "new_mode": new_mode,
                    "previous_mode": self.current_mode,
                    "data": {
                        "concept_id": self.current_concept['id'] if self.current_concept else None,
                        "activity": f"Switched to {new_mode} mode",
                        "timestamp": datetime.now().isoformat()
                    }
                }
                await self._room.local_participant.publish_data(
                    json.dumps(mode_data).encode('utf-8'),
                    topic="tutor_session"
                )
                logger.info(f"Mode changed from {self.current_mode} to {new_mode}")
            except Exception as e:
                logger.error(f"Failed to send mode change: {e}")
    
    async def _send_tutor_update(self, activity: str, score: float = None, concept_id: str = None):
        """Send learning activity update to frontend."""
        if self._room:
            try:
                update_data = {
                    "type": "tutor_update",
                    "mode": self.current_mode,
                    "data": {
                        "activity": activity,
                        "score": score,
                        "concept_id": concept_id or (self.current_concept['id'] if self.current_concept else None),
                        "current_concept": self.current_concept,
                        "timestamp": datetime.now().isoformat()
                    }
                }
                await self._room.local_participant.publish_data(
                    json.dumps(update_data).encode('utf-8'),
                    topic="tutor_session"
                )
                logger.info(f"Sent tutor update: {activity}")
            except Exception as e:
                logger.error(f"Failed to send tutor update: {e}")
    
    @function_tool
    async def switch_to_learn_mode(self, context: RunContext):
        """Switch to LEARN mode where Matthew explains concepts."""
        self.current_mode = "learn"
        await self._send_mode_change("learn")
        # Note: Voice switching would need to be handled at the session level
        return "Switching to LEARN mode! Matthew will now explain programming concepts to you. What would you like to learn about? Available concepts: variables, loops, functions, conditionals."
    
    @function_tool
    async def switch_to_quiz_mode(self, context: RunContext):
        """Switch to QUIZ mode where Alicia tests your understanding."""
        self.current_mode = "quiz"
        await self._send_mode_change("quiz")
        return "Switching to QUIZ mode! Alicia will now test your understanding with questions. Which concept would you like to be quizzed on? Available concepts: variables, loops, functions, conditionals."
    
    @function_tool
    async def switch_to_teach_back_mode(self, context: RunContext):
        """Switch to TEACH_BACK mode where Ken listens to your explanations."""
        self.current_mode = "teach_back"
        await self._send_mode_change("teach_back")
        return "Switching to TEACH_BACK mode! Ken is ready to listen as you explain programming concepts. Which concept would you like to teach back? Available concepts: variables, loops, functions, conditionals."
    
    @function_tool
    async def explain_learning_modes(self, context: RunContext):
        """Explain the three available learning modes."""
        explanation = """Welcome to the Teach-the-Tutor Active Recall Coach! I offer three learning modes:

        🎓 LEARN Mode (Matthew): I'll explain programming concepts clearly with examples and analogies. Perfect for learning new topics.

        🧠 QUIZ Mode (Alicia): I'll test your understanding with questions and provide feedback. Great for checking what you know.

        👨‍🏫 TEACH_BACK Mode (Ken): You explain concepts back to me, and I'll listen and provide feedback. The best way to solidify your learning!

        Which mode would you like to start with? Just say 'learn', 'quiz', or 'teach back' followed by the concept you're interested in."""
        
        return explanation
    
    @function_tool
    async def get_current_mode(self, context: RunContext):
        """Get the current learning mode."""
        if self.current_mode and self.current_mode != "coordinator":
            return f"You're currently in {self.current_mode.upper()} mode. You can switch modes anytime by saying 'switch to learn', 'switch to quiz', or 'switch to teach back'."
        else:
            return "You haven't selected a learning mode yet. Would you like me to explain the available modes?"

    # LEARN MODE FUNCTIONS
    @function_tool
    async def explain_concept(self, context: RunContext, concept_id: str):
        """Explain a specific programming concept in detail (LEARN mode).
        
        Args:
            concept_id: The ID of the concept to explain (variables, loops, functions, conditionals)
        """
        concept = self.tutor_content.get_concept(concept_id)
        if not concept:
            return f"I don't have information about '{concept_id}'. Available concepts are: {', '.join([c['id'] for c in self.tutor_content.get_all_concepts()])}"
        
        self.current_concept = concept
        self.current_mode = "learn"
        await self._send_mode_change("learn")
        await self._send_tutor_update(f"Started learning {concept['title']}", concept_id=concept_id)
        
        explanation = f"Let me explain {concept['title']} for you. {concept['summary']} "
        explanation += f"This is a fundamental concept in programming that you'll use constantly. "
        explanation += f"Would you like me to go deeper into any aspect of {concept['title']}, or are you ready to test your understanding?"
        
        return explanation

    @function_tool
    async def list_available_concepts(self, context: RunContext):
        """List all available programming concepts that can be learned."""
        concepts = self.tutor_content.get_all_concepts()
        concept_list = ", ".join([f"{c['title']} ({c['id']})" for c in concepts])
        return f"I can teach you about these programming concepts: {concept_list}. Which one would you like to learn about?"

    # QUIZ MODE FUNCTIONS
    @function_tool
    async def ask_question_about_concept(self, context: RunContext, concept_id: str):
        """Ask a quiz question about a specific programming concept (QUIZ mode).
        
        Args:
            concept_id: The ID of the concept to quiz about (variables, loops, functions, conditionals)
        """
        concept = self.tutor_content.get_concept(concept_id)
        if not concept:
            return f"I don't have quiz questions about '{concept_id}'. Available concepts are: {', '.join([c['id'] for c in self.tutor_content.get_all_concepts()])}"
        
        self.current_concept = concept
        self.current_mode = "quiz"
        await self._send_mode_change("quiz")
        await self._send_tutor_update(f"Started quiz on {concept['title']}", concept_id=concept_id)
        
        return f"Great! Let's test your understanding of {concept['title']}. Here's your question: {concept['sample_question']}"

    @function_tool
    async def evaluate_answer(self, context: RunContext, user_answer: str):
        """Evaluate the user's answer to the current quiz question (QUIZ mode).
        
        Args:
            user_answer: The user's response to the quiz question
        """
        if not self.current_concept:
            return "I haven't asked a question yet. Would you like me to ask you about a specific concept?"
        
        # Simple keyword-based evaluation
        answer_lower = user_answer.lower()
        concept_id = self.current_concept['id']
        
        # Define key points for each concept
        key_points = {
            "variables": ["store", "container", "data", "value", "reuse"],
            "loops": ["repeat", "iteration", "for", "while", "condition"],
            "functions": ["reusable", "parameters", "return", "organize", "block"],
            "conditionals": ["decision", "if", "condition", "true", "false"]
        }
        
        matched_keywords = []
        if concept_id in key_points:
            matched_keywords = [keyword for keyword in key_points[concept_id] if keyword in answer_lower]
        
        score = len(matched_keywords) / len(key_points.get(concept_id, [])) if concept_id in key_points else 0
        
        # Send score update to frontend
        await self._send_tutor_update(f"Answered question about {self.current_concept['title']}", score=score)
        
        if score >= 0.5:  # 50% or more keywords matched
            feedback = f"Excellent answer! You mentioned key points like {', '.join(matched_keywords)}. "
            feedback += f"You clearly understand {self.current_concept['title']}. "
            feedback += "Would you like to try another question or switch to teach-back mode to explain a concept to me?"
        elif score >= 0.25:  # 25-49% keywords matched
            feedback = f"Good start! You got some important points like {', '.join(matched_keywords)}. "
            feedback += f"Let me give you a hint: {self.current_concept['summary'][:100]}... "
            feedback += "Would you like to try answering again or move on to another concept?"
        else:  # Less than 25% keywords matched
            feedback = f"That's a good attempt! Let me help you understand {self.current_concept['title']} better. "
            feedback += f"{self.current_concept['summary']} "
            feedback += "Now that you have more context, would you like to try the question again?"
        
        return feedback

    # TEACH BACK MODE FUNCTIONS
    @function_tool
    async def request_explanation(self, context: RunContext, concept_id: str):
        """Ask the user to explain a programming concept back (TEACH_BACK mode).
        
        Args:
            concept_id: The ID of the concept for the user to explain (variables, loops, functions, conditionals)
        """
        concept = self.tutor_content.get_concept(concept_id)
        if not concept:
            return f"I don't have information about '{concept_id}'. Available concepts are: {', '.join([c['id'] for c in self.tutor_content.get_all_concepts()])}"
        
        self.current_concept = concept
        self.current_mode = "teach_back"
        await self._send_mode_change("teach_back")
        await self._send_tutor_update(f"Started teach-back session for {concept['title']}", concept_id=concept_id)
        
        return f"Perfect! I'd love to hear you explain {concept['title']} to me. Pretend I'm a complete beginner - can you teach me what {concept['title'].lower()} are and why they're important in programming? Take your time and explain it in your own words."

    @function_tool
    async def provide_feedback(self, context: RunContext, user_explanation: str):
        """Provide feedback on the user's explanation of a concept (TEACH_BACK mode).
        
        Args:
            user_explanation: The user's explanation of the programming concept
        """
        if not self.current_concept:
            return "I haven't asked you to explain anything yet. Would you like me to ask you to explain a specific concept?"
        
        # Analyze the explanation for key concepts
        explanation_lower = user_explanation.lower()
        concept_id = self.current_concept['id']
        
        # Define key points for each concept
        key_points = {
            "variables": ["store", "data", "value", "container", "reuse", "name"],
            "loops": ["repeat", "iteration", "for", "while", "condition", "multiple"],
            "functions": ["reusable", "parameters", "return", "organize", "input", "output"],
            "conditionals": ["decision", "if", "condition", "true", "false", "branch"]
        }
        
        covered_points = []
        if concept_id in key_points:
            covered_points = [point for point in key_points[concept_id] if point in explanation_lower]
        
        coverage_score = len(covered_points) / len(key_points.get(concept_id, [])) if concept_id in key_points else 0
        
        # Send feedback score to frontend
        await self._send_tutor_update(f"Explained {self.current_concept['title']} in teach-back mode", score=coverage_score)
        
        feedback = f"Thank you for that explanation! "
        
        if coverage_score >= 0.7:  # 70% or more key points covered
            feedback += f"You did an excellent job explaining {self.current_concept['title']}! "
            feedback += f"You covered the key concepts like {', '.join(covered_points)}. "
            feedback += "Your explanation shows you really understand this topic. "
            feedback += "Would you like to explain another concept or try a different learning mode?"
        elif coverage_score >= 0.4:  # 40-69% key points covered
            feedback += f"That's a good explanation! You mentioned important points like {', '.join(covered_points)}. "
            feedback += f"Can you also tell me about how {self.current_concept['title'].lower()} help with organizing code or making it more efficient? "
            feedback += "What examples can you think of?"
        else:  # Less than 40% key points covered
            feedback += f"I can see you're thinking about {self.current_concept['title']}! "
            feedback += f"Let me ask you this: {self.current_concept['sample_question']} "
            feedback += "Try to think about the main purpose and benefits. What problem do they solve?"
        
        return feedback


# SDR Lead State
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


# Company FAQ Manager
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


# SDR Agent
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
        self.leads_file = "leads.json"
    
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
                summary += "Since you're looking to get started right away, our team will reach out to you at {self.lead_state.email} within the next few hours to help you get set up. "
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


# Food Ordering Cart State
class CartState:
    def __init__(self):
        self.items: List[Dict] = []
        self.customer_name: Optional[str] = None
        self.customer_address: Optional[str] = None
        self.order_complete: bool = False
    
    def add_item(self, item: Dict, quantity: int = 1, notes: str = ""):
        """Add an item to the cart."""
        # Check if item already exists in cart
        for cart_item in self.items:
            if cart_item["id"] == item["id"] and cart_item.get("notes", "") == notes:
                cart_item["quantity"] += quantity
                return
        
        # Add new item to cart
        cart_item = {
            **item,
            "quantity": quantity,
            "notes": notes,
            "subtotal": item["price"] * quantity
        }
        self.items.append(cart_item)
    
    def remove_item(self, item_id: str):
        """Remove an item from the cart."""
        self.items = [item for item in self.items if item["id"] != item_id]
    
    def update_quantity(self, item_id: str, new_quantity: int):
        """Update the quantity of an item in the cart."""
        for item in self.items:
            if item["id"] == item_id:
                if new_quantity <= 0:
                    self.remove_item(item_id)
                else:
                    item["quantity"] = new_quantity
                    item["subtotal"] = item["price"] * new_quantity
                break
    
    def get_total(self) -> float:
        """Calculate the total price of items in cart."""
        return sum(item["subtotal"] for item in self.items)
    
    def get_item_count(self) -> int:
        """Get total number of items in cart."""
        return sum(item["quantity"] for item in self.items)
    
    def clear(self):
        """Clear all items from cart."""
        self.items = []
    
    def to_dict(self) -> Dict:
        return {
            "items": self.items,
            "customer_name": self.customer_name,
            "customer_address": self.customer_address,
            "total": self.get_total(),
            "item_count": self.get_item_count(),
            "order_complete": self.order_complete
        }


# Food Catalog Manager
class FoodCatalog:
    def __init__(self, catalog_file: str = "food_catalog.json"):
        self.catalog_file = catalog_file
        self.data = self._load_catalog()
        self.items = self._flatten_items()
        self.recipes = self.data.get("recipes", {})
    
    def _load_catalog(self) -> Dict:
        """Load catalog data from JSON file."""
        try:
            with open(self.catalog_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load catalog: {e}")
            return {"catalog": {}, "recipes": {}}
    
    def _flatten_items(self) -> Dict[str, Dict]:
        """Create a flat dictionary of all items by ID."""
        items = {}
        catalog = self.data.get("catalog", {})
        for category, category_items in catalog.items():
            for item in category_items:
                items[item["id"]] = item
        return items
    
    def search_items(self, query: str) -> List[Dict]:
        """Search for items by name, category, or tags."""
        query_lower = query.lower()
        matches = []
        
        for item in self.items.values():
            # Check name
            if query_lower in item["name"].lower():
                matches.append(item)
                continue
            
            # Check category
            if query_lower in item["category"].lower():
                matches.append(item)
                continue
            
            # Check tags
            if any(query_lower in tag.lower() for tag in item.get("tags", [])):
                matches.append(item)
                continue
            
            # Check brand
            if query_lower in item.get("brand", "").lower():
                matches.append(item)
        
        return matches
    
    def get_item_by_id(self, item_id: str) -> Optional[Dict]:
        """Get an item by its ID."""
        return self.items.get(item_id)
    
    def get_recipe_ingredients(self, recipe_name: str) -> List[Dict]:
        """Get ingredients for a recipe."""
        recipe_key = recipe_name.lower().replace(" ", "_")
        recipe = self.recipes.get(recipe_key)
        
        if not recipe:
            return []
        
        ingredients = []
        for ingredient_id in recipe["ingredients"]:
            item = self.get_item_by_id(ingredient_id)
            if item:
                ingredients.append(item)
        
        return ingredients
    
    def search_recipes(self, query: str) -> List[str]:
        """Search for recipes by name."""
        query_lower = query.lower()
        matches = []
        
        for recipe_key, recipe in self.recipes.items():
            if query_lower in recipe["name"].lower() or query_lower in recipe_key:
                matches.append(recipe["name"])
        
        return matches


# Food Ordering Agent
class FoodOrderingAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions="""You are Alex, a friendly and helpful food & grocery ordering assistant for FreshMart, your neighborhood grocery store and deli.

            Your personality:
            - Warm, enthusiastic, and helpful
            - Knowledgeable about food and cooking
            - Patient with questions about products
            - Excited to help customers find what they need
            - Conversational and natural, not robotic

            Your role:
            1. Greet customers warmly and explain what you can help with
            2. Help customers find and add items to their cart
            3. Handle intelligent requests like "ingredients for pasta" or "what I need for a sandwich"
            4. Manage their cart (add, remove, update quantities)
            5. Provide information about products (price, size, brand, etc.)
            6. Confirm cart contents when asked
            7. Process orders when customers are ready to checkout
            8. Save completed orders to JSON files

            Key capabilities:
            - Search for items by name, category, or type
            - Add items with specific quantities and notes
            - Handle recipe-based requests intelligently
            - Show cart contents and totals
            - Remove or update items in cart
            - Complete orders and save them

            Guidelines:
            - Always confirm what you're adding to the cart
            - Ask for clarification on quantities, sizes, or brands when needed
            - Be helpful with suggestions for related items
            - Keep track of the running total
            - When customers say they're done, confirm the order and save it
            - Capture basic customer info (name, address) for delivery

            Remember: You're here to make grocery shopping easy and enjoyable!"""
        )
        self.cart = CartState()
        self.catalog = FoodCatalog()
        self._room = None
        self.orders_dir = "orders"
    
    def set_room(self, room):
        """Set the room for sending data updates."""
        self._room = room
    
    async def _send_cart_update(self):
        """Send cart state update to frontend via data channel."""
        if self._room:
            try:
                cart_data = {
                    "type": "cart_update",
                    "data": self.cart.to_dict()
                }
                await self._room.local_participant.publish_data(
                    json.dumps(cart_data).encode('utf-8'),
                    topic="food_ordering"
                )
                logger.info(f"Sent cart update: {self.cart.get_item_count()} items, ${self.cart.get_total():.2f}")
            except Exception as e:
                logger.error(f"Failed to send cart update: {e}")
    
    @function_tool
    async def search_products(self, context: RunContext, query: str):
        """Search for food and grocery products.
        
        Args:
            query: What to search for (e.g., "bread", "snacks", "organic", "pasta")
        """
        matches = self.catalog.search_items(query)
        
        if not matches:
            return f"I couldn't find any items matching '{query}'. Try searching for categories like 'groceries', 'snacks', or 'prepared food', or specific items like 'bread', 'milk', or 'pizza'."
        
        if len(matches) == 1:
            item = matches[0]
            return f"I found {item['name']} by {item['brand']} for ${item['price']:.2f} ({item['size']}). Would you like to add this to your cart?"
        
        # Multiple matches - show options
        result = f"I found {len(matches)} items for '{query}':\n"
        for i, item in enumerate(matches[:5], 1):  # Show first 5 matches
            result += f"{i}. {item['name']} by {item['brand']} - ${item['price']:.2f} ({item['size']})\n"
        
        if len(matches) > 5:
            result += f"...and {len(matches) - 5} more items."
        
        result += "\nWhich one would you like to add to your cart?"
        return result
    
    @function_tool
    async def add_item_to_cart(self, context: RunContext, item_name: str, quantity: int = 1, notes: str = ""):
        """Add a specific item to the cart.
        
        Args:
            item_name: Name of the item to add
            quantity: How many to add (default: 1)
            notes: Any special notes (e.g., "large size", "whole wheat")
        """
        # Search for the item
        matches = self.catalog.search_items(item_name)
        
        if not matches:
            return f"I couldn't find '{item_name}' in our catalog. Try searching first to see what's available."
        
        if len(matches) > 1:
            # Multiple matches - ask for clarification
            result = f"I found multiple items for '{item_name}':\n"
            for i, item in enumerate(matches[:3], 1):
                result += f"{i}. {item['name']} by {item['brand']} - ${item['price']:.2f}\n"
            result += "Which one did you want?"
            return result
        
        # Single match - add to cart
        item = matches[0]
        self.cart.add_item(item, quantity, notes)
        await self._send_cart_update()
        
        subtotal = item["price"] * quantity
        notes_text = f" ({notes})" if notes else ""
        
        logger.info(f"Added to cart: {quantity}x {item['name']}{notes_text} = ${subtotal:.2f}")
        
        return f"Added {quantity}x {item['name']} by {item['brand']}{notes_text} to your cart for ${subtotal:.2f}. Your cart total is now ${self.cart.get_total():.2f}."
    
    @function_tool
    async def add_recipe_ingredients(self, context: RunContext, recipe_or_dish: str):
        """Add ingredients for a specific recipe or dish.
        
        Args:
            recipe_or_dish: The recipe or dish name (e.g., "peanut butter sandwich", "pasta for two", "breakfast")
        """
        # First try exact recipe match
        ingredients = self.catalog.get_recipe_ingredients(recipe_or_dish)
        
        if not ingredients:
            # Try searching recipes
            recipe_matches = self.catalog.search_recipes(recipe_or_dish)
            if recipe_matches:
                # Use first match
                ingredients = self.catalog.get_recipe_ingredients(recipe_matches[0])
        
        if not ingredients:
            return f"I don't have a specific recipe for '{recipe_or_dish}'. Try asking for specific ingredients like 'bread and peanut butter' or search for individual items."
        
        # Add all ingredients to cart
        added_items = []
        total_added = 0
        
        for ingredient in ingredients:
            self.cart.add_item(ingredient, 1)
            added_items.append(ingredient["name"])
            total_added += ingredient["price"]
        
        await self._send_cart_update()
        
        logger.info(f"Added recipe ingredients for {recipe_or_dish}: {', '.join(added_items)}")
        
        return f"I've added all the ingredients for {recipe_or_dish} to your cart: {', '.join(added_items)}. That's ${total_added:.2f} added to your cart. Your total is now ${self.cart.get_total():.2f}."
    
    @function_tool
    async def show_cart(self, context: RunContext):
        """Show the current contents of the shopping cart."""
        if not self.cart.items:
            return "Your cart is empty. What would you like to add?"
        
        result = f"Here's what's in your cart ({self.cart.get_item_count()} items):\n\n"
        
        for item in self.cart.items:
            notes_text = f" ({item['notes']})" if item.get('notes') else ""
            result += f"• {item['quantity']}x {item['name']}{notes_text} - ${item['subtotal']:.2f}\n"
        
        result += f"\nTotal: ${self.cart.get_total():.2f}"
        
        return result
    
    @function_tool
    async def remove_item_from_cart(self, context: RunContext, item_name: str):
        """Remove an item from the cart.
        
        Args:
            item_name: Name of the item to remove
        """
        # Find matching item in cart
        removed_item = None
        for item in self.cart.items:
            if item_name.lower() in item["name"].lower():
                removed_item = item
                break
        
        if not removed_item:
            return f"I couldn't find '{item_name}' in your cart. Your cart has: {', '.join([item['name'] for item in self.cart.items])}"
        
        self.cart.remove_item(removed_item["id"])
        await self._send_cart_update()
        
        logger.info(f"Removed from cart: {removed_item['name']}")
        
        return f"Removed {removed_item['name']} from your cart. Your new total is ${self.cart.get_total():.2f}."
    
    @function_tool
    async def update_item_quantity(self, context: RunContext, item_name: str, new_quantity: int):
        """Update the quantity of an item in the cart.
        
        Args:
            item_name: Name of the item to update
            new_quantity: New quantity (use 0 to remove)
        """
        # Find matching item in cart
        target_item = None
        for item in self.cart.items:
            if item_name.lower() in item["name"].lower():
                target_item = item
                break
        
        if not target_item:
            return f"I couldn't find '{item_name}' in your cart."
        
        old_quantity = target_item["quantity"]
        
        if new_quantity <= 0:
            self.cart.remove_item(target_item["id"])
            await self._send_cart_update()
            return f"Removed {target_item['name']} from your cart. Your new total is ${self.cart.get_total():.2f}."
        else:
            self.cart.update_quantity(target_item["id"], new_quantity)
            await self._send_cart_update()
            
            logger.info(f"Updated quantity: {target_item['name']} from {old_quantity} to {new_quantity}")
            
            return f"Updated {target_item['name']} quantity from {old_quantity} to {new_quantity}. Your new total is ${self.cart.get_total():.2f}."
    
    @function_tool
    async def get_customer_info(self, context: RunContext, name: str, address: str = ""):
        """Collect customer information for the order.
        
        Args:
            name: Customer's name
            address: Customer's delivery address (optional)
        """
        self.cart.customer_name = name
        if address:
            self.cart.customer_address = address
        
        await self._send_cart_update()
        
        logger.info(f"Customer info: {name}, {address}")
        
        if address:
            return f"Got it! Order for {name}, delivering to {address}."
        else:
            return f"Thanks {name}! If you need delivery, just let me know your address."
    
    @function_tool
    async def complete_order(self, context: RunContext):
        """Complete the order and save it to a JSON file."""
        if not self.cart.items:
            return "Your cart is empty! Add some items before placing your order."
        
        if not self.cart.customer_name:
            return "I need your name to complete the order. What's your name?"
        
        # Create order data
        timestamp = datetime.now()
        order_data = {
            "order_id": f"ORDER_{timestamp.strftime('%Y%m%d_%H%M%S')}_{self.cart.customer_name.replace(' ', '')}",
            "timestamp": timestamp.isoformat(),
            "date": timestamp.strftime("%Y-%m-%d"),
            "time": timestamp.strftime("%H:%M:%S"),
            "customer": {
                "name": self.cart.customer_name,
                "address": self.cart.customer_address or "Pickup"
            },
            "items": self.cart.items,
            "summary": {
                "total_items": self.cart.get_item_count(),
                "subtotal": self.cart.get_total(),
                "tax": round(self.cart.get_total() * 0.08, 2),  # 8% tax
                "total": round(self.cart.get_total() * 1.08, 2)
            },
            "status": "confirmed"
        }
        
        # Create orders directory if it doesn't exist
        os.makedirs(self.orders_dir, exist_ok=True)
        
        # Save order to JSON file
        order_filename = f"{self.orders_dir}/{order_data['order_id']}.json"
        try:
            with open(order_filename, 'w') as f:
                json.dump(order_data, f, indent=2)
            
            logger.info(f"Order saved: {order_filename}")
            
            # Send completion notification
            if self._room:
                completion_data = {
                    "type": "order_complete",
                    "data": order_data
                }
                await self._room.local_participant.publish_data(
                    json.dumps(completion_data).encode('utf-8'),
                    topic="food_ordering"
                )
            
            # Create confirmation message
            delivery_text = f"for delivery to {self.cart.customer_address}" if self.cart.customer_address else "for pickup"
            
            confirmation = f"Perfect! Your order has been placed and saved as {order_data['order_id']}.\n\n"
            confirmation += f"Order Summary for {self.cart.customer_name}:\n"
            confirmation += f"• {self.cart.get_item_count()} items\n"
            confirmation += f"• Subtotal: ${order_data['summary']['subtotal']:.2f}\n"
            confirmation += f"• Tax: ${order_data['summary']['tax']:.2f}\n"
            confirmation += f"• Total: ${order_data['summary']['total']:.2f}\n\n"
            confirmation += f"Order {delivery_text} - we'll have it ready soon! Is there anything else I can help you with?"
            
            # Mark order as complete and clear cart
            self.cart.order_complete = True
            await self._send_cart_update()
            
            # Clear cart for next order
            self.cart = CartState()
            
            return confirmation
            
        except Exception as e:
            logger.error(f"Failed to save order: {e}")
            return f"I've confirmed your order for {self.cart.customer_name}, but there was an issue saving it. Don't worry - we have all your details and will process it manually!"


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
        self.fraud_cases_file = "fraud_cases.json"
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


def prewarm(proc: JobProcess):
    # Load VAD with more sensitive settings for better voice detection
    proc.userdata["vad"] = silero.VAD.load(
        # Shorter min speech duration to catch quick words (in seconds)
        min_speech_duration=0.05,
        # Shorter min silence duration to be more responsive (in seconds)
        min_silence_duration=0.3
    )


async def entrypoint(ctx: JobContext):
    # Logging setup
    # Add any other context you want in all log entries here
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    # Create a dynamic TTS function that can switch voices based on mode
    current_voice = {"voice": "en-US-matthew"}  # Default coordinator voice
    
    def get_tts():
        return murf.TTS(
            voice=current_voice["voice"],
            style="Conversation",
            tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
            text_pacing=True
        )

    # Set up a voice AI pipeline using OpenAI, Cartesia, AssemblyAI, and the LiveKit turn detector
    session = AgentSession(
        # Speech-to-text (STT) is your agent's ears, turning the user's speech into text that the LLM can understand
        # See all available models at https://docs.livekit.io/agents/models/stt/
        stt=deepgram.STT(
            model="nova-2",  # Using nova-2 for better real-time performance
            language="en",
            smart_format=True,
            interim_results=True,
            # Additional settings for better voice detection
            punctuate=True
        ),
        # A Large Language Model (LLM) is your agent's brain, processing user input and generating a response
        # See all available models at https://docs.livekit.io/agents/models/llm/
        llm=google.LLM(
                model="gemini-2.5-flash",
            ),
        # Text-to-speech (TTS) is your agent's voice, turning the LLM's text into speech that the user can hear
        # See all available models as well as voice selections at https://docs.livekit.io/agents/models/tts/
        tts=get_tts(),
        # VAD and turn detection are used to determine when the user is speaking and when the agent should respond
        # See more at https://docs.livekit.io/agents/build/turns
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        # allow the LLM to generate a response while waiting for the end of turn
        # See more at https://docs.livekit.io/agents/build/audio/#preemptive-generation
        preemptive_generation=True,
    )

    # To use a realtime model instead of a voice pipeline, use the following session setup instead.
    # (Note: This is for the OpenAI Realtime API. For other providers, see https://docs.livekit.io/agents/models/realtime/))
    # 1. Install livekit-agents[openai]
    # 2. Set OPENAI_API_KEY in .env
    # 3. Add `from livekit.plugins import openai` to the top of this file
    # 4. Use the following session setup instead of the version above
    # session = AgentSession(
    #     llm=openai.realtime.RealtimeModel(voice="marin")
    # )

    # Metrics collection, to measure pipeline performance
    # For more information, see https://docs.livekit.io/agents/build/metrics/
    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)

    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Usage: {summary}")

    ctx.add_shutdown_callback(log_usage)

    # # Add a virtual avatar to the session, if desired
    # # For other providers, see https://docs.livekit.io/agents/models/avatar/
    # avatar = hedra.AvatarSession(
    #   avatar_id="...",  # See https://docs.livekit.io/agents/models/avatar/plugins/hedra
    # )
    # # Start the avatar and wait for it to join
    # await avatar.start(session, room=ctx.room)

    # Determine which agent to use based on room metadata or default to Food Ordering
    # You can set agent_type in room metadata when creating the room
    agent_type = ctx.room.metadata or "food"  # Default to Food Ordering agent
    
    # Create the appropriate agent based on type
    if agent_type == "food":
        agent = FoodOrderingAgent()
        logger.info("🛒 Starting Food Ordering Agent")
    elif agent_type == "fraud":
        agent = FraudAlertAgent()
        logger.info("🚨 Starting Fraud Alert Agent")
    elif agent_type == "wellness":
        agent = HealthWellnessCompanion()
        logger.info("💚 Starting Health & Wellness Agent")
    elif agent_type == "tutor":
        agent = TutorCoordinatorAgent()
        logger.info("📚 Starting Tutor Coordinator Agent")
    elif agent_type == "sdr":
        agent = SDRAgent()
        logger.info("📞 Starting SDR Agent")
    else:
        # Fallback to food ordering if unknown type
        agent = FoodOrderingAgent()
        logger.info("🛒 Starting Food Ordering Agent (fallback)")
    
    agent.set_room(ctx.room)
    
    # Add event handlers for debugging voice input
    @session.on("user_speech_committed")
    def on_user_speech_committed(msg: str):
        logger.info(f"✅ User speech committed: '{msg}'")

    @session.on("agent_speech_committed")  
    def on_agent_speech_committed(msg: str):
        logger.info(f"🤖 Agent speech committed: '{msg}'")

    @session.on("user_started_speaking")
    def on_user_started_speaking():
        logger.info("🎤 User started speaking")

    @session.on("user_stopped_speaking")
    def on_user_stopped_speaking():
        logger.info("🔇 User stopped speaking")

    @session.on("function_calls_collected")
    def on_function_calls_collected(function_calls):
        logger.info(f"🔧 Function calls collected: {[call.function_info.name for call in function_calls]}")

    @session.on("function_calls_finished")
    def on_function_calls_finished(called_functions):
        logger.info(f"✅ Function calls finished: {[func.function_info.name for func in called_functions]}")

    # Start the session, which initializes the voice pipeline and warms up the models
    await session.start(
        agent=agent,
        room=ctx.room,
    )
    
    logger.info("🚀 Agent session started successfully")
    logger.info("🎯 Voice pipeline initialized - ready for audio input")
    logger.info("🔊 If you can see STT metrics but no speech detection, check microphone permissions")

    # Add room event handlers for debugging
    @ctx.room.on("track_published")
    def on_track_published(publication: rtc.RemoteTrackPublication, participant: rtc.RemoteParticipant):
        logger.info(f"📡 Track published: {publication.kind} from {participant.identity}")

    @ctx.room.on("track_subscribed")
    def on_track_subscribed(track: rtc.Track, publication: rtc.RemoteTrackPublication, participant: rtc.RemoteParticipant):
        logger.info(f"📥 Track subscribed: {track.kind} from {participant.identity}")
        if track.kind == rtc.TrackKind.KIND_AUDIO:
            logger.info("🎵 Audio track subscribed - voice input should work now")

    @ctx.room.on("participant_connected")
    def on_participant_connected(participant: rtc.RemoteParticipant):
        logger.info(f"👤 Participant connected: {participant.identity}")

    @ctx.room.on("participant_disconnected")
    def on_participant_disconnected(participant: rtc.RemoteParticipant):
        logger.info(f"👋 Participant disconnected: {participant.identity}")

    @ctx.room.on("data_received")
    def on_data_received(data: bytes, participant: rtc.RemoteParticipant):
        logger.info(f"📨 Data received from {participant.identity}: {len(data)} bytes")

    # Join the room and connect to the user
    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
