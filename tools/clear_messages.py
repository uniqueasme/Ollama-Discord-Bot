"""
clear_messages.py
Clears a number of recent messages or all messages in the current channel.
Usage: /clear_messages <number|all>
"""

import discord

class clear_messages:
    admin_only = True
    description = "Clears a number of recent messages or all messages in the current channel. Usage: /clear_messages <number|all>"
    async def run(self, ctx, bot_tools, *args, **kwargs):
        # Helper to send a message for both text and slash commands
        async def send_message(msg):
            if hasattr(ctx, 'response') and hasattr(ctx.response, 'is_done'):
                if not ctx.response.is_done():
                    await ctx.response.send_message(msg, ephemeral=True)
            else:
                await ctx.send(msg)
        if not args:
            await send_message("Please specify the number of messages to clear, or 'all' to clear all messages. Usage: /clear_messages <number|all>")
            return
        arg = args[0].lower()
        is_slash = hasattr(ctx, 'response') and hasattr(ctx.response, 'is_done')
        if arg == 'all':
            if is_slash and not ctx.response.is_done():
                await ctx.response.send_message("🧹 Clearing all non-pinned messages in this channel...", ephemeral=True)
                deleted = await ctx.channel.purge(check=lambda m: not m.pinned, bulk=True)
                # Send result to channel after purge
                await ctx.channel.send(f"🧹 Cleared {len(deleted)} messages in #{ctx.channel.name}.")
                try:
                    await ctx.user.send(f"🧹 Cleared {len(deleted)} messages in #{ctx.channel.name}.")
                except Exception:
                    pass
                return
            else:
                deleted = await ctx.channel.purge(check=lambda m: not m.pinned, bulk=True)
                await ctx.channel.send(f"🧹 Cleared {len(deleted)} messages in #{ctx.channel.name}.")
        else:
            try:
                num = int(arg)
                if num < 1:
                    await send_message("Please specify a positive number of messages to clear.")
                    return
                if is_slash and not ctx.response.is_done():
                    await ctx.response.send_message(f"🧹 Clearing up to {num} non-pinned messages in this channel...", ephemeral=True)
                    deleted = await ctx.channel.purge(limit=num+1, check=lambda m: not m.pinned, bulk=True)
                    await ctx.channel.send(f"🧹 Cleared {len(deleted)} messages in #{ctx.channel.name}.")
                    try:
                        await ctx.user.send(f"🧹 Cleared {len(deleted)} messages in #{ctx.channel.name}.")
                    except Exception:
                        pass
                    return
                else:
                    deleted = await ctx.channel.purge(limit=num+1, check=lambda m: not m.pinned, bulk=True)
                    await ctx.channel.send(f"🧹 Cleared {len(deleted)} messages in #{ctx.channel.name}.")
            except ValueError:
                await send_message("Invalid argument. Usage: /clear_messages <number|all>")
