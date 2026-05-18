import csv
import os
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
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
    image_tasks = []
    
    print("Parsing full catalog from source dataset...")
    with open(csv_path, mode='r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        reader.fieldnames = [name.strip() for name in reader.fieldnames] if reader.fieldnames else []
        
        for row in reader:
            try:
                prod_id_str = row.get('p_id')
                if not prod_id_str:
                    continue
                    
                prod_id = int(float(prod_id_str))
                price = float(row.get('price', '0') or 0.0)
                rating = float(row.get('avg_rating', '0') or 0.0)
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
                image_tasks.append((prod_id, url))
            except Exception:
                continue

    total_records = len(dim_records)
    print(f"Staging dimensions completed. Found {total_records} clean item rows.")
    
    print("Bulk loading metadata dimensions into database...")
    load_dimension_data(dim_records)
    
    print(f"Extracting high-dimensional feature vectors using Multi-threading...")
    raw_vectors = []
    valid_ids = []
    
    def process_single_item(task):
        p_id, url = task
        try:
            vec = engine.extract_vector(url)
            if vec is not None and vec.any():
                return p_id, vec
        except Exception:
            pass
        return None

    # Max workers balances network bandwidth and CPU cores
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(process_single_item, task): task for task in image_tasks}
        
        completed_count = 0
        for future in as_completed(futures):
            completed_count += 1
            result = future.result()
            if result:
                p_id, vec = result
                raw_vectors.append(vec)
                valid_ids.append(p_id)
            
            if completed_count % 10 == 0 or completed_count == total_records:
                print(f"Progress: [{completed_count}/{total_records}] items analyzed. Vectorized: {len(raw_vectors)}", end="\r")
                
    print(f"\nExtraction complete. Successfully vectorized {len(raw_vectors)} items.")
    
    if len(raw_vectors) == 0:
        print("Error: Failed to extract features from any image URLs.")
        return
        
    print("\nExecuting Data Mining Cluster Pass...")
    cluster_assignments = cluster_vectors(raw_vectors, n_clusters=12)
    
    print("Writing analytical fact transformations to database...")
    for idx, p_id in enumerate(valid_ids):
        vec_json = json.dumps(raw_vectors[idx].tolist())
        load_fact_embedding(p_id, vec_json, int(cluster_assignments[idx]))
        
    print("ETL execution successfully completed! Production database is packed and ready.")

if __name__ == '__main__':
    run_etl()