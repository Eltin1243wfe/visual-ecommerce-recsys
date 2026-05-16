import streamlit as st
import sqlite3
import json
import numpy as np
import os
import sys
from PIL import Image


# Dynamic Path Correction: Force Python to see the root directory
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Now these imports will resolve flawlessly regardless of where Streamlit launches from
from visual_recsys.src.warehouse import fetch_all_products
from visual_recsys.src.engine import calculate_similarity_matrix, get_top_k_recommendations

st.set_page_config(page_title="Visual E-Commerce RecSys", layout="wide")

st.title("🛍️ Visual E-Commerce Recommendation Engine")
st.markdown("---")

@st.cache_data
def load_data_from_warehouse():
    raw_data = fetch_all_products()
    if not raw_data:
        return [], None
        
    products = []
    vectors = []
    
    for row in raw_data:
        prod_id, name, category, price, img_path, vector_json = row
        products.append({
            "id": prod_id,
            "name": name,
            "category": category,
            "price": price,
            "image_path": img_path
        })
        vectors.append(json.loads(vector_json))
        
    similarity_matrix = calculate_similarity_matrix(vectors)
    return products, similarity_matrix

products, similarity_matrix = load_data_from_warehouse()

if not products:
    st.error("No data found in the Warehouse. Please verify that your ETL script ran successfully.")
else:
    product_options = {f"{p['id']} - {p['name']} ({p['category']})": i for i, p in enumerate(products)}
    
    st.sidebar.header("Target Inventory Explorer")
    selected_label = st.sidebar.selectbox("Choose a product to analyze:", list(product_options.keys()))
    target_idx = product_options[selected_label]
    
    target_prod = products[target_idx]
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Selected Item Focus")
        if os.path.exists(target_prod['image_path']):
            img = Image.open(target_prod['image_path'])
            st.image(img, use_column_width=True)
        else:
            st.warning(f"Image missing at {target_prod['image_path']}")
            
    with col2:
        st.markdown(f"### **Product Name:** {target_prod['name']}")
        st.markdown(f"**Category Cluster:** {target_prod['category']}")
        st.markdown(f"**Warehouse Valuation Price:** ${target_prod['price']:.2f}")
        st.markdown(f"**System Database ID:** `PROD_REF_{target_prod['id']}`")
        
    st.markdown("---")
    st.subheader("🤖 Visual Mining Recommendations (Top 3 Nearest Neighbors)")
    
    recs = get_top_k_recommendations(similarity_matrix, target_idx, k=3)
    
    rec_cols = st.columns(3)
    for rank, (rec_idx, score) in enumerate(recs):
        rec_prod = products[rec_idx]
        with rec_cols[rank]:
            st.markdown(f"#### Rank {rank+1}: {rec_prod['name']}")
            st.caption(f"Visual Match Confidence: **{score*100:.2f}%**")
            
            if os.path.exists(rec_prod['image_path']):
                rec_img = Image.open(rec_prod['image_path'])
                st.image(rec_img, use_column_width=True)
                
            st.write(f"Category: {rec_prod['category']}")
            st.write(f"Price: ${rec_prod['price']:.2f}")