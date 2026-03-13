from flask import Flask, jsonify, request
import json
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# ---------- Create upload folder if not exists ----------
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# ---------- Load products database safely ----------
PRODUCTS = {}

if os.path.exists("products.json"):
    try:
        with open("products.json", "r", encoding="utf-8") as f:
            PRODUCTS = json.load(f)
    except:
        PRODUCTS = {}

# ---------- Ingredient Helper ----------
class IngredientHelper:

    HIGH_RISK = ["sugar", "hfcs", "palm oil", "preservative"]
    MODERATE = ["salt", "flavour", "color", "spices", "emulsifier"]

    SIMPLIFY_MAP = {
        "hfcs": "High Fructose Corn Syrup",
        "palm oil": "Palm Oil",
        "emulsifier": "Emulsifier",
        "phosphoric acid": "Acid",
        "cocoa mass": "Cocoa",
        "wheat flour": "Flour",
        "milk solids": "Milk",
        "carbonated water": "Water"
    }

    @staticmethod
    def simplify(name):
        name_lower = name.lower()

        for key, value in IngredientHelper.SIMPLIFY_MAP.items():
            if key in name_lower:
                return value

        return name.title()

    @staticmethod
    def risk(name):
        name_lower = name.lower()

        if any(word in name_lower for word in IngredientHelper.HIGH_RISK):
            return "High Risk"

        elif any(word in name_lower for word in IngredientHelper.MODERATE):
            return "Moderate"

        else:
            return "Safe"


# ---------- Routes ----------

@app.route("/")
def home():
    return "AI Food Analyzer Backend is Running 🚀"


@app.route("/product/<barcode>", methods=["GET"])
def get_product(barcode):

    product = PRODUCTS.get(barcode)

    if not product:
        return jsonify({"error": "Product not found"}), 404

    ingredients_raw = product.get("ingredients_text", "")

    ingredients_list = [i.strip() for i in ingredients_raw.split(",")]

    simplified_ingredients = []

    for ing in ingredients_list:

        simplified_ingredients.append({
            "original": ing,
            "simplified": IngredientHelper.simplify(ing),
            "risk": IngredientHelper.risk(ing)
        })

    response = {
        "product_name": product.get("product_name", "Unknown Product"),
        "ingredients": simplified_ingredients
    }

    return jsonify(response)


# ---------- Run Server (Render Compatible) ----------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)