# DiscordBot

A powerful Discord bot powered by Ollama for AI chat, image analysis, server management, and advanced moderation. Supports both text and slash commands, dynamic tool registration, and easy extensibility.

## Features
- **AI Chat & Q&A**: Natural language chat and question answering using local Ollama models.
- **Image Analysis**: Vision model support for image description, analysis, and context-aware Q&A.
- **Dynamic Tool Registration**: All Python files in `tools/` are auto-registered as commands.
- **Slash Command Support**: Modern Discord slash commands for all features (e.g., `/ask`, `/model`).
- **Channel Management**: Allow or restrict bot usage to specific channels.
- **Welcome Message Management**: Enable/disable and customize welcome messages per channel.
- **Model Management**: List, switch, and pull new chat or vision models on the fly.
- **Moderation Tools**: Bulk delete messages, clear history, manage allowed channels, and more.
- **Admin/Moderator Management**: Add/remove bot admins and moderators by user or role.
- **Extensible**: Add new commands by dropping Python files in the `tools/` directory.
- **Robust Permissions**: All destructive/moderation actions require admin or mod rights.
- **Strict LLM Guardrails**: The bot never invents tools or commands not listed in its system prompt.

## Setup

### 1. Requirements
- Python 3.8+
- [Ollama](https://ollama.com/) running locally or remotely
- Discord bot token ([How to create a bot](https://discordpy.readthedocs.io/en/stable/discord.html))

### 2. Installation
```sh
pip install -r requirements.txt
```

### 3. Configuration
- Open the `.env` file in the project root.
- Paste your Discord bot token in place of `<DISCORD_TOKEN>`:
  ```
  DISCORD_TOKEN=<DISCORD_TOKEN>
  ```
- (Optional) Set the Ollama server URL in your environment or `.env`:
  ```
  OLLAMA_BASE_URL=http://localhost:11434/api
  ```
  If not set, defaults to `http://localhost:11434/api`.

### 4. Running the Bot
```sh
python main.py
```

## Usage
- Use `/help` in Discord for a list of commands.
- Example slash commands:
  - `/ask <question>` — Ask the AI a question
  - `/image <url>` — Analyze an image
  - `/model <model_name>` — Switch chat model
  - `/set_image_model <model_name>` — Switch vision model
  - `/add_channel` — Allow bot in current channel
  - `/clear_messages <number|all>` — Bulk delete messages
  - `/add_mod @user` — Add a moderator
  - `/remove_mod @user` — Remove a moderator
  - `/list_mods` — List all moderators
  - `/toggle_welcome` — Enable/disable welcome messages
  - `/server_status` — Show Ollama and bot status
  - `/help` — Show all available commands

## Environment Variables
- `DISCORD_TOKEN` — Your Discord bot token
- `OLLAMA_BASE_URL` — (Optional) URL to your Ollama server (default: `http://localhost:11434/api`)

## Permissions
The bot requires the following Discord permissions in your server:
- **Read Messages**
- **Send Messages**
- **Manage Messages** (for moderation commands like `/clear_messages`)
- **Read Message History**
- **Attach Files** (for image analysis)
- **Embed Links** (for rich responses)
- **Use Slash Commands**

## Notes & Recommendations
- **Bot Role**: Place the bot's role high enough in the role list to manage messages from all users (for moderation).
- **Ollama Models**: Ensure your Ollama server has the required models pulled for both chat and vision features.
- **Channel Restrictions**: You can restrict the bot to only respond in allowed channels using `/add_channel` and `/toggle_channel_restriction`.
- **Admin/Mod Management**: Only server owners or designated bot admins/mods can use moderation and configuration commands.
- **Extending the Bot**: Add new features by dropping Python files in the `tools/` directory. Each file is auto-registered as a command.
- **System Prompt**: The bot uses a strict system prompt to prevent the LLM from inventing tools or commands not actually available.
- **Slash Commands**: All features are available as slash commands. Text prefix commands are deprecated.

## Customization & Extensibility
- All code that talks to Ollama uses the `OLLAMA_BASE_URL` variable for easy configuration.
- Add or modify commands in the `tools/` directory. Each Python file is auto-registered as a command.
- The system prompt is strict: the bot will never invent or mention tools/commands not listed in its help or system prompt.

## Troubleshooting
- If the bot can't connect to Ollama, check that Ollama is running and the URL/port is correct.
- For help, use `/server_status` or `/help` in Discord.
- Ensure the bot has the following Discord permissions in your server:
  - Read Messages
  - Send Messages
  - Manage Messages (for moderation)
  - Read Message History
  - Attach Files (for image analysis)

---
MIT License
