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

MENU = {
    "Food": {
        "Biryani": {"Veg Biryani": 150, "Chicken Biryani": 250, "Mutton Biryani": 400, "Paneer Biryani": 280, "Egg Biryani": 200},
        "Pizza": {"Pizza Margherita": 300, "Pizza Vegetarian": 350, "Pepperoni Pizza": 400, "BBQ Chicken Pizza": 420},
        "Burger": {"Cheese Burger": 200, "Chicken Burger": 220, "Veg Burger": 150, "Double Patty Burger": 300},
        "Sandwich": {"Club Sandwich": 200, "Grilled Veg Sandwich": 140, "Paneer Tikka Sandwich": 170, "Egg Sandwich": 120},
        "Pasta": {"Pasta 4 Formaggi": 280, "Penne Arrabiata": 250, "Spaghetti Bolognese": 300, "Alfredo Pasta": 270},
        "Starters": {"Chicken 65": 250, "Paneer Tikka": 220, "Gobi Manchurian": 180, "French Fries": 120, "Chicken Wings": 280},
        "Soup": {"Tomato Soup": 100, "Sweet Corn Soup": 120, "Hot and Sour Soup": 130, "Mushroom Soup": 140},
        "Dessert": {"Gulab Jamun": 80, "Ice Cream Vanilla": 100, "Brownie with Ice Cream": 180, "Rasmalai": 100},
    },
    "Drinks": {
        "Coffee": {"Espresso": 120, "Cappuccino": 150, "Latte": 160, "Cold Coffee": 140},
        "Tea": {"Ice Tea": 80, "Masala Chai": 50, "Green Tea": 70, "Lemon Tea": 60},
        "Juice": {"Mango Juice": 100, "Orange Juice": 90, "Watermelon Juice": 80},
        "Shake": {"Milkshake Banana": 150, "Milkshake Chocolate": 170, "Milkshake Oreo": 180},
        "Soft Drinks": {"Coca-Cola": 60, "Pepsi": 60, "Sprite": 60, "Water": 30},
        "Lassi": {"Sweet Lassi": 80, "Mango Lassi": 100, "Rose Lassi": 90},
    },
    "Combo": {
        "Lunch Combos": {"Burger Menu Combo": 400, "Pizza Combo": 650, "Biryani Combo": 350, "Pasta Combo": 400},
        "Family Combos": {"Family Meal": 800, "Party Pack": 1200, "Weekend Special": 500},
        "Value Meals": {"Budget Meal": 250, "Student Meal": 200, "Kids Meal": 180},
    },
}

sessions = {}

def get_token():
    r = requests.post("https://accounts.zoho.com/oauth/v2/token", data={
        "refresh_token": ZOHO_REFRESH_TOKEN, "client_id": ZOHO_CLIENT_ID,
        "client_secret": ZOHO_CLIENT_SECRET, "grant_type": "refresh_token"
    })
    return r.json().get("access_token")

def num_list(items):
    return "\n".join([f"{i+1}. {x}" for i, x in enumerate(items)])

def show_cart(cart):
    lines = []
    total = 0
    for i, item in enumerate(cart):
        n = f" ({item['note']})" if item.get('note') else ""
        lines.append(f"{i+1}. {item['name']}{n} - Rs.{item['price']}")
        total += item['price']
    lines.append(f"\nTotal: Rs.{total}")
    return "\n".join(lines), total

