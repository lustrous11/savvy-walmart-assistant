from fastapi import FastAPI

app = FastAPI(title="Community Service")

# Mock database of interactions
interactions_db = []

@app.post("/interactions")
def create_interaction(interaction: dict):
    # interaction = {"user_id": 1, "recipe_id": 716429, "interaction_type": "save"}
    interactions_db.append(interaction)
    return {"message": "Interaction recorded"}

@app.get("/recipes/trending")
def get_trending_recipes(region: str = "Midwest"):
    # In a real system, you'd query a DB and perform calculations.
    # We'll return a mock list of popular recipe IDs.
    print(f"Calculating trending recipes for region: {region}")
    return {"trending_recipe_ids": [716429, 715497]} # Example recipe IDs