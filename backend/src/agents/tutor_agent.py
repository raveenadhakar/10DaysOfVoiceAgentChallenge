import logging
import json
import random
from datetime import datetime
from typing import Dict, List, Optional

from livekit.agents import Agent, function_tool, RunContext

logger = logging.getLogger("tutor_agent")


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
        
        if score >= 0.5:
            feedback = f"Excellent answer! You mentioned key points like {', '.join(matched_keywords)}. "
            feedback += f"You clearly understand {self.current_concept['title']}. "
            feedback += "Would you like to try another question or switch to teach-back mode to explain a concept to me?"
        elif score >= 0.25:
            feedback = f"Good start! You got some important points like {', '.join(matched_keywords)}. "
            feedback += f"Let me give you a hint: {self.current_concept['summary'][:100]}... "
            feedback += "Would you like to try answering again or move on to another concept?"
        else:
            feedback = f"That's a good attempt! Let me help you understand {self.current_concept['title']} better. "
            feedback += f"{self.current_concept['summary']} "
            feedback += "Now that you have more context, would you like to try the question again?"
        
        return feedback

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
        
        if coverage_score >= 0.7:
            feedback += f"You did an excellent job explaining {self.current_concept['title']}! "
            feedback += f"You covered the key concepts like {', '.join(covered_points)}. "
            feedback += "Your explanation shows you really understand this topic. "
            feedback += "Would you like to explain another concept or try a different learning mode?"
        elif coverage_score >= 0.4:
            feedback += f"That's a good explanation! You mentioned important points like {', '.join(covered_points)}. "
            feedback += f"Can you also tell me about how {self.current_concept['title'].lower()} help with organizing code or making it more efficient? "
            feedback += "What examples can you think of?"
        else:
            feedback += f"I can see you're thinking about {self.current_concept['title']}! "
            feedback += f"Let me ask you this: {self.current_concept['sample_question']} "
            feedback += "Try to think about the main purpose and benefits. What problem do they solve?"
        
        return feedback
