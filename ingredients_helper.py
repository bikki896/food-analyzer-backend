# Simple functions to simplify chemical names and classify risk

# Map complex chemical names to layman terms
SIMPLIFY_MAP = {
    "sodium chloride": "Salt",
    "sucrose": "Sugar",
    "monosodium glutamate": "Flavor Enhancer",
    "high fructose corn syrup": "Sugar",
    "ascorbic acid": "Vitamin C"
}

HIGH_RISK = ["sugar", "hfcs", "palm oil", "preservative"]
MODERATE_RISK = ["salt", "flavour", "color"]

def simplify_ingredient(name: str) -> str:
    name_lower = name.lower()
    for key, value in SIMPLIFY_MAP.items():
        if key in name_lower:
            return value
    return name.capitalize()

def classify_risk(name: str) -> str:
    name_lower = name.lower()
    if any(word in name_lower for word in HIGH_RISK):
        return "High Risk"
    elif any(word in name_lower for word in MODERATE_RISK):
        return "Moderate"
    else:
        return "Safe"