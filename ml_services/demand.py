from sklearn.linear_model import LinearRegression
import numpy as np

def predict_demand(data):
    """
    data = [
        {"day": 1, "orders": 10},
        {"day": 2, "orders": 15}
    ]
    """

    if not data or len(data) < 2:
        return {
            "predicted_orders": 0.0,
            "message": "Not enough data for prediction"
        }

    X = np.array([[d["day"]] for d in data], dtype=float)
    y = np.array([d["orders"] for d in data], dtype=float)

    model = LinearRegression()
    model.fit(X, y)

    next_day = np.array([[len(data) + 1]], dtype=float)

    prediction = model.predict(next_day)[0]

    # safety clamp (IMPORTANT)
    prediction = max(0, prediction)

    return {
        "predicted_orders": float(round(prediction, 2))
    }