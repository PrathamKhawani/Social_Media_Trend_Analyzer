import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from utils.ui import set_premium_ui
from utils.trend_fetcher import get_niche_score, level_color, level_emoji, compare_keywords

st.set_page_config(page_title="Competitor Benchmarking", page_icon="🏆", layout="wide")

set_premium_ui()

st.markdown("""
<h1>🏆 Competitor Benchmarking</h1>
<p>
Compare your estimated engagement against a competitor. Enter your profiles, and our <b>AI Benchmarker</b> will simulate and visualize the performance gap.
</p>
""", unsafe_allow_html=True)

with st.expander("📖 How to use the Benchmarker", expanded=False):
    st.markdown("""
    1. **Enter Your Stats**: Input your follower count and estimated average engagement rate.
    2. **Enter Competitor Stats**: Input their handle and follower count.
    3. Click **📊 Run AI Simulation**. The system will generate a realistic engagement profile for your competitor based on their size and niche.
    4. **Compare**: Use the Radar Chart and KPI cards to see exactly where you win or lose!
    """)

# ─── Inputs ──────────────────────────────────────────────────────────────────
st.markdown("### 📝 Profile Configuration")
c1, c2 = st.columns(2)

with c1:
    st.markdown("#### 👤 Your Profile")
    my_followers = st.number_input("Your Followers", 0, 10000000, 50000, step=1000, key="my_f")
    my_eng_rate  = st.slider("Your Avg Engagement Rate (%)", 0.1, 15.0, 3.5, 0.1, key="my_e")
    my_niche     = st.selectbox("Your Niche", ["Technology", "Fitness", "Beauty", "Finance", "Food", "Travel", "Gaming"], key="my_n")

with c2:
    st.markdown("#### 🤼 Competitor Profile")
    comp_handle    = st.text_input("Competitor Handle", "@competitor", key="c_h")
    comp_followers = st.number_input("Competitor Followers", 0, 10000000, 120000, step=1000, key="c_f")
    comp_niche     = st.selectbox("Competitor Niche", ["Technology", "Fitness", "Beauty", "Finance", "Food", "Travel", "Gaming"], key="c_n")

submitted = st.button("📊 Run AI Simulation", use_container_width=True)

