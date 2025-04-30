"""
server_status.py
Checks if the Ollama server is running and shows the number of available models, current model, vision model, allowed channels, restriction status, and welcome message settings.
Usage: !server_status
"""

import aiohttp
import os

# OLLAMA_BASE_URL configuration
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434/api')

class server_status:
    description = "Checks if the Ollama server is running and shows the number of available models, current model, vision model, allowed channels, restriction status, and welcome message settings. Usage: !server_status"
    
    async def run(self, ctx, bot_tools, *args, **kwargs):
        # Try to connect to Ollama and fetch model/server stats
        async def send_message(msg):
            if hasattr(ctx, 'response') and hasattr(ctx.response, 'is_done'):
                if not ctx.response.is_done():
                    await ctx.response.send_message(msg)
                else:
                    await ctx.followup.send(msg)
            else:
                await ctx.send(msg)

        try:
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
                url = OLLAMA_BASE_URL + '/tags'
                async with session.get(url, timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        model_count = 0
                        model_names = []
                        if 'models' in data:
                            model_count = len(data['models'])
                            model_names = [m['name'] for m in data['models']]
                        elif isinstance(data, list):
                            model_count = len(data)
                            model_names = [m['name'] for m in data]
                        # Discord bot stats
                        allowed_channels = getattr(bot_tools, 'ALLOWED_CHANNELS', [])
                        restriction_enabled = getattr(bot_tools, 'CHANNEL_RESTRICTION_ENABLED', False)
                        default_model = getattr(bot_tools, 'DEFAULT_MODEL', None)
                        image_model = getattr(bot_tools, 'IMAGE_MODEL', None)
                        welcome_enabled = getattr(bot_tools, 'WELCOME_MESSAGE_ENABLED', True)
                        welcome_channels = getattr(bot_tools, 'WELCOME_MESSAGE_CHANNEL_IDS', [])
                        bot = getattr(bot_tools, 'bot', None)
                        channel_mentions = []
                        if bot:
                            for cid in allowed_channels:
                                ch = bot.get_channel(cid)
                                channel_mentions.append(ch.mention if ch else f"Unknown ({cid})")
                        else:
                            channel_mentions = [str(cid) for cid in allowed_channels]
                        welcome_mentions = []
                        if bot:
                            for cid in welcome_channels:
                                ch = bot.get_channel(cid)
                                welcome_mentions.append(ch.mention if ch else f"Unknown ({cid})")
                        else:
                            welcome_mentions = [str(cid) for cid in welcome_channels]
                        msg = (
                            f"**Ollama Server Status:**\n"
                            f"- Models available: {model_count}\n"
                            f"- Model names: {', '.join(model_names) if model_names else 'None'}\n\n"
                            f"**Bot Stats:**\n"
                            f"- Current model: `{default_model}`\n"
                            f"- Vision model: `{image_model}`\n"
                            f"- Channel restriction: {'enabled' if restriction_enabled else 'disabled'}\n"
                            f"- Allowed channels: {', '.join(channel_mentions) if channel_mentions else 'None'}\n"
                            f"- Welcome message: {'enabled' if welcome_enabled else 'disabled'}\n"
                            f"- Welcome channels: {', '.join(welcome_mentions) if welcome_mentions else 'None'}\n"
                        )
                        await send_message(msg)
                    else:
                        await send_message(f"Ollama server returned status code {response.status}. Response: {await response.text()}")
        except aiohttp.ClientConnectorError:
            await send_message("Could not connect to Ollama server. Please make sure Ollama is running with 'ollama serve'.")
        except Exception as e:
            await send_message(f"Error checking Ollama status: {str(e)}")