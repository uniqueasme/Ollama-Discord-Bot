"""
status.py
Shows which AI model is currently active.
Usage: !status
"""

class status:
    description = "Shows which AI model is currently active. Usage: !status"
    
    async def run(self, ctx, bot_tools, *args, **kwargs):
        # Get the current default model
        default_model = getattr(bot_tools, 'DEFAULT_MODEL', None)
        
        async def send_message(msg):
            if hasattr(ctx, 'response') and hasattr(ctx.response, 'is_done'):
                if not ctx.response.is_done():
                    await ctx.response.send_message(msg)
                else:
                    await ctx.followup.send(msg)
            else:
                await ctx.send(msg)
                
        await send_message(f"🤖 Currently using model: **{default_model}**")