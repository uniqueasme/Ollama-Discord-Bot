"""
clear_welcome_channels.py
Clears the list of specific channels for welcome messages, reverting to default behavior.
Usage: !clear_welcome_channels
"""

class clear_welcome_channels:
    admin_only = True
    description = "Clears the list of specific channels for welcome messages, reverting to default behavior. Usage: !clear_welcome_channels"
    async def run(self, ctx, bot_tools, *args, **kwargs):
        # Get the list of welcome message channel IDs
        welcome_message_channel_ids = getattr(bot_tools, 'WELCOME_MESSAGE_CHANNEL_IDS', [])
        save_channel_data = getattr(bot_tools, 'save_channel_data', None)
        
        async def send_message(msg):
            if hasattr(ctx, 'response') and hasattr(ctx.response, 'is_done'):
                if not ctx.response.is_done():
                    await ctx.response.send_message(msg)
                else:
                    await ctx.followup.send(msg)
            else:
                await ctx.send(msg)
                
        # If the list is not empty, clear it and notify user
        if welcome_message_channel_ids:
            welcome_message_channel_ids.clear()
            if save_channel_data:
                save_channel_data()
            await send_message("Cleared the specific welcome channel list. Welcome message will now use default behavior.")
        else:
            await send_message("The specific welcome channel list is already empty.")