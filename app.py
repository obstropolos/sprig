import os
import requests
import ssl
import certifi
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from github import Github
from flask import Flask, request, Response

app = Flask(__name__)

ssl_context = ssl.create_default_context(cafile=certifi.where())

# Create a client instance
slack_token = os.environ["SLACK_BOT_TOKEN"]
client = WebClient(token=slack_token, ssl=ssl_context)

# Github token
g = Github(os.environ["GITHUB_TOKEN"])

# PR list
pr_list = []

# Add method
@app.route('/sprig/add', methods=['POST'])
def add_pr():
    text = request.form.get('text')
    pr_list.append(text)
    
    # Send confirmation message to Slack
    channel_id = request.form.get('channel_id')
    send_message(channel_id, f"PR {text} has been added to the list.")
    
    return Response(), 200

# List PRs
@app.route('/sprig/list', methods=['POST'])
def list_prs():
    attachments = []
    for pr_url in pr_list:
        repo_name = extract_repo_name(pr_url)
        if repo_name:
            pr_number = extract_pr_number(pr_url)
            if pr_number:
                repo = g.get_repo(repo_name)
                pr = repo.get_pull(pr_number)
    
                # Check status
                reviews = pr.get_reviews()
                status = ":red_circle:"
                for review in reviews:
                    if review.state == "APPROVED":
                        status = ":large_green_circle:"
                        break
                    elif review.state == "CHANGES_REQUESTED":
                        status = ":yellow_circle:"
    
                attachments.append({
                    "text": f"{status} {pr.html_url}"
                })
    
    try:
        response = client.chat_postMessage(
            channel="#general",
            text="PR List:",
            attachments=attachments
        )
        assert response["ok"]
        print(response)  # Print the response content for debugging
    except SlackApiError as e:
        print(f"Slack API error: {e.response['error']}")
    
    return Response(), 200

def extract_repo_name(pr_url):
    # Extract the repository name from the PR URL
    parts = pr_url.split('/')
    
    if len(parts) >= 5:
        return f"{parts[3]}/{parts[4]}"
    
    return None

def extract_pr_number(pr_url):
    # Extract the PR number from the PR URL
    parts = pr_url.split('/')
    
    if len(parts) >= 7:
        return int(parts[6])
    
    return None

def send_message(channel_id, text):
    try:
        response = client.chat_postMessage(
            channel=channel_id,
            text=text
        )
        assert response["ok"]
    except SlackApiError as e:
        print(f"Slack API error: {e.response['error']}")

@app.route('/github/webhook', methods=['POST'])
def github_webhook():
    data = request.json
    action = data['action']
    pr_url = data['pull_request']['html_url']
    
    if action == 'closed' and pr_url in pr_list:
        pr_list.remove(pr_url)
        
    return Response(), 200
