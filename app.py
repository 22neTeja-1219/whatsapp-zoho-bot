from flask import Flask, request
import requests
import os
import json

app = Flask(__name__)

ZOHO_REFRESH_TOKEN = os.environ.get("ZOHO_REFRESH_TOKEN")
ZOHO_CLIENT_ID = os.environ.get("ZOHO_CLIENT_ID")
ZOHO_CLIENT_SECRET = os.environ.get("ZOHO_CLIENT_SECRET")
ZOHO_OWNER = os.environ.get("ZOHO_OWNER")
APP_LINK = os.environ.get("APP_LINK")
FORM_LINK = os.environ.get("FORM_LINK")

META_TOKEN = os.environ.get("META_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "myverifytoken123")

META_API = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages" if PHONE_NUMBER_ID else ""

MENU = {
    "Food": {
        "Biryani": {
            "Veg Biryani": 150,
            "Chicken Biryani": 250,
            "Mutton Biryani": 400,
            "Paneer Biryani": 280,
            "Egg Biryani": 200,
            "Prawn Biryani": 350,
        },
        "Pizza": {
            "Pizza Margherita": 300,
            "Pizza Vegetarian": 350,
            "Pepperoni Pizza": 400,
            "BBQ Chicken Pizza": 420,
            "Mushroom Pizza": 330,
        },
        "Burger": {
            "Cheese Burger": 200,
            "Chicken Burger": 220,
            "Veg Burger": 150,
            "Double Patty Burger": 300,
        },
        "Sandwich": {
            "Club Sandwich": 200,
            "Grilled Veg Sandwich": 140,
            "Paneer Tikka Sandwich": 170,
            "Egg Sandwich": 120,
        },
        "Pasta": {
            "Pasta 4 Formaggi": 280,
            "Penne Arrabiata": 250,
            "Spaghetti Bolognese": 300,
            "Alfredo Pasta": 270,
        },
        "Starters": {
            "Chicken 65": 250,
            "Paneer Tikka": 220,
            "Gobi Manchurian": 180,
            "French Fries": 120,
            "Chicken Wings": 280,
        },
        "Soup": {
            "Tomato Soup": 100,
            "Sweet Corn Soup": 120,
            "Hot and Sour Soup": 130,
            "Mushroom Soup": 140,
        },
        "Dessert": {
            "Gulab Jamun": 80,
            "Ice Cream Vanilla": 100,
            "Brownie with Ice Cream": 180,
            "Rasmalai": 100,
        },
    },
    "Drinks": {
        "Coffee": {
            "Espresso": 120,
            "Cappuccino": 150,
            "Latte": 160,
            "Cold Coffee": 140,
        },
        "Tea": {
            "Ice Tea": 80,
            "Masala Chai": 50,
            "Green Tea": 70,
        },
        "Juice": {
            "Mango Juice": 100,
            "Orange Juice": 90,
            "Watermelon Juice": 80,
        },
        "Shake": {
            "Milkshake Banana": 150,
            "Milkshake Chocolate": 170,
            "Milkshake Oreo": 180,
        },
        "Soft Drinks": {
            "Coca-Cola": 60,
            "Pepsi": 60,
            "Sprite": 60,
            "Water": 30,
        },
        "Lassi": {
            "Sweet Lassi": 80,
            "Mango Lassi": 100,
            "Rose Lassi": 90,
        },
    },
    "Combo": {
        "Lunch Combos": {
            "Burger Menu Combo": 400,
            "Pizza Combo": 650,
            "Biryani Combo": 350,
            "Pasta Combo": 400,
        },
        "Family Combos": {
            "Family Meal Serves 4": 800,
            "Party Pack Serves 6": 1200,
            "Weekend Special Serves 2": 500,
        },
        "Value Meals": {
            "Budget Meal": 250,
            "Student Meal": 200,
            "Kids Meal": 180,
        },
    },
}

user_sessions = {}

def get_zoho_token():
    r = requests.post("https://accounts.zoho.com/oauth/v2/token", data={
        "refresh_token": ZOHO_REFRESH_TOKEN,
        "client_id": ZOHO_CLIENT_ID,
        "client_secret": ZOHO_CLIENT_SECRET,
        "grant_type": "refresh_token"
    })
    return r.json().get("access_token")

def send_text(to, text):
    requests.post(META_API, headers={
        "Authorization": f"Bearer {META_TOKEN}",
        "Content-Type": "application/json"
    }, json={
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    })

def send_buttons(to, body_text, buttons):
    btn_list = []
    for btn in buttons[:3]:
        btn_list.append({
            "type": "reply",
            "reply": {"id": btn["id"], "title": btn["title"][:20]}
        })
    requests.post(META_API, headers={
        "Authorization": f"Bearer {META_TOKEN}",
        "Content-Type": "application/json"
    }, json={
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": body_text},
            "action": {"buttons": btn_list}
        }
    })

