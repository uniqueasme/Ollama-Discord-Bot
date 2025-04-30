"""
list_welcome_channels.py
Lists all channels set to receive the welcome message on bot startup.
Usage: !list_welcome_channels
"""

class list_welcome_channels:
    description = "Lists all channels set to receive the welcome message on bot startup. Usage: !list_welcome_channels"
    async def run(self, ctx, bot_tools, *args, **kwargs):
        # Get welcome message channel IDs and status
        welcome_message_channel_ids = getattr(bot_tools, 'WELCOME_MESSAGE_CHANNEL_IDS', [])
        welcome_message_enabled = getattr(bot_tools, 'WELCOME_MESSAGE_ENABLED', True)
        bot = getattr(bot_tools, 'bot', None)
        
        async def send_message(msg):
            if hasattr(ctx, 'response') and hasattr(ctx.response, 'is_done'):
                if not ctx.response.is_done():
                    await ctx.response.send_message(msg)
                else:
                    await ctx.followup.send(msg)
            else:
                await ctx.send(msg)
                
        # Build a list of channel mentions or IDs
        if welcome_message_channel_ids:
            channel_mentions = []
            for channel_id in welcome_message_channel_ids:
                ch = bot.get_channel(channel_id) if bot else None
                channel_mentions.append(ch.mention if ch else f"Unknown Channel ({channel_id})")
            msg = f"**Specific Welcome Message Channels:**\n" + '\n'.join(channel_mentions)
        else:
            msg = "No specific channels set for the welcome message. It will be sent to the first available/allowed channel in each server."
        msg += f"\nWelcome message on startup is currently **{'enabled' if welcome_message_enabled else 'disabled'}**."
        await send_message(msg)