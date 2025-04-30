# NOTE: Do NOT run this file directly.
# To start the bot, use: python main.py
# This file is imported and managed by main.py for proper restart and error handling.
# discord_bot.py
# Main entry point for the Discord AI bot. Handles bot setup, event loop, command routing, and integration with Ollama.

import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from bot_tools import BotTools
import aiohttp
import asyncio
import base64
import re
import signal
import sys
import json
from discord import app_commands

# Load environment variables from .env file
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

# OLLAMA_BASE_URL configuration for all Ollama API calls
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434/api')

# Bot configuration: set up Discord intents and bot instance
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# --- Globals and helpers (minimal, for demo) ---
# These hold bot state and configuration
DEFAULT_MODEL = ""
IMAGE_MODEL = ""
ALLOWED_CHANNELS = []
CHANNEL_RESTRICTION_ENABLED = False
LAST_IMAGE_SENT = {}
CONVERSATION_HISTORY = {}
WELCOME_MESSAGE_ENABLED = True
WELCOME_MESSAGE_CHANNEL_IDS = []

# --- Real Ollama API call for text and image ---
# Sends a prompt to the Ollama server and returns the response
async def get_ollama_response(prompt, model=None, images=None):
    OLLAMA_API_URL = f"{OLLAMA_BASE_URL}/generate"
    global DEFAULT_MODEL, bot_tools
    if model is None:
        model = DEFAULT_MODEL
    # Use the dynamic system prompt from BotTools
    system_prompt = bot_tools.get_system_prompt()
    payload = {
        "model": model,
        "prompt": prompt,
        "system": system_prompt,
        "stream": False
    }
    if images:
        payload["images"] = images
    try:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            async with session.post(OLLAMA_API_URL, json=payload) as response:
                response_text = await response.text()
                if response.status == 200:
                    data = await response.json()
                    return data.get('response', response_text)
                else:
                    return f"Error: Ollama returned status {response.status}: {response_text}"
    except Exception as e:
        return f"Error communicating with Ollama: {e}"

