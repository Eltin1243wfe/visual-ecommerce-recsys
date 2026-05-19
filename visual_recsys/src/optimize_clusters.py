import json
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from visual_recsys.src.warehouse import fetch_all_products

def find_optimal_clusters():
    print("Fetching high-dimensional feature vectors from warehouse...")
    db_rows = fetch_all_products()
    
    if not db_rows:
        print("Warehouse is empty! Run your ETL pipeline first.")
        return
        
    raw_vectors = []
    for row in db_rows:
        vec_json = row[7]
        raw_vectors.append(json.loads(vec_json))
        
    matrix = np.array(raw_vectors)
    print(f"Loaded matrix shape: {matrix.shape}")
    
    # Take a representative sample to keep the validation phase extremely fast
    if len(matrix) > 3000:
        indices = np.random.choice(len(matrix), 3000, replace=False)
        sample_matrix = matrix[indices]
    else:
        sample_matrix = matrix

    cluster_candidates = [5, 10, 15, 20, 25]
    best_k = 5
    best_score = -1
    
    print("\nEvaluating cluster configurations...")
    print(f"{'Clusters (K)':<15}{'Silhouette Score':<20}")
    print("-" * 35)
    
    for k in cluster_candidates:
        kmeans = KMeans(n_clusters=k, init='k-means++', n_init=10, random_state=42)
        labels = kmeans.fit_predict(sample_matrix)
        
        score = silhouette_score(sample_matrix, labels)
        print(f"{k:<15}{score:.4f}")
        
        if score > best_score:
            best_score = score
            best_k = k
            
    print("-" * 35)
    print(f"Mathematical Choice: K = {best_k} yields the cleanest style groupings.\n")
    return best_k

if __name__ == "__main__":
    find_optimal_clusters()