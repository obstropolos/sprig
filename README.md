# Sprigbot 

The following is a Sprig slackbot proof of concept that I will 
keep building in Python until I figure out how to make it Rust. 

## Functional Requirements 
- Flask 
- Python 3+ 
- A Slack workspace 
- ngrok (if testing locally)

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

- After that, set up your `add`, `clear`, and `list` slash commands by going to
the `Slash Commands` menu in the Slack interface. 
    - For `add`, create a new command with `/add` as the command, and
    `https://<your ngrok url>/sprig/add` as the Request URL. 
    - For `clear`, create a new command with `/clear` as the command, and 
    `https://<your ngrok url>/sprig/clear` as the Request URL. 
    - For `list`, create a new command with `/add` as the command, and 
    `https://<your ngrok url>/sprig/list` as the Request URL.
    - Note: the additional hints and info can be anything you want here.

- Finally, make sure to give the bot some permissions in your Slack 
workspace by going to the `OAuth & Permissions` menu in the Slack interface
scrolling down to `Scopes` and adding permissions for `chat:write`, 
`commands`, `incoming-webhook`, `links:read`, and `links:write`.

Alright now it's time to boot this up. Go to the folder with `app.py` in it
and run the following: 

```
pip3 install slack_sdk PyGithub
```

Before running this application, make sure to set your tokens up via the 
following commands:

```
export SLACK_BOT_TOKEN=<your Slack OAUTH token> 
export GITHUB_TOKEN=<your GitHub API key>  
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

Any PRs closed or merged should be removed from Sprig. 
