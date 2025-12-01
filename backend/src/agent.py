import logging
import ssl
import os

from dotenv import load_dotenv
from livekit.agents import (
    AgentSession,
    JobContext,
    JobProcess,
    MetricsCollectedEvent,
    WorkerOptions,
    cli,
    metrics,
    tokenize,
)
from livekit import rtc
from livekit.plugins import murf, silero, google, deepgram
from livekit.plugins.turn_detector.multilingual import MultilingualModel

# Import all agent classes from separate files
from agents.food_agent import FoodOrderingAgent
from agents.fraud_agent import FraudAlertAgent
from agents.wellness_agent import HealthWellnessCompanion
from agents.tutor_agent import TutorCoordinatorAgent
from agents.sdr_agent import SDRAgent
from agents.gm_agent import GameMasterAgent
from agents.commerce_agent import CommerceAgent
from agents.improv_agent import ImprovBattleAgent

logger = logging.getLogger("agent")

load_dotenv(".env")

# Disable SSL verification for development (only if needed)
# This is a workaround for SSL certificate issues in development
if os.getenv("DISABLE_SSL_VERIFY", "false").lower() == "true":
    ssl._create_default_https_context = ssl._create_unverified_context
    logger.warning("⚠️ SSL verification disabled - only use in development!")


def prewarm(proc: JobProcess):
    # Load VAD with more sensitive settings for better voice detection
    proc.userdata["vad"] = silero.VAD.load(
        # Shorter min speech duration to catch quick words (in seconds)
        min_speech_duration=0.05,
        # Shorter min silence duration to be more responsive (in seconds)
        min_silence_duration=0.3
    )


async def entrypoint(ctx: JobContext):
    import asyncio
    
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

    # Determine which agent to use based on room name or metadata
    # Room name format: voice_assistant_{agent_type}_{random_number}
    
    agent_type = None
    
    # First, try to extract agent type from room name (most reliable method)
    room_name = ctx.room.name
    logger.info(f"🎯 Room name: '{room_name}'")
    
    if room_name.startswith("voice_assistant_"):
        # Extract agent type from room name
        parts = room_name.split("_")
        if len(parts) >= 3:
            # Format: voice_assistant_{agent_type}_{number}
            potential_agent_type = parts[2]
            valid_agent_types = ["food", "fraud", "wellness", "tutor", "sdr", "gm", "commerce", "improv"]
            if potential_agent_type in valid_agent_types:
                agent_type = potential_agent_type
                logger.info(f"🎯 ✅ Extracted agent type from room name: '{agent_type}'")
    
    # Fallback: Try room metadata (with retries)
    if not agent_type:
        logger.info("🎯 Agent type not found in room name, trying metadata...")
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            logger.info(f"🎯 [Attempt {retry_count + 1}] Room metadata: '{ctx.room.metadata}'")
            
            if ctx.room.metadata and ctx.room.metadata.strip():
                agent_type = ctx.room.metadata.strip()
                logger.info(f"🎯 ✅ Found metadata: '{agent_type}'")
                break
            
            retry_count += 1
            if retry_count < max_retries:
                logger.info(f"🎯 ⏳ Metadata not available yet, waiting 200ms...")
                await asyncio.sleep(0.2)
    
    # Final fallback: default to food
    if not agent_type:
        agent_type = "food"
        logger.warning(f"🎯 ⚠️ No agent type found in room name or metadata, defaulting to 'food'")
    
    # Log what we extracted
    logger.info(f"🎯 Extracted agent_type before validation: '{agent_type}'")
    
    # Additional validation
    valid_agent_types = ["food", "fraud", "wellness", "tutor", "sdr", "gm", "commerce", "improv"]
    if agent_type not in valid_agent_types:
        logger.warning(f"⚠️ Invalid agent type '{agent_type}', defaulting to 'food'")
        agent_type = "food"
    
    logger.info(f"🎯 Agent type selected: '{agent_type}' (validated)")
    logger.info(f"🎯 Creating agent instance for type: '{agent_type}'")
    
    # Create the appropriate agent based on type
    if agent_type == "food":
        agent = FoodOrderingAgent()
        logger.info("🛒 ✅ Food Ordering Agent created successfully")
    elif agent_type == "fraud":
        agent = FraudAlertAgent()
        logger.info("🚨 ✅ Fraud Alert Agent created successfully")
    elif agent_type == "wellness":
        agent = HealthWellnessCompanion()
        logger.info("💚 ✅ Health & Wellness Agent created successfully")
    elif agent_type == "tutor":
        agent = TutorCoordinatorAgent()
        logger.info("📚 ✅ Tutor Coordinator Agent created successfully")
    elif agent_type == "sdr":
        agent = SDRAgent()
        logger.info("📞 ✅ SDR Agent created successfully")
    elif agent_type == "gm":
        agent = GameMasterAgent()
        logger.info("🎲 ✅ Game Master Agent created successfully")
    elif agent_type == "commerce":
        agent = CommerceAgent()
        logger.info("🛍️ ✅ E-commerce Agent created successfully")
    elif agent_type == "improv":
        agent = ImprovBattleAgent()
        logger.info("🎭 ✅ Improv Battle Agent created successfully")
    else:
        # Fallback to food ordering if unknown type
        agent = FoodOrderingAgent()
        logger.info(f"🛒 ⚠️ Starting Food Ordering Agent (fallback for unknown type: '{agent_type}')")
    
    # Log the agent's instructions to verify correct agent was created
    logger.info(f"📝 Agent instructions preview: {agent.instructions[:100]}...")
    
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
    def on_data_received(data_packet: rtc.DataPacket):
        logger.info(f"📨 Data received from {data_packet.participant.identity if data_packet.participant else 'unknown'}: {len(data_packet.data)} bytes")

    # Join the room and connect to the user
    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
