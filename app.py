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

# Valid categories
VALID_CATEGORIES = ["Food", "Drinks", "Combo"]

# Valid product names (add all your real product names here)
VALID_PRODUCTS = [
    "Biryani", "Paneer Biryani", "Mutton Biryani", "Veg Biryani",
    "Chicken 65", "Chicken Curry Sandwich", "Cheese Burger", "Bacon Burger",
    "Mozzarella Sandwich", "Pizza Margherita", "Pizza Vegetarian",
    "Pasta 4 Formaggi", "Sushi Lunch Combo", "Burger Menu Combo",
    "Milkshake Banana", "Ice Tea", "Coca-Cola", "Espresso", "Water",
    "Mango Juice", "Family Meal", "pasta"
]

def get_access_token():
    r = requests.post("https://accounts.zoho.com/oauth/v2/token", data={
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

    # Help command
    if msg.lower() in ["help", "hi", "hello"]:
        product_list = ", ".join(VALID_PRODUCTS)
        return _reply(
            f"Welcome! Send data like:\n"
            f"Product Name, Category, Price, Note\n\n"
            f"Valid Categories: Food, Drinks, Combo\n\n"
            f"Valid Products: {product_list}\n\n"
            f"Example: Biryani, Food, 300, Extra Spicy"
        )

    parts = [p.strip() for p in msg.split(",")]

    if len(parts) < 2:
        return _reply("Invalid format. Send like:\nBiryani, Food, 300, Extra Spicy\n\nSend 'help' for valid products list.")

    product_name = parts[0]
    category = parts[1] if len(parts) > 1 else ""
    currency = parts[2] if len(parts) > 2 else ""
    modifier = parts[3] if len(parts) > 3 else ""

    # Validate product name (case-insensitive check)
    matched_product = None
    for p in VALID_PRODUCTS:
        if p.lower() == product_name.lower():
            matched_product = p
            break

    if not matched_product:
        return _reply(
            f"'{product_name}' is not a valid product.\n\n"
            f"Send 'help' to see the list of valid products."
        )

    # Validate category
    matched_category = None
    for c in VALID_CATEGORIES:
        if c.lower() == category.lower():
            matched_category = c
            break

    if not matched_category:
        return _reply(
            f"'{category}' is not a valid category.\n\n"
            f"Valid categories are: Food, Drinks, Combo"
        )

    data = {
        "Product_Name": matched_product,
        "Category": matched_category,
    }
    if currency:
        data["Currency"] = currency
    if modifier:
        data["Modifier_Note"] = modifier

    try:
        token = get_access_token()
        url = f"https://creator.zoho.com/api/v2/{ZOHO_OWNER}/{APP_LINK}/form/{FORM_LINK}"
        resp = requests.post(url, json={"data": data}, headers={
            "Authorization": f"Zoho-oauthtoken {token}"
        })
        if resp.status_code == 200:
            return _reply(f"Added: {matched_product} ({matched_category}) - Rs.{currency}")
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
