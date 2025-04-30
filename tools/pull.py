"""
pull.py
Downloads a new AI model from Ollama by name and makes it available for use.
Usage: !pull <model_name>
"""

import aiohttp
import os
import asyncio

# OLLAMA_BASE_URL configuration
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434/api')

class pull:
    description = "Downloads a new AI model from Ollama by name and makes it available for use. Usage: !pull <model_name>"
    async def run(self, ctx, bot_tools, *args, **kwargs):
        # Require a model name argument
        if not args:
            await ctx.send("Please specify a model name. Usage: !pull <model_name>")
            return
        model_name = args[0]
        get_available_models = getattr(bot_tools, 'get_available_models', None)
        if not get_available_models:
            await ctx.send("Could not retrieve available models.")
            return
        # Send a pull request to Ollama for the specified model
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            url = OLLAMA_BASE_URL + '/pull'
            payload = {"model": model_name}
            async with session.post(url, json=payload, timeout=60) as response:
                if response.status == 200:
                    # Poll for model availability
                    poll_attempts = 40  # ~2 minutes (3s interval)
                    for _ in range(poll_attempts):
                        available_models = await get_available_models()
                        if model_name in available_models:
                            await ctx.send(f"Successfully pulled model '{model_name}'. It is now available.")
                            return
                        await asyncio.sleep(3)
                    await ctx.send(f"Pull request sent, but model '{model_name}' is not yet available after waiting. It may still be downloading.")
                else:
                    error_text = await response.text()
                    await ctx.send(f"Failed to pull model '{model_name}'. Status: {response.status}. Details: {error_text}")