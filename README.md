# Linkify Bot

Linkify Bot adds a green hat to the intra profile pictures of 42 students

## Quick Start

Ensure Docker is installed on your system. Visit [Docker's official site](https://docs.docker.com/get-docker/) for installation instructions if needed.

### Setup

1. **Clone and Navigate**:
   ```bash
   git clone git@github.com:Links-bde/linkify-bot.git
   cd linkify-bot
   ```

2. **Configure Environment**:
   Create a `.env` file in the project root with your Discord bot token:
   ```plaintext
   DISCORD_TOKEN=<Your_Discord_Bot_Token>
   ```

3. **Prepare Profile Data**:
   Generate a `profile_pics.json` in the project root, mapping usernames to profile picture links:
   ```json
   {
     "username1": "profile_pic_link1",
     "username2": "profile_pic_link2"
   }
   ```

### Build & Run

```bash
docker compose up -d
```

## Note

The project was created quickly for fun as a random experiment. The code is ugly and inefficient. It's just a quick draft with some ChatGPT glued code.