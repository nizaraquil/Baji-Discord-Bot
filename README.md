# Baji

This is a Discord bot I built that manages user levels and aura balances across multiple guilds. The bot allows users to gain experience, level up, and check their aura balance through various commands.

## Features

- **Leveling System**: Users gain experience points (XP) for each message they send, which contributes to their level.
- **Aura Management**: Users can earn Aura, it is granted from a server's Wizard.
- **Server-Specific Data**: Each user's experience, level, and aura are stored separately for each server.
- **Commands**:
  - `/LVL`: Check your current level.
  - `/LVL-ALL`: Check the levels of all users in the current guild.
  - `/joke`: Get a random joke.
  - `/info [subject]`: Get a summarized Wikipedia article on the given subject.

## Requirements

To run this bot, you'll need to install the required Python packages. You can do this using the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

## Dependencies
  - `discord.py`: The library used to interact with the Discord API.
  - `requests`: For making HTTP requests to external APIs.
  - `python-dotenv`: To load environment variables from a `.env` file.