if submitted:
    with st.spinner("AI is fetching live niche trend data and simulating competitor metrics..."):
        # Get live Google Trends scores for both niches
        my_niche_score   = get_niche_score(my_niche)    # 0–100 live score
        comp_niche_score = get_niche_score(comp_niche)  # 0–100 live score

        # Niche multiplier is now DATA-DRIVEN from Google Trends
        # Score 75+ → 1.25x boost, 50-75 → 1.1x, 25-50 → 0.95x, <25 → 0.85x
        def score_to_mult(s):
            if s >= 75: return 1.25
            elif s >= 50: return 1.1
            elif s >= 25: return 0.95
            else: return 0.85

        my_niche_mult   = score_to_mult(my_niche_score)
        comp_niche_mult = score_to_mult(comp_niche_score)

        # Size-based adjustment (larger accounts have lower % engagement)
        size_multiplier = (my_followers / max(comp_followers, 1)) ** 0.1
        base_comp_eng   = my_eng_rate * size_multiplier * np.random.uniform(0.8, 1.2)
        comp_eng_rate   = round(base_comp_eng * comp_niche_mult, 2)

        # Adjust your engagement based on live niche score too
        adj_my_eng_rate = round(my_eng_rate * my_niche_mult, 2)

        my_reach   = round(adj_my_eng_rate * np.random.uniform(2.5, 4.0), 1)
        comp_reach = round(comp_eng_rate * np.random.uniform(2.5, 4.0), 1)
        my_save    = round(adj_my_eng_rate * np.random.uniform(0.1, 0.3), 2)
        comp_save  = round(comp_eng_rate * np.random.uniform(0.1, 0.3), 2)
        my_share   = round(adj_my_eng_rate * np.random.uniform(0.05, 0.2), 2)
        comp_share = round(comp_eng_rate * np.random.uniform(0.05, 0.2), 2)

    st.markdown("---")

    # ── Live Niche Trend Context ─────────────────────────────────────────────
    bn1, bn2 = st.columns(2)
    with bn1:
        c = level_color("High" if my_niche_score >= 50 else "Medium" if my_niche_score >= 25 else "Low")
        st.markdown(f"""
        <div style="background:{c}12;border:1px solid {c}44;border-left:4px solid {c};
                    border-radius:8px;padding:10px 16px;margin-bottom:12px;">
            <b style="color:{c};">Your Niche ({my_niche})</b> —
            Google Trends Score: <b>{my_niche_score}/100</b> · Multiplier: <b>{my_niche_mult:.2f}x</b>
        </div>""", unsafe_allow_html=True)
    with bn2:
        c2 = level_color("High" if comp_niche_score >= 50 else "Medium" if comp_niche_score >= 25 else "Low")
        st.markdown(f"""
        <div style="background:{c2}12;border:1px solid {c2}44;border-left:4px solid {c2};
                    border-radius:8px;padding:10px 16px;margin-bottom:12px;">
            <b style="color:{c2};">Competitor Niche ({comp_niche})</b> —
            Google Trends Score: <b>{comp_niche_score}/100</b> · Multiplier: <b>{comp_niche_mult:.2f}x</b>
        </div>""", unsafe_allow_html=True)

    st.markdown(f"### 🎯 Head-to-Head: You vs {comp_handle}")
    
    # ─── KPI Cards ───────────────────────────────────────────────────────────
    r1, r2, r3, r4 = st.columns(4)
    
    metrics = [
        ("Engagement Rate", my_eng_rate, comp_eng_rate, "%"),
        ("Reach Rate", my_reach, comp_reach, "%"),
        ("Save Rate", my_save, comp_save, "%"),
        ("Share Rate", my_share, comp_share, "%")
    ]
    
    cols = [r1, r2, r3, r4]
    
    for col, (title, my_val, comp_val, symbol) in zip(cols, metrics):
        diff = round(my_val - comp_val, 2)
        diff_cls = "diff-positive" if diff >= 0 else "diff-negative"
        diff_sign = "+" if diff >= 0 else ""
        color = "#00b4d8" if diff >= 0 else "#e63946"
        
        col.markdown(f"""
        <div class='card'>
            <div class='card-title'>{title}</div>
            <div class='card-value' style='color:{color}'>{my_val}{symbol}</div>
            <div class='{diff_cls}'>{diff_sign}{diff}{symbol} vs {comp_handle} ({comp_val}{symbol})</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ─── Charts ──────────────────────────────────────────────────────────────
    c_chart1, c_chart2 = st.columns([1, 1])
    
    with c_chart1:
        st.markdown("#### 🕸️ Performance Radar")
        df_radar = pd.DataFrame({
            'Metric': ['Engagement', 'Reach', 'Saves', 'Shares'] * 2,
            'Value': [my_eng_rate, my_reach, my_save, my_share, comp_eng_rate, comp_reach, comp_save, comp_share],
            'Profile': ['You', 'You', 'You', 'You', comp_handle, comp_handle, comp_handle, comp_handle]
        })
        
        # Normalize for radar so scales look decent
        for m in df_radar['Metric'].unique():
            max_val = df_radar[df_radar['Metric'] == m]['Value'].max()
            df_radar.loc[df_radar['Metric'] == m, 'Normalized'] = df_radar['Value'] / max_val
            
        fig_radar = px.line_polar(
            df_radar, r='Normalized', theta='Metric', color='Profile',
            line_close=True,
            color_discrete_sequence=['#888888', '#0070F3']
        )
        fig_radar.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            polar=dict(radialaxis=dict(visible=False)),
            legend=dict(title="")
        )
        # Custom hover data to show real value, not normalized
        fig_radar.update_traces(hovertemplate="%{theta}: <br>Normalized: %{r}<extra></extra>")
        st.plotly_chart(fig_radar, use_container_width=True)
        
    with c_chart2:
        st.markdown("#### 📊 Absolute Values Comparison")
        fig_bar = px.bar(
            df_radar, x='Metric', y='Value', color='Profile', barmode='group',
            color_discrete_sequence=['#888888', '#0070F3']
        )
        fig_bar.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(title="")
        )
        st.plotly_chart(fig_bar, use_container_width=True)
