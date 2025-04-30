"""
remove_channel.py
Removes the current channel from the list of allowed channels for bot commands.
Usage: !remove_channel
"""

class remove_channel:
    admin_only = True
    description = "Removes the current channel from the list of allowed channels for bot commands. Usage: !remove_channel"
    async def run(self, ctx, bot_tools, *args, **kwargs):
        # Get the current channel ID
        channel_id = ctx.channel.id
        allowed_channels = getattr(bot_tools, 'ALLOWED_CHANNELS', [])
        save_channel_data = getattr(bot_tools, 'save_channel_data', None)
        
        async def send_message(msg):
            if hasattr(ctx, 'response') and hasattr(ctx.response, 'is_done'):
                if not ctx.response.is_done():
                    await ctx.response.send_message(msg)
                else:
                    await ctx.followup.send(msg)
            else:
                await ctx.send(msg)
                
        # If the channel is in the allowed list, remove it
        if channel_id in allowed_channels:
            allowed_channels.remove(channel_id)
            if save_channel_data:
                save_channel_data()
            # Remove conversation and image context for this channel
            if hasattr(bot_tools, 'CONVERSATION_HISTORY') and channel_id in bot_tools.CONVERSATION_HISTORY:
                del bot_tools.CONVERSATION_HISTORY[channel_id]
            if hasattr(bot_tools, 'LAST_IMAGE_SENT') and channel_id in bot_tools.LAST_IMAGE_SENT:
                del bot_tools.LAST_IMAGE_SENT[channel_id]
            await send_message("Removed channel from the allowed list. The bot will no longer respond in this channel.")
        else:
            await send_message("Channel is not in the allowed list.")