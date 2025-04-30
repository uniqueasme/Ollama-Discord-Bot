"""
set_classifier_model.py
Sets the preferred model for intent classification.
Usage: !set_classifier_model <model_name>
"""

import json

class set_classifier_model:
    admin_only = True
    description = "Sets the preferred model for intent classification. Usage: !set_classifier_model <model_name>"
    async def run(self, ctx, bot_tools, *args, **kwargs):
        # Require a model name argument
        if not args:
            await ctx.send("Please specify a model name. Usage: !set_classifier_model <model_name>")
            return
        model_name = args[0]
        get_available_models = getattr(bot_tools, 'get_available_models', None)
        if not get_available_models:
            await ctx.send("Could not retrieve available models.")
            return
        available_models = await get_available_models()
        if model_name not in available_models:
            await ctx.send(f"Model '{model_name}' not found. Available models: {', '.join(available_models)}")
            return
        # Save the classifier model to channel_data.json
        try:
            with open('channel_data.json', 'r') as f:
                data = json.load(f)
            data['classifier_model'] = model_name
            with open('channel_data.json', 'w') as f:
                json.dump(data, f)
            await ctx.send(f"Classifier model set to '{model_name}'.")
        except Exception as e:
            await ctx.send(f"Error saving classifier model: {e}")