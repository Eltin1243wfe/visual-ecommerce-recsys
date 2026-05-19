import json
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from visual_recsys.src.warehouse import fetch_all_products
from visual_recsys.src.engine import get_top_k_recommendations

app = FastAPI(title="AuraMarket Core RecSys Engine")

# Crucial: Allows your modern frontend to talk to your Python server securely
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global memory cache to keep database reads instant
db_rows = fetch_all_products()
PRODUCTS = {}
CLUSTER_POOLS = {}

for row in db_rows:
    p_id, title, brand, colour, price, rating, url, vec_json, cluster = row
    PRODUCTS[p_id] = {
        "id": p_id, "title": title, "brand": brand, "colour": colour,
        "price": price, "rating": rating, "url": url, "vector": np.array(json.loads(vec_json))
    }
    if cluster not in CLUSTER_POOLS:
        CLUSTER_POOLS[cluster] = []
    CLUSTER_POOLS[cluster].append(p_id)

@app.get("/api/products")
def get_products():
    out = []
    for pid, p in PRODUCTS.items():
        out.append({
            "id": pid, "title": p["title"], "brand": p["brand"],
            "colour": p["colour"], "price": p["price"], "rating": p["rating"], "url": p["url"]
        })
    return out

@app.get("/api/recommendations/{product_id}")
def get_recs(product_id: int):
    if product_id not in PRODUCTS:
        raise HTTPException(status_code=404, detail="Product variant not found")
        
    target_item = PRODUCTS[product_id]
    target_cluster = None
    
    for c, p_ids in CLUSTER_POOLS.items():
        if product_id in p_ids:
            target_cluster = c
            break
            
    if target_cluster is None:
        return []
        
    pool_ids = [pid for pid in CLUSTER_POOLS[target_cluster] if pid != product_id]
    pool_vectors = [PRODUCTS[pid]["vector"] for pid in pool_ids]
    
    recommendations = get_top_k_recommendations(target_item["vector"], pool_vectors, pool_ids, k=4)
    
    out = []
    for rec_id, score in recommendations:
        r = PRODUCTS[rec_id]
        out.append({
            "id": rec_id, "title": r["title"], "brand": r["brand"],
            "price": r["price"], "url": r["url"], "confidence": float(score)
        })
    return out