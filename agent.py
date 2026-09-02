import asyncio
import logging
import os
from dotenv import load_dotenv

from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    WorkerOptions,
    cli,
    RunContext,
    function_tool,
)
from livekit.plugins import rime, deepgram, groq, silero

from recipe import RECIPE

load_dotenv()
STRESS_TEST = os.getenv("STRESS_TEST", "false").lower() == "true"

logger = logging.getLogger("sousvoice")


class RecipeAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions=(
                "You are SousVoice, a hands-free cooking assistant. "
                "You are reading out a recipe step by step. "
                "Keep responses short and spoken-friendly. "
                "When the user says 'next', call the next_step tool. "
                "When the user asks an unrelated question (like a "
                "measurement conversion), answer it briefly and then "
                "remind them you'll continue from the current step."
            )
        )
        self.current_step = 0

    async def on_enter(self):
        # Jab agent room mein enter kare, pehla message bole
        await self.session.say(
            f"Starting recipe: {RECIPE['title']}. "
            "Say 'next' when you're ready for step one."
        )

    @function_tool
    async def next_step(self, context: RunContext):
        """Move to the next recipe step after a deliberate delay for interruption testing."""

        if self.current_step >= len(RECIPE["steps"]):
            return "The recipe is already complete."

        step_index = self.current_step
        step_text = RECIPE["steps"][step_index]

        logger.info(
            "NEXT_STEP_START step=%d",
            step_index + 1,
        )

        # Only add the artificial delay during the stress test.
        work = None

        if STRESS_TEST:
            work = asyncio.create_task(asyncio.sleep(5))
            await context.speech_handle.wait_if_not_interrupted([work])

        # User interrupted while the tool was waiting.
        if context.speech_handle.interrupted:
            if work is not None:
                work.cancel()

            logger.info(
                "NEXT_STEP_INTERRUPTED step=%d current_step=%d",
                step_index + 1,
                self.current_step,
            )

            return None

        # Only advance state after the operation successfully completes.
        self.current_step += 1

        logger.info(
            "NEXT_STEP_COMPLETE step=%d current_step=%d",
            step_index + 1,
            self.current_step,
        )

        return step_text

    @function_tool
    async def repeat_step(self, context: RunContext):
        """Call this when the user asks to repeat the current step."""

        if self.current_step == 0:
            return "We haven't started yet. Say 'next' to begin."

        step_text = RECIPE["steps"][self.current_step - 1]
        return step_text


async def entrypoint(ctx: JobContext):
    await ctx.connect()

    session = AgentSession(
        stt=deepgram.STT(model="nova-2"),
        llm=groq.LLM(model="openai/gpt-oss-20b"),
        tts=rime.TTS(
            speaker="lyra",
            model="coda",
        ),
        vad=silero.VAD.load(),
    )

    await session.start(
        room=ctx.room,
        agent=RecipeAgent(),
    )


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))