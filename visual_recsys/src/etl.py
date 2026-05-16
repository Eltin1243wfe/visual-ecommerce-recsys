import csv
import os
import json
from visual_recsys.src.warehouse import init_warehouse, load_dimension_data, load_fact_embedding
from visual_recsys.src.engine import FeatureExtractionEngine, cluster_vectors

def run_etl():
    csv_path = 'visual_recsys/data/raw/Fashion Dataset.csv'
    
    if not os.path.exists(csv_path):
        print(f"File not found at: {csv_path}")
        return

    print("Initializing Data Warehouse structure...")
    init_warehouse()
    
    print("Spawning Production ML Extraction Engine...")
    engine = FeatureExtractionEngine()
    
    dim_records = []
    image_urls = []
    product_ids = []
    
    max_records = 500
    
    with open(csv_path, mode='r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        
        reader.fieldnames = [name.strip() for name in reader.fieldnames] if reader.fieldnames else []
        print(f"Detected CSV columns: {reader.fieldnames}")
        
        for i, row in enumerate(reader):
            if len(dim_records) >= max_records:
                break
            try:
                prod_id_str = row.get('p_id')
                if not prod_id_str:
                    continue
                    
                prod_id = int(float(prod_id_str))
                
                price_str = row.get('price', '0')
                price = float(price_str) if price_str else 0.0
                
                rating_str = row.get('avg_rating', '0')
                rating = float(rating_str) if rating_str else 0.0
                
                url = row.get('img')
                if not url:
                    continue
                    
                dim_records.append((
                    prod_id,
                    row.get('name', 'Unknown'),
                    row.get('brand', 'Unknown'),
                    row.get('colour', 'Unknown'),
                    price,
                    rating,
                    url
                ))
                image_urls.append(url)
                product_ids.append(prod_id)
            except Exception as e:
                continue

    print(f"Staging dimensions completed. Found {len(dim_records)} clean item rows.")
    
    if len(dim_records) == 0:
        print("Error: Could not parse any rows from the CSV file. Please double check file formatting.")
        return
        
    load_dimension_data(dim_records)
    
    print("Extracting high-dimensional feature vectors...")
    raw_vectors = []
    valid_ids = []
    valid_urls = []
    
    for idx, url in enumerate(image_urls):
        p_id = product_ids[idx]
        print(f"Mining features [{idx+1}/{len(image_urls)}] ID: {p_id}...")
        vec = engine.extract_vector(url)
        
        if vec.any():
            raw_vectors.append(vec)
            valid_ids.append(p_id)
            valid_urls.append(url)
            
    if len(raw_vectors) == 0:
        print("Error: Failed to extract features from any image URLs. Check network availability.")
        return
        
    print("\nExecuting Data Mining Cluster Pass...")
    cluster_assignments = cluster_vectors(raw_vectors, n_clusters=5)
    
    print("Writing analytical fact transformations to database...")
    for idx, p_id in enumerate(valid_ids):
        vec_json = json.dumps(raw_vectors[idx].tolist())
        load_fact_embedding(p_id, vec_json, cluster_assignments[idx])
        
    print("ETL execution successfully completed! Production analytical warehouse is live.")

if __name__ == '__main__':
    run_etl()