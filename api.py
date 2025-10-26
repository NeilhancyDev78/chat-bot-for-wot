# api.py
"""
ok so this file is like my assistant’s brain power-up pack 💥  
it tells the AI how to do simple smart home stuff like “yo, what’s the temp in my room?”
and it works with different LiveKit versions cuz versions be weird sometimes lol
"""

import logging
import enum
from typing import Annotated

# setup the logger thingy (so we can print stuff that looks hacker-y)
logger = logging.getLogger("assistant")
logger.setLevel(logging.INFO)

# --- TRYING TO IMPORT THE LLM THING (it’s like the big brain from livekit) ---
try:
    from livekit.agents import llm
except Exception:
    llm = None  # if this fails, we go to backup mode like pros

# --- ROOM ZONES (aka where the AI controls temp like a boss) ---
class Zone(enum.Enum):
    LIVING_ROOM = "living_room"
    BEDROOM = "bedroom"
    KITCHEN = "kitchen"
    BATHROOM = "bathroom"
    OFFICE = "office"

# define some vars for later (kinda placeholders rn)
AssistantFnc = None
tools = None

# --- MAIN BIG BRAIN PATH: using FunctionContext if it exists ---
if llm is not None and hasattr(llm, "FunctionContext"):
    class AssistantFnc(llm.FunctionContext):
        def __init__(self) -> None:
            super().__init__()
            # setting up default temps for each zone cuz cold rooms suck ❄️🔥
            self._temperature = {
                Zone.LIVING_ROOM: 22,
                Zone.BEDROOM: 20,
                Zone.KITCHEN: 24,
                Zone.BATHROOM: 23,
                Zone.OFFICE: 21,
            }

        # --- AI callable (fancy word for “the AI can run this function by name”) ---
        @llm.ai_callable(description="Get the temperature in a specific room")
        def get_temperature(self, zone: Annotated[Zone, llm.TypeInfo(description="The specific zone")]):
            z = Zone(zone)
            temp = self._temperature[z]
            logger.info("get_temperature called: %s -> %s", z, temp)
            return f"The temperature in the {z.value.replace('_',' ')} is {temp}°C"

        # --- Another AI callable (for changing temps like a boss) ---
        @llm.ai_callable(description="Set the temperature in a specific room")
        def set_temperature(self, zone: Annotated[Zone, llm.TypeInfo(description="The specific zone")],
                            temp: Annotated[int, llm.TypeInfo(description="The temperature to set")]):
            z = Zone(zone)
            self._temperature[z] = int(temp)
            logger.info("set_temperature called: %s -> %s", z, temp)
            return f"Temperature in the {z.value.replace('_',' ')} set to {temp}°C"

# --- BACKUP MODE: if FunctionContext doesn’t exist (old livekit or smth) ---
else:
    try:
        # ok so this decorator lets us mark functions so the AI can use them
        from livekit.agents import function_tool, RunContext

        # lil helper for getting temperature
        @function_tool()
        async def get_temperature(ctx: RunContext, zone: str) -> str:
            z = zone.lower()
            mapping = {
                "living_room": 22, "bedroom": 20, "kitchen": 24, "bathroom": 23, "office": 21
            }
            if z not in mapping:
                # oopsie invalid zone 😭
                return f"Unknown zone '{zone}'. Available: {', '.join(mapping.keys())}."
            temp = mapping[z]
            logger.info("get_temperature (func) called: %s -> %s", z, temp)
            return f"The temperature in the {z.replace('_', ' ')} is {temp}°C"

        # lil helper for setting temperature
        @function_tool()
        async def set_temperature(ctx: RunContext, zone: str, temp: int) -> str:
            z = zone.lower()
            logger.info("set_temperature (func) called: %s -> %s", z, temp)
            # doesn’t save cuz it’s the lazy fallback version 💤
            return f"Temperature in the {z.replace('_', ' ')} set to {int(temp)}°C"

        # the AI uses these two as its toolbox
        tools = [get_temperature, set_temperature]

    # --- FINAL RESCUE MODE (no llm, no decorator, just old-school functions) ---
    except Exception:
        def get_temperature(zone: str) -> str:
            mapping = {
                "living_room": 22, "bedroom": 20, "kitchen": 24, "bathroom": 23, "office": 21
            }
            z = zone.lower()
            if z not in mapping:
                return f"Unknown zone '{zone}'. Available: {', '.join(mapping.keys())}."
            return f"The temperature in the {z.replace('_',' ')} is {mapping[z]}°C"

        def set_temperature(zone: str, temp: int) -> str:
            # doesn’t actually save cuz we’re in baby mode here 😅
            return f"Temperature in the {zone.replace('_',' ')} set to {int(temp)}°C"

        # tools go here too (like tiny Pokémon moves list)
        tools = [get_temperature, set_temperature]
