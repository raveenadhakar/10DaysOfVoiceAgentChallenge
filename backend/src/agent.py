import logging
import json
import os
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
        tts=murf.TTS(
                voice="en-US-matthew", 
                style="Conversation",
                tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
                text_pacing=True
            ),
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

    # Create the agent and set the room reference
    agent = HealthWellnessCompanion()
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
