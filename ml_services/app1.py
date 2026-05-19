from fastapi import FastAPI

app = FastAPI()

# ================= SIMPLE CLUSTERING =================
def cluster_locations(locations, k=2):
    clusters = {}

    for i, loc in enumerate(locations):
        cluster_id = str(i % k)

        if cluster_id not in clusters:
            clusters[cluster_id] = []

        clusters[cluster_id].append(loc)

    return clusters


# ================= SIMPLE DEMAND PREDICTION =================
def predict_demand(history):
    total = sum(item["orders"] for item in history)
    avg = total / len(history) if history else 0

    return {
        "total_orders": total,
        "average_per_day": avg,
        "prediction": "high" if avg > 5 else "low"
    }


# ================= ROUTES =================
@app.get("/")
def home():
    return {"message": "ML Service Running"}

@app.post("/cluster")
def cluster(data: dict):
    clusters = cluster_locations(data["locations"], data.get("k", 2))

    return {"clusters": clusters}

@app.post("/predict")
def predict(data: dict):
    result = predict_demand(data["history"])
    return result