import streamlit as st
import json
import numpy as np
from visual_recsys.src.warehouse import fetch_all_products
from visual_recsys.src.engine import get_top_k_recommendations

def render_dashboard():
    st.set_page_config(page_title="Enterprise Visual RecSys", layout="wide")
    st.title("🛍️ Enterprise Visual Recommendation Dashboard")
    st.markdown("---")

    db_rows = fetch_all_products()

    if not db_rows:
        st.warning("Data warehouse is empty. Please check your ETL process.")
        return

    products = {}
    cluster_pools = {}
    
    for row in db_rows:
        p_id, title, brand, colour, price, rating, url, vec_json, cluster = row
        vec = np.array(json.loads(vec_json))
        
        products[p_id] = {
            "title": title, "brand": brand, "colour": colour,
            "price": price, "rating": rating, "url": url, "vector": vec
        }
        
        if cluster not in cluster_pools:
            cluster_pools[cluster] = []
        cluster_pools[cluster].append(p_id)
        
    st.sidebar.header("Product Discovery Inventory")
    product_options = {f"{p['brand']} - {p['title']} ({p_id})": p_id for p_id, p in products.items()}
    selected_option = st.sidebar.selectbox("Select a Product to view Recommendations:", list(product_options.keys()))
    
    if selected_option:
        target_id = product_options[selected_option]
        target_item = products[target_id]
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(target_item["url"], use_container_width=True)
        with col2:
            st.subheader(target_item["title"])
            st.write(f"**Brand:** {target_item['brand']} | **Color:** {target_item['colour']}")
            st.write(f"**Price:** ₹{target_item['price']} | **Rating:** ⭐ {target_item['rating']}")
            
        st.markdown("---")
        st.subheader("🤖 Style Cluster-Optimized Recommendations")
        
        target_cluster = None
        for c, p_ids in cluster_pools.items():
            if target_id in p_ids:
                target_cluster = c
                break
                
        if target_cluster is not None:
            pool_ids = [pid for pid in cluster_pools[target_cluster] if pid != target_id]
            pool_vectors = [products[pid]["vector"] for pid in pool_ids]
            
            recommendations = get_top_k_recommendations(target_item["vector"], pool_vectors, pool_ids, k=4)
            
            if recommendations:
                cols = st.columns(len(recommendations))
                for idx, (rec_id, score) in enumerate(recommendations):
                    rec_item = products[rec_id]
                    with cols[idx]:
                        st.image(rec_item["url"], use_container_width=True)
                        st.caption(f"**{rec_item['brand']}**")
                        st.write(f"Confidence: {score*100:.1f}%")
                        st.write(f"Price: ₹{rec_item['price']}")
            else:
                st.info("No matching stylistic cluster pairings found in this data slice.")