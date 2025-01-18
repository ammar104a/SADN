# utils/discord_notify.py (for example)
import requests

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1330208359961596084/PhYL3jAq1wy_FHHkxXm5_ud0DF8NrxGvULIrQ65OjC1QyneVZis4FKwf6lg2Aiq_x7QX"  # Paste your webhook URL

def send_discord_notification(message):
    """
    Sends a simple text message to a configured Discord channel via webhook.
    """
    payload = {"content": message}
    headers = {"Content-Type": "application/json"}
    resp = requests.post(DISCORD_WEBHOOK_URL, json=payload, headers=headers)
    if resp.status_code != 204:  # Discord responds with 204 No Content on success
        print(f"Error sending message to Discord: {resp.text}")
