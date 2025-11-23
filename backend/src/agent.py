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

# Order state structure
class OrderState:
    def __init__(self):
        self.drink_type: Optional[str] = None
        self.size: Optional[str] = None
        self.milk: Optional[str] = None
        self.extras: List[str] = []
        self.name: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "drinkType": self.drink_type,
            "size": self.size,
            "milk": self.milk,
            "extras": self.extras,
            "name": self.name
        }
    
    def is_complete(self) -> bool:
        return all([
            self.drink_type is not None,
            self.size is not None,
            self.milk is not None,
            self.name is not None
        ])
    
    def get_missing_fields(self) -> List[str]:
        missing = []
        if not self.drink_type:
            missing.append("drink type")
        if not self.size:
            missing.append("size")
        if not self.milk:
            missing.append("milk preference")
        if not self.name:
            missing.append("name")
        return missing


class CoffeeShopBarista(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are Maya, a friendly and enthusiastic barista at Brew & Bean Coffee Shop. You're passionate about coffee and love helping customers find their perfect drink.

            Your personality:
            - Warm, welcoming, and energetic
            - Knowledgeable about coffee drinks and ingredients
            - Patient when customers are deciding
            - Use casual, conversational language
            - Occasionally mention coffee facts or recommendations

            Your job is to take complete coffee orders by collecting:
            1. Drink type (espresso, latte, cappuccino, americano, macchiato, mocha, frappuccino, etc.)
            2. Size (small, medium, large)
            3. Milk preference (whole milk, 2% milk, oat milk, almond milk, soy milk, coconut milk, no milk)
            4. Any extras (extra shot, decaf, vanilla syrup, caramel syrup, whipped cream, extra hot, iced, etc.)
            5. Customer's name for the order

            Always ask clarifying questions until you have all required information. Be conversational and helpful. When the order is complete, confirm all details and let them know you're processing their order.

            Keep responses concise and natural - you're speaking, not writing.""",
        )
        self.order_state = OrderState()
        self._room = None

    def set_room(self, room):
        """Set the room for sending data updates."""
        self._room = room

    async def _send_order_update(self):
        """Send order state update to frontend via data channel."""
        if self._room:
            try:
                order_data = {
                    "type": "order_update",
                    "data": self.order_state.to_dict()
                }
                await self._room.local_participant.publish_data(
                    json.dumps(order_data).encode('utf-8'),
                    topic="coffee_order"
                )
                logger.info(f"Sent order update: {order_data}")
            except Exception as e:
                logger.error(f"Failed to send order update: {e}")

    @function_tool
    async def update_drink_type(self, context: RunContext, drink_type: str):
        """Update the customer's drink choice.
        
        Args:
            drink_type: The type of coffee drink (e.g., latte, cappuccino, americano, mocha)
        """
        self.order_state.drink_type = drink_type.lower()
        logger.info(f"Updated drink type to: {drink_type}")
        await self._send_order_update()
        return f"Got it! One {drink_type}."

    @function_tool
    async def update_size(self, context: RunContext, size: str):
        """Update the size of the drink.
        
        Args:
            size: The size of the drink (small, medium, large)
        """
        self.order_state.size = size.lower()
        logger.info(f"Updated size to: {size}")
        await self._send_order_update()
        return f"Perfect! {size.capitalize()} size."

    @function_tool
    async def update_milk(self, context: RunContext, milk_type: str):
        """Update the milk preference for the drink.
        
        Args:
            milk_type: Type of milk (whole milk, 2% milk, oat milk, almond milk, soy milk, coconut milk, no milk)
        """
        self.order_state.milk = milk_type.lower()
        logger.info(f"Updated milk to: {milk_type}")
        await self._send_order_update()
        return f"Noted! {milk_type.capitalize()}."

    @function_tool
    async def add_extra(self, context: RunContext, extra: str):
        """Add an extra item or modification to the drink.
        
        Args:
            extra: Extra item like extra shot, syrup, whipped cream, etc.
        """
        if extra.lower() not in self.order_state.extras:
            self.order_state.extras.append(extra.lower())
        logger.info(f"Added extra: {extra}")
        await self._send_order_update()
        return f"Added {extra} to your order!"

    @function_tool
    async def update_name(self, context: RunContext, name: str):
        """Update the customer's name for the order.
        
        Args:
            name: Customer's name
        """
        self.order_state.name = name.title()
        logger.info(f"Updated name to: {name}")
        await self._send_order_update()
        return f"Thanks {name}!"

    @function_tool
    async def check_order_status(self, context: RunContext):
        """Check what information is still needed to complete the order."""
        missing = self.order_state.get_missing_fields()
        if not missing:
            return "Your order is complete! Let me process that for you."
        else:
            return f"I still need: {', '.join(missing)}"

    @function_tool
    async def complete_order(self, context: RunContext):
        """Complete and save the order when all information is collected."""
        if not self.order_state.is_complete():
            missing = self.order_state.get_missing_fields()
            return f"I still need to get your {', '.join(missing)} before I can complete the order."
        
        # Create orders directory if it doesn't exist
        orders_dir = "orders"
        os.makedirs(orders_dir, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{orders_dir}/order_{timestamp}_{self.order_state.name.replace(' ', '_')}.json"
        
        # Prepare order data
        order_data = {
            **self.order_state.to_dict(),
            "timestamp": datetime.now().isoformat(),
            "order_id": f"ORD-{timestamp}"
        }
        
        # Save to JSON file
        try:
            with open(filename, 'w') as f:
                json.dump(order_data, f, indent=2)
            
            logger.info(f"Order saved to {filename}")
            
            # Send order completion notification
            completion_data = {
                "type": "order_complete",
                "data": order_data
            }
            if self._room:
                await self._room.local_participant.publish_data(
                    json.dumps(completion_data).encode('utf-8'),
                    topic="coffee_order"
                )
            
            # Create order summary
            extras_text = f" with {', '.join(self.order_state.extras)}" if self.order_state.extras else ""
            summary = f"Perfect! I've got your order: {self.order_state.size} {self.order_state.drink_type} with {self.order_state.milk}{extras_text} for {self.order_state.name}. Your order has been saved and we'll have it ready shortly!"
            
            # Reset order state for next customer
            self.order_state = OrderState()
            await self._send_order_update()  # Send empty state for next order
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to save order: {e}")
            return "I'm sorry, there was an issue processing your order. Please try again."


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
    agent = CoffeeShopBarista()
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
