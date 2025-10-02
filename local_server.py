import uvicorn
import json
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import date
import torch
from peft import PeftModel
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from json_repair import loads as repair_json

# --- Configuration ---
SPOONACULAR_API_KEY = "d6e16aadf7ea4e0c81987b07c22fcf04" # Your key
base_model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
adapter_path = "./tinyllama-savvy-finetuned"

# --- In-Memory "Database" ---
pantry_db: Dict[str, List[Dict]] = {"1": []}
profile_db: Dict[str, Dict] = {"1": {"household_size": 2, "dietary_restrictions": [], "health_goals": []}}
shopping_list_db: Dict[str, List[Dict]] = {"1": []}
next_item_id = 1
substitution_map = {
    "shredded cheddar cheese": {"name": "Great Value Shredded Cheddar", "savings": "0.80"},
    "milk": {"name": "Great Value 1% Milk", "savings": "0.50"},
    "eggs": {"name": "Great Value Large White Eggs", "savings": "0.65"},
}

# --- Load AI Model ---
print("Loading fine-tuned TinyLlama model...")
bnb_config = BitsAndBytesConfig(load_in_8bit=True)
base_model = AutoModelForCausalLM.from_pretrained(
    base_model_id,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True
)
tokenizer = AutoTokenizer.from_pretrained(base_model_id)
tokenizer.pad_token = tokenizer.eos_token
model = PeftModel.from_pretrained(base_model, adapter_path)
print("✅ Model loaded successfully. Starting server...")

# --- FastAPI App and Pydantic Models ---
app = FastAPI(title="Local Walmart Savvy Server")

class TasteProfile(BaseModel):
    household_size: int = 2
    dietary_restrictions: List[str] = []
    health_goals: List[str] = []

class RecommendRequest(BaseModel):
    user_id: int
    query_text: str

class PantryItemCreate(BaseModel):
    item_name: str
    expiry_date: Optional[date] = None


# --- API Endpoints ---
@app.get("/smart-cart/{user_id}/{recipe_id}", tags=["Shopping List"])
def get_smart_cart(user_id: int, recipe_id: int):
    """
    Compares recipe ingredients with the user's pantry and returns only the missing items.
    """
    print(f"Generating Smart Cart for user {user_id} and recipe {recipe_id}")
    
    # 1. Get the user's current pantry items (as a simple list of names)
    user_pantry_items = {item['item_name'].lower() for item in pantry_db.get(str(user_id), [])}
    print(f"User pantry contains: {user_pantry_items}")

    # 2. Get the recipe's ingredients from Spoonacular
    url = f"https://api.spoonacular.com/recipes/{recipe_id}/information"
    params = {"apiKey": SPOONACULAR_API_KEY}
    try:
        with httpx.Client() as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            recipe_data = response.json()
            recipe_ingredients = {ingredient['name'].lower() for ingredient in recipe_data.get("extendedIngredients", [])}
            print(f"Recipe needs: {recipe_ingredients}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not fetch recipe ingredients: {e}")

    # 3. Find the ingredients that are missing from the pantry
    missing_ingredients = [name.capitalize() for name in recipe_ingredients if name not in user_pantry_items]
    print(f"Missing ingredients: {missing_ingredients}")
    
    # 4. Return the list of missing ingredients
    return {"missing_ingredients": missing_ingredients}



@app.get("/recipe/{recipe_id}", tags=["Recipes"])
def get_recipe_details(recipe_id: int):
    """
    Fetches detailed information for a single recipe from Spoonacular.
    """
    print(f"Fetching details for recipe ID: {recipe_id}")
    url = f"https://api.spoonacular.com/recipes/{recipe_id}/information"
    params = {"apiKey": SPOONACULAR_API_KEY}

    with httpx.Client() as client:
        try:
            response = client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch recipe details: {e}")    


@app.get("/pantry/{user_id}", tags=["Pantry"])
def get_pantry(user_id: int):
    return pantry_db.get(str(user_id), [])

