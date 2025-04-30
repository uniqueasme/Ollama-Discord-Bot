"""
model.py
Changes the AI model used for responses.
Usage: !model <model_name>
"""

class model:
    description = "Changes the AI model used for responses. Usage: !model <model_name>"
    async def run(self, ctx, bot_tools, *args, **kwargs):
        # Require a model name argument
        if not args:
            await ctx.send("Please specify a model name. Usage: !model <model_name>")
            return
        model_name = args[0]
        get_available_models = getattr(bot_tools, 'get_available_models', None)
        get_ollama_response = getattr(bot_tools, 'get_ollama_response', None)
        save_default_model = getattr(bot_tools, '_save_default_model', None)
        # Check for required functions
        if not (get_available_models and get_ollama_response and save_default_model):
            await ctx.send("Model switching is not available in this context.")
            return
        available_models = await get_available_models()
        if not available_models:
            await ctx.send("Could not retrieve available models. Please check if Ollama is running.")
            return
        if model_name not in available_models:
            await ctx.send(f"Model '{model_name}' not found. Available models: {', '.join(available_models)}")
            return
        # Test the model with a simple prompt
        test_response = await get_ollama_response("Hi", model_name)
        if isinstance(test_response, str) and test_response.startswith("Error:"):
            await ctx.send(test_response)
            return
        save_default_model(model_name)
        await ctx.send(f"Successfully switched to model: {model_name}")