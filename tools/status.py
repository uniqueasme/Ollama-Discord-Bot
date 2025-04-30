"""
status.py
Shows which AI model is currently active.
Usage: !status
"""

class status:
    description = "Shows which AI model is currently active. Usage: !status"
    
    def run(self, ctx, bot_tools, *args, **kwargs):
        # Get the current default model
        default_model = getattr(bot_tools, 'DEFAULT_MODEL', None)
        return f"🤖 Currently using model: **{default_model}**"