@app.post("/pantry/{user_id}", status_code=201, tags=["Pantry"])
def add_pantry_item(user_id: int, item: PantryItemCreate):
    global next_item_id
    new_item = {"id": next_item_id, "item_name": item.item_name, "expiry_date": str(item.expiry_date) if item.expiry_date else None, "user_id": user_id}
    if str(user_id) not in pantry_db:
        pantry_db[str(user_id)] = []
    pantry_db[str(user_id)].append(new_item)
    next_item_id += 1
    print(f"✅ Item Added: {new_item}. Current pantry: {pantry_db[str(user_id)]}")
    return new_item

@app.delete("/pantry/item/{item_id}", tags=["Pantry"])
def delete_pantry_item_from_db(item_id: int):
    if '1' in pantry_db:
        initial_len = len(pantry_db['1'])
        pantry_db['1'] = [item for item in pantry_db['1'] if item['id'] != item_id]
        if len(pantry_db['1']) < initial_len:
            print(f"✅ Item Deleted: ID {item_id}. Current pantry: {pantry_db['1']}")
            return {"ok": True}
    raise HTTPException(status_code=404, detail="Item not found")

@app.patch("/users/{user_id}/profile", tags=["User Profile"])
def update_user_taste_profile(user_id: int, profile: TasteProfile):
    if str(user_id) not in profile_db:
        raise HTTPException(status_code=404, detail="User not found")
    profile_db[str(user_id)] = profile.dict()
    print(f"✅ Profile Updated for user {user_id}: {profile_db[str(user_id)]}")
    return profile_db[str(user_id)]

@app.post("/shopping-list/{user_id}/{recipe_id}", tags=["Shopping List"])
def add_missing_to_shopping_list(user_id: int, recipe_id: int):
    user_pantry_items = {item['item_name'].lower() for item in pantry_db.get(str(user_id), [])}
    url = f"https://api.spoonacular.com/recipes/{recipe_id}/information"
    params = {"apiKey": SPOONACULAR_API_KEY}
    with httpx.Client() as client:
        response = client.get(url, params=params)
        recipe_data = response.json()
    recipe_ingredients = recipe_data.get("extendedIngredients", [])
    missing_ingredients = []
    for ingredient in recipe_ingredients:
        name = ingredient.get("name", "").lower()
        if name and name not in user_pantry_items:
            item_to_add = {"name": ingredient.get("original")}
            if name in substitution_map:
                item_to_add["substitution"] = substitution_map[name]
            missing_ingredients.append(item_to_add)
    shopping_list_db.setdefault(str(user_id), []).extend(missing_ingredients)
    print(f"✅ Added {len(missing_ingredients)} items to shopping list for user {user_id}")
    return {"added_items": missing_ingredients}

@app.get("/shopping-list/{user_id}", tags=["Shopping List"])
def get_shopping_list(user_id: int):
    return shopping_list_db.get(str(user_id), [])

