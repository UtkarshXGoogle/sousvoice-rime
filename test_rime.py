import asyncio
import os
from dotenv import load_dotenv
from livekit.agents.utils import http_context
from livekit.plugins import rime

load_dotenv()

async def main():
    async with http_context.open():
        tts = rime.TTS(
            api_key=os.getenv("RIME_API_KEY"),
            speaker="lyra",
            model="coda",
        )

        text = "Hello, this is a test of Rime text to speech."

        async for audio_frame in tts.synthesize(text):
            print("Audio frame received:", len(audio_frame.frame.data), "bytes")

if __name__ == "__main__":
    asyncio.run(main())