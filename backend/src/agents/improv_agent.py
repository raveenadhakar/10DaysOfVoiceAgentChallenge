import logging
import json
import random
from typing import Dict, List

from livekit.agents import Agent, function_tool, RunContext

logger = logging.getLogger("improv_agent")


class ImprovBattleAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions="""You are the host of a TV improv show called 'Improv Battle'! You are high-energy, witty, and clear about rules.

            Your personality:
            - High-energy and enthusiastic like a game show host
            - Witty and entertaining with your commentary
            - Clear and direct about rules and expectations
            - Realistic in your reactions - sometimes amused, sometimes unimpressed, sometimes pleasantly surprised
            - Not always supportive - light teasing and honest critique are allowed
            - Stay respectful and non-abusive at all times
            - Randomly choose between supportive, neutral, or mildly critical tones while staying constructive

            Your role as host:
            1. Introduce the show and explain the basic rules when a player joins
            2. Run 3-5 improv rounds with the player
            3. For each round:
               - Set up a clear scenario with character, situation, and tension
               - Ask the player to start improvising
               - Listen to their performance
               - React with varied, realistic feedback when they finish
            4. Provide a closing summary of their improv style and memorable moments
            5. Handle early exits gracefully if requested

            Round structure:
            - Announce the scenario clearly
            - Tell the player to start improvising
            - Listen for their performance
            - When they indicate they're done (saying "End scene", "Okay", long pause, or similar), provide your reaction
            - Move to the next round

            Reaction guidelines:
            - Comment on what worked, what was weird, or what felt flat
            - Mix your feedback: sometimes positive ("That was hilarious!"), sometimes constructive ("That felt rushed")
            - Be specific about what you noticed in their performance
            - Keep reactions concise but engaging
            - Remember details for your final summary

            Remember: You're creating an entertaining improv game show experience where the player is the star performer!"""
        )
        self._room = None
        self.improv_state = {
            "player_name": None,
            "current_round": 0,
            "max_rounds": 3,
            "rounds": [],  # each: {"scenario": str, "host_reaction": str}
            "phase": "intro",  # "intro" | "awaiting_improv" | "reacting" | "done"
        }
        
        # Pre-defined improv scenarios
        self.scenarios = [
            "You are a time-travelling tour guide explaining modern smartphones to someone from the 1800s.",
            "You are a restaurant waiter who must calmly tell a customer that their order has escaped the kitchen.",
            "You are a customer trying to return an obviously cursed object to a very skeptical shop owner.",
            "You are a barista who has to tell a customer that their latte is actually a portal to another dimension.",
            "You are a librarian trying to convince someone that the book they want to check out is actually alive and doesn't want to leave.",
            "You are a taxi driver whose car has just started flying, and you need to explain this to your very confused passenger.",
            "You are a museum security guard who has to tell visitors that one of the dinosaur skeletons has gone missing.",
            "You are a pizza delivery person who has arrived at the wrong century and must deliver to a medieval castle.",
            "You are a tech support representative helping someone whose computer has gained consciousness.",
            "You are a wedding planner explaining to the bride that the venue has been taken over by a family of bears.",
            "You are a dentist who has to inform your patient that their tooth is actually a tiny alien spaceship.",
            "You are a dog walker trying to explain to the owner why their pet has learned to speak French.",
        ]
    
    def set_room(self, room):
        """Set the room for sending data updates."""
        self._room = room
    
    async def _send_improv_update(self):
        """Send improv state update to frontend via data channel."""
        if self._room:
            try:
                improv_data = {
                    "type": "improv_update",
                    "data": self.improv_state
                }
                await self._room.local_participant.publish_data(
                    json.dumps(improv_data).encode('utf-8'),
                    topic="improv_session"
                )
                logger.info(f"Sent improv update: Round {self.improv_state['current_round']}, Phase: {self.improv_state['phase']}")
            except Exception as e:
                logger.error(f"Failed to send improv update: {e}")
    
    @function_tool
    async def start_improv_battle(self, context: RunContext, player_name: str = None):
        """Begin a new Improv Battle game.
        
        Args:
            player_name: The name of the contestant (optional)
        """
        if player_name:
            self.improv_state["player_name"] = player_name
        
        self.improv_state["phase"] = "intro"
        await self._send_improv_update()
        
        intro = f"""Welcome to IMPROV BATTLE! I'm your host, and you're about to become our star performer! 
        
        Here's how it works: I'll give you {self.improv_state['max_rounds']} different improv scenarios. 
        For each one, I'll set the scene and tell you who you are and what's happening. 
        Then YOU get to act it out! When you're done with a scene, just say 'End scene' or 'Okay' and I'll give you my reaction.
        
        Ready to show me what you've got? Let's start with round one!"""
        
        return intro
    
    @function_tool
    async def set_player_name(self, context: RunContext, name: str):
        """Set the player's name for the game.
        
        Args:
            name: The contestant's name
        """
        self.improv_state["player_name"] = name
        await self._send_improv_update()
        return f"Great to meet you, {name}! Let's get this improv battle started!"
    
    @function_tool
    async def start_next_round(self, context: RunContext):
        """Start the next improv round with a new scenario."""
        if self.improv_state["current_round"] >= self.improv_state["max_rounds"]:
            return await self.end_show(context)
        
        self.improv_state["current_round"] += 1
        self.improv_state["phase"] = "awaiting_improv"
        
        # Select a random scenario
        scenario = random.choice(self.scenarios)
        
        # Add round to state
        round_data = {"scenario": scenario, "host_reaction": ""}
        self.improv_state["rounds"].append(round_data)
        
        await self._send_improv_update()
        
        round_intro = f"""Round {self.improv_state['current_round']}! Here's your scenario:

        {scenario}

        Alright, the scene is set! Take it away - start improvising now!"""
        
        return round_intro
    
    @function_tool
    async def react_to_performance(self, context: RunContext, reaction: str):
        """Provide host reaction to the player's improv performance.
        
        Args:
            reaction: The host's reaction and feedback to the performance
        """
        if self.improv_state["rounds"]:
            self.improv_state["rounds"][-1]["host_reaction"] = reaction
        
        self.improv_state["phase"] = "reacting"
        await self._send_improv_update()
        
        # Determine if we should continue or end
        if self.improv_state["current_round"] >= self.improv_state["max_rounds"]:
            return f"{reaction}\n\nThat wraps up our final round! Let me give you my overall thoughts..."
        else:
            return f"{reaction}\n\nAlright, ready for the next challenge?"
    
    @function_tool
    async def end_show(self, context: RunContext):
        """Provide closing summary and end the improv battle."""
        self.improv_state["phase"] = "done"
        await self._send_improv_update()
        
        player_name = self.improv_state["player_name"] or "contestant"
        
        # Generate summary based on performance
        summary_options = [
            f"What a performance, {player_name}! You showed great character work and really committed to each scenario.",
            f"Impressive stuff, {player_name}! You've got a knack for finding the humor in absurd situations.",
            f"Well done, {player_name}! Your emotional range and quick thinking really stood out today.",
            f"Great job, {player_name}! You weren't afraid to take risks and really go for it in each scene.",
        ]
        
        summary = random.choice(summary_options)
        
        # Add specific moments if we have reactions
        if self.improv_state["rounds"]:
            memorable_round = random.randint(1, len(self.improv_state["rounds"]))
            summary += f" That moment in round {memorable_round} was particularly memorable!"
        
        summary += f"\n\nThanks for playing Improv Battle! You've been a fantastic contestant. Until next time, keep improvising!"
        
        return summary
    
    @function_tool
    async def handle_early_exit(self, context: RunContext):
        """Handle when a player wants to stop the game early."""
        self.improv_state["phase"] = "done"
        await self._send_improv_update()
        
        player_name = self.improv_state["player_name"] or "contestant"
        
        exit_message = f"No problem, {player_name}! Thanks for playing Improv Battle with us today. "
        
        if self.improv_state["current_round"] > 0:
            exit_message += f"You did great in the {self.improv_state['current_round']} round{'s' if self.improv_state['current_round'] > 1 else ''} we played! "
        
        exit_message += "Hope to see you back on the improv stage soon!"
        
        return exit_message
    
    @function_tool
    async def get_game_status(self, context: RunContext):
        """Get the current status of the improv battle game."""
        status = f"Improv Battle Status:\n"
        status += f"Player: {self.improv_state['player_name'] or 'Unknown'}\n"
        status += f"Round: {self.improv_state['current_round']}/{self.improv_state['max_rounds']}\n"
        status += f"Phase: {self.improv_state['phase']}\n"
        
        if self.improv_state["rounds"]:
            status += f"Scenarios completed: {len([r for r in self.improv_state['rounds'] if r['host_reaction']])}\n"
        
        return status
    
    @function_tool
    async def restart_game(self, context: RunContext):
        """Restart the improv battle with a fresh game."""
        self.improv_state = {
            "player_name": self.improv_state.get("player_name"),  # Keep the name if we have it
            "current_round": 0,
            "max_rounds": 3,
            "rounds": [],
            "phase": "intro",
        }
        await self._send_improv_update()
        return await self.start_improv_battle(context, self.improv_state["player_name"])