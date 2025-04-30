"""
clear_messages.py
Clears a number of recent messages or all messages in the current channel.
Usage: !clear_messages <number|all>
"""

import discord

class clear_messages:
    admin_only = True
    description = "Clears a number of recent messages or all messages in the current channel. Usage: !clear_messages <number|all>"
    async def run(self, ctx, bot_tools, *args, **kwargs):
        # Check for argument specifying number or 'all'
        if not args:
            await ctx.send("Please specify the number of messages to clear, or 'all' to clear all messages. Usage: !clear_messages <number|all>")
            return
        arg = args[0].lower()
        if arg == 'all':
            # Delete all non-pinned messages in the channel
            def not_pinned(msg):
                return not msg.pinned
            deleted = await ctx.channel.purge(check=not_pinned, bulk=True)
            await ctx.send(f"🧹 Cleared {len(deleted)} messages in this channel.")
        else:
            try:
                num = int(arg)
                if num < 1:
                    await ctx.send("Please specify a positive number of messages to clear.")
                    return
                def not_pinned(msg):
                    return not msg.pinned
                # Delete the specified number of messages (plus the command itself)
                deleted = await ctx.channel.purge(limit=num+1, check=not_pinned, bulk=True)
                await ctx.send(f"🧹 Cleared {len(deleted)} messages in this channel.")
            except ValueError:
                await ctx.send("Invalid argument. Usage: !clear_messages <number|all>")
