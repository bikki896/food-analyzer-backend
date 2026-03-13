from flask import Flask, jsonify
import json
import os

app = Flask(__name__)

# ---------------- Upload Folder ----------------
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------- Load Products Database ----------------
PRODUCTS = {}

if os.path.exists("products.json"):
    try:
        with open("products.json", "r", encoding="utf-8") as f:
            PRODUCTS = json.load(f)
    except Exception as e:
        print("Error loading products.json:", e)
        PRODUCTS = {}

# ---------------- Ingredient Helper ----------------
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


# ---------------- Routes ----------------

@app.route("/")
def home():
    return jsonify({
        "message": "AI Food Analyzer Backend is Running 🚀",
        "status": "success"
    })


@app.route("/product/<barcode>", methods=["GET"])
def get_product(barcode):

    product = PRODUCTS.get(barcode)

    if not product:
        return jsonify({
            "status": "error",
            "message": "Product not found",
            "barcode": barcode
        }), 404

    ingredients_raw = product.get("ingredients_text", "")

    ingredients_list = [i.strip() for i in ingredients_raw.split(",") if i.strip()]

    simplified_ingredients = []

    for ing in ingredients_list:

        simplified_ingredients.append({
            "original": ing,
            "simplified": IngredientHelper.simplify(ing),
            "risk": IngredientHelper.risk(ing)
        })

    response = {
        "status": "success",
        "barcode": barcode,
        "product_name": product.get("product_name", "Unknown Product"),
        "ingredients": simplified_ingredients
    }

    return jsonify(response)


# ---------------- Health Check Route ----------------
@app.route("/health")
def health():
    return jsonify({"status": "backend running"})


# ---------------- Run Server ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)