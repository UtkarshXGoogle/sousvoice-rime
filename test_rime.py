import asyncio
import os

from dotenv import load_dotenv
from livekit.agents.utils import http_context
from livekit.plugins import rime


load_dotenv()


async def main():
    api_key = os.getenv("RIME_API_KEY")

    if not api_key:
        raise RuntimeError("RIME_API_KEY is not set in the environment.")

    async with http_context.open():
        tts = rime.TTS(
            api_key=api_key,
            speaker="lyra",
            model="coda",
        )

        text = "Hello, this is a test of Rime text to speech."

        frame_count = 0
        total_bytes = 0

        async for audio_frame in tts.synthesize(text):
            frame_count += 1
            total_bytes += len(audio_frame.frame.data)

        if frame_count == 0:
            raise RuntimeError("Rime returned no audio frames.")

        print("Rime TTS test passed.")
        print("Audio frames:", frame_count)
        print("Total audio bytes:", total_bytes)


if __name__ == "__main__":
    asyncio.run(main())
