"""
image.py
Downloads and processes an image from a given URL for analysis or other bot features.
Usage: !image <image_url>
"""

import aiohttp
import os
import discord
import base64

# OLLAMA_BASE_URL configuration
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434/api')

class image:
    description = "Downloads and processes an image from a given URL for analysis or other bot features. Usage: !image <image_url>"
    
    async def run(self, ctx, bot_tools, *args, **kwargs):
        # Check for image URL argument
        if not args:
            await ctx.send("Please provide an image URL. Usage: !image <image_url>")
            return
        url = args[0]
        # Download the image from the provided URL
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    await ctx.send(f"Failed to download image: {response.status}")
                    return
                filename = url.split("/")[-1]
                image_bytes = await response.read()
                # Save image to disk temporarily
                with open(filename, "wb") as f:
                    f.write(image_bytes)
                await ctx.send(file=discord.File(filename))
                os.remove(filename)
                # Save image to memory for follow-up questions and analyze it
                channel_id = ctx.channel.id
                if hasattr(bot_tools, 'LAST_IMAGE_SENT'):
                    base64_image = base64.b64encode(image_bytes).decode('utf-8')
                    # Analyze the image using the vision model if available
                    image_model = getattr(bot_tools, 'IMAGE_MODEL', None)
                    get_ollama_response = getattr(bot_tools, 'get_ollama_response', None)
                    available_models = await bot_tools.get_available_models() if hasattr(bot_tools, 'get_available_models') else []
                    detailed_report = None
                    if image_model and image_model in available_models and get_ollama_response:
                        analysis_prompt = "Give a painfully detailed analysis of this image, including color composition and subject."
                        detailed_report = await get_ollama_response(analysis_prompt, model=image_model, images=[base64_image])
                    bot_tools.LAST_IMAGE_SENT[channel_id] = {'image': base64_image, 'report': detailed_report}

    async def download_image(self, url):
        # Helper to download an image and save to disk
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return False, f"Failed to download image: {response.status}", None
                filename = url.split("/")[-1]
                with open(filename, "wb") as f:
                    f.write(await response.read())
                return True, filename, None