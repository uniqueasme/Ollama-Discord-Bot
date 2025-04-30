"""
toggle_channel_restriction.py
Toggles channel restriction on or off globally for the bot.
Usage: !toggle_channel_restriction
"""

class toggle_channel_restriction:
    description = "Toggles channel restriction on or off globally for the bot. Usage: !toggle_channel_restriction"
    async def run(self, ctx, bot_tools, *args, **kwargs):
        # Toggle the restriction flag
        save_channel_data = getattr(bot_tools, 'save_channel_data', None)
        bot_tools.CHANNEL_RESTRICTION_ENABLED = not getattr(bot_tools, 'CHANNEL_RESTRICTION_ENABLED', False)
        state = 'enabled' if bot_tools.CHANNEL_RESTRICTION_ENABLED else 'disabled'
        await ctx.send(f"Channel restriction is now {state}.")
        if save_channel_data:
            save_channel_data()
        # Also update the JSON file directly to ensure persistence
        import json
        try:
            with open('channel_data.json', 'r') as f:
                data = json.load(f)
            data['restriction_enabled'] = bot_tools.CHANNEL_RESTRICTION_ENABLED
            with open('channel_data.json', 'w') as f:
                json.dump(data, f)
        except Exception as e:
            await ctx.send(f"Warning: Could not update channel_data.json: {e}")