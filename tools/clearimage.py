"""
clearimage.py
Clears the last image context for the current channel.
Usage: !clearimage
"""

class clearimage:
    description = "Clears the last image context for the current channel. Usage: !clearimage"
    
    async def run(self, ctx, bot_tools, *args, **kwargs):
        # Get the current channel ID
        channel_id = ctx.channel.id
        # Get the last image sent dictionary
        last_image_sent = getattr(bot_tools, 'LAST_IMAGE_SENT', {})
        # If there is image context for this channel, clear it
        if channel_id in last_image_sent:
            del last_image_sent[channel_id]
            await ctx.send("Last image context cleared for this channel.")
        else:
            await ctx.send("No image context to clear for this channel.")