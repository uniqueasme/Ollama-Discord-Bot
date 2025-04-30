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
            "For each command, write the description as a complete sentence, ending with a period. "
            "For example:\n"
            "- `/ask`: Asks the AI a question and gets a response.\n"
            "- `/model`: Changes the AI model used for responses.\n"
            "Explain what each command does and provide a brief example if helpful. "
            f"Mention that users can also interact by replying to you or mentioning you (@{bot_name})."
        )
        ai_help_explanation = None
        if get_ollama_response:
            try:
                ai_help_explanation = await get_ollama_response(help_prompt)
            except Exception:
                ai_help_explanation = None

        async def send_message(ctx, msg):
            if hasattr(ctx, 'response') and hasattr(ctx.response, 'is_done'):
                if not ctx.response.is_done():
                    await ctx.response.send_message(msg)
                else:
                    await ctx.followup.send(msg)
            else:
                await ctx.send(msg)

        def split_message_safely(text, max_length=2000):
            import re
            # Split by list items (lines starting with - or *)
            lines = text.split('\n')
            chunks = []
            current = ''
            for line in lines:
                # If adding this line would exceed max_length, start a new chunk
                if len(current) + len(line) + 1 > max_length:
                    if current:
                        chunks.append(current.strip())
                    current = line
                else:
                    if current:
                        current += '\n' + line
                    else:
                        current = line
            if current:
                chunks.append(current.strip())
            # Fallback: hard split any chunk still too long
            final_chunks = []
            for chunk in chunks:
                if len(chunk) <= max_length:
                    final_chunks.append(chunk)
                else:
                    for i in range(0, len(chunk), max_length):
                        final_chunks.append(chunk[i:i+max_length])
            return final_chunks

        # If model/server is down, show a static help message
        if not ai_help_explanation or (isinstance(ai_help_explanation, str) and ai_help_explanation.strip().lower().startswith("error")):
            static_help = f"👋 **Hello! Here's how you can interact with me ({bot_name}):**\n\nYou can use the following commands:\n\n{command_list_str}\n\n*You can also often get me to perform actions like listing models or asking for help by just replying to me or mentioning me (@{bot_name}) with your request!*\n*I work best in allowed channels or DMs if we share a server.*"
            for chunk in split_message_safely(static_help):
                await send_message(ctx, chunk)
            return
        # Send the AI-generated or static help message
        final_help_message = f"👋 **Hello! Here's how you can interact with me ({bot_name}):**\n\nYou can use the following commands:\n\n{ai_help_explanation}\n\n*You can also often get me to perform actions like listing models or asking for help by just replying to me or mentioning me (@{bot_name}) with your request!*\n*I work best in allowed channels or DMs if we share a server.*"
        for chunk in split_message_safely(final_help_message):
            await send_message(ctx, chunk)