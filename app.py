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
        "Biryani": {
            "Veg Biryani": 150,
            "Chicken Biryani": 250,
            "Mutton Biryani": 400,
            "Paneer Biryani": 280,
            "Egg Biryani": 200,
            "Prawn Biryani": 350,
            "Hyderabadi Dum Biryani": 320,
        },
        "Pizza": {
            "Pizza Margherita": 300,
            "Pizza Vegetarian": 350,
            "Pepperoni Pizza": 400,
            "BBQ Chicken Pizza": 420,
            "Mushroom Pizza": 330,
            "Four Cheese Pizza": 380,
        },
        "Burger": {
            "Cheese Burger": 200,
            "Bacon Burger": 250,
            "Chicken Burger": 220,
            "Veg Burger": 150,
            "Double Patty Burger": 300,
            "Fish Burger": 270,
        },
        "Sandwich": {
            "Chicken Curry Sandwich": 180,
            "Mozzarella Sandwich": 160,
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
            "Mac and Cheese": 240,
        },
        "Rice & Noodles": {
            "Fried Rice Veg": 150,
            "Fried Rice Chicken": 200,
            "Schezwan Noodles": 180,
            "Hakka Noodles Veg": 160,
            "Hakka Noodles Chicken": 200,
        },
        "Starters": {
            "Chicken 65": 250,
            "Paneer Tikka": 220,
            "Gobi Manchurian": 180,
            "Spring Rolls Veg": 150,
            "Chicken Wings": 280,
            "Fish Fingers": 260,
            "French Fries": 120,
            "Onion Rings": 130,
        },
        "Soup": {
            "Tomato Soup": 100,
            "Sweet Corn Soup": 120,
            "Hot and Sour Soup": 130,
            "Mushroom Soup": 140,
            "Chicken Clear Soup": 150,
        },
        "Dessert": {
            "Gulab Jamun": 80,
            "Ice Cream Vanilla": 100,
            "Ice Cream Chocolate": 120,
            "Brownie with Ice Cream": 180,
            "Rasmalai": 100,
            "Fruit Salad": 90,
        },
    },
    "Drinks": {
        "Coffee": {
            "Espresso": 120,
            "Cappuccino": 150,
            "Latte": 160,
            "Cold Coffee": 140,
            "Black Coffee": 100,
        },
        "Tea": {
            "Ice Tea": 80,
            "Masala Chai": 50,
            "Green Tea": 70,
            "Lemon Tea": 60,
        },
        "Juice": {
            "Mango Juice": 100,
            "Orange Juice": 90,
            "Watermelon Juice": 80,
            "Pineapple Juice": 90,
            "Mixed Fruit Juice": 110,
        },
        "Shake": {
            "Milkshake Banana": 150,
            "Milkshake Chocolate": 170,
            "Milkshake Strawberry": 160,
            "Milkshake Oreo": 180,
        },
        "Soft Drinks": {
            "Coca-Cola": 60,
            "Pepsi": 60,
            "Sprite": 60,
            "Fanta": 60,
            "Water": 30,
            "Soda": 40,
        },
        "Lassi": {
            "Sweet Lassi": 80,
            "Mango Lassi": 100,
            "Salt Lassi": 70,
            "Rose Lassi": 90,
        },
    },
    "Combo": {
        "Lunch Combos": {
            "Sushi Lunch Combo": 500,
            "Burger Menu Combo": 400,
            "Pizza Combo (2 Pizza + Drink)": 650,
            "Biryani Combo (Biryani + Raita + Drink)": 350,
            "Pasta Combo (Pasta + Soup + Drink)": 400,
        },
        "Family Combos": {
            "Family Meal (Serves 4)": 800,
            "Party Pack (Serves 6)": 1200,
            "Weekend Special (Serves 2)": 500,
        },
        "Value Meals": {
            "Budget Meal (Burger + Fries + Drink)": 250,
            "Student Meal (Sandwich + Juice)": 200,
            "Kids Meal (Nuggets + Fries + Juice)": 180,
        },
    },
}

