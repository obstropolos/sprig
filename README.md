# Sprigbot 

The following is a slackbot called "Sprig" that tracks GitHub PRs, and lists 
them based on status.

### To Dos
- Add assignment capabilities to tag slack members

## Functional Requirements 
- Flask 
- Python 3+ 
- A Slack workspace 

These instructions use ngrok for testing.

## API Requirements
- Slack OAUTH token (obtained in this guide)
- GitHub API key (obtained on your own - req. read permissions)

## Running Sprigbot
- First, set up a new app instance in Slack at `api.slack.com` and add it 
to your designated workspace. Call it "sprig". 

- After doing so, obtain a Slack OAUTH token by booting up your ngrok 
instance at whatever port you want by running `ngrok http <port#>`
    -- Note: if you're using a Mac, don't use 5000 because that's already
    assigned and you'll run into some issues. 

- Next go to your `OAuth & Permissions` menu in the Slack interface
and add your ngrok URL as a redirect URL. Once done, you should be able
to obtain a "Bot User OAuth Token" which is required to run Sprigbot. 

- After that, set up your `add`, `clear`, `refresh`, and `list` slash 
commands by going to the `Slash Commands` menu in the Slack interface. 
    - For each command, create a new command with the name as the 
    command, and `https://<your ngrok url>/sprig/add` as the Request URL. 

- Finally, make sure to give the bot some permissions in your Slack 
workspace by going to the `OAuth & Permissions` menu in the Slack interface
scrolling down to `Scopes` and adding permissions for `chat:write`, 
`commands`, `incoming-webhook`, `links:read`, and `links:write`.

Before running this bot, make sure to set your tokens up via the 
following commands:

```
export SLACK_BOT_TOKEN=<your Slack OAUTH token> 
export GITHUB_TOKEN=<your GitHub API key>  
```

Alright now it's time to boot this up. Go to the folder with `app.py` in it
and run the following: 

```
pip3 install slack_sdk PyGithub
```

Now run this app on the same specified port you had for ngrok by running the
following:

```
python3 -m flask run --port <port#> 
```

Now your flask app and ngrok should be running. Let's test this bot out. 

- Go to your Slack instance, add Sprig to your #general channel, and try
the following commands: 

- `/add <GitHub PR link>` to add a GitHub PR link to Sprig.
- `/list` which lists all added PRs, with review status indicated by a color.
Green means it's approved, red means there's no reviews, and yellow means
changes have been requested.
- `/clear <GitHub PR link>` to remove a PR from your list. 
- `/refresh` to refresh the statuses of the PRs. 

Any PRs closed or merged should be removed from Sprig. 
