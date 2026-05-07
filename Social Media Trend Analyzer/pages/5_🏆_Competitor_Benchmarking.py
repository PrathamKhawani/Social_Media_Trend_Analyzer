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
    with st.spinner("AI is analyzing niche averages and simulating competitor metrics..."):
        # AI Simulation Logic
        # As follower count increases, engagement rate typically drops (law of large numbers)
        size_multiplier = (my_followers / max(comp_followers, 1)) ** 0.1
        
        # Base competitor engagement is a function of yours + size difference + some randomness
        base_comp_eng = my_eng_rate * size_multiplier * np.random.uniform(0.8, 1.2)
        # Niche multiplier (e.g., fitness might have slightly higher engagement than finance)
        niche_mult = 1.1 if comp_niche in ["Fitness", "Beauty", "Gaming"] else 0.9
        comp_eng_rate = round(base_comp_eng * niche_mult, 2)
        
        # Simulate secondary metrics based on engagement rate
        # Reach % is usually higher than engagement
        my_reach = round(my_eng_rate * np.random.uniform(2.5, 4.0), 1)
        comp_reach = round(comp_eng_rate * np.random.uniform(2.5, 4.0), 1)
        
        # Save & Share rates are fractions of engagement
        my_save = round(my_eng_rate * np.random.uniform(0.1, 0.3), 2)
        comp_save = round(comp_eng_rate * np.random.uniform(0.1, 0.3), 2)
        
        my_share = round(my_eng_rate * np.random.uniform(0.05, 0.2), 2)
        comp_share = round(comp_eng_rate * np.random.uniform(0.05, 0.2), 2)

    st.markdown("---")
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
