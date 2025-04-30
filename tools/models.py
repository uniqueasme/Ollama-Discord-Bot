"""
models.py
Lists all available AI models and shows the current one.
Usage: !models
"""

class models:
    description = "Lists all available AI models and shows the current one. Usage: !models"
    async def run(self, ctx, bot_tools, *args, **kwargs):
        # Get available models and current default model
        get_available_models = getattr(bot_tools, 'get_available_models', None)
        default_model = getattr(bot_tools, 'DEFAULT_MODEL', None)
        if not get_available_models:
            await ctx.send("Could not retrieve available models.")
            return
        available_models = await get_available_models()
        if not available_models:
            await ctx.send("No models found. You may need to pull models first with Ollama.")
            return
        current = f"Current model: **{default_model}**\n\n"
        models_list = "\n".join([f"• {model}" for model in available_models])
        await ctx.send(f"{current}**Available Models:**\n{models_list}\n\nUse `!model <model_name>` to switch models.")