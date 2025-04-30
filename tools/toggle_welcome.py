"""
toggle_welcome.py
Enables or disables the welcome message on bot startup.
Usage: !toggle_welcome
"""

class toggle_welcome:
    description = "Enables or disables the welcome message on bot startup. Usage: !toggle_welcome"
    async def run(self, ctx, bot_tools, *args, **kwargs):
        # Toggle the welcome message enabled flag
        welcome_message_enabled = getattr(bot_tools, 'WELCOME_MESSAGE_ENABLED', True)
        save_channel_data = getattr(bot_tools, 'save_channel_data', None)
        bot_tools.WELCOME_MESSAGE_ENABLED = not welcome_message_enabled
        if save_channel_data:
            save_channel_data()
        state = 'enabled' if bot_tools.WELCOME_MESSAGE_ENABLED else 'disabled'
        await ctx.send(f"Welcome message on startup is now {state}.")