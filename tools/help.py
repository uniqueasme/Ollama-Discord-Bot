"""
help.py
Shows a help message explaining all available commands and their usage.
Usage: /help
"""

class help:
    description = "Shows a help message explaining all available commands and their usage. Usage: /help"
    
    async def run(self, ctx, bot_tools, *args, **kwargs):
        # Get bot name and model for help context
        bot_name = bot_tools.bot.user.name if hasattr(bot_tools.bot, 'user') and bot_tools.bot.user else 'Bot'
        default_model = getattr(bot_tools, 'DEFAULT_MODEL', '')
        get_ollama_response = getattr(bot_tools, 'get_ollama_response', None)
        import os, importlib.util
        tools_path = os.path.join(os.path.dirname(os.path.abspath(__file__)))
        command_list = {}
        # Dynamically build a list of all available commands and their descriptions
        for filename in os.listdir(tools_path):
            if filename.endswith('.py') and not filename.startswith('__'):
                tool_name = filename[:-3]
                spec = importlib.util.spec_from_file_location(tool_name, os.path.join(tools_path, filename))
                module = importlib.util.module_from_spec(spec)
                try:
                    spec.loader.exec_module(module)
                    tool_class = getattr(module, tool_name, None)
                    if tool_class and hasattr(tool_class, 'description'):
                        desc = getattr(tool_class, 'description')
                        summary = desc.split(". Usage:")[0] if ". Usage:" in desc else desc
                        command_list[f'/{tool_name}'] = summary
                except Exception:
                    continue
        command_list_str = "\n".join([f"- `{cmd}`: {desc}" for cmd, desc in command_list.items()])
        # Compose the help prompt for the AI model
        help_prompt = (
            f"You are the AI assistant {bot_name} powered by {default_model}.\n"
            "ONLY explain the following commands. Do NOT invent or mention any commands that are not in this list. "
            "If a user asks for a command not in this list, say it does not exist.\n"
            f"Available Commands:\n{command_list_str}\n"
            "Explain what each command does and provide a brief example if helpful. "
            f"Mention that users can also interact by replying to you or mentioning you (@{bot_name})."
        )
        ai_help_explanation = None
        if get_ollama_response:
            try:
                ai_help_explanation = await get_ollama_response(help_prompt)
            except Exception:
                ai_help_explanation = None
        # If model/server is down, show a static help message
        async def send_message(msg):
            if hasattr(ctx, 'response') and hasattr(ctx.response, 'is_done'):
                if not ctx.response.is_done():
                    await ctx.response.send_message(msg)
                else:
                    await ctx.followup.send(msg)
            else:
                await ctx.send(msg)
        def split_message_by_sentence(text, max_length=2000):
            import re
            sentences = re.split(r'(?<=[.!?]) +', text)
            chunks = []
            current_chunk = ''
            for sentence in sentences:
                if len(current_chunk) + len(sentence) + 1 > max_length:
                    if current_chunk:
                        chunks.append(current_chunk)
                    current_chunk = sentence
                else:
                    if current_chunk:
                        current_chunk += ' ' + sentence
                    else:
                        current_chunk = sentence
            if current_chunk:
                chunks.append(current_chunk)
            return chunks
        if not ai_help_explanation or (isinstance(ai_help_explanation, str) and ai_help_explanation.strip().lower().startswith("error")):
            static_help = f"👋 **Hello! Here's how you can interact with me ({bot_name}):**\n\nYou can use the following commands:\n\n{command_list_str}\n\n*You can also often get me to perform actions like listing models or asking for help by just replying to me or mentioning me (@{bot_name}) with your request!*\n*I work best in allowed channels or DMs if we share a server.*"
            for chunk in split_message_by_sentence(static_help):
                await send_message(chunk)
            return
        # Send the AI-generated or static help message
        final_help_message = f"👋 **Hello! Here's how you can interact with me ({bot_name}):**\n\nYou can use the following commands:\n\n{ai_help_explanation}\n\n*You can also often get me to perform actions like listing models or asking for help by just replying to me or mentioning me (@{bot_name}) with your request!*\n*I work best in allowed channels or DMs if we share a server.*"
        for chunk in split_message_by_sentence(final_help_message):
            await send_message(chunk)