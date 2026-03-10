# 🎵 Spotify to Twitter/X Release Bot

This is a lightweight Python automation bot that monitors a specific artist on Spotify and automatically publishes a tweet to Twitter/X whenever they drop a new album or single. 

## ✨ Features

- **Spotify API Integration:** Periodically checks an artist's discography for the latest releases (albums or singles) using client credentials.
- **Twitter/X API v2:** Automatically formats and posts a tweet with the release name, date, and a direct Spotify link using OAuth 1.0a user tokens.
- **Duplicate Prevention:** Keeps track of previously posted releases locally in a `state.json` file so it never posts the same update twice.
- **Flexible Execution:** Can be run as a one-off script (`once`) or as a continuous background process (`loop`).

## 🛠️ Prerequisites

To use this bot, you will need:
- Python 3.x installed on your machine.
- A **Spotify Developer App** (to get your Client ID and Secret).
- A **Twitter/X Developer App** with read and write permissions (to get your API keys and tokens).

## 🚀 Setup & Installation

**1. Clone the repository**
```bash
git clone https://github.com/Awskiszef/spoti-x-bot.git
cd spoti-x-bot


**2. Install dependencies**
Install the required packages (`python-dotenv`, `requests`, and `requests-oauthlib`):

```bash
pip install -r requirements.txt


**3. Configure environment variables**
Copy the provided `.env.example` file to create your own `.env` file:

```bash
cp .env.example .env


Open the `.env` file and fill in your specific credentials and settings:

| Variable | Description |
| --- | --- |
| `SPOTIFY_CLIENT_ID` | Your Spotify App Client ID. |
| `SPOTIFY_CLIENT_SECRET` | Your Spotify App Client Secret. |
| `SPOTIFY_ARTIST_NAME` | The exact name of the artist you want to monitor (e.g., *Taylor Swift*). |
| `TWITTER_API_KEY` | Your Twitter App API Key. |
| `TWITTER_API_SECRET` | Your Twitter App API Secret. |
| `TWITTER_ACCESS_TOKEN` | Your Twitter App Access Token. |
| `TWITTER_ACCESS_TOKEN_SECRET` | Your Twitter App Access Token Secret. |
| `BOT_MODE` | Set to `once` for a single check, or `loop` to keep polling. |
| `CHECK_INTERVAL_SECONDS` | How often to check for new releases in `loop` mode (default is 3600 seconds). |

## 💻 Usage

**Run a single check:**
Ensure `BOT_MODE` is set to `once` in your `.env` file, then run:

```bash
python bot.py


**Run continuously:**
Ensure `BOT_MODE` is set to `loop` in your `.env` file, then run:

```bash
python bot.py


*Note: For production use, it is highly recommended to run the bot using a process manager (like `systemd` or `PM2`) or schedule the `once` mode via cron jobs rather than keeping a terminal window open.*

## 📂 State Management

The bot automatically creates and updates a `state.json` file in the root directory. This file stores the IDs of the Spotify releases that have already been tweeted, ensuring your timeline stays clean and spam-free.