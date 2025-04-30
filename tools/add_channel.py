"""
add_channel.py
Adds the current channel to the list of allowed channels for bot commands.
Usage: !add_channel
"""

class add_channel:
    description = "Adds the current channel to the list of allowed channels for bot commands. Usage: !add_channel"
    async def run(self, ctx, bot_tools, *args, **kwargs):
        # Get the current channel ID
        channel_id = ctx.channel.id
        # Get the list of allowed channels from bot_tools
        allowed_channels = getattr(bot_tools, 'ALLOWED_CHANNELS', [])
        channel_restriction_enabled = getattr(bot_tools, 'CHANNEL_RESTRICTION_ENABLED', False)
        save_channel_data = getattr(bot_tools, 'save_channel_data', None)
        # If already allowed, notify user
        if channel_id in allowed_channels:
            await ctx.send("Channel is already in the allowed list.")
            return
        # Add channel to allowed list
        allowed_channels.append(channel_id)
        # Enable restriction if this is the first allowed channel
        if len(allowed_channels) == 1 and not channel_restriction_enabled:
            channel_restriction_enabled = True
        if save_channel_data:
            save_channel_data()
        await ctx.send("Added channel to the allowed list.")