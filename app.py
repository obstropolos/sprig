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

# PR cache
pr_cache = {}

@app.route('/sprig/add', methods=['POST'])
def add_pr():
    text = request.form.get('text')
    
    # Fetch PR details and store them in the cache
    repo_name = extract_repo_name(text)
    if repo_name:
        pr_number = extract_pr_number(text)
        if pr_number:
            repo = g.get_repo(repo_name)
            pr = repo.get_pull(pr_number)
            pr_cache[text] = get_pr_status(pr)
    
    # Send confirmation message to Slack
    channel_id = request.form.get('channel_id')
    send_message(channel_id, f"PR {text} has been added to the list.")
    
    return Response(), 200

# List PRs
@app.route('/sprig/list', methods=['POST'])
def list_prs():
    if not pr_cache:
        # Send message to Slack
        channel_id = request.form.get('channel_id')
        send_message(channel_id, "There are currently no PRs in the list.")
        return Response(), 200

    attachments = []
    for pr_url, status in pr_cache.items():
        attachments.append({
            "text": f"{status} {pr_url}"
        })
    
    try:
        response = client.chat_postMessage(
            channel="#newnew",
            text="PR List:",
            attachments=attachments
        )
        assert response["ok"]
        print(response)  # Print the response content for debugging
    except SlackApiError as e:
        print(f"Slack API error: {e.response['error']}")
    
    return Response(), 200

# Clear PR
@app.route('/sprig/clear', methods=['POST'])
def clear_pr():
    text = request.form.get('text')
    
    if text not in pr_cache:
        # Send message to Slack
        channel_id = request.form.get('channel_id')
        send_message(channel_id, f"That PR {text} isn't on this list.")
    else:
        # Remove PR from the cache
        del pr_cache[text]
        
        # Send message to Slack
        channel_id = request.form.get('channel_id')
        send_message(channel_id, f"PR {text} removed!")

    return Response(), 200

# Refresh cache
@app.route('/sprig/refresh', methods=['POST'])
def refresh_cache():
    for pr_url in list(pr_cache.keys()):  # Use list to avoid RuntimeError due to size change during iteration
        repo_name = extract_repo_name(pr_url)
        if repo_name:
            pr_number = extract_pr_number(pr_url)
            if pr_number:
                repo = g.get_repo(repo_name)
                pr = repo.get_pull(pr_number)
                pr_cache[pr_url] = get_pr_status(pr)
    
    # Send confirmation message to Slack
    channel_id = request.form.get('channel_id')
    send_message(channel_id, "PR statuses have now been updated.")
    
    return Response(), 200

# Helper functions
def get_pr_status(pr):
    reviews = pr.get_reviews().reversed  # reversed to get the latest reviews first
    status = ":red_circle:"
    for review in reviews:
        # Ignore reviews by the PR author
        if review.user.login == pr.user.login:
            continue
        # Ignore comments and pending reviews
        if review.state not in ["APPROVED", "CHANGES_REQUESTED"]:
            continue
        # Return the status based on the latest relevant review
        if review.state == "APPROVED":
            return ":large_green_circle:"
        elif review.state == "CHANGES_REQUESTED":
            return ":large_yellow_circle:"
    return status

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
