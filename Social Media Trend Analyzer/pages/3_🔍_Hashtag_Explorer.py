import streamlit as st
import pandas as pd
import plotly.express as px
import joblib
import numpy as np
import os

import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from utils.ui import set_premium_ui

st.set_page_config(page_title="Hashtag Explorer | Social Trend Analyzer", page_icon="🔍", layout="wide")

set_premium_ui()

st.markdown("""
<h1>🔍 Hashtag Clustering Explorer</h1>
<p>
Discover hidden groups in trending hashtag data using our <b>AI Grouping Engine</b>. 
Each cluster represents hashtags that behave similarly in terms of reach and engagement.
</p>
""", unsafe_allow_html=True)

with st.expander("📖 How to use the Hashtag Explorer", expanded=False):
    st.markdown("""
    1. **Explore the Cluster Map** below to see how our AI grouped thousands of hashtags based on their performance.
    2. Dots that are closer together represent hashtags with similar engagement patterns.
    3. Use the filters to drill down into specific **Platforms** or **Regions**.
    4. Switch to the **Cluster Analysis** tab to compare average performance across different groups.
    """)

@st.cache_resource
def load_assets():
    try:
        hsh_path = os.path.join(BASE_DIR, 'hashtags.csv')
        try:    df = pd.read_csv(hsh_path)
        except: df = pd.read_csv(hsh_path, encoding='latin1')
        
        models_path = os.path.join(BASE_DIR, 'models', 'hashtag_clustering.pkl')
        models = joblib.load(models_path)
        return df, models
    except Exception as e:
        st.error(f"Error loading assets: {e}")
        return None, None

df, models = load_assets()

if df is None or models is None:
    st.error("Assets not found. Run `python utils/model_trainer.py` first.")
    st.stop()

# ─── Precompute Clusters ──────────────────────────────────────────────────────
numeric_cols = ['Views', 'Likes', 'Shares', 'Comments']
df_c = df.dropna(subset=numeric_cols).copy()

scaler = models['scaler']
kmeans = models['kmeans']
pca    = models['pca']

X_scaled   = scaler.transform(df_c[numeric_cols])
df_c['Cluster'] = kmeans.predict(X_scaled).astype(str)

pca_result  = pca.transform(X_scaled)
df_c['PCA1'] = pca_result[:, 0]
df_c['PCA2'] = pca_result[:, 1]

# Friendly cluster names
cluster_names = {'0': '🔥 Viral Giants', '1': '📈 Rising Stars', '2': '💬 Community Hubs', '3': '🌱 Emerging Niches'}
df_c['Cluster Label'] = df_c['Cluster'].map(cluster_names).fillna(df_c['Cluster'])