@app.post("/recommend", tags=["Recommendations"])
def get_recommendations(request: RecommendRequest):
    print(f"\n--- New Request ---")
    print(f"Received query: '{request.query_text}'")
    decision_log = []
    
    # --- AI Parsing and User Data Setup ---
    # ... (This initial part for AI parsing, pantry, and profile data remains the same) ...
    structured_query = {}
    ai_did_succeed = False
    try:
        system_prompt = "You are an expert at parsing user queries..."
        prompt = f"<|system|>\n{system_prompt}</s>\n<|user|>\nParse the query: '{request.query_text}'</s>\n<|assistant|>\n" + "{"
        inputs = tokenizer(prompt, return_tensors="pt", return_attention_mask=False).to(model.device)
        outputs = model.generate(**inputs, max_new_tokens=200, eos_token_id=tokenizer.eos_token_id)
        raw_output = tokenizer.batch_decode(outputs)[0]
        json_part = "{" + raw_output.split("<|assistant|>")[1].replace("{", "", 1).replace("</s>", "").strip()
        structured_query = repair_json(json_part)
        if "keywords" in structured_query:
            ai_did_succeed = True
            decision_log.append(f"✅ AI parsing successful.")
        else:
            raise ValueError("AI output missing 'keywords' key.")    
    except Exception as e:
        decision_log.append(f"❌ AI validation failed. Using fallback logic. (Error: {e})")
        pass # Fail silently and proceed to fallbacks

    pantry_ingredients = ", ".join([item['item_name'] for item in pantry_db.get(str(request.user_id), [])])
    user_diet = ",".join(profile_db.get(str(request.user_id), {}).get("dietary_restrictions", []))
    
    # --- The Definitive 3-Step Search Logic ---
    # --- Final Log and API Call ---
    print("\n--- Recommendation Decision Log ---")
    for log_item in decision_log:
        print(f"[INFO] {log_item}")
    print("-----------------------------------")
    # decision_log.append(f"▶ Base query is user's text: '{final_query_text}'")
    with httpx.Client() as client:
        base_params = {"apiKey": SPOONACULAR_API_KEY, "number": 10}
        if user_diet:
            # decision_log.append(f"▶ Filtering by profile diet: '{user_diet}'")
            base_params["diet"] = user_diet

        # --- Attempt 1: The "AI-Powered Mix" (AI Keywords + User Text + Pantry + Diet) ---
        if ai_did_succeed:
            # decision_log.append(f"▶ Refining query with AI keywords: '{ai_keywords}'")
            print("--- Attempt 1: Searching with AI + Text + Pantry + Diet ---")
            params1 = base_params.copy()
            params1["query"] = f"{request.query_text}, {', '.join(structured_query.get('keywords',[]))}"
            if pantry_ingredients:
                # decision_log.append(f"▶ Boosting results with pantry items: '{pantry_ingredients}'")
                params1["includeIngredients"] = pantry_ingredients
                params1["ranking"] = 2
            
                # decision_log.append("▶ No pantry items to influence results.")    
            try:
                response = client.get("https://api.spoonacular.com/recipes/complexSearch", params={k: v for k, v in params1.items() if v})
                response.raise_for_status()
                recipes = response.json().get("results", [])
                if recipes: return {"recipes": recipes}
                print("⚠️ Found 0 recipes, trying next step.")
            except Exception as e:
                print(f"⚠️ Attempt 1 failed: {e}")

        # --- Attempt 2: The "Standard Mix" (User Text + Pantry + Diet) ---
        # This is the main fallback, always respecting the user's text and pantry.
        print("\n--- Attempt 2: Searching with Text + Pantry + Diet ---")
        params2 = base_params.copy()
        params2["query"] = request.query_text
        if pantry_ingredients:
            params2["includeIngredients"] = pantry_ingredients
            params2["ranking"] = 2
        # else:
        #     decision_log.append("▶ No pantry items to influence results.")    
        try:
            response = client.get("https://api.spoonacular.com/recipes/complexSearch", params={k: v for k, v in params2.items() if v})
            response.raise_for_status()
            recipes = response.json().get("results", [])
            if recipes:
                print(f"✅ Found {len(recipes)} recipes.")
                return {"recipes": recipes}
            print("⚠️ Found 0 recipes, trying final fallback.")
        except Exception as e:
            print(f"⚠️ Attempt 2 failed: {e}")

        # --- Attempt 3: The "Broadest Search" (User Text + Diet only) ---
        # This is the final safety net if the pantry items are too restrictive.
        print("\n--- Attempt 3: Final fallback. Searching by TEXT + Diet only. ---")
        params3 = base_params.copy()
        params3["query"] = request.query_text
        try:
            response = client.get("https://api.spoonacular.com/recipes/complexSearch", params={k: v for k, v in params3.items() if v})
            response.raise_for_status()
            recipes = response.json().get("results", [])
            print(f"✅ Found {len(recipes)} recipes.")
            return {"recipes": recipes}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to process recipes from Spoonacular: {e}")

# --- Run the Server ---
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)