"""
add_admin_role.py
Adds all members of a specified role as bot admins.
Usage: !add_admin @RoleName
"""

from discord.ext import commands

class add_admin:
    admin_only = True
    description = "Adds all members of a specified role as bot admins. Usage: !add_admin @RoleName"
    @commands.has_permissions(administrator=True)
    async def run(self, ctx, bot_tools, *args, **kwargs):
        """
        Adds all members of a specified role as bot admins.
        Usage: !add_admin @RoleName
        """
        async def send_message(msg):
            if hasattr(ctx, 'response') and hasattr(ctx.response, 'is_done'):
                if not ctx.response.is_done():
                    await ctx.response.send_message(msg)
                else:
                    await ctx.followup.send(msg)
            else:
                await ctx.send(msg)

        # Convert the first argument to a discord.Role object
        if not args:
            await send_message("Please specify a role. Usage: !add_admin @RoleName")
            return
        role_arg = args[0]
        role = None
        # Try to resolve the role by mention, ID, or name
        if role_arg.startswith('<@&') and role_arg.endswith('>'):
            # Role mention format
            role_id = int(role_arg[3:-1])
            role = ctx.guild.get_role(role_id)
        elif role_arg.isdigit():
            role = ctx.guild.get_role(int(role_arg))
        else:
            # Try by name (case-insensitive)
            for r in ctx.guild.roles:
                if r.name.lower() == role_arg.lower():
                    role = r
                    break
        if not role:
            await send_message(f"Role '{role_arg}' not found.")
            return
        # Save the role ID to admin_data.json as an admin role
        import json, os
        admin_data_file = 'admin_data.json'
        data = {}
        if os.path.exists(admin_data_file):
            with open(admin_data_file, 'r') as f:
                data = json.load(f)
        admin_roles = set(data.get('admin_roles', []))
        admin_roles.add(role.id)
        data['admin_roles'] = list(admin_roles)
        # Preserve existing user admins if present
        if 'admins' in data:
            data['admins'] = list(set(data['admins']))
        with open(admin_data_file, 'w') as f:
            json.dump(data, f)
        await send_message(f"✅ Added role {role.mention} as a bot admin role.")
