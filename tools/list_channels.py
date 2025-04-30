"""
list_channels.py
Lists all channels where the bot is currently allowed to operate.
Usage: !list_channels
"""

class list_channels:
    description = "Lists all channels where the bot is currently allowed to operate. Usage: !list_channels"
    async def run(self, ctx, bot_tools, *args, **kwargs):
        # Get allowed channels and restriction status
        allowed_channels = getattr(bot_tools, 'ALLOWED_CHANNELS', [])
        channel_restriction_enabled = getattr(bot_tools, 'CHANNEL_RESTRICTION_ENABLED', False)
        bot = getattr(bot_tools, 'bot', None)
        # If no allowed channels, notify user
        if not allowed_channels:
            await ctx.send(f"No channels are in the allowed list. Channel restriction is currently {'enabled' if channel_restriction_enabled else 'disabled'}.")
            return
        channel_names = []
        # Build a list of channel names or IDs
        for channel_id in allowed_channels:
            channel = bot.get_channel(channel_id) if bot else None
            if channel:
                channel_names.append(f"#{channel.name} (ID: {channel_id})")
            else:
                channel_names.append(f"Unknown channel (ID: {channel_id})")
        channels_list = "\n".join(channel_names)
        await ctx.send(f"**Allowed Channels:**\n{channels_list}\nChannel restriction is currently {'enabled' if channel_restriction_enabled else 'disabled'}.")