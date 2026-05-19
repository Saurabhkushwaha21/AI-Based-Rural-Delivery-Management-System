from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import numpy as np

def cluster_locations(locations, k=2):

    if not locations:
        return {}

    coords = np.array([
        [float(loc["lat"]), float(loc["lon"])]
        for loc in locations
    ])

    # scale coordinates (IMPORTANT for stability)
    scaler = StandardScaler()
    coords_scaled = scaler.fit_transform(coords)

    k = min(k, len(coords_scaled))

    kmeans = KMeans(n_clusters=k, random_state=0, n_init=10)
    labels = kmeans.fit_predict(coords_scaled)

    result = {}

    for i, label in enumerate(labels):

        label = int(label)

        if label not in result:
            result[label] = []

        result[label].append({
            "lat": float(coords[i][0]),
            "lon": float(coords[i][1]),
            "order_id": int(locations[i].get("order_id", i))
        })

    return result