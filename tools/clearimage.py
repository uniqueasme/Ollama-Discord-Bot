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
        
        async def send_message(msg):
            if hasattr(ctx, 'response') and hasattr(ctx.response, 'is_done'):
                if not ctx.response.is_done():
                    await ctx.response.send_message(msg)
                else:
                    await ctx.followup.send(msg)
            else:
                await ctx.send(msg)
                
        # If there is image context for this channel, clear it
        if channel_id in last_image_sent:
            del last_image_sent[channel_id]
            await send_message("Last image context cleared for this channel.")
        else:
            await send_message("No image context to clear for this channel.")