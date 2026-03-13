from flask import Flask, jsonify
import json
import os
import requests

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------- Local product database ----------
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

        if any(word in name_lower for word in IngredientHelper.MODERATE):
            return "Moderate"

        return "Safe"


# ---------- Routes ----------

@app.route("/")
def home():
    return jsonify({"status": "AI Food Analyzer Backend Running"})


@app.route("/product/<barcode>")
def get_product(barcode):

    # 1️⃣ Check local database first
    product = PRODUCTS.get(barcode)

    if product:
        ingredients_raw = product.get("ingredients_text", "")
        product_name = product.get("product_name", "Unknown Product")

    else:

        # 2️⃣ Fetch from OpenFoodFacts
        url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
        response = requests.get(url)

        if response.status_code != 200:
            return jsonify({"status": "error", "message": "Product not found"})

        data = response.json()

        if data.get("status") == 0:
            return jsonify({"status": "error", "message": "Product not found"})

        product_data = data["product"]

        product_name = product_data.get("product_name", "Unknown Product")
        ingredients_raw = product_data.get("ingredients_text", "")

    ingredients_list = [i.strip() for i in ingredients_raw.split(",") if i.strip()]

    simplified_ingredients = []

    for ing in ingredients_list:
        simplified_ingredients.append({
            "original": ing,
            "simplified": IngredientHelper.simplify(ing),
            "risk": IngredientHelper.risk(ing)
        })

    return jsonify({
        "status": "success",
        "barcode": barcode,
        "product_name": product_name,
        "ingredients": simplified_ingredients
    })


@app.route("/health")
def health():
    return jsonify({"status": "backend running"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)