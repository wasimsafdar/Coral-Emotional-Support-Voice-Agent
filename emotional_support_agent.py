from dotenv import load_dotenv
import os
import urllib.parse
from dataclasses import dataclass, field
from typing import Optional
import logging

from livekit import agents
from livekit.agents.llm import function_tool
from livekit.agents import JobContext, AgentSession, Agent, RoomInputOptions, cli, mcp, AgentSession, RunContext

from livekit.plugins import (
    openai,
    cartesia,
    deepgram,
    noise_cancellation,
    silero,
)
from utils import load_prompt
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("voice-agent-emotion-support")
logger.setLevel(logging.INFO)

load_dotenv(override=True)

@dataclass
class UserData:
    """Stores data and agents to be shared across the session"""
    personas: dict[str, Agent] = field(default_factory=dict)
    prev_agent: Optional[Agent] = None
    ctx: Optional[JobContext] = None

    def summarize(self) -> str:
        return "User data: Emotional support system"

RunContext_T = RunContext[UserData]

class BaseAgent(Agent):
    async def on_enter(self) -> None:
        agent_name = self.__class__.__name__
        logger.info(f"Entering {agent_name}")

        userdata: UserData = self.session.userdata
        if userdata.ctx and userdata.ctx.room:
            await userdata.ctx.room.local_participant.set_attributes({"agent": agent_name})

        chat_ctx = self.chat_ctx.copy()

        if userdata.prev_agent:
            items_copy = self._truncate_chat_ctx(
                userdata.prev_agent.chat_ctx.items, keep_function_call=True
            )
            existing_ids = {item.id for item in chat_ctx.items}
            items_copy = [item for item in items_copy if item.id not in existing_ids]
            chat_ctx.items.extend(items_copy)

        chat_ctx.add_message(
            role="system",
            content=f"You are the {agent_name}. {userdata.summarize()}"
        )
        await self.update_chat_ctx(chat_ctx)
        self.session.generate_reply()

    def _truncate_chat_ctx(
        self,
        items: list,
        keep_last_n_messages: int = 6,
        keep_system_message: bool = False,
        keep_function_call: bool = False,
    ) -> list:
        """Truncate the chat context to keep the last n messages."""
        def _valid_item(item) -> bool:
            if not keep_system_message and item.type == "message" and item.role == "system":
                return False
            if not keep_function_call and item.type in ["function_call", "function_call_output"]:
                return False
            return True

        new_items = []
        for item in reversed(items):
            if _valid_item(item):
                new_items.append(item)
            if len(new_items) >= keep_last_n_messages:
                break
        new_items = new_items[::-1]

        while new_items and new_items[0].type in ["function_call", "function_call_output"]:
            new_items.pop(0)

        return new_items

    async def _transfer_to_agent(self, name: str, context: RunContext_T) -> Agent:
        """Transfer to another agent while preserving context"""
        userdata = context.userdata
        current_agent = context.session.current_agent
        next_agent = userdata.personas[name]
        userdata.prev_agent = current_agent

        return next_agent

class VoiceAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            instructions=load_prompt('voice_prompt.yaml'),
            stt=deepgram.STT(model="nova-3", language="multi"),
            llm=openai.LLM(model="gpt-4o-mini"),
            tts=cartesia.TTS(model="sonic-2", voice="f786b574-daa5-4673-aa0c-cbe3e8534c02"),
            vad=silero.VAD.load()
        )

    @function_tool
    async def transfer_to_emotional_support_agent(self, context: RunContext_T) -> Agent:
        await self.session.say("I'll transfer you to our Emotional Support agent who can help you to deal with emotional distress.")
        return await self._transfer_to_agent("emotional support agent", context)

class EmotionalSupportAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            instructions=load_prompt('support_prompt.yaml'),
            stt=deepgram.STT(),
            llm=openai.LLM(model="gpt-4o-mini"),
            tts=cartesia.TTS(),
            vad=silero.VAD.load()
        )

    @function_tool
    async def transfer_to_voice_agent(self, context: RunContext_T) -> Agent:
        await self.session.say("I'll transfer you back to our Voice if you do not want emotional support. He will assist you further.")
        return await self._transfer_to_agent("voice agent", context)

    
async def entrypoint(ctx: JobContext):
    await ctx.connect()

    # MCP Server configuration
    base_url = os.getenv("CORAL_SSE_URL")
    params = {
       # "waitForAgents": 1,
        "agentId": os.getenv("CORAL_AGENT_ID"),
        "agentDescription": "You are a helpful voice assistant. You analyze user emotions. If the user is in emotional distress, you transfer the user to the emotional support agent. For other requests, you assist the user as a voice assistant.",
    }
    query_string = urllib.parse.urlencode(params)
    MCP_SERVER_URL = f"{base_url}?{query_string}"

    userdata = UserData(ctx=ctx)
    voice_agent = VoiceAgent()
    emotional_support_agent = EmotionalSupportAgent()

    # Register all agents in the userdata
    userdata.personas.update({
        "voice agent": voice_agent,
        "emotional support agent": emotional_support_agent,
    })

    session = AgentSession[UserData](
        userdata=userdata,
        mcp_servers=[
            mcp.MCPServerHTTP(
                url=MCP_SERVER_URL,
                timeout=10,
                client_session_timeout_seconds=10,
            ),
        ]
    )
    

    await ctx.connect()

    await session.start(
        agent=voice_agent, 
        room=ctx.room,
    )

    await session.generate_reply(
        instructions="Greet the user and offer your assistance."
    )

    
if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))    



