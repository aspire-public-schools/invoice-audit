import os
import time
import requests
from dotenv import load_dotenv
from .utils import log

load_dotenv()

def update_env_file(new_token, new_lifetime, env_file='.env'):
    try:
        with open(env_file, 'r') as file:
            lines = file.readlines()
    except FileNotFoundError:
        lines = []

    token_written = False
    lifetime_written = False
    new_lines = []

    for line in lines:
        if line.startswith("access_token="):
            new_lines.append(f"access_token={new_token}\n")
            token_written = True
        elif line.startswith("token_life_time="):
            new_lines.append(f"token_life_time={new_lifetime}\n")
            lifetime_written = True
        else:
            new_lines.append(line)

    if not token_written:
        new_lines.append(f"access_token={new_token}\n")
    if not lifetime_written:
        new_lines.append(f"token_life_time={new_lifetime}\n")

    with open(env_file, 'w') as file:
        file.writelines(new_lines)
    log(".env file updated.", "info")

def get_access_token():
    token_url = os.getenv('token_url')
    client_id = os.getenv('client_id')
    client_secret = os.getenv('client_secret')
    scope = os.getenv('scope')
    access_token = os.getenv('access_token')
    token_life_time = os.getenv('token_life_time')
    current_time = time.time() * 1000

    try:
        token_life_time = float(token_life_time) if token_life_time else 0
    except ValueError:
        token_life_time = 0

    if token_life_time <= current_time or not access_token:
        log("Access token expired or not available. Requesting new token...", "warn")
        payload = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
            'scope': scope
        }
        headers = {
            'ACCEPT': os.getenv('ACCEPT', 'application/json'),
            'Content-Type': os.getenv('Content-Type', 'application/x-www-form-urlencoded')
        }
        response = requests.post(token_url, data=payload, headers=headers)
        if response.status_code == 200:
            json_response = response.json()
            new_access_token = json_response.get('access_token')
            if new_access_token:
                new_token_life_time = current_time + 20 * 60 * 60 * 1000
                update_env_file(new_access_token, new_token_life_time)
                log("New access token acquired.", "success")
                return new_access_token
            else:
                log("Error: 'access_token' not found in response.", "error")
                return None
        else:
            log(f"Failed to get token. Status code: {response.status_code}", "error")
            log(response.text, "error")
            return None
    else:
        log("Existing access token is still valid.", "info")
        return access_token