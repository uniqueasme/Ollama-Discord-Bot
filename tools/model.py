"""
model.py
Changes the AI model used for responses.
Usage: /model <model_name>
"""

class model:
    admin_only = True
    description = "Changes the AI model used for responses. Usage: /model <model_name>"
    async def run(self, ctx, bot_tools, *args, **kwargs):
        async def send_message(msg):
            if hasattr(ctx, 'response') and hasattr(ctx.response, 'is_done'):
                if not ctx.response.is_done():
                    await ctx.response.send_message(msg)
                else:
                    await ctx.followup.send(msg)
            else:
                await ctx.send(msg)
        # Require a model name argument
        if not args:
            await send_message("Please specify a model name. Usage: !model <model_name>")
            return
        model_name = args[0]
        get_available_models = getattr(bot_tools, 'get_available_models', None)
        get_ollama_response = getattr(bot_tools, 'get_ollama_response', None)
        save_default_model = getattr(bot_tools, '_save_default_model', None)
        # Check for required functions
        if not (get_available_models and get_ollama_response and save_default_model):
            await send_message("Model switching is not available in this context.")
            return
        available_models = await get_available_models()
        if not available_models:
            await send_message("Could not retrieve available models. Please check if Ollama is running.")
            return
        if model_name not in available_models:
            await send_message(f"Model '{model_name}' not found. Available models: {', '.join(available_models)}")
            return
        # Test the model with a simple prompt
        test_response = await get_ollama_response("Hi", model_name)
        if isinstance(test_response, str) and test_response.startswith("Error:"):
            await send_message(test_response)
            return
        save_default_model(model_name)
        await send_message(f"Successfully switched to model: {model_name}")