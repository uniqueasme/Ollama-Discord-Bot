"""
remove_admin.py
Removes a specified role from the bot admin roles list.
Usage: !remove_admin @RoleName
"""

class remove_admin:
    admin_only = True
    description = "Removes a specified role from the bot admin roles list. Usage: !remove_admin @RoleName"
    async def run(self, ctx, bot_tools, *args, **kwargs):
        # Convert the first argument to a discord.Role object
        if not args:
            await send_message("Please specify a role. Usage: !remove_admin @RoleName")
            return
        role_arg = args[0]
        role = None
        # Try to resolve the role by mention, ID, or name
        if role_arg.startswith('<@&') and role_arg.endswith('>'):
            role_id = int(role_arg[3:-1])
            role = ctx.guild.get_role(role_id)
        elif role_arg.isdigit():
            role = ctx.guild.get_role(int(role_arg))
        else:
            for r in ctx.guild.roles:
                if r.name.lower() == role_arg.lower():
                    role = r
                    break
        if not role:
            await send_message(f"Role '{role_arg}' not found.")
            return
        # Remove the role ID from admin_data.json admin_roles
        import json, os
        admin_data_file = 'admin_data.json'
        data = {}
        if os.path.exists(admin_data_file):
            with open(admin_data_file, 'r') as f:
                data = json.load(f)
        admin_roles = set(data.get('admin_roles', []))
        if role.id in admin_roles:
            admin_roles.remove(role.id)
            data['admin_roles'] = list(admin_roles)
            with open(admin_data_file, 'w') as f:
                json.dump(data, f)
            await send_message(f"✅ Removed role {role.mention} from bot admin roles.")
        else:
            await send_message(f"Role {role.mention} is not in the bot admin roles list.")

        async def send_message(msg):
            if hasattr(ctx, 'response') and hasattr(ctx.response, 'is_done'):
                if not ctx.response.is_done():
                    await ctx.response.send_message(msg)
                else:
                    await ctx.followup.send(msg)
            else:
                await ctx.send(msg)
