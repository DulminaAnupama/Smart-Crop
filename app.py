from flask import Flask, render_template, request

app = Flask(__name__)

# Sri Lankan crop data with growing conditions and yield estimates
CROPS_DATA = {
    "rice": {
        "name": "Rice (පඩි)",
        "soil_types": ["clay", "loamy", "alluvial"],
        "min_rainfall": 1000,
        "max_rainfall": 2500,
        "min_temp": 20,
        "max_temp": 35,
        "yield_per_acre": 1800,  # kg per acre
        "season": "Yala & Maha seasons",
        "tips": "Requires standing water. Best planted in lowland areas."
    },
    "tea": {
        "name": "Tea (තේ)",
        "soil_types": ["loamy", "red"],
        "min_rainfall": 1500,
        "max_rainfall": 3000,
        "min_temp": 13,
        "max_temp": 28,
        "yield_per_acre": 800,
        "season": "Year-round",
        "tips": "Thrives in highland areas. Requires well-drained acidic soil."
    },
    "coconut": {
        "name": "Coconut (පොල්)",
        "soil_types": ["sandy", "loamy", "laterite"],
        "min_rainfall": 1000,
        "max_rainfall": 2000,
        "min_temp": 25,
        "max_temp": 35,
        "yield_per_acre": 3000,
        "season": "Year-round harvest",
        "tips": "Coastal and lowland areas. Tolerates sandy soil well."
    },
    "rubber": {
        "name": "Rubber (රබර්)",
        "soil_types": ["laterite", "loamy", "red"],
        "min_rainfall": 2000,
        "max_rainfall": 3500,
        "min_temp": 25,
        "max_temp": 34,
        "yield_per_acre": 500,
        "season": "Year-round tapping",
        "tips": "Wet zone crop. Requires consistent rainfall."
    },
    "cinnamon": {
        "name": "Cinnamon (කුරුඳු)",
        "soil_types": ["sandy", "loamy"],
        "min_rainfall": 1250,
        "max_rainfall": 2500,
        "min_temp": 25,
        "max_temp": 32,
        "yield_per_acre": 150,
        "season": "Harvest twice yearly",
        "tips": "Sri Lanka's premium export. Grows well in southern coastal areas."
    },
    "pepper": {
        "name": "Black Pepper (ගම්මිරිස්)",
        "soil_types": ["loamy", "red", "laterite"],
        "min_rainfall": 1500,
        "max_rainfall": 3000,
        "min_temp": 20,
        "max_temp": 35,
        "yield_per_acre": 400,
        "season": "December to March harvest",
        "tips": "Vine crop, needs support trees. Shade tolerant."
    },
    "vegetables": {
        "name": "Vegetables (එළවළු)",
        "soil_types": ["loamy", "sandy", "clay", "alluvial", "red"],
        "min_rainfall": 500,
        "max_rainfall": 2000,
        "min_temp": 15,
        "max_temp": 35,
        "yield_per_acre": 4000,
        "season": "Year-round with rotation",
        "tips": "Diverse options: tomatoes, beans, cabbage, carrots based on region."
    },
    "maize": {
        "name": "Maize (බඩ ඉරිඟු)",
        "soil_types": ["loamy", "sandy", "alluvial"],
        "min_rainfall": 500,
        "max_rainfall": 1500,
        "min_temp": 20,
        "max_temp": 35,
        "yield_per_acre": 2500,
        "season": "Yala & Maha seasons",
        "tips": "Drought tolerant. Good for dry zone farming."
    },
    "banana": {
        "name": "Banana (කෙසෙල්)",
        "soil_types": ["loamy", "clay", "alluvial"],
        "min_rainfall": 1000,
        "max_rainfall": 2500,
        "min_temp": 22,
        "max_temp": 35,
        "yield_per_acre": 8000,
        "season": "Year-round harvest",
        "tips": "High yield crop. Multiple varieties suited for Sri Lanka."
    },
    "sugarcane": {
        "name": "Sugarcane (උක්)",
        "soil_types": ["loamy", "clay", "alluvial"],
        "min_rainfall": 750,
        "max_rainfall": 1500,
        "min_temp": 20,
        "max_temp": 35,
        "yield_per_acre": 25000,
        "season": "12-18 month cycle",
        "tips": "Industrial crop. Suited for dry and intermediate zones."
    }
}


def calculate_crop_score(crop_data, soil_type, rainfall, temperature):
    """Calculate how suitable a crop is for given conditions."""
    score = 0
    
    # Soil match (40 points)
    if soil_type.lower() in crop_data["soil_types"]:
        score += 40
    
    # Rainfall match (30 points)
    if crop_data["min_rainfall"] <= rainfall <= crop_data["max_rainfall"]:
        score += 30
    elif rainfall < crop_data["min_rainfall"]:
        diff = crop_data["min_rainfall"] - rainfall
        score += max(0, 30 - (diff / 50))
    else:
        diff = rainfall - crop_data["max_rainfall"]
        score += max(0, 30 - (diff / 50))
    
    # Temperature match (30 points)
    if crop_data["min_temp"] <= temperature <= crop_data["max_temp"]:
        score += 30
    elif temperature < crop_data["min_temp"]:
        diff = crop_data["min_temp"] - temperature
        score += max(0, 30 - (diff * 3))
    else:
        diff = temperature - crop_data["max_temp"]
        score += max(0, 30 - (diff * 3))
    
    return score


def get_recommendations(soil_type, rainfall, temperature, land_area):
    """Get crop recommendations based on input conditions."""
    recommendations = []
    
    for crop_id, crop_data in CROPS_DATA.items():
        score = calculate_crop_score(crop_data, soil_type, rainfall, temperature)
        
        if score >= 50:  # Only recommend if score is reasonable
            expected_yield = crop_data["yield_per_acre"] * land_area
            
            # Adjust yield based on conditions match
            yield_factor = score / 100
            adjusted_yield = expected_yield * yield_factor
            
            recommendations.append({
                "name": crop_data["name"],
                "score": round(score, 1),
                "yield": round(adjusted_yield, 0),
                "yield_per_acre": crop_data["yield_per_acre"],
                "season": crop_data["season"],
                "tips": crop_data["tips"]
            })
    
    # Sort by score descending
    recommendations.sort(key=lambda x: x["score"], reverse=True)
    
    return recommendations[:5]  # Return top 5


@app.route("/", methods=["GET", "POST"])
def index():
    recommendations = None
    inputs = None
    
    if request.method == "POST":
        soil_type = request.form.get("soil_type")
        rainfall = float(request.form.get("rainfall"))
        temperature = float(request.form.get("temperature"))
        land_area = float(request.form.get("land_area"))
        
        inputs = {
            "soil_type": soil_type,
            "rainfall": rainfall,
            "temperature": temperature,
            "land_area": land_area
        }
        
        recommendations = get_recommendations(soil_type, rainfall, temperature, land_area)
    
    return render_template("index.html", recommendations=recommendations, inputs=inputs)


if __name__ == "__main__":
    app.run(debug=True)

