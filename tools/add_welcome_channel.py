"""
add_welcome_channel.py
Adds the current channel to the list of channels that receive the welcome message on bot startup.
Usage: !add_welcome_channel
"""

class add_welcome_channel:
    admin_only = True
    description = "Adds the current channel to the list of channels that receive the welcome message on bot startup. Usage: !add_welcome_channel"
    async def run(self, ctx, bot_tools, *args, **kwargs):
        # Get the current channel ID
        channel_id = ctx.channel.id
        # Get the list of welcome message channel IDs
        welcome_message_channel_ids = getattr(bot_tools, 'WELCOME_MESSAGE_CHANNEL_IDS', [])
        save_channel_data = getattr(bot_tools, 'save_channel_data', None)
        # If already in the list, notify user
        if channel_id not in welcome_message_channel_ids:
            welcome_message_channel_ids.append(channel_id)
            if save_channel_data:
                save_channel_data()
            await ctx.send(f"Added channel (ID: {channel_id}) to the specific welcome message channels list.")
        else:
            await ctx.send(f"Channel (ID: {channel_id}) is already in the specific welcome message channels list.")