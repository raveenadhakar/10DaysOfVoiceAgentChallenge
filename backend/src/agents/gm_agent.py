import logging
import json
from typing import Dict, List

from livekit.agents import Agent, function_tool, RunContext

logger = logging.getLogger("gm_agent")


class GameMasterAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions="""You are an engaging and dramatic Game Master running a fantasy adventure story. You create an immersive D&D-style experience through voice interaction.

            Your personality:
            - Dramatic and theatrical in your narration
            - Descriptive and vivid with scenes
            - Responsive to player choices
            - Creative in adapting the story based on player actions
            - Encouraging of player creativity and decisions

            Your universe: High Fantasy
            - Medieval fantasy world with magic, monsters, and adventure
            - Dragons, wizards, ancient ruins, and mystical artifacts
            - Kingdoms in conflict, dark forces rising, heroes needed

            Your role:
            1. Start by setting the scene dramatically - describe where the player is and what's happening
            2. Always end your narration with a clear prompt for action: "What do you do?"
            3. Listen to the player's choice and continue the story based on their decision
            4. Remember key details: character names, locations visited, items found, NPCs met
            5. Create a mini-arc over 8-15 exchanges (finding something, escaping danger, solving a mystery)
            6. Build tension and excitement through your descriptions
            7. Give the player meaningful choices that affect the story

            Story structure:
            - Opening: Set the scene with immediate tension or intrigue
            - Rising action: Present challenges and choices
            - Climax: Build to an exciting moment of decision or action
            - Resolution: Conclude the mini-arc with consequences of player choices

            Guidelines:
            - Keep narration concise but vivid (2-4 sentences per turn)
            - Always give the player agency - let their choices matter
            - Use sensory details (sights, sounds, smells) to bring scenes alive
            - Create memorable NPCs with distinct personalities
            - Balance danger with hope - make it exciting but not hopeless
            - Track story continuity using the conversation history
            - End each response with "What do you do?" or similar action prompt

            Remember: You're creating an interactive story where the player is the hero!"""
        )
        self._room = None
        self.story_state = {
            "location": None,
            "npcs_met": [],
            "items_found": [],
            "key_events": [],
            "turn_count": 0
        }
    
    def set_room(self, room):
        """Set the room for sending data updates."""
        self._room = room
    
    async def _send_story_update(self):
        """Send story state update to frontend via data channel."""
        if self._room:
            try:
                story_data = {
                    "type": "story_update",
                    "data": self.story_state
                }
                await self._room.local_participant.publish_data(
                    json.dumps(story_data).encode('utf-8'),
                    topic="gm_session"
                )
                logger.info(f"Sent story update: Turn {self.story_state['turn_count']}")
            except Exception as e:
                logger.error(f"Failed to send story update: {e}")
    
    @function_tool
    async def start_adventure(self, context: RunContext):
        """Begin a new adventure story."""
        self.story_state = {
            "location": "The Crossroads Inn",
            "npcs_met": [],
            "items_found": [],
            "key_events": ["Adventure begins"],
            "turn_count": 0
        }
        await self._send_story_update()
        
        opening = """You awaken in a dimly lit tavern called the Crossroads Inn. The smell of ale and roasted meat fills the air. 
        A hooded figure at the corner table catches your eye - they seem to be watching you intently. 
        The innkeeper is wiping down the bar, and you hear urgent whispers from a group of travelers near the fireplace. 
        What do you do?"""
        
        return opening
    
    @function_tool
    async def record_location(self, context: RunContext, location: str):
        """Record when the player moves to a new location.
        
        Args:
            location: The name of the location the player has moved to
        """
        self.story_state["location"] = location
        self.story_state["key_events"].append(f"Traveled to {location}")
        await self._send_story_update()
        return f"You are now at {location}."
    
    @function_tool
    async def record_npc_encounter(self, context: RunContext, npc_name: str, npc_description: str = ""):
        """Record when the player meets a new NPC.
        
        Args:
            npc_name: The name of the NPC
            npc_description: Brief description of the NPC (optional)
        """
        npc_entry = {"name": npc_name, "description": npc_description}
        if npc_entry not in self.story_state["npcs_met"]:
            self.story_state["npcs_met"].append(npc_entry)
            self.story_state["key_events"].append(f"Met {npc_name}")
        await self._send_story_update()
        return f"You've encountered {npc_name}."
    
    @function_tool
    async def record_item_found(self, context: RunContext, item_name: str, item_description: str = ""):
        """Record when the player finds or receives an item.
        
        Args:
            item_name: The name of the item
            item_description: Brief description of the item (optional)
        """
        item_entry = {"name": item_name, "description": item_description}
        if item_entry not in self.story_state["items_found"]:
            self.story_state["items_found"].append(item_entry)
            self.story_state["key_events"].append(f"Found {item_name}")
        await self._send_story_update()
        return f"You've acquired {item_name}."
    
    @function_tool
    async def record_key_event(self, context: RunContext, event_description: str):
        """Record a significant story event.
        
        Args:
            event_description: Description of the important event that occurred
        """
        self.story_state["key_events"].append(event_description)
        self.story_state["turn_count"] += 1
        await self._send_story_update()
        return f"Event recorded: {event_description}"
    
    @function_tool
    async def get_story_summary(self, context: RunContext):
        """Get a summary of the adventure so far."""
        summary = f"Adventure Summary (Turn {self.story_state['turn_count']}):\n"
        summary += f"Current Location: {self.story_state['location']}\n"
        
        if self.story_state['npcs_met']:
            summary += f"NPCs Met: {', '.join([npc['name'] for npc in self.story_state['npcs_met']])}\n"
        
        if self.story_state['items_found']:
            summary += f"Items Found: {', '.join([item['name'] for item in self.story_state['items_found']])}\n"
        
        if self.story_state['key_events']:
            summary += f"Key Events: {', '.join(self.story_state['key_events'][-3:])}\n"
        
        return summary
    
    @function_tool
    async def restart_story(self, context: RunContext):
        """Restart the adventure with a fresh story."""
        return await self.start_adventure(context)