# Fetches the list of available models from Ollama
async def get_available_models():
    OLLAMA_MODELS_URL = f"{OLLAMA_BASE_URL}/tags"
    try:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            async with session.get(OLLAMA_MODELS_URL, timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'models' in data:
                        return [model['name'] for model in data['models']]
                    elif isinstance(data, list):
                        return [model['name'] for model in data]
                return []
    except Exception as e:
        print(f"Error getting models: {e}")
        return []

# --- Channel data helpers ---
# Loads and saves channel and model configuration from channel_data.json
CHANNEL_DATA_FILE = "channel_data.json"
def load_channel_data():
    global ALLOWED_CHANNELS, CHANNEL_RESTRICTION_ENABLED, DEFAULT_MODEL, IMAGE_MODEL, WELCOME_MESSAGE_ENABLED, WELCOME_MESSAGE_CHANNEL_IDS
    try:
        if os.path.exists(CHANNEL_DATA_FILE):
            with open(CHANNEL_DATA_FILE, 'r') as f:
                data = json.load(f)
            ALLOWED_CHANNELS[:] = data.get("allowed_channels", [])
            CHANNEL_RESTRICTION_ENABLED = data.get("restriction_enabled", False)
            DEFAULT_MODEL = data.get("default_model", None)
            IMAGE_MODEL = data.get("image_model", None)
            WELCOME_MESSAGE_ENABLED = data.get("welcome_message_enabled", True)
            WELCOME_MESSAGE_CHANNEL_IDS[:] = data.get("welcome_message_channel_ids", [])
    except Exception as e:
        print(f"Error loading channel data: {e}")

def save_channel_data():
    data = {
        "allowed_channels": ALLOWED_CHANNELS,
        "restriction_enabled": CHANNEL_RESTRICTION_ENABLED,
        "default_model": DEFAULT_MODEL,
        "image_model": IMAGE_MODEL,
        "welcome_message_enabled": WELCOME_MESSAGE_ENABLED,
        "welcome_message_channel_ids": WELCOME_MESSAGE_CHANNEL_IDS
    }
    try:
        with open(CHANNEL_DATA_FILE, 'w') as f:
            json.dump(data, f)
    except Exception as e:
        print(f"Error saving channel data: {e}")

def is_channel_allowed(channel_id):
    if not CHANNEL_RESTRICTION_ENABLED:
        return True
    return channel_id in ALLOWED_CHANNELS

# Load channel data at startup and set defaults
load_channel_data()

# Actually set bot defaults from channel data
bot_tools = BotTools(
    bot,
    get_ollama_response,
    is_channel_allowed,
    get_available_models,
    save_channel_data,
    DEFAULT_MODEL,
    ALLOWED_CHANNELS,
    CHANNEL_RESTRICTION_ENABLED,
    LAST_IMAGE_SENT,
    CONVERSATION_HISTORY,
    WELCOME_MESSAGE_ENABLED,
    WELCOME_MESSAGE_CHANNEL_IDS
)
bot_tools.DEFAULT_MODEL = DEFAULT_MODEL
bot_tools.ALLOWED_CHANNELS = ALLOWED_CHANNELS
bot_tools.CHANNEL_RESTRICTION_ENABLED = CHANNEL_RESTRICTION_ENABLED
bot_tools.WELCOME_MESSAGE_ENABLED = WELCOME_MESSAGE_ENABLED
bot_tools.WELCOME_MESSAGE_CHANNEL_IDS = WELCOME_MESSAGE_CHANNEL_IDS
bot_tools.register_dynamic_tools()

# --- Intent classification helper (copied from discord_bot_final.py) ---
# Uses the LLM to classify user messages into intents for routing
import re
async def get_command_intent(user_message):
    """Ask the LLM to classify the user's intent based on their message."""
    available_models = await get_available_models()
    # No model should ever be specified by default here
    prompt = f"""Analyze the following user request and determine the primary intent. Respond ONLY with a JSON object containing 'intent' and optional 'parameters'.\n\nPossible intents are:\n- 'get_help': User is asking for help or how to use the bot.\n- 'list_models': User wants to see the available models.\n- 'change_model': User wants to switch the AI model. Include the requested model name/keyword in parameters['model_query'].\n- 'check_status': User wants to know the current model.\n- 'general_question': User is asking a general question or making a statement not matching other intents.\n\nUser Request: \"{user_message}\"\n\nJSON Response:"""
    response_text = await get_ollama_response(prompt, model=classifier_model)
    cleaned_response = response_text.strip()
    try:
        match = re.search(r'```(?:json)?\s*({.*?})\s*```', cleaned_response, re.DOTALL)
        if match:
            cleaned_response = match.group(1).strip()
        else:
            json_start = cleaned_response.find('{')
            json_end = cleaned_response.rfind('}')
            if json_start != -1 and json_end != -1 and json_start < json_end:
                cleaned_response = cleaned_response[json_start:json_end+1]
            else:
                raise Exception("Could not extract JSON object from response")
        intent_data = json.loads(cleaned_response)
        if 'intent' not in intent_data:
            raise Exception("Missing 'intent' key in JSON response.")
        if 'parameters' in intent_data and not isinstance(intent_data['parameters'], dict):
            intent_data['parameters'] = {}
        return intent_data
    except Exception:
        return {'intent': 'general_question', 'parameters': {}}

# --- Replace on_message to use intent classification and tool invocation ---
# This event handler routes messages to the correct command or tool
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    ctx = await bot.get_context(message)
    # Only classify if not a command (let commands run as normal)
    if not message.content.startswith('!'):
        if bot.user in message.mentions:
            # Only respond if channel is allowed
            if not is_channel_allowed(message.channel.id):
                return
            user_message = message.content.replace(f'<@{bot.user.id}>', '').strip()
            if not user_message:
                await message.channel.send("Hi! Use `!ask <your question>` or mention me with your question.")
                return
            # --- Image handling ---
            image_data_list = []
            if message.attachments:
                attachment = message.attachments[0]
                if attachment.content_type and attachment.content_type.startswith('image/'):
                    try:
                        image_bytes = await attachment.read()
                        base64_image = base64.b64encode(image_bytes).decode('utf-8')
                        image_data_list.append(base64_image)
                        LAST_IMAGE_SENT[message.channel.id] = base64_image
                    except Exception as e:
                        await message.channel.send(f"⚠️ Error processing image attachment: {e}", delete_after=10)
            elif message.channel.id in LAST_IMAGE_SENT and LAST_IMAGE_SENT[message.channel.id]:
                image_data_list.append(LAST_IMAGE_SENT[message.channel.id])
            # --- Intent classification ---
            intent_data = await get_command_intent(user_message)
            intent = intent_data.get('intent')
            params = intent_data.get('parameters', {})
            async with message.channel.typing():
                # Always pass image if present, and add a hint to the prompt
                if image_data_list:
                    prompt_with_hint = f"[An image is attached to this message.]\n{user_message}"
                    await ctx.invoke(bot.get_command('ask'), prompt_with_hint)
                    return
                if intent == 'list_models':
                    await ctx.invoke(bot.get_command('models'))
                    return
                elif intent == 'check_status':
                    await ctx.invoke(bot.get_command('status'))
                    return
                elif intent == 'change_model' and 'model_query' in params:
                    await ctx.invoke(bot.get_command('model'), params['model_query'])
                    return
                elif intent == 'get_help':
                    await ctx.invoke(bot.get_command('help'))
                    return
                # Otherwise, treat as a general question
                await ctx.invoke(bot.get_command('ask'), user_message)
                return
    # For !commands, also check channel restriction, but always allow add_channel and toggle_channel_restriction
    if (
        message.content.startswith('!')
        and not is_channel_allowed(message.channel.id)
        and not any(
            message.content.lstrip('!').startswith(cmd)
            for cmd in ('add_channel', 'toggle_channel_restriction')
        )
    ):
        return
    await bot.process_commands(message)

# --- on_ready event: runs when the bot connects to Discord ---
@bot.event
async def on_ready():
    async def ensure_models():
        await bot.wait_until_ready()
        # Find a channel to send the prompt (prefer allowed, else first text channel)
        channel = None
        for cid in WELCOME_MESSAGE_CHANNEL_IDS + ALLOWED_CHANNELS:
            ch = bot.get_channel(cid)
            if ch and hasattr(ch, 'send'):
                channel = ch
                break
        if not channel:
            for guild in bot.guilds:
                for ch in guild.text_channels:
                    if ch.permissions_for(guild.me).send_messages:
                        channel = ch
                        break
                if channel:
                    break
        if not channel:
            print("No suitable channel found to prompt for model selection.")
            return
        # Check if models are set and valid
        available_models = await get_available_models()
        # Load persisted image model if present
        image_model = None
        try:
            with open('channel_data.json', 'r') as f:
                data = json.load(f)
                image_model = data.get('image_model')
        except Exception:
            pass
        needs_chat = not bot_tools.DEFAULT_MODEL or bot_tools.DEFAULT_MODEL not in available_models
        needs_vision = not image_model or image_model not in available_models
        if needs_chat or needs_vision:
            msg = """⚠️ **Model selection required!**\n"""
            if needs_chat:
                msg += "Please select a chat model for the bot.\n"
            if needs_vision:
                msg += "Please select a vision model for the bot.\n"
            msg += "\nAvailable models:\n" + "\n".join(f"• {m}" for m in available_models)
            msg += "\n\nUse the `/model` command for chat or `/set_image_model` for vision."
            await channel.send(msg)
        # Send welcome message if enabled and models are selected
        if WELCOME_MESSAGE_ENABLED and bot_tools.DEFAULT_MODEL and bot_tools.IMAGE_MODEL:
            welcome_msg = f"👋 **{bot.user.name} is now online!**\nReady to help. Use `/help` for commands."
            try:
                await channel.send(welcome_msg)
            except Exception:
                pass
        # Check for reset flag and notify if present
        try:
            if os.path.exists('reset_flag.txt'):
                os.remove('reset_flag.txt')
                notify_channel = channel
                if notify_channel:
                    await notify_channel.send('🔄 The bot was just reset and is now back online!')
        except Exception:
            pass
    # Sync slash commands with Discord
    await bot.tree.sync()
    bot.loop.create_task(ensure_models())

# --- Admin/mod management ---
# Functions and commands for managing bot moderators
ADMIN_DATA_FILE = 'admin_data.json'

def load_admins():
    if os.path.exists(ADMIN_DATA_FILE):
        import json
        with open(ADMIN_DATA_FILE, 'r') as f:
            return set(json.load(f).get('admins', []))
    return set()

def save_admins(admins):
    import json
    with open(ADMIN_DATA_FILE, 'w') as f:
        json.dump({'admins': list(admins)}, f)

def is_admin(user, guild):
    admins = load_admins()
    # Always allow server owner
    if guild and user.id == guild.owner_id:
        return True
    # Check if user is in the admin user list
    if user.id in admins:
        return True
    # Check if user has any admin role
    try:
        import json
        with open('admin_data.json', 'r') as f:
            data = json.load(f)
        admin_roles = set(data.get('admin_roles', []))
        if hasattr(user, 'roles'):
            user_role_ids = {role.id for role in getattr(user, 'roles', [])}
            if admin_roles & user_role_ids:
                return True
    except Exception:
        pass
    return False

# --- Moderator commands ---
@bot.command(name='add_mod')
@commands.has_permissions(administrator=True)
async def add_mod(ctx, user: discord.Member):
    admins = load_admins()
    admins.add(user.id)
    save_admins(admins)
    await ctx.send(f"✅ {user.mention} has been added as a bot moderator.")

@bot.command(name='remove_mod')
@commands.has_permissions(administrator=True)
async def remove_mod(ctx, user: discord.Member):
    admins = load_admins()
    if user.id in admins:
        admins.remove(user.id)
        save_admins(admins)
        await ctx.send(f"✅ {user.mention} has been removed as a bot moderator.")
    else:
        await ctx.send(f"{user.mention} is not a bot moderator.")

@bot.command(name='list_mods')
@commands.has_permissions(administrator=True)
async def list_mods(ctx):
    admins = load_admins()
    mentions = []
    for uid in admins:
        member = ctx.guild.get_member(uid)
        if member:
            mentions.append(member.mention)
        else:
            mentions.append(f"Unknown User ({uid})")
    await ctx.send("**Bot Moderators:**\n" + "\n".join(mentions) if mentions else "No additional moderators set.")

@bot.command(name='reset')
async def reset(ctx):
    if not is_admin(ctx.author, ctx.guild):
        await ctx.send("❌ Only the server owner or a bot moderator can use this command.")
        return
    await ctx.send("♻️ Restarting bot...")
    global SHOULD_RESTART
    try:
        with open('reset_flag.txt', 'w') as f:
            f.write('reset')
    except Exception:
        pass
    SHOULD_RESTART = True
    bot.loop.call_soon_threadsafe(bot.loop.stop)

@app_commands.command(name="reset", description="Restart the bot (admin only)")
async def reset_slash(interaction):
    if not is_admin(interaction.user, interaction.guild):
        await interaction.response.send_message("❌ Only the server owner or a bot moderator can use this command.", ephemeral=True)
        return
    await interaction.response.send_message("♻️ Restarting bot...", ephemeral=True)
    global SHOULD_RESTART
    try:
        with open('reset_flag.txt', 'w') as f:
            f.write('reset')
    except Exception:
        pass
    SHOULD_RESTART = True
    bot.loop.call_soon_threadsafe(bot.loop.stop)

# Register the slash command
bot.tree.add_command(reset_slash)

# --- Main entry point for running the bot ---
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run the Discord AI bot.")
    parser.add_argument("-verbose", action="store_true", help="Enable verbose debug output")
    args = parser.parse_args()

    VERBOSE_MODE = args.verbose if hasattr(args, 'verbose') else False
    if (VERBOSE_MODE):
        print("Verbose mode enabled.")

    if not DISCORD_TOKEN:
        print("Error: Discord token not found. Please set DISCORD_TOKEN in .env file")
        sys.exit(1)
    print("Running bot...")
    SHOULD_RESTART = False
    try:
        bot.run(DISCORD_TOKEN)
    finally:
        if SHOULD_RESTART:
            sys.exit(100)
        else:
            sys.exit(0)