def send_list(to, body_text, button_text, sections):
    requests.post(META_API, headers={
        "Authorization": f"Bearer {META_TOKEN}",
        "Content-Type": "application/json"
    }, json={
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "body": {"text": body_text},
            "action": {
                "button": button_text[:20],
                "sections": sections
            }
        }
    })

def format_cart(cart):
    lines = []
    total = 0
    for i, item in enumerate(cart):
        note = f" ({item['note']})" if item.get('note') else ""
        lines.append(f"{i+1}. {item['name']}{note} - Rs.{item['price']}")
        total += item['price']
    lines.append(f"\nTotal: Rs.{total}")
    return "\n".join(lines), total

@app.route("/", methods=["GET"])
def home():
    return "WhatsApp-Zoho Bot is running!", 200

@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Forbidden", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    try:
        entry = data["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]
        if "messages" not in value:
            return "OK", 200
        message = value["messages"][0]
        sender = message["from"]
        if message["type"] == "text":
            msg = message["text"]["body"].strip()
        elif message["type"] == "interactive":
            interactive = message["interactive"]
            if interactive["type"] == "button_reply":
                msg = interactive["button_reply"]["id"]
            elif interactive["type"] == "list_reply":
                msg = interactive["list_reply"]["id"]
            else:
                msg = ""
        else:
            msg = ""
        handle_message(sender, msg)
    except Exception as e:
        print(f"Error: {e}")
    return "OK", 200

def handle_message(sender, msg):
    if sender not in user_sessions:
        user_sessions[sender] = {"step": "start", "cart": []}
    session = user_sessions[sender]
    step = session["step"]

    if msg.lower() in ["hi", "hello", "hey", "start", "menu", "reset"]:
        user_sessions[sender] = {"step": "choose_category", "cart": []}
        categories = list(MENU.keys())
        rows = []
        emojis = {"Food": "🍕", "Drinks": "🥤", "Combo": "🎁"}
        for cat in categories:
            rows.append({
                "id": f"cat_{cat}",
                "title": f"{emojis.get(cat, '')} {cat}",
                "description": f"Browse {cat} items"
            })
        send_list(sender, "🍽️ Welcome to Restaurant Register!\n\nPlease select a category from the menu below:", "View Menu", [{"title": "Categories", "rows": rows}])
        return

    if step == "choose_category" and msg.startswith("cat_"):
        category = msg.replace("cat_", "")
        if category in MENU:
            session["category"] = category
            session["step"] = "choose_item"
            items = list(MENU[category].keys())
            rows = []
            for item in items:
                count = len(MENU[category][item])
                rows.append({
                    "id": f"item_{item}",
                    "title": item[:24],
                    "description": f"{count} varieties"
                })
            send_list(sender, f"🍴 {category}\n\nSelect an item:", "View Items", [{"title": category, "rows": rows}])
        return

    if step == "choose_item" and msg.startswith("item_"):
        item_name = msg.replace("item_", "")
        category = session["category"]
        if item_name in MENU[category]:
            session["item"] = item_name
            session["step"] = "choose_variety"
            varieties = MENU[category][item_name]
            rows = []
            for name, price in varieties.items():
                rows.append({
                    "id": f"var_{name}",
                    "title": name[:24],
                    "description": f"Rs.{price}"
                })
            send_list(sender, f"📝 {item_name}\n\nSelect your choice:", "View Options", [{"title": item_name, "rows": rows}])
        return

    if step == "choose_variety" and msg.startswith("var_"):
        variety_name = msg.replace("var_", "")
        category = session["category"]
        item = session["item"]
        varieties = MENU[category][item]
        if variety_name in varieties:
            price = varieties[variety_name]
            session["variety"] = variety_name
            session["price"] = price
            session["step"] = "add_note"
            send_buttons(sender, f"✅ {variety_name}\n💰 Price: Rs.{price}\n\nAdd a note?", [
                {"id": "note_skip", "title": "No Note"},
                {"id": "note_spicy", "title": "Extra Spicy"},
                {"id": "note_custom", "title": "Type My Note"},
            ])
        return

    if step == "add_note":
        if msg == "note_skip":
            note = ""
        elif msg == "note_spicy":
            note = "Extra Spicy"
        elif msg == "note_custom":
            session["step"] = "type_note"
            send_text(sender, "Type your note and send:")
            return
        else:
            note = msg
        session["cart"].append({
            "name": session["variety"],
            "category": session["category"],
            "price": session["price"],
            "note": note,
        })
        cart_text, total = format_cart(session["cart"])
        session["step"] = "after_add"
        send_buttons(sender, f"🛒 Added to cart!\n\nYour Cart:\n{cart_text}\n\nWhat next?", [
            {"id": "action_more", "title": "Add More"},
            {"id": "action_confirm", "title": "Confirm Order"},
            {"id": "action_clear", "title": "Clear Cart"},
        ])
        return

    if step == "type_note":
        note = msg
        session["cart"].append({
            "name": session["variety"],
            "category": session["category"],
            "price": session["price"],
            "note": note,
        })
        cart_text, total = format_cart(session["cart"])
        session["step"] = "after_add"
        send_buttons(sender, f"🛒 Added to cart!\n\nYour Cart:\n{cart_text}\n\nWhat next?", [
            {"id": "action_more", "title": "Add More"},
            {"id": "action_confirm", "title": "Confirm Order"},
            {"id": "action_clear", "title": "Clear Cart"},
        ])
        return

    if step == "after_add":
        if msg == "action_more":
            session["step"] = "choose_category"
            categories = list(MENU.keys())
            rows = []
            emojis = {"Food": "🍕", "Drinks": "🥤", "Combo": "🎁"}
            for cat in categories:
                rows.append({"id": f"cat_{cat}", "title": f"{emojis.get(cat, '')} {cat}", "description": f"Browse {cat} items"})
            send_list(sender, "Select a category:", "View Menu", [{"title": "Categories", "rows": rows}])
        elif msg == "action_confirm":
            session["step"] = "confirm_order"
            cart_text, total = format_cart(session["cart"])
            send_buttons(sender, f"📋 Your Final Order:\n\n{cart_text}\n\nConfirm this order?", [
                {"id": "order_yes", "title": "Confirm"},
                {"id": "order_no", "title": "Cancel"},
            ])
        elif msg == "action_clear":
            session["cart"] = []
            session["step"] = "choose_category"
            categories = list(MENU.keys())
            rows = []
            emojis = {"Food": "🍕", "Drinks": "🥤", "Combo": "🎁"}
            for cat in categories:
                rows.append({"id": f"cat_{cat}", "title": f"{emojis.get(cat, '')} {cat}", "description": f"Browse {cat} items"})
            send_list(sender, "Cart cleared!\n\nSelect a category:", "View Menu", [{"title": "Categories", "rows": rows}])
        return

    if step == "confirm_order":
        if msg == "order_yes":
            cart = session["cart"]
            try:
                token = get_zoho_token()
                url = f"https://creator.zoho.com/api/v2/{ZOHO_OWNER}/{APP_LINK}/form/{FORM_LINK}"
                success = 0
                for item in cart:
                    data = {"Product_Name": item["name"], "Category": item["category"], "Currency": str(item["price"])}
                    if item.get("note"):
                        data["Modifier_Note"] = item["note"]
                    resp = requests.post(url, json={"data": data}, headers={"Authorization": f"Zoho-oauthtoken {token}"})
                    if resp.status_code == 200:
                        success += 1
                order_lines = [f"  {item['name']} - Rs.{item['price']}" for item in cart]
                _, total = format_cart(cart)
                user_sessions[sender] = {"step": "start", "cart": []}
                send_text(sender, f"✅ Order Confirmed!\n\n" + "\n".join(order_lines) + f"\n\nTotal: Rs.{total}\nItems added: {success}/{len(cart)}\n\nThank you! Send hi to order again")
            except Exception as e:
                user_sessions[sender] = {"step": "start", "cart": []}
                send_text(sender, f"Error: {str(e)[:100]}\nSend hi to try again")
        elif msg == "order_no":
            user_sessions[sender] = {"step": "start", "cart": []}
            send_text(sender, "Order cancelled.\nSend hi to start again.")
        return

    send_text(sender, "Send hi to start ordering! 🍽️")

@app.route("/whatsapp", methods=["POST"])
def twilio_whatsapp():
    return "Use Meta WhatsApp API now.", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
