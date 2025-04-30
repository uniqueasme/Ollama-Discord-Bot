# bot_tools.py
# Contains the BotTools class and helpers for dynamic tool registration, model management, and system prompt construction.

import discord
from discord.ext import commands
import aiohttp
import base64
import os
import asyncio
import json

# Decorator for tool metadata (description and usage)
def tool_meta(description, usage):
    def decorator(func):
        func._tool_description = description
        func._tool_usage = usage
        return func
    return decorator

class BotTools:
    def __init__(self, bot, get_ollama_response, is_channel_allowed, get_available_models, save_channel_data, DEFAULT_MODEL, ALLOWED_CHANNELS, CHANNEL_RESTRICTION_ENABLED, LAST_IMAGE_SENT, CONVERSATION_HISTORY, WELCOME_MESSAGE_ENABLED, WELCOME_MESSAGE_CHANNEL_IDS):
        # Store references to bot and helpers
        self.bot = bot
        self.get_ollama_response = get_ollama_response
        self.is_channel_allowed = is_channel_allowed
        self.get_available_models = get_available_models
        self.save_channel_data = save_channel_data
        self.DEFAULT_MODEL = DEFAULT_MODEL
        self.ALLOWED_CHANNELS = ALLOWED_CHANNELS
        self.CHANNEL_RESTRICTION_ENABLED = CHANNEL_RESTRICTION_ENABLED
        self.LAST_IMAGE_SENT = LAST_IMAGE_SENT
        self.CONVERSATION_HISTORY = CONVERSATION_HISTORY
        self.WELCOME_MESSAGE_ENABLED = WELCOME_MESSAGE_ENABLED
        self.WELCOME_MESSAGE_CHANNEL_IDS = WELCOME_MESSAGE_CHANNEL_IDS
        # Add image model config
        self.IMAGE_MODEL = self._load_image_model()
        self.VISION_MODEL = None

    # Load the image model from channel_data.json
    def _load_image_model(self):
        try:
            with open('channel_data.json', 'r') as f:
                data = json.load(f)
            return data.get('image_model', None)
        except Exception:
            return None

    # Save the image model to channel_data.json
    def _save_image_model(self, model_name):
        try:
            with open('channel_data.json', 'r') as f:
                data = json.load(f)
            data['image_model'] = model_name
            # Also save the current default_model if set
            if hasattr(self, 'DEFAULT_MODEL') and self.DEFAULT_MODEL:
                data['default_model'] = self.DEFAULT_MODEL
            with open('channel_data.json', 'w') as f:
                json.dump(data, f)
            self.IMAGE_MODEL = model_name
        except Exception:
            pass

    # Save the default model to channel_data.json
    def _save_default_model(self, model_name):
        try:
            with open('channel_data.json', 'r') as f:
                data = json.load(f)
            data['default_model'] = model_name
            # Also save the current image_model if set
            if hasattr(self, 'IMAGE_MODEL') and self.IMAGE_MODEL:
                data['image_model'] = self.IMAGE_MODEL
            with open('channel_data.json', 'w') as f:
                json.dump(data, f)
            self.DEFAULT_MODEL = model_name
        except Exception:
            pass

    # Ensure both chat and vision models are selected and available
    async def _ensure_models_selected(self):
        available_models = await self.get_available_models()
        # Check for default_model (chat) and vision_model
        config_changed = False
        if not hasattr(self, 'DEFAULT_MODEL') or self.DEFAULT_MODEL not in available_models:
            # Ask user to pick a chat model
            self.DEFAULT_MODEL = await self._prompt_model_selection('chat', available_models)
            config_changed = True
        if not hasattr(self, 'VISION_MODEL') or not self.VISION_MODEL or self.VISION_MODEL not in available_models:
            # Ask user to pick a vision model
            self.VISION_MODEL = await self._prompt_model_selection('vision', available_models)
            config_changed = True
        if config_changed:
            self.save_channel_data()

    # Prompt user to select a model (placeholder logic)
    async def _prompt_model_selection(self, model_type, available_models):
        # This is a placeholder for actual Discord prompt logic
        # In production, you would send a message to the admin or allowed channel and wait for a reply
        # For now, just pick the first available model
        for model in available_models:
            if model_type == 'vision' and ("vision" in model or "llava" in model):
                return model
            if model_type == 'chat' and ("chat" in model or "llama" in model):
                return model
        return available_models[0] if available_models else None

    def register(self):
        # This method is now deprecated. Use register_dynamic_tools instead.
        pass

    # Dynamically register all tools in the tools/ directory as bot commands
    def register_dynamic_tools(self):
        import importlib.util
        import inspect
        import glob
        import sys
        from discord.ext import commands
        
        tools_path = os.path.join(os.path.dirname(__file__), 'tools')
        tool_files = glob.glob(os.path.join(tools_path, '*.py'))
        def make_dynamic_command(tool_class, tool_name, description):
            async def dynamic_command(ctx, *args):
                # Always allow !add_channel and !toggle_channel_restriction in any channel, even if restriction is enabled
                if tool_name in ('add_channel', 'toggle_channel_restriction'):
                    pass
                elif not self.is_channel_allowed(ctx.channel.id):
                    await ctx.send("This channel is not allowed. Use !add_channel to enable bot commands here.")
                    return
                run_method = getattr(tool_class, 'run', None)
                if run_method is None:
                    await ctx.send(f"Tool '{tool_name}' does not implement a run method.")
                    return
                import inspect
                sig = inspect.signature(run_method)
                params = list(sig.parameters.keys())
                try:
                    async with ctx.typing():
                        result = run_method(tool_class(), ctx, self, *args)
                        if inspect.isawaitable(result):
                            result = await result
                        if isinstance(result, tuple):
                            await ctx.send(str(result[1]))
                        elif result is not None:
                            await ctx.send(str(result))
                except Exception as e:
                    await ctx.send(f"Error running tool '{tool_name}': {e}")
            return self.bot.command(name=tool_name, help=description, ignore_extra=True)(dynamic_command)
        for tool_file in tool_files:
            tool_name = os.path.splitext(os.path.basename(tool_file))[0]
            if tool_name.startswith('__'):
                continue
            spec = importlib.util.spec_from_file_location(tool_name, tool_file)
            module = importlib.util.module_from_spec(spec)
            sys.modules[tool_name] = module
            spec.loader.exec_module(module)
            tool_class = getattr(module, tool_name, None)
            if tool_class is None or not inspect.isclass(tool_class):
                continue
            description = getattr(tool_class, 'description', f'No description for {tool_name}')
            make_dynamic_command(tool_class, tool_name, description)

    # Get a string listing all registered tools and their descriptions
    @staticmethod
    def get_tools_info_string():
        lines = []
        for attr in dir(BotTools):
            func = getattr(BotTools, attr)
            if callable(func) and hasattr(func, '_tool_description') and hasattr(func, '_tool_usage'):
                lines.append(f"{func._tool_usage}: {func._tool_description}")
        return "\n".join(lines)

    # Build the system prompt for the LLM, listing all available tools
    def get_system_prompt(self):
        tool_list = self.get_tools_info_string()
        return (
            "You are an helpfull assistant of the coolest Discord server."
            "You have access to the following tools/commands, each with a specific function. "
            "If a user asks for something that can be accomplished with a tool/command, you must use the tool directly in code, never by outputting a !command as a user would. "
            "Never invent or simulate the results of a tool/command—always use the real tool/command when available. "
            "If you are unsure which tool to use, or if you need to explain the available tools to a user, use the help tool directly, not by outputting !help. "
            "Do not invent or mention tools/commands that are not listed below. "
            "If a user attaches an image, you must carefully check if their request is about the image (e.g., asking for analysis, description, or information about the image) or if it is a general question. Only use your vision/image analysis capabilities if the user is clearly referring to the image. If not, treat the request as a normal text question. "
            "Here are the available tools/commands, each with its usage and description:\n"
            f"{tool_list}\n"
            "If you are asked to do something that requires a tool, use the tool directly in code and wait for the result. Never output !commands as a user would."
        )