user_sessions = {}

def get_access_token():
    r = requests.post("https://accounts.zoho.com/oauth/v2/token", data={
        "refresh_token": ZOHO_REFRESH_TOKEN,
        "client_id": ZOHO_CLIENT_ID,
        "client_secret": ZOHO_CLIENT_SECRET,
        "grant_type": "refresh_token"
    })
    return r.json().get("access_token")

def build_numbered_list(items):
    return "\n".join([f"{i+1}. {item}" for i, item in enumerate(items)])

def format_cart(cart):
    lines = []
    total = 0
    for i, item in enumerate(cart):
        lines.append(f"{i+1}. {item['name']} ({item['category']}) - Rs.{item['price']}")
        total += item['price']
    lines.append(f"\nTotal: Rs.{total}")
    return "\n".join(lines), total

@app.route("/", methods=["GET"])
def home():
    return "WhatsApp-Zoho Bot is running!", 200

@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    msg = request.form.get("Body", "").strip()
    sender = request.form.get("From", "")

    if sender not in user_sessions:
        user_sessions[sender] = {"step": "start", "cart": []}

    session = user_sessions[sender]
    step = session["step"]

    # Reset
    if msg.lower() in ["hi", "hello", "hey", "start", "menu", "reset"]:
        user_sessions[sender] = {"step": "choose_category", "cart": []}
        categories = list(MENU.keys())
        return _reply(
            f"Welcome to Restaurant Register!\n\n"
            f"Choose a category:\n\n"
            f"{build_numbered_list(categories)}\n\n"
            f"Reply with the number"
        )

    # Step 1: Choose Category
    if step == "choose_category":
        categories = list(MENU.keys())
        try:
            choice = int(msg) - 1
            if 0 <= choice < len(categories):
                session["category"] = categories[choice]
                session["step"] = "choose_item"
                items = list(MENU[session["category"]].keys())
                return _reply(
                    f"Category: {session['category']}\n\n"
                    f"Choose an item:\n\n"
                    f"{build_numbered_list(items)}\n\n"
                    f"Reply with the number"
                )
            else:
                return _reply(f"Invalid. Pick 1 to {len(categories)}")
        except ValueError:
            return _reply(f"Please reply with a number (1 to {len(categories)})")

    # Step 2: Choose Item
    if step == "choose_item":
        category = session["category"]
        items = list(MENU[category].keys())
        try:
            choice = int(msg) - 1
            if 0 <= choice < len(items):
                selected_item = items[choice]
                session["item"] = selected_item
                varieties = MENU[category][selected_item]
                session["step"] = "choose_variety"
                variety_list = [f"{name} - Rs.{price}" for name, price in varieties.items()]
                return _reply(
                    f"Varieties of {selected_item}:\n\n"
                    f"{build_numbered_list(variety_list)}\n\n"
                    f"Reply with the number"
                )
            else:
                return _reply(f"Invalid. Pick 1 to {len(items)}")
        except ValueError:
            return _reply(f"Please reply with a number (1 to {len(items)})")

    # Step 3: Choose Variety
    if step == "choose_variety":
        category = session["category"]
        item = session["item"]
        varieties = MENU[category][item]
        variety_names = list(varieties.keys())
        try:
            choice = int(msg) - 1
            if 0 <= choice < len(variety_names):
                selected_variety = variety_names[choice]
                price = varieties[selected_variety]
                session["variety"] = selected_variety
                session["price"] = price
                session["step"] = "add_note"
                return _reply(
                    f"Selected: {selected_variety} - Rs.{price}\n\n"
                    f"Add a note (e.g. Extra Spicy, No Onion)\n"
                    f"Or type 'skip' for no note"
                )
            else:
                return _reply(f"Invalid. Pick 1 to {len(variety_names)}")
        except ValueError:
            return _reply(f"Please reply with a number (1 to {len(variety_names)})")

    # Step 4: Add Note
    if step == "add_note":
        note = "" if msg.lower() == "skip" else msg
        session["cart"].append({
            "name": session["variety"],
            "category": session["category"],
            "price": session["price"],
            "note": note,
        })
        cart_text, total = format_cart(session["cart"])
        session["step"] = "after_add"
        return _reply(
            f"Added to cart!\n\n"
            f"Your Cart:\n{cart_text}\n\n"
            f"What next?\n"
            f"1. Add more items\n"
            f"2. Confirm Order\n"
            f"3. Clear cart & start over\n\n"
            f"Reply with the number"
        )

    # Step 5: After adding - add more or confirm
    if step == "after_add":
        if msg == "1":
            session["step"] = "choose_category"
            categories = list(MENU.keys())
            return _reply(
                f"Choose a category:\n\n"
                f"{build_numbered_list(categories)}\n\n"
                f"Reply with the number"
            )
        elif msg == "2":
            session["step"] = "confirm_order"
            cart_text, total = format_cart(session["cart"])
            return _reply(
                f"Your Final Order:\n\n"
                f"{cart_text}\n\n"
                f"Type 'confirm' to place this order\n"
                f"Type 'cancel' to cancel"
            )
        elif msg == "3":
            user_sessions[sender] = {"step": "choose_category", "cart": []}
            categories = list(MENU.keys())
            return _reply(
                f"Cart cleared!\n\n"
                f"Choose a category:\n\n"
                f"{build_numbered_list(categories)}\n\n"
                f"Reply with the number"
            )
        else:
            return _reply("Please reply 1, 2, or 3")

    # Step 6: Confirm Order - Add all items to Zoho
    if step == "confirm_order":
        if msg.lower() == "confirm":
            cart = session["cart"]
            token = get_access_token()
            url = f"https://creator.zoho.com/api/v2/{ZOHO_OWNER}/{APP_LINK}/form/{FORM_LINK}"
            success_count = 0
            errors = []

            for item in cart:
                data = {
                    "Product_Name": item["name"],
                    "Category": item["category"],
                    "Currency": str(item["price"]),
                }
                if item["note"]:
                    data["Modifier_Note"] = item["note"]

                try:
                    resp = requests.post(url, json={"data": data}, headers={
                        "Authorization": f"Zoho-oauthtoken {token}"
                    })
                    if resp.status_code == 200:
                        success_count += 1
                    else:
                        errors.append(f"{item['name']}: {resp.status_code}")
                except Exception as e:
                    errors.append(f"{item['name']}: {str(e)[:50]}")

            user_sessions[sender] = {"step": "start", "cart": []}

            _, total = format_cart(cart)
            if errors:
                return _reply(
                    f"Order placed with some errors.\n"
                    f"Added: {success_count}/{len(cart)} items\n"
                    f"Errors: {', '.join(errors)}\n\n"
                    f"Send 'hi' to order again"
                )
            else:
                order_lines = [f"  {item['name']} - Rs.{item['price']}" for item in cart]
                return _reply(
                    f"Order Confirmed! All {success_count} items added.\n\n"
                    f"Order Summary:\n"
                    f"{chr(10).join(order_lines)}\n"
                    f"Total: Rs.{total}\n\n"
                    f"Thank you! Send 'hi' to order again"
                )

        elif msg.lower() == "cancel":
            user_sessions[sender] = {"step": "start", "cart": []}
            return _reply("Order cancelled. Send 'hi' to start again.")
        else:
            return _reply("Type 'confirm' to place order or 'cancel' to cancel")

    return _reply("Send 'hi' to start ordering!")

def _reply(message):
    return (
        f'<?xml version="1.0" encoding="UTF-8"?>'
        f'<Response><Message>{message}</Message></Response>',
        200,
        {"Content-Type": "text/xml"}
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
