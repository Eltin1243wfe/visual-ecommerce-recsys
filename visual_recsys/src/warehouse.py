import sqlite3
import json
import os

DB_PATH = 'visual_recsys/data/processed/warehouse.db'

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_warehouse():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dim_products (
            product_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            image_path TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fact_embeddings (
            embedding_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            vector_json TEXT NOT NULL,
            FOREIGN KEY (product_id) REFERENCES dim_products (product_id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Data Warehouse initialized with dim_products and fact_embeddings tables.")

def load_dimension_data(products_list):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.executemany('''
        INSERT OR REPLACE INTO dim_products (product_id, name, category, price, image_path)
        VALUES (?, ?, ?, ?, ?)
    ''', products_list)
    
    conn.commit()
    conn.close()

def load_fact_embedding(product_id, vector):
    conn = get_connection()
    cursor = conn.cursor()
    vector_string = json.dumps(vector.tolist() if hasattr(vector, 'tolist') else vector)
    
    cursor.execute('''
        INSERT OR REPLACE INTO fact_embeddings (product_id, vector_json)
        VALUES (?, ?)
    ''', (product_id, vector_string))
    
    conn.commit()
    conn.close()

def fetch_all_products():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT p.product_id, p.name, p.category, p.price, p.image_path, f.vector_json
        FROM dim_products p
        JOIN fact_embeddings f ON p.product_id = f.product_id
    ''')
    
    rows = cursor.fetchall()
    conn.close()
    return rows