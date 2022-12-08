# pidlwick

Pidlwick is a Discord bot for the **Enter Ravenloft** server. It's written in Python using the [discord.py](https://discordpy.readthedocs.io/en/latest/index.html) library and it's deployed using [Heroku](https://www.heroku.com/home).

## Discord Setup

These are the steps for setting up a new Discord application & bot user. You won't need to do this yourself unless
you're forking the project to create your own bot. Refer to the [Discord docs](https://discord.com/developers/docs/getting-started) for the gritty details and more examples.

Go to the [Developer Dashboard](https://discord.com/developers/applications) and click **New Application**.
Fill out the app name & a description.

In the sidebar, click **Bot** and then **Add Bot**. Fill out the name and give it a fun icon.
Click **Reset Token** and save the token somewhere safe, like a password manager.

Under **Privileged Gateway Intents**, toggle "Message Content Intent" to ON. (This allows the bot to respond to prefix commands.)

To install the bot on a new server, click on **OAuth2** in the sidebar and then **URL Generator**. Under **Scopes**, select "bot". Under **Bot Permissions**, select "Send Messages" under Text Permissions. Then copy the Generated URL and paste it into a browser: you'll be prompted to allow the app to access your Discord account and add it to a server.

The bot should show up in the server sidebar now, although it might be grayed out if it's not running (see Deployment below). You can test that the bot is working with the "hello" command, e.g. `$pw hello`.

## Heroku Deployment

I'm using Heroku for hosting the bot because it's easy to use with a broad knowledge base and excellent GitHub integration for deployments. Unfortunately Heroku ended support for their free tier of service in November 2022, but the good news is that at our tiny scale we can use their cheapest instance plan.

Again, you won't need to do these steps yourselves unless you're starting over from scratch with a new Heroku account.

Create a Heroku account if you don't already have one and fill out your personal & billing info.

Create a new app and give it a name (preferably the same as the Discord bot & git repo for simplicity). On the **Deploy** tab, select "GitHub" for **Deployment Method** and then select the repo you're using for the bot code. This will prompt you to authenticate to GitHub in order to allow the Heroku itegration - do so.

You also need to set up environment variables, which Heroku calls "Config Vars". Settings > Config Vars > Reveal, and add a key/value pair for every environment variable defined in `.env`.

Once the app is connected to GitHub, you can manually deploy by going to the App Dashboard > Deploy > Manual Deploy from branch `main`. (I haven't set up automatic deploys yet, but will do so if this takes off.)

## Local Development

You'll need a Python environment supporting v3.10.8 or higher. After cloning this repo, install required dependencies using
```
pip install -r requirements.txt
```

Then, edit the `.env` file to provide the required channel names for the server you're developing on. You'll need to follow the steps under **Discord Setup** for adding the bot to your dev server. Ask Ian if you need the `DISCORD_BOT_TOKEN` value for the Enter Ravenloft App.

Once everything is set up, you can run the bot locally using
```
python3 app.py
```