# ─── Stats Row ────────────────────────────────────────────────────────────────
st.markdown("### 📊 Dataset Overview")
s1, s2, s3, s4 = st.columns(4)
for col, label, val in zip([s1, s2, s3, s4],
    ["Total Hashtags", "Platforms", "Regions", "Clusters"],
    [len(df_c), df_c['Platform'].nunique(), df_c['Region'].nunique(), 4]):
    col.markdown(f"""
    <div class='stat-card'>
        <div class='stat-label'>{label}</div>
        <div class='stat-value'>{val:,}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Main Tabs ────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["🗺️ Cluster Map", "📊 Cluster Analysis", "📋 Raw Data"])

with tab1:
    st.markdown("#### AI Hashtag Grouping Map")
    st.markdown("<small style='color:#5a6678;'>Each dot = 1 hashtag. Colors show AI-generated similarity groups based on Views, Likes, Shares & Comments.</small>", unsafe_allow_html=True)

    # Sidebar filters inside tab
    fc1, fc2 = st.columns([1, 3])
    with fc1:
        sel_platform = st.selectbox("Filter by Platform", ["All"] + sorted(df_c['Platform'].dropna().unique().tolist()))
        sel_region   = st.selectbox("Filter by Region",   ["All"] + sorted(df_c['Region'].dropna().unique().tolist()))

    view_df = df_c.copy()
    if sel_platform != "All": view_df = view_df[view_df['Platform'] == sel_platform]
    if sel_region   != "All": view_df = view_df[view_df['Region']   == sel_region]

    with fc2:
        fig = px.scatter(
            view_df, x='PCA1', y='PCA2', color='Cluster Label',
            hover_data={'Hashtag': True, 'Platform': True, 'Views': ':,', 'Likes': ':,', 'PCA1': False, 'PCA2': False},
            title=f"AI Hashtag Clusters — {len(view_df):,} Hashtags",
            template='plotly_dark', opacity=0.75,
            color_discrete_sequence=['#fca311', '#00b4d8', '#00e676', '#e63946']
        )
        fig.update_traces(marker=dict(size=6))
        fig.update_layout(
            paper_bgcolor='rgba(14,21,32,0.9)',
            plot_bgcolor='rgba(14,21,32,0.5)',
            font_color='#ecf0f1',
            legend=dict(bgcolor='rgba(14,21,32,0.8)', bordercolor='#1e2a3e'),
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    <div class='cluster-legend'>
        <b style='color:#fca311;'>🔥 Viral Giants</b> — Extremely high views, likes and shares.<br>
        <b style='color:#00b4d8;'>📈 Rising Stars</b> — Strong growth trajectory, high engagement momentum.<br>
        <b style='color:#00e676;'>💬 Community Hubs</b> — Strong comment activity, niche but loyal audience.<br>
        <b style='color:#e63946;'>🌱 Emerging Niches</b> — Lower volume but high potential for early adopters.
    </div>""", unsafe_allow_html=True)

with tab2:
    st.markdown("#### Cluster Performance Comparison")
    agg = df_c.groupby('Cluster Label')[numeric_cols].mean().reset_index()

    c1, c2 = st.columns(2)
    with c1:
        fig2 = px.bar(agg, x='Cluster Label', y='Views',
                      color='Cluster Label',
                      color_discrete_sequence=['#fca311','#00b4d8','#00e676','#e63946'],
                      title="Average Views per Cluster")
        fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    with c2:
        fig3 = px.bar(agg, x='Cluster Label', y=['Likes','Shares','Comments'],
                      barmode='group',
                      title="Avg Likes / Shares / Comments per Cluster")
        fig3.update_layout(paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig3, use_container_width=True)

    # Radar / spider chart
    categories = numeric_cols
    radar_agg = agg.copy()
    for col in numeric_cols:
        if radar_agg[col].max() > 0:
            radar_agg[col] = radar_agg[col] / radar_agg[col].max()

    fig_radar = px.line_polar(
        radar_agg.melt(id_vars='Cluster Label', value_vars=numeric_cols),
        r='value', theta='variable', color='Cluster Label',
        line_close=True,
        title="Cluster Behaviour Radar Chart",
        color_discrete_sequence=['#fca311','#00b4d8','#00e676','#e63946']
    )
    fig_radar.update_layout(paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_radar, use_container_width=True)

with tab3:
    fc_col1, fc_col2 = st.columns(2)
    with fc_col1:
        sel_cl = st.selectbox("Cluster", ["All"] + sorted(df_c['Cluster Label'].unique().tolist()))
    with fc_col2:
        sel_pl = st.selectbox("Platform", ["All"] + sorted(df_c['Platform'].dropna().unique().tolist()), key='raw_plat')

    raw = df_c.copy()
    if sel_cl != "All": raw = raw[raw['Cluster Label'] == sel_cl]
    if sel_pl != "All": raw = raw[raw['Platform'] == sel_pl]

    st.dataframe(
        raw[['Hashtag','Platform','Region','Views','Likes','Shares','Comments','Engagement_Level','Cluster Label']].sort_values('Views', ascending=False),
        use_container_width=True
    )
    st.download_button("⬇️ Download Cluster Data", raw.to_csv(index=False), "clusters.csv", "text/csv")
