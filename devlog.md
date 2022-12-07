# DevLog

Writing down what I did so that maybe I or others can replicate it.

## Setup Python environment

(These commands are for Mac.)

Ensure Python3 and pip are installed
```python
pip install -r requirements.txt
```

## Create Discord Application

Follow the Discord [developer docs](https://discord.com/developers/docs/getting-started)

[Developer Dashboard](https://discord.com/developers/applications) -> **New Application**
Fill out name & description.

**Bot** -> **Add Bot**
Fill out name (Pidlwick II) and icon.
Click **Reset Token**.
```
IMPORTANT: Keep the token secret (password manager) and never check it into git. 
```

### Bot Configuration

**Privileged Gateway Intents** -> enable "Message Content Intent"


## Installing the Bot


## Running the Bot

Build `docker build -t pidlwick-bot .`

Run `docker run pidlwick-bot`

## Deploying to Heroku

Outdated? https://remarkablemark.org/blog/2021/03/12/github-actions-deploy-to-heroku/

Heroku Dashboard -> Pidlwick app -> Deploy -> Deployment method: GitHub -> connect app to GitHub