def reply(msg):
    return (f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{msg}</Message></Response>', 200, {"Content-Type": "text/xml"})

@app.route("/", methods=["GET"])
def home():
    return "Bot running!", 200

@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    msg = request.form.get("Body", "").strip()
    sender = request.form.get("From", "")

    if sender not in sessions:
        sessions[sender] = {"step": "start", "cart": []}

    s = sessions[sender]
    step = s["step"]

    # Only reset on hi/hello/menu - NOT on 0
    if msg.lower() in ["hi", "hello", "hey", "start", "menu", "reset"]:
        sessions[sender] = {"step": "cat", "cart": []}
        return reply(f"🍽 Welcome to Restaurant Register!\n\nSelect category:\n\n1. 🍕 Food\n2. 🥤 Drinks\n3. 🎁 Combo\n\nReply with number")

    # Step 1: Choose Category
    if step == "cat":
        cats = list(MENU.keys())
        try:
            c = int(msg) - 1
            if 0 <= c < len(cats):
                s["category"] = cats[c]
                s["step"] = "item"
                items = list(MENU[cats[c]].keys())
                return reply(f"🍴 {cats[c]}\n\nSelect item:\n\n{num_list(items)}\n\nReply with number")
            else:
                return reply("Invalid. Reply 1, 2, or 3")
        except ValueError:
            return reply("Invalid. Reply 1, 2, or 3")

    # Step 2: Choose Item
    if step == "item":
        items = list(MENU[s["category"]].keys())
        try:
            c = int(msg) - 1
            if 0 <= c < len(items):
                s["item"] = items[c]
                s["step"] = "variety"
                varieties = MENU[s["category"]][items[c]]
                vl = [f"{name} - Rs.{price}" for name, price in varieties.items()]
                return reply(f"📝 {items[c]}\n\n{num_list(vl)}\n\nReply with number")
            else:
                return reply(f"Invalid. Reply 1 to {len(items)}")
        except ValueError:
            return reply(f"Invalid. Reply 1 to {len(items)}")

    # Step 3: Choose Variety
    if step == "variety":
        varieties = MENU[s["category"]][s["item"]]
        vnames = list(varieties.keys())
        try:
            c = int(msg) - 1
            if 0 <= c < len(vnames):
                s["variety"] = vnames[c]
                s["price"] = varieties[vnames[c]]
                s["step"] = "note"
                return reply(f"✅ {vnames[c]} - Rs.{varieties[vnames[c]]}\n\nType a note (e.g. Extra Spicy)\nOr reply skip for no note")
            else:
                return reply(f"Invalid. Reply 1 to {len(vnames)}")
        except ValueError:
            return reply(f"Invalid. Reply 1 to {len(vnames)}")

    # Step 4: Add Note - use "skip" instead of "0"
    if step == "note":
        note = "" if msg.lower() == "skip" else msg
        s["cart"].append({"name": s["variety"], "category": s["category"], "price": s["price"], "note": note})
        ct, total = show_cart(s["cart"])
        s["step"] = "after"
        return reply(f"🛒 Added to cart!\n\nYour Cart:\n{ct}\n\n1. Add more items\n2. Confirm order\n3. Clear cart\n\nReply with number")

    # Step 5: After Add
    if step == "after":
        if msg == "1":
            s["step"] = "cat"
            return reply(f"Select category:\n\n1. 🍕 Food\n2. 🥤 Drinks\n3. 🎁 Combo\n\nReply with number")
        elif msg == "2":
            s["step"] = "confirm"
            ct, total = show_cart(s["cart"])
            return reply(f"📋 Final Order:\n\n{ct}\n\nReply yes to confirm\nReply no to cancel")
        elif msg == "3":
            s["cart"] = []
            s["step"] = "cat"
            return reply(f"Cart cleared!\n\nSelect category:\n\n1. 🍕 Food\n2. 🥤 Drinks\n3. 🎁 Combo\n\nReply with number")
        else:
            return reply("Reply 1, 2, or 3")

    # Step 6: Confirm Order
    if step == "confirm":
        if msg.lower() == "yes":
            cart = s["cart"]
            try:
                token = get_token()
                url = f"https://creator.zoho.com/api/v2/{ZOHO_OWNER}/{APP_LINK}/form/{FORM_LINK}"
                ok = 0
                for item in cart:
                    d = {"Product_Name": item["name"], "Category": item["category"], "Currency": str(item["price"])}
                    if item.get("note"):
                        d["Modifier_Note"] = item["note"]
                    r = requests.post(url, json={"data": d}, headers={"Authorization": f"Zoho-oauthtoken {token}"})
                    if r.status_code == 200:
                        ok += 1
                ol = "\n".join([f"  {x['name']} - Rs.{x['price']}" for x in cart])
                _, total = show_cart(cart)
                sessions[sender] = {"step": "start", "cart": []}
                return reply(f"✅ Order Confirmed!\n\n{ol}\n\nTotal: Rs.{total}\nAdded: {ok}/{len(cart)}\n\nSend hi to order again")
            except Exception as e:
                sessions[sender] = {"step": "start", "cart": []}
                return reply(f"Error: {str(e)[:80]}\nSend hi to retry")
        elif msg.lower() == "no":
            sessions[sender] = {"step": "start", "cart": []}
            return reply("Order cancelled. Send hi to start again.")
        else:
            return reply("Reply yes or no")

    return reply("Send hi to start ordering! 🍽")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
