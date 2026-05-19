import streamlit as st
import json
import numpy as np
from visual_recsys.src.warehouse import fetch_all_products
from visual_recsys.src.engine import get_top_k_recommendations

def render_dashboard():
    st.set_page_config(
        page_title="Minimalist Premium Storefront",
        page_icon="🛍️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            background-color: #FAFAFA !important;
            color: #18181B !important;
        }
        
        .main-container {
            padding: 32px;
        }
        
        .store-brand {
            font-size: 0.85rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.15em;
            color: #71717A;
            margin-bottom: 4px;
        }
        
        .main-header {
            font-size: 2.5rem;
            font-weight: 700;
            color: #18181B;
            letter-spacing: -0.02em;
            margin-bottom: 24px;
        }
        
        .product-showcase-card {
            background-color: #FFFFFF;
            border: 1px solid #E4E4E7;
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0px 1px 2px -1px rgba(0,0,0,0.08), 0px 2px 4px 0px rgba(0,0,0,0.04);
        }
        
        .product-card {
            background-color: #FFFFFF;
            border: 1px solid #E4E4E7;
            border-radius: 16px;
            padding: 16px;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0px 1px 2px -1px rgba(0,0,0,0.08), 0px 2px 4px 0px rgba(0,0,0,0.04);
            height: 100%;
        }
        
        .product-card:hover {
            transform: translateY(-4px);
            border-color: #A1A1AA;
            box-shadow: 0px 0px 0px 1px rgba(0,0,0,0.08), 0px 1px 2px -1px rgba(0,0,0,0.08), 0px 2px 8px 0px rgba(0,0,0,0.1);
        }
        
        .price-display {
            font-size: 1.5rem;
            font-weight: 700;
            color: #18181B;
            margin: 16px 0px;
        }
        
        .rec-price {
            font-weight: 700;
            color: #18181B;
            font-size: 1.1rem;
            margin-top: 4px;
        }
        
        .brand-pill {
            display: inline-block;
            background: #F4F4F5;
            color: #52525B;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 8px;
        }
        
        .section-divider {
            font-size: 1.5rem;
            font-weight: 700;
            margin-top: 48px;
            margin-bottom: 24px;
            color: #18181B;
            letter-spacing: -0.01em;
        }
        
        .match-badge {
            font-size: 0.8rem;
            color: #059669;
            font-weight: 600;
            background-color: #ECFDF5;
            padding: 2px 8px;
            border-radius: 4px;
            display: inline-block;
            margin-top: 8px;
        }
        
        div[data-testid="stSidebar"] {
            background-color: #FFFFFF !important;
            border-right: 1px solid #E4E4E7;
        }
        
        /* Premium button injection */
        button[kind="primary"] {
            background-color: #18181B !important;
            color: #FFFFFF !important;
            border: 1px solid #18181B !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            padding: 12px 24px !important;
            transition: background-color 0.2s ease !important;
        }
        
        button[kind="primary"]:hover {
            background-color: #27272A !important;
            border-color: #27272A !important;
        }
        </style>
    """, unsafe_allow_html=True)

    db_rows = fetch_all_products()

    if not db_rows:
        st.warning("Data warehouse is empty. Please verify your ETL pipeline.")
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

    st.sidebar.markdown("### 🔍 Collection Filter")
    brand_list = sorted(list(set([p["brand"] for p in products.values()])))
    selected_brand = st.sidebar.selectbox("Brand Selection:", ["All Brands"] + brand_list)
    
    if selected_brand != "All Brands":
        filtered_products = {pid: p for pid, p in products.items() if p["brand"] == selected_brand}
    else:
        filtered_products = products

    product_options = {f"{p['brand']} — {p['title'][:40]}...": pid for pid, p in filtered_products.items()}
    
    if not product_options:
        st.sidebar.info("No styles match this combination.")
        return
        
    selected_option = st.sidebar.selectbox("Active Display Product:", list(product_options.keys()))
    
    if selected_option:
        target_id = product_options[selected_option]
        target_item = products[target_id]
        
        st.markdown('<div class="store-brand">Studio Collection</div>', unsafe_allow_html=True)
        st.markdown('<div class="main-header">Curated Lookbook Storefront</div>', unsafe_allow_html=True)
        
        detail_col1, detail_col2 = st.columns([1.1, 1])
        
        with detail_col1:
            st.image(target_item["url"], use_container_width=True)
            
        with detail_col2:
            st.markdown('<div class="product-showcase-card">', unsafe_allow_html=True)
            st.markdown(f'<span class="brand-pill">{target_item["brand"]}</span>', unsafe_allow_html=True)
            st.markdown(f'<h1 style="font-size: 2rem; font-weight: 700; line-height: 1.2; margin: 8px 0px; color: #18181B;">{target_item["title"]}</h1>', unsafe_allow_html=True)
            
            rating_val = target_item["rating"]
            stars = "★" * int(round(rating_val)) + "☆" * (5 - int(round(rating_val)))
            st.markdown(f'<span style="color: #18181B; font-size: 1rem;">{stars}</span> <span style="color: #71717A; font-size: 0.85rem;">({rating_val:.2f})</span>', unsafe_allow_html=True)
            
            st.markdown(f'<div class="price-display">₹{target_item["price"]:,}</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="color: #52525B; font-size: 0.95rem; margin-bottom: 24px;"><b>Color Palette:</b> {target_item["colour"]}</div>', unsafe_allow_html=True)
            
            st.button("Add to Shopping Bag", use_container_width=True, type="primary")
            
            st.markdown('<div style="margin-top: 24px; border-top: 1px solid #E4E4E7; padding-top: 24px; font-size: 0.9rem; color: #71717A; line-height: 1.6;">'
                        '✨ <b>Premium Craftsmanship</b><br>Finely curated silhouette mapped directly onto our visual feature arrays. '
                        'Includes carbon-neutral courier logistics tracking directly to your door.</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-divider">Complete the Look</div>', unsafe_allow_html=True)
        
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
                rec_cols = st.columns(4)
                for idx, (rec_id, score) in enumerate(recommendations):
                    rec_item = products[rec_id]
                    with rec_cols[idx]:
                        st.markdown('<div class="product-card">', unsafe_allow_html=True)
                        st.image(rec_item["url"], use_container_width=True)
                        st.markdown(f'<span class="brand-pill" style="margin-top: 12px; margin-bottom: 4px;">{rec_item["brand"]}</span>', unsafe_allow_html=True)
                        st.markdown(f'<div style="font-weight: 600; font-size: 0.95rem; height: 40px; overflow: hidden; line-height: 1.3; color: #18181B;">{rec_item["title"][:40]}...</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="rec-price">₹{rec_item["price"]:,}</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="match-badge">Similarity: {score*100:.1f}%</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)