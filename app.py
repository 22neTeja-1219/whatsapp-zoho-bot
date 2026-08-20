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

# ========== MENU (English names + prices) ==========
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

# ========== TRANSLATIONS ==========
LANG = {
    "en": {
        "welcome": "🍽️ *Welcome to Restaurant Register!*\n\nPlease select your language:\n\n1. English\n2. తెలుగు (Telugu)\n3. हिन्दी (Hindi)\n4. தமிழ் (Tamil)\n5. ಕನ್ನಡ (Kannada)\n\nReply with the number",
        "select_category": "📋 *Menu*\n\nSelect a category:\n\n{list}\n\nReply with the number",
        "select_item": "🍴 *{category}*\n\nSelect an item:\n\n{list}\n\nReply with the number",
        "select_variety": "📝 *{item}*\n\n{list}\n\nReply with the number",
        "selected_item": "✅ *{name}* - ₹{price}\n\nAdd a note (e.g. Extra Spicy, No Onion)\nOr reply *0* for no note",
        "added_to_cart": "🛒 *Added to cart!*\n\n*Your Cart:*\n{cart}\n\n1️⃣ Add more items\n2️⃣ Confirm Order ✅\n3️⃣ Clear cart 🗑️\n\nReply with the number",
        "final_order": "📋 *Your Final Order:*\n\n{cart}\n\nReply *yes* to confirm\nReply *no* to cancel",
        "order_confirmed": "✅ *Order Confirmed!*\n\n{summary}\n\n🙏 Thank you for your order!\nSend *hi* to order again",
        "order_cancelled": "❌ Order cancelled.\nSend *hi* to start again.",
        "invalid": "⚠️ Invalid choice. Please try again.",
        "error": "❌ Error: {error}\nSend *hi* to try again.",
        "category_names": {"Food": "🍕 Food", "Drinks": "🥤 Drinks", "Combo": "🎁 Combo"},
    },
    "te": {
        "welcome": "🍽️ *రెస్టారెంట్ రిజిస్టర్‌కు స్వాగతం!*\n\nదయచేసి మీ భాషను ఎంచుకోండి:\n\n1. English\n2. తెలుగు (Telugu)\n3. हिन्दी (Hindi)\n4. தமிழ் (Tamil)\n5. ಕನ್ನಡ (Kannada)\n\nనంబర్‌తో రిప్లై చేయండి",
        "select_category": "📋 *మెనూ*\n\nవర్గాన్ని ఎంచుకోండి:\n\n{list}\n\nనంబర్‌తో రిప్లై చేయండి",
        "select_item": "🍴 *{category}*\n\nఐటమ్‌ను ఎంచుకోండి:\n\n{list}\n\nనంబర్‌తో రిప్లై చేయండి",
        "select_variety": "📝 *{item}*\n\n{list}\n\nనంబర్‌తో రిప్లై చేయండి",
        "selected_item": "✅ *{name}* - ₹{price}\n\nనోట్ జోడించండి (ఉదా: ఎక్స్ట్రా స్పైసీ)\nనోట్ వద్దు అంటే *0* రిప్లై చేయండి",
        "added_to_cart": "🛒 *కార్ట్‌కు జోడించబడింది!*\n\n*మీ కార్ట్:*\n{cart}\n\n1️⃣ మరిన్ని ఐటమ్‌లు జోడించు\n2️⃣ ఆర్డర్ కన్ఫర్మ్ చేయి ✅\n3️⃣ కార్ట్ క్లియర్ చేయి 🗑️\n\nనంబర్‌తో రిప్లై చేయండి",
        "final_order": "📋 *మీ ఫైనల్ ఆర్డర్:*\n\n{cart}\n\nకన్ఫర్మ్ చేయడానికి *yes* రిప్లై చేయండి\nక్యాన్సిల్ చేయడానికి *no* రిప్లై చేయండి",
        "order_confirmed": "✅ *ఆర్డర్ కన్ఫర్మ్ అయింది!*\n\n{summary}\n\n🙏 మీ ఆర్డర్‌కు ధన్యవాదాలు!\nమళ్ళీ ఆర్డర్ చేయడానికి *hi* పంపండి",
        "order_cancelled": "❌ ఆర్డర్ క్యాన్సిల్ చేయబడింది.\nమళ్ళీ ప్రారంభించడానికి *hi* పంపండి.",
        "invalid": "⚠️ చెల్లని ఎంపిక. దయచేసి మళ్ళీ ప్రయత్నించండి.",
        "error": "❌ ఎర్రర్: {error}\nమళ్ళీ ప్రయత్నించడానికి *hi* పంపండి.",
        "category_names": {"Food": "🍕 ఆహారం", "Drinks": "🥤 డ్రింక్స్", "Combo": "🎁 కాంబో"},
    },
    "hi": {
        "welcome": "🍽️ *रेस्टोरेंट रजिस्टर में स्वागत है!*\n\nकृपया अपनी भाषा चुनें:\n\n1. English\n2. తెలుగు (Telugu)\n3. हिन्दी (Hindi)\n4. தமிழ் (Tamil)\n5. ಕನ್ನಡ (Kannada)\n\nनंबर से रिप्लाई करें",
        "select_category": "📋 *मेनू*\n\nश्रेणी चुनें:\n\n{list}\n\nनंबर से रिप्लाई करें",
        "select_item": "🍴 *{category}*\n\nआइटम चुनें:\n\n{list}\n\nनंबर से रिप्लाई करें",
        "select_variety": "📝 *{item}*\n\n{list}\n\nनंबर से रिप्लाई करें",
        "selected_item": "✅ *{name}* - ₹{price}\n\nनोट जोड़ें (जैसे एक्स्ट्रा स्पाइसी)\nनोट नहीं चाहिए तो *0* रिप्लाई करें",
        "added_to_cart": "🛒 *कार्ट में जोड़ा गया!*\n\n*आपका कार्ट:*\n{cart}\n\n1️⃣ और आइटम जोड़ें\n2️⃣ ऑर्डर कन्फर्म करें ✅\n3️⃣ कार्ट खाली करें 🗑️\n\nनंबर से रिप्लाई करें",
        "final_order": "📋 *आपका फाइनल ऑर्डर:*\n\n{cart}\n\nकन्फर्म करने के लिए *yes* रिप्लाई करें\nकैंसल करने के लिए *no* रिप्लाई करें",
        "order_confirmed": "✅ *ऑर्डर कन्फर्म हो गया!*\n\n{summary}\n\n🙏 आपके ऑर्डर के लिए धन्यवाद!\nफिर से ऑर्डर करने के लिए *hi* भेजें",
        "order_cancelled": "❌ ऑर्डर कैंसल कर दिया गया.\nफिर से शुरू करने के लिए *hi* भेजें.",
        "invalid": "⚠️ गलत चॉइस. कृपया फिर से कोशिश करें.",
        "error": "❌ एरर: {error}\nफिर से कोशिश के लिए *hi* भेजें.",
        "category_names": {"Food": "🍕 खाना", "Drinks": "🥤 ड्रिंक्स", "Combo": "🎁 कॉम्बो"},
    },
    "ta": {
        "welcome": "🍽️ *உணவகத்திற்கு வரவேற்கிறோம்!*\n\nஉங்கள் மொழியைத் தேர்ந்தெடுக்கவும்:\n\n1. English\n2. తెలుగు (Telugu)\n3. हिन्दी (Hindi)\n4. தமிழ் (Tamil)\n5. ಕನ್ನಡ (Kannada)\n\nஎண்ணை பதிலளிக்கவும்",
        "select_category": "📋 *மெனு*\n\nவகையைத் தேர்ந்தெடுக்கவும்:\n\n{list}\n\nஎண்ணை பதிலளிக்கவும்",
        "select_item": "🍴 *{category}*\n\nபொருளைத் தேர்ந்தெடுக்கவும்:\n\n{list}\n\nஎண்ணை பதிலளிக்கவும்",
        "select_variety": "📝 *{item}*\n\n{list}\n\nஎண்ணை பதிலளிக்கவும்",
        "selected_item": "✅ *{name}* - ₹{price}\n\nகுறிப்பு சேர்க்கவும் (எ.கா. கூடுதல் காரம்)\nகுறிப்பு வேண்டாம் என்றால் *0* பதிலளிக்கவும்",
        "added_to_cart": "🛒 *கார்ட்டில் சேர்க்கப்பட்டது!*\n\n*உங்கள் கார்ட்:*\n{cart}\n\n1️⃣ மேலும் பொருட்கள் சேர்\n2️⃣ ஆர்டரை உறுதிப்படுத்து ✅\n3️⃣ கார்ட்டை அழி 🗑️\n\nஎண்ணை பதிலளிக்கவும்",
        "final_order": "📋 *உங்கள் இறுதி ஆர்டர்:*\n\n{cart}\n\nஉறுதிப்படுத்த *yes* பதிலளிக்கவும்\nரத்து செய்ய *no* பதிலளிக்கவும்",
        "order_confirmed": "✅ *ஆர்டர் உறுதிப்படுத்தப்பட்டது!*\n\n{summary}\n\n🙏 உங்கள் ஆர்டருக்கு நன்றி!\nமீண்டும் ஆர்டர் செய்ய *hi* அனுப்பவும்",
        "order_cancelled": "❌ ஆர்டர் ரத்து செய்யப்பட்டது.\nமீண்டும் தொடங்க *hi* அனுப்பவும்.",
        "invalid": "⚠️ தவறான தேர்வு. மீண்டும் முயற்சிக்கவும்.",
        "error": "❌ பிழை: {error}\nமீண்டும் முயற்சிக்க *hi* அனுப்பவும்.",
        "category_names": {"Food": "🍕 உணவு", "Drinks": "🥤 பானங்கள்", "Combo": "🎁 காம்போ"},
    },
    "kn": {
        "welcome": "🍽️ *ರೆಸ್ಟೋರೆಂಟ್ ರಿಜಿಸ್ಟರ್‌ಗೆ ಸ್ವಾಗತ!*\n\nದಯವಿಟ್ಟು ನಿಮ್ಮ ಭಾಷೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ:\n\n1. English\n2. తెలుగు (Telugu)\n3. हिन्दी (Hindi)\n4. தமிழ் (Tamil)\n5. ಕನ್ನಡ (Kannada)\n\nಸಂಖ್ಯೆಯಿಂದ ರಿಪ್ಲೈ ಮಾಡಿ",
        "select_category": "📋 *ಮೆನು*\n\nವರ್ಗವನ್ನು ಆಯ್ಕೆಮಾಡಿ:\n\n{list}\n\nಸಂಖ್ಯೆಯಿಂದ ರಿಪ್ಲೈ ಮಾಡಿ",
        "select_item": "🍴 *{category}*\n\nಐಟಂ ಆಯ್ಕೆಮಾಡಿ:\n\n{list}\n\nಸಂಖ್ಯೆಯಿಂದ ರಿಪ್ಲೈ ಮಾಡಿ",
        "select_variety": "📝 *{item}*\n\n{list}\n\nಸಂಖ್ಯೆಯಿಂದ ರಿಪ್ಲೈ ಮಾಡಿ",
        "selected_item": "✅ *{name}* - ₹{price}\n\nನೋಟ್ ಸೇರಿಸಿ (ಉದಾ: ಎಕ್ಸ್ಟ್ರಾ ಸ್ಪೈಸಿ)\nನೋಟ್ ಬೇಡ ಎಂದರೆ *0* ರಿಪ್ಲೈ ಮಾಡಿ",
        "added_to_cart": "🛒 *ಕಾರ್ಟ್‌ಗೆ ಸೇರಿಸಲಾಗಿದೆ!*\n\n*ನಿಮ್ಮ ಕಾರ್ಟ್:*\n{cart}\n\n1️⃣ ಇನ್ನಷ್ಟು ಐಟಂ ಸೇರಿಸಿ\n2️⃣ ಆರ್ಡರ್ ಕನ್ಫರ್ಮ್ ✅\n3️⃣ ಕಾರ್ಟ್ ಖಾಲಿ ಮಾಡಿ 🗑️\n\nಸಂಖ್ಯೆಯಿಂದ ರಿಪ್ಲೈ ಮಾಡಿ",
        "final_order": "📋 *ನಿಮ್ಮ ಅಂತಿಮ ಆರ್ಡರ್:*\n\n{cart}\n\nಕನ್ಫರ್ಮ್ ಮಾಡಲು *yes* ರಿಪ್ಲೈ ಮಾಡಿ\nರದ್ದು ಮಾಡಲು *no* ರಿಪ್ಲೈ ಮಾಡಿ",
        "order_confirmed": "✅ *ಆರ್ಡರ್ ಕನ್ಫರ್ಮ್ ಆಗಿದೆ!*\n\n{summary}\n\n🙏 ನಿಮ್ಮ ಆರ್ಡರ್‌ಗೆ ಧನ್ಯವಾದಗಳು!\nಮತ್ತೆ ಆರ್ಡರ್ ಮಾಡಲು *hi* ಕಳುಹಿಸಿ",
        "order_cancelled": "❌ ಆರ್ಡರ್ ರದ್ದಾಗಿದೆ.\nಮತ್ತೆ ಪ್ರಾರಂಭಿಸಲು *hi* ಕಳುಹಿಸಿ.",
        "invalid": "⚠️ ತಪ್ಪಾದ ಆಯ್ಕೆ. ದಯವಿಟ್ಟು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.",
        "error": "❌ ದೋಷ: {error}\nಮತ್ತೆ ಪ್ರಯತ್ನಿಸಲು *hi* ಕಳುಹಿಸಿ.",
        "category_names": {"Food": "🍕 ಆಹಾರ", "Drinks": "🥤 ಪಾನೀಯಗಳು", "Combo": "🎁 ಕಾಂಬೋ"},
    },
}

