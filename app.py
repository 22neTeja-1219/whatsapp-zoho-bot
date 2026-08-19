from flask import Flask, request
import requests
import os

app = Flask(__name__)

ZOHO_REFRESH_TOKEN = os.environ.get("ZOHO_REFRESH_TOKEN")
ZOHO_CLIENT_ID = os.environ.get("ZOHO_CLIENT_ID")
ZOHO_CLIENT_SECRET = os.environ.get("ZOHO_CLIENT_SECRET")
ZOHO_OWNER = os.environ.get("ZOHO_OWNER")
APP_LINK = os.environ.get("APP_LINK")
FORM_LINK = os.environ.get("FORM_LINK")

def get_access_token():
    r = requests.post("https://accounts.zoho.in/oauth/v2/token", data={
        "refresh_token": ZOHO_REFRESH_TOKEN,
        "client_id": ZOHO_CLIENT_ID,
        "client_secret": ZOHO_CLIENT_SECRET,
        "grant_type": "refresh_token"
    })
    return r.json().get("access_token")

@app.route("/", methods=["GET"])
def home():
    return "WhatsApp-Zoho Bot is running!", 200

@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    msg = request.form.get("Body", "").strip()
    parts = [p.strip() for p in msg.split(",")]
    fields = ["Product_Name", "Category", "Currency", "Modifier_Note"]
    data = {}
    for i, field in enumerate(fields):
        if i < len(parts) and parts[i]:
            data[field] = parts[i]

    if not data:
        return _reply("Please send data like: Biryani, Food, INR, Extra spicy")

    try:
        token = get_access_token()
        url = f"https://creator.zoho.in/api/v2/{ZOHO_OWNER}/{APP_LINK}/form/{FORM_LINK}"
        resp = requests.post(url, json={"data": data}, headers={
            "Authorization": f"Zoho-oauthtoken {token}"
        })
        if resp.status_code == 200:
            return _reply(f"Added: {data.get('Product_Name', 'record')}")
        else:
            return _reply(f"Zoho error: {resp.status_code} - {resp.text[:100]}")
    except Exception as e:
        return _reply(f"Error: {str(e)[:100]}")

def _reply(message):
    return (
        f'<?xml version="1.0" encoding="UTF-8"?>'
        f'<Response><Message>{message}</Message></Response>',
        200,
        {"Content-Type": "text/xml"}
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
