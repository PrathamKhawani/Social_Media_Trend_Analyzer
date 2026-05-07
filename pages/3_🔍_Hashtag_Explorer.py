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
from utils.trend_fetcher import get_live_trend_score, compare_keywords, level_color, level_emoji, get_trending_now

st.set_page_config(page_title="Hashtag Explorer | Social Trend Analyzer", page_icon="🔍", layout="wide")
set_premium_ui()

st.markdown("""
<h1>🔍 Hashtag Clustering Explorer</h1>
<p>
Discover hidden groups in trending hashtag data using our <b>AI Grouping Engine</b>.
Each cluster represents hashtags that behave similarly. Now powered with <b>live Google Trends scores</b>
so you can see which clusters are hot <i>right now</i>.
</p>
""", unsafe_allow_html=True)

with st.expander("📖 How to use the Hashtag Explorer", expanded=False):
    st.markdown("""
    1. **Explore the Cluster Map** — see how the AI grouped thousands of hashtags.
    2. Use **Live Trend Check** to instantly see the real Google Trends score for any hashtag.
    3. Use the filters to drill down by **Platform** or **Region**.
    4. Switch to **Cluster Analysis** to compare average performance across groups.
    5. Use the **Trending Now** tab to see what's hot right now from Google Trends.
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

X_scaled        = scaler.transform(df_c[numeric_cols])
df_c['Cluster'] = kmeans.predict(X_scaled).astype(str)
pca_result      = pca.transform(X_scaled)
df_c['PCA1']    = pca_result[:, 0]
df_c['PCA2']    = pca_result[:, 1]

cluster_names = {
    '0': '🔥 Viral Giants',
    '1': '📈 Rising Stars',
    '2': '💬 Community Hubs',
    '3': '🌱 Emerging Niches'
}
df_c['Cluster Label'] = df_c['Cluster'].map(cluster_names).fillna(df_c['Cluster'])

# ─── Live Trend Check Widget (top of page) ────────────────────────────────────
st.markdown("### 📡 Live Hashtag Trend Check")
st.caption("Check the real-time Google Trends score for any hashtag before you use it.")

lc1, lc2 = st.columns([3, 1])
with lc1:
    live_check_kw = st.text_input("Enter a hashtag to check its live trend score", value="#AI",
                                  placeholder="#AI, #fitness, #crypto…", label_visibility="collapsed")
with lc2:
    do_live_check = st.button("🔍 Check Live Score", use_container_width=True)

if do_live_check and live_check_kw:
    with st.spinner(f"Fetching live Google Trends data for {live_check_kw}…"):
        result = get_live_trend_score(live_check_kw)
    tc = level_color(result["level"])
    te = level_emoji(result["level"])
    src = "📡 Live Google Trends" if result["source"] == "google_trends" else "🧠 Cached Intelligence"

    la, lb, lc, ld = st.columns(4)
    la.markdown(f"""
    <div class='result-card'>
        <div class='result-label'>Trend Level</div>
        <div class='result-value' style='color:{tc};'>{te} {result["level"].upper()}</div>
    </div>""", unsafe_allow_html=True)
    lb.markdown(f"""
    <div class='result-card'>
        <div class='result-label'>Google Score</div>
        <div class='result-value' style='color:#00b4d8;'>{result["score"]}<span style='font-size:1rem;opacity:0.6;'>/100</span></div>
    </div>""", unsafe_allow_html=True)
    lc.markdown(f"""
    <div class='result-card'>
        <div class='result-label'>Peak Score (30 days)</div>
        <div class='result-value' style='color:#a78bfa;'>{result.get("peak", result["score"])}<span style='font-size:1rem;opacity:0.6;'>/100</span></div>
    </div>""", unsafe_allow_html=True)
    ld.markdown(f"""
    <div class='result-card'>
        <div class='result-label'>Data Source</div>
        <div style='font-size:0.9rem; font-weight:600; margin-top:12px;'>{src}</div>
    </div>""", unsafe_allow_html=True)

    if result.get("interest_df") is not None and not result["interest_df"].empty:
        fig_lc = px.area(
            result["interest_df"], x='date', y='interest',
            template='plotly_dark', color_discrete_sequence=[tc],
            labels={'interest': 'Search Interest (0–100)', 'date': 'Date'},
            title=f"Live Interest Trend for {live_check_kw} (Last 30 Days)"
        )
        fig_lc.update_traces(fill='tozeroy', fillcolor=f"{tc}25")
        fig_lc.update_layout(paper_bgcolor='rgba(14,21,32,0.9)', plot_bgcolor='rgba(0,0,0,0)', height=220)
        st.plotly_chart(fig_lc, use_container_width=True)

    if result.get("related"):
        st.markdown("**🔗 Related Rising Topics:**  " + "  ·  ".join([f"`{r}`" for r in result["related"]]))

st.markdown("---")

# ─── Stats Row ────────────────────────────────────────────────────────────────
st.markdown("### 📊 Dataset Overview")
s1, s2, s3, s4 = st.columns(4)
for col, label, val in zip([s1, s2, s3, s4],
    ["Total Hashtags", "Platforms", "Regions", "AI Clusters"],
    [len(df_c), df_c['Platform'].nunique(), df_c['Region'].nunique(), 4]):
    col.markdown(f"""
    <div class='result-card'>
        <div class='result-label'>{label}</div>
        <div class='result-value'>{val:,}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Main Tabs ────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["🗺️ Cluster Map", "📊 Cluster Analysis", "🔥 Trending Now", "📋 Raw Data"])

