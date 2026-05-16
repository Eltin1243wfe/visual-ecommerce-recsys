import sqlite3
import os

DB_PATH = 'visual_recsys/data/warehouse.db'

def init_warehouse():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dim_products (
            product_id INTEGER PRIMARY KEY,
            title TEXT,
            brand TEXT,
            colour TEXT,
            price REAL,
            rating REAL,
            image_url TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fact_embeddings (
            product_id INTEGER PRIMARY KEY,
            embedding_json TEXT,
            style_cluster INTEGER,
            FOREIGN KEY (product_id) REFERENCES dim_products (product_id)
        )
    ''')
    
    conn.commit()
    conn.close()

def load_dimension_data(products_list):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.executemany('''
        INSERT OR REPLACE INTO dim_products 
        (product_id, title, brand, colour, price, rating, image_url)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', products_list)
    conn.commit()
    conn.close()

def load_fact_embedding(product_id, embedding_json, cluster_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO fact_embeddings (product_id, embedding_json, style_cluster)
        VALUES (?, ?, ?)
    ''', (product_id, embedding_json, cluster_id))
    conn.commit()
    conn.close()

def fetch_all_products():
    if not os.path.exists(DB_PATH):
        return []
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.product_id, p.title, p.brand, p.colour, p.price, p.rating, p.image_url, f.embedding_json, f.style_cluster
        FROM dim_products p
        JOIN fact_embeddings f ON p.product_id = f.product_id
    ''')
    rows = cursor.fetchall()
    conn.close()
    return rows