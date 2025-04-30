"""
remove_welcome_channel.py
Removes the current channel from the list of channels that receive the welcome message on bot startup.
Usage: !remove_welcome_channel
"""

class remove_welcome_channel:
    description = "Removes the current channel from the list of channels that receive the welcome message on bot startup. Usage: !remove_welcome_channel"
    admin_only = True
    async def run(self, ctx, bot_tools, *args, **kwargs):
        # Get the current channel ID
        channel_id = ctx.channel.id
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
                
        # If the channel is in the welcome list, remove it
        if channel_id in welcome_message_channel_ids:
            welcome_message_channel_ids.remove(channel_id)
            if save_channel_data:
                save_channel_data()
            msg = f"Removed channel (ID: {channel_id}) from the specific welcome message channels list."
            if not welcome_message_channel_ids:
                msg += " The specific welcome channel list is now empty. Welcome message will use default behavior."
            await send_message(msg)
        else:
            await send_message(f"Channel (ID: {channel_id}) is not in the specific welcome message channels list.")