with tab1:
    st.markdown("#### AI Hashtag Grouping Map")
    st.markdown("<small style='color:#5a6678;'>Each dot = 1 hashtag. Colors show AI-generated similarity groups based on Views, Likes, Shares & Comments.</small>", unsafe_allow_html=True)
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
            paper_bgcolor='rgba(14,21,32,0.9)', plot_bgcolor='rgba(14,21,32,0.5)',
            font_color='#ecf0f1', legend=dict(bgcolor='rgba(14,21,32,0.8)', bordercolor='#1e2a3e'),
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("""
    <div style='background:var(--secondary-background-color);border:1px solid rgba(128,128,128,0.2);border-radius:8px;padding:16px;'>
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
        fig2 = px.bar(agg, x='Cluster Label', y='Views', color='Cluster Label',
                      color_discrete_sequence=['#fca311','#00b4d8','#00e676','#e63946'],
                      title="Average Views per Cluster")
        fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)
    with c2:
        fig3 = px.bar(agg, x='Cluster Label', y=['Likes','Shares','Comments'],
                      barmode='group', title="Avg Likes / Shares / Comments per Cluster")
        fig3.update_layout(paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig3, use_container_width=True)
    radar_agg = agg.copy()
    for col in numeric_cols:
        if radar_agg[col].max() > 0:
            radar_agg[col] = radar_agg[col] / radar_agg[col].max()
    fig_radar = px.line_polar(
        radar_agg.melt(id_vars='Cluster Label', value_vars=numeric_cols),
        r='value', theta='variable', color='Cluster Label', line_close=True,
        title="Cluster Behaviour Radar Chart",
        color_discrete_sequence=['#fca311','#00b4d8','#00e676','#e63946']
    )
    fig_radar.update_layout(paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_radar, use_container_width=True)

with tab3:
    st.markdown("#### 🔥 What's Trending Right Now — Live from Google Trends")
    st.caption("Auto-refreshed every hour · Source: Google Trends (Worldwide)")
    with st.spinner("Loading live trending topics…"):
        live_now = get_trending_now()
    if live_now:
        t_cols = st.columns(5)
        for i, t in enumerate(live_now[:10]):
            with t_cols[i % 5]:
                st.markdown(f"""
                <div style="background:var(--secondary-background-color);border:1px solid rgba(255,107,53,0.3);
                            border-radius:8px;padding:14px;text-align:center;margin-bottom:10px;">
                    <div style="font-size:0.9rem;font-weight:700;">{t['title']}</div>
                    <div style="color:#ff6b35;font-size:0.8rem;margin-top:6px;">{t['traffic']}</div>
                </div>""", unsafe_allow_html=True)

    # ── Compare up to 3 hashtags ──────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 📊 Compare Hashtags Head-to-Head (Live Google Trends)")
    comp_input = st.text_input("Enter up to 3 hashtags separated by commas", value="#AI, #fitness, #crypto")
    if st.button("📊 Compare Live", use_container_width=True):
        keywords = [k.strip() for k in comp_input.split(",") if k.strip()][:3]
        with st.spinner("Fetching live comparison data…"):
            comp_df = compare_keywords(keywords)
        if not comp_df.empty:
            fig_comp = px.line(comp_df.reset_index(), x='date', y=comp_df.columns.tolist(),
                               template='plotly_dark',
                               color_discrete_sequence=['#ff6b35','#00e676','#00b4d8'],
                               title="Head-to-Head Trend Comparison (Last 3 Months)",
                               labels={'value':'Interest (0–100)', 'date':'Date', 'variable':'Hashtag'})
            fig_comp.update_layout(paper_bgcolor='rgba(14,21,32,0.9)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_comp, use_container_width=True)
        else:
            st.info("Could not fetch comparison data. Try again or check your keyword spelling.")

with tab4:
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
