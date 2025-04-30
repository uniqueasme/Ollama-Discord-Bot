"""
clearhistory.py
Clears the conversation history and last image context for the current channel.
Usage: !clearhistory
"""

class clearhistory:
    description = "Clears the conversation history and last image context for the current channel. Usage: !clearhistory"
    async def run(self, ctx, bot_tools, *args, **kwargs):
        # Get the current channel ID
        channel_id = ctx.channel.id
        # Get conversation history and last image sent for this channel
        conversation_history = getattr(bot_tools, 'CONVERSATION_HISTORY', {})
        last_image_sent = getattr(bot_tools, 'LAST_IMAGE_SENT', {})
        cleared_history = False
        cleared_image = False
        # Clear conversation history if present
        if channel_id in conversation_history:
            conversation_history[channel_id] = []
            cleared_history = True
        # Clear last image context if present
        if channel_id in last_image_sent:
            del last_image_sent[channel_id]
            cleared_image = True
        # Notify user of what was cleared
        if cleared_history or cleared_image:
            await ctx.send("Conversation history and last image context cleared for this channel.")
        else:
            await ctx.send("No conversation history or image context to clear.")