"""
add_channel.py
Adds the current channel to the list of allowed channels for bot commands.
Usage: /add_channel
"""

class add_channel:
    admin_only = True
    description = "Adds the current channel to the list of allowed channels for bot commands. Usage: /add_channel"
    async def run(self, ctx, bot_tools, *args, **kwargs):
        # Get the current channel ID
        channel_id = ctx.channel.id
        # Get the list of allowed channels from bot_tools
        allowed_channels = getattr(bot_tools, 'ALLOWED_CHANNELS', [])
        channel_restriction_enabled = getattr(bot_tools, 'CHANNEL_RESTRICTION_ENABLED', False)
        save_channel_data = getattr(bot_tools, 'save_channel_data', None)
        
        async def send_message(msg):
            if hasattr(ctx, 'response') and hasattr(ctx.response, 'is_done'):
                if not ctx.response.is_done():
                    await ctx.response.send_message(msg)
                else:
                    await ctx.followup.send(msg)
            else:
                await ctx.send(msg)
                
        # If already allowed, notify user
        if channel_id in allowed_channels:
            await send_message("Channel is already in the allowed list.")
            return
        # Add channel to allowed list
        allowed_channels.append(channel_id)
        # Enable restriction if this is the first allowed channel
        if len(allowed_channels) == 1 and not channel_restriction_enabled:
            channel_restriction_enabled = True
        if save_channel_data:
            save_channel_data()
        await send_message("Added channel to the allowed list.")