LANG_CODES = ["en", "te", "hi", "ta", "kn"]

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

def t(session, key):
    lang = session.get("lang", "en")
    return LANG[lang][key]

def format_cart(cart):
    lines = []
    total = 0
    for i, item in enumerate(cart):
        note_text = f" ({item['note']})" if item.get('note') else ""
        lines.append(f"{i+1}. {item['name']}{note_text} - ₹{item['price']}")
        total += item['price']
    lines.append(f"\n💰 *Total: ₹{total}*")
    return "\n".join(lines), total

@app.route("/", methods=["GET"])
def home():
    return "WhatsApp-Zoho Bot is running!", 200

@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    msg = request.form.get("Body", "").strip()
    sender = request.form.get("From", "")

    if sender not in user_sessions:
        user_sessions[sender] = {"step": "start", "cart": [], "lang": "en"}

    session = user_sessions[sender]
    step = session["step"]

    # Reset / Start
    if msg.lower() in ["hi", "hello", "hey", "start", "menu", "reset", "0"]:
        user_sessions[sender] = {"step": "choose_lang", "cart": [], "lang": "en"}
        return _reply(LANG["en"]["welcome"])

    # Step 0: Choose Language
    if step == "choose_lang":
        try:
            choice = int(msg) - 1
            if 0 <= choice < len(LANG_CODES):
                session["lang"] = LANG_CODES[choice]
                session["step"] = "choose_category"
                categories = list(MENU.keys())
                cat_names = t(session, "category_names")
                display_cats = [cat_names.get(c, c) for c in categories]
                return _reply(t(session, "select_category").format(list=build_numbered_list(display_cats)))
            else:
                return _reply(t(session, "invalid"))
        except ValueError:
            return _reply(t(session, "invalid"))

    # Step 1: Choose Category
    if step == "choose_category":
        categories = list(MENU.keys())
        try:
            choice = int(msg) - 1
            if 0 <= choice < len(categories):
                session["category"] = categories[choice]
                session["step"] = "choose_item"
                items = list(MENU[session["category"]].keys())
                return _reply(t(session, "select_item").format(
                    category=t(session, "category_names").get(session["category"], session["category"]),
                    list=build_numbered_list(items)
                ))
            else:
                return _reply(t(session, "invalid"))
        except ValueError:
            return _reply(t(session, "invalid"))

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
                variety_list = [f"{name} - ₹{price}" for name, price in varieties.items()]
                return _reply(t(session, "select_variety").format(
                    item=selected_item,
                    list=build_numbered_list(variety_list)
                ))
            else:
                return _reply(t(session, "invalid"))
        except ValueError:
            return _reply(t(session, "invalid"))

    # Step 3: Choose Variety
    if step == "choose_variety":
        category = session["category"]
        item = session["item"]
        varieties = MENU[category][item]
        variety_names = list(varieties.keys())
        try:
            choice = int(msg) - 1
            if 0 <= choice < len(variety_names):
                selected = variety_names[choice]
                price = varieties[selected]
                session["variety"] = selected
                session["price"] = price
                session["step"] = "add_note"
                return _reply(t(session, "selected_item").format(name=selected, price=price))
            else:
                return _reply(t(session, "invalid"))
        except ValueError:
            return _reply(t(session, "invalid"))

    # Step 4: Add Note
    if step == "add_note":
        note = "" if msg == "0" else msg
        session["cart"].append({
            "name": session["variety"],
            "category": session["category"],
            "price": session["price"],
            "note": note,
        })
        cart_text, total = format_cart(session["cart"])
        session["step"] = "after_add"
        return _reply(t(session, "added_to_cart").format(cart=cart_text))

    # Step 5: After Add
    if step == "after_add":
        if msg == "1":
            session["step"] = "choose_category"
            categories = list(MENU.keys())
            cat_names = t(session, "category_names")
            display_cats = [cat_names.get(c, c) for c in categories]
            return _reply(t(session, "select_category").format(list=build_numbered_list(display_cats)))
        elif msg == "2":
            session["step"] = "confirm_order"
            cart_text, total = format_cart(session["cart"])
            return _reply(t(session, "final_order").format(cart=cart_text))
        elif msg == "3":
            session["cart"] = []
            session["step"] = "choose_category"
            categories = list(MENU.keys())
            cat_names = t(session, "category_names")
            display_cats = [cat_names.get(c, c) for c in categories]
            return _reply(t(session, "select_category").format(list=build_numbered_list(display_cats)))
        else:
            return _reply(t(session, "invalid"))

    # Step 6: Confirm Order
    if step == "confirm_order":
        if msg.lower() == "yes":
            cart = session["cart"]
            try:
                token = get_access_token()
                url = f"https://creator.zoho.com/api/v2/{ZOHO_OWNER}/{APP_LINK}/form/{FORM_LINK}"
                success = 0
                for item in cart:
                    data = {
                        "Product_Name": item["name"],
                        "Category": item["category"],
                        "Currency": str(item["price"]),
                    }
                    if item.get("note"):
                        data["Modifier_Note"] = item["note"]
                    resp = requests.post(url, json={"data": data}, headers={
                        "Authorization": f"Zoho-oauthtoken {token}"
                    })
                    if resp.status_code == 200:
                        success += 1

                order_lines = [f"  • {item['name']} - ₹{item['price']}" for item in cart]
                _, total = format_cart(cart)
                summary = "\n".join(order_lines) + f"\n\n💰 *Total: ₹{total}*\n📦 Items added: {success}/{len(cart)}"

                user_sessions[sender] = {"step": "start", "cart": [], "lang": session.get("lang", "en")}
                return _reply(t(session, "order_confirmed").format(summary=summary))
            except Exception as e:
                user_sessions[sender] = {"step": "start", "cart": [], "lang": session.get("lang", "en")}
                return _reply(t(session, "error").format(error=str(e)[:100]))

        elif msg.lower() == "no":
            user_sessions[sender] = {"step": "start", "cart": [], "lang": session.get("lang", "en")}
            return _reply(t(session, "order_cancelled"))
        else:
            return _reply(t(session, "invalid"))

    return _reply("Send *hi* to start ordering! 🍽️")

def _reply(message):
    return (
        f'<?xml version="1.0" encoding="UTF-8"?>'
        f'<Response><Message>{message}</Message></Response>',
        200,
        {"Content-Type": "text/xml"}
    )
@app.route("/ping", methods=["GET"])
def ping():
    return "pong", 200
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
