"""
set_image_model.py
Sets the model used for image reading and analysis.
Usage: !set_image_model <model_name>
"""

import json

class set_image_model:
    description = "Sets the model used for image reading and analysis. Usage: !set_image_model <model_name>"
    async def run(self, ctx, bot_tools, *args, **kwargs):
        # Require a model name argument
        if not args:
            await ctx.send("Please specify a model name. Usage: !set_image_model <model_name>")
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
        # Save the image model to channel_data.json and update bot_tools
        try:
            with open('channel_data.json', 'r') as f:
                data = json.load(f)
            data['image_model'] = model_name
            with open('channel_data.json', 'w') as f:
                json.dump(data, f)
            bot_tools.IMAGE_MODEL = model_name
            await ctx.send(f"Image model set to '{model_name}'.")
        except Exception as e:
            await ctx.send(f"Error saving image model: {e}")