# Render deployment

1. Push this repository to GitHub and create a Render **Web Service** from it.
2. Choose the **Docker** runtime so Render uses the included `Dockerfile`.
3. Add the required environment variables from `.env.example` in Render's Environment page. Use your own real values; do not commit secrets to GitHub.
4. Keep `CLONE_MODE`, `MULTIPLE_DATABASE`, and other feature flags unset unless you have configured their additional databases and settings. Boolean values accept `true/false`, `1/0`, `yes/no`, or `on/off`.
5. Deploy. Check the Render logs for the `Bot Started`/startup output and MongoDB connectivity.

`OPENAI_API_KEY` is optional. The `/openai` command will report that it is disabled when no key is configured.

The bot needs a reachable MongoDB database, a Telegram bot token, Telegram API credentials, and a log channel where the bot has permission to post. Render's free instances may sleep or restart; continuous 24/7 availability is not guaranteed on a free instance.
