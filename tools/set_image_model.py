"""
set_image_model.py
Sets the model used for image reading and analysis.
Usage: /set_image_model <model_name>
"""

import json

class set_image_model:
    admin_only = True
    description = "Sets the model used for image reading and analysis. Usage: /set_image_model <model_name>"
    async def run(self, ctx, bot_tools, *args, **kwargs):
        # Require a model name argument
        if not args:
            await send_message("Please specify a model name. Usage: !set_image_model <model_name>")
            return
        model_name = args[0]
        get_available_models = getattr(bot_tools, 'get_available_models', None)
        if not get_available_models:
            await send_message("Could not retrieve available models.")
            return
        available_models = await get_available_models()
        if model_name not in available_models:
            await send_message(f"Model '{model_name}' not found. Available models: {', '.join(available_models)}")
            return
        # Save the image model to channel_data.json and update bot_tools
        try:
            with open('channel_data.json', 'r') as f:
                data = json.load(f)
            data['image_model'] = model_name
            with open('channel_data.json', 'w') as f:
                json.dump(data, f)
            bot_tools.IMAGE_MODEL = model_name
            await send_message(f"Image model set to '{model_name}'.")
        except Exception as e:
            await send_message(f"Error saving image model: {e}")

        async def send_message(msg):
            if hasattr(ctx, 'response') and hasattr(ctx.response, 'is_done'):
                if not ctx.response.is_done():
                    await ctx.response.send_message(msg)
                else:
                    await ctx.followup.send(msg)
            else:
                await ctx.send(msg)