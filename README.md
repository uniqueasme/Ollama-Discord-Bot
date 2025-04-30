# DiscordBot

A Discord bot powered by Ollama for AI chat, image analysis, and server management.

## Features
- AI chat and Q&A using local Ollama models
- Image analysis with vision models
- Channel and welcome message management
- Model switching and listing
- Moderation tools

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
- Open the `.env` file in the project root (or `.env` if running from that folder).
- Paste your Discord bot token in place of `<DISCORD_TOKEN>`:
  ```
  DISCORD_TOKEN=<DISCORD_TOKEN
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
- Use `!help` in Discord for a list of commands.
- Example commands:
  - `!ask <question>` — Ask the AI a question
  - `!image <url>` — Analyze an image
  - `!model <model_name>` — Switch chat model
  - `!set_image_model <model_name>` — Switch vision model
  - `!add_channel` — Allow bot in current channel
  - `!clear_messages <number|all>` — Bulk delete messages

## Environment Variables
- `DISCORD_TOKEN` — Your Discord bot token
- `OLLAMA_BASE_URL` — (Optional) URL to your Ollama server (default: `http://localhost:11434/api`)

## Customization
- All code that talks to Ollama uses the `OLLAMA_BASE_URL` variable for easy configuration.
- Add or modify commands in the `tools/` directory.

## Troubleshooting
- If the bot can't connect to Ollama, check that Ollama is running and the URL/port is correct.
- For help, use `!server_status` or `!help` in Discord.
 
---
MIT License
