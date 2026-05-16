import csv
import os
from visual_recsys.src.warehouse import init_warehouse, load_dimension_data, load_fact_embedding
from visual_recsys.src.engine import FeatureExtractionEngine

def run_etl():
    # Direct path to our freshly generated csv file
    csv_path = 'visual_recsys/data/raw/products.csv'
    
    if not os.path.exists(csv_path):
        print(f"Error: Raw data file not found at {csv_path}.")
        return

    print(f"Found dataset at: {csv_path}")
    print("Initializing Data Warehouse structures...")
    init_warehouse()
    
    print("Loading Machine Learning Feature Extraction Engine (ResNet-50)...")
    engine = FeatureExtractionEngine()
    
    products_for_dim = []
    raw_records = []
    
    with open(csv_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            raw_records.append(row)
            products_for_dim.append((
                int(row['product_id']),
                row['name'],
                row['category'],
                float(row['price']),
                row['image_path']
            ))
            
    print(f"Extracting metadata completed. Found {len(products_for_dim)} products.")
    
    print("Loading dimension data into warehouse...")
    load_dimension_data(products_for_dim)
    
    print("Starting visual data mining and transformation phase...")
    for record in raw_records:
        prod_id = int(record['product_id'])
        img_path = record['image_path']
        
        print(f"Processing product ID {prod_id}: {record['name']}...")
        vector = engine.extract_vector(img_path)
        
        load_fact_embedding(prod_id, vector)
        
    print("ETL execution successfully completed! All tables updated.")

if __name__ == '__main__':
    run_etl()