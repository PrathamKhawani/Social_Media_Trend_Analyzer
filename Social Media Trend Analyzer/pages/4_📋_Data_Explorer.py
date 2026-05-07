import streamlit as st
import pandas as pd
import plotly.express as px
import os

import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from utils.ui import set_premium_ui

st.set_page_config(page_title="Data Explorer", page_icon="📋", layout="wide")

set_premium_ui()

st.markdown("""
<h1>📋 Raw Data Explorer</h1>
<p>Browse, filter, and download the underlying data that powers our AI predictions.</p>
""", unsafe_allow_html=True)

with st.expander("📖 How to use the Data Explorer", expanded=False):
    st.markdown("""
    1. **Navigate the tabs** to switch between Instagram Engagement, Hashtag, and YouTube data.
    2. **Use the filters** to narrow down the data to specific categories, media types, or regions.
    3. Explore the **Summary Statistics** charts to spot trends.
    4. Click **Download CSV** to export the filtered data for your own analysis.
    """)

@st.cache_data
def load_all():
    try:
        eng = pd.read_csv(os.path.join(BASE_DIR, 'engagement.csv'))
    except Exception:
        eng = None
    try:
        hsh = pd.read_csv(os.path.join(BASE_DIR, 'hashtags.csv'))
    except Exception:
        try: hsh = pd.read_csv(os.path.join(BASE_DIR, 'hashtags.csv'), encoding='latin1')
        except Exception: hsh = None
    try:
        ts = pd.read_csv(os.path.join(BASE_DIR, 'time_series.csv'))
    except Exception:
        try: ts = pd.read_csv(os.path.join(BASE_DIR, 'time_series.csv'), encoding='latin1')
        except Exception: ts = None
    return eng, hsh, ts

eng_df, hsh_df, ts_df = load_all()

tab1, tab2, tab3 = st.tabs(["📝 Engagement Data", "#️⃣ Hashtag Data", "▶️ YouTube Data"])

# ── Tab 1: Engagement ──────────────────────────────────────────────────────────
with tab1:
    if eng_df is not None:
        st.markdown('<p class="section-header">Filters</p>', unsafe_allow_html=True)
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            mt = st.multiselect("Media Type", eng_df['media_type'].dropna().unique(), default=list(eng_df['media_type'].dropna().unique()))
        with fc2:
            cat = st.multiselect("Content Category", eng_df['content_category'].dropna().unique(), default=list(eng_df['content_category'].dropna().unique())[:3])
        with fc3:
            perf = st.multiselect("Performance Bucket", eng_df['performance_bucket_label'].dropna().unique(), default=list(eng_df['performance_bucket_label'].dropna().unique()))

        filtered = eng_df[eng_df['media_type'].isin(mt) & eng_df['content_category'].isin(cat) & eng_df['performance_bucket_label'].isin(perf)]
        
        st.markdown(f"**Showing {len(filtered):,} of {len(eng_df):,} records**")
        st.dataframe(filtered[['post_id','media_type','content_category','post_hour','likes','comments','engagement_rate','performance_bucket_label']].head(500), use_container_width=True)
        
        st.download_button("⬇️ Download Filtered CSV", filtered.to_csv(index=False), "engagement_filtered.csv", "text/csv")

        st.markdown('<p class="section-header">Summary Statistics</p>', unsafe_allow_html=True)
        sc1, sc2 = st.columns(2)
        with sc1:
            fig = px.histogram(filtered, x='engagement_rate', nbins=40, title="Engagement Rate Distribution",
                               color_discrete_sequence=['#fca311'])
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
        with sc2:
            dow = filtered.groupby('day_of_week')['engagement_rate'].mean().reset_index()
            cats = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            dow['day_of_week'] = pd.Categorical(dow['day_of_week'], categories=cats, ordered=True)
            dow = dow.sort_values('day_of_week')
            fig2 = px.line(dow, x='day_of_week', y='engagement_rate', markers=True,
                           title="Avg Engagement by Day of Week",
                           color_discrete_sequence=['#00b4d8'])
            fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig2, use_container_width=True)

# ── Tab 2: Hashtags ────────────────────────────────────────────────────────────
with tab2:
    if hsh_df is not None:
        hfc1, hfc2 = st.columns(2)
        with hfc1:
            plat = st.multiselect("Platform", hsh_df['Platform'].dropna().unique(), default=list(hsh_df['Platform'].dropna().unique()))
        with hfc2:
            region = st.multiselect("Region", hsh_df['Region'].dropna().unique(), default=list(hsh_df['Region'].dropna().unique())[:3])
        
        filt_h = hsh_df[hsh_df['Platform'].isin(plat) & hsh_df['Region'].isin(region)]
        st.markdown(f"**Showing {len(filt_h):,} of {len(hsh_df):,} records**")
        st.dataframe(filt_h.head(500), use_container_width=True)
        st.download_button("⬇️ Download Filtered CSV", filt_h.to_csv(index=False), "hashtags_filtered.csv", "text/csv")
        
        hc1, hc2 = st.columns(2)
        with hc1:
            top_hsh = filt_h.groupby('Hashtag')['Views'].sum().nlargest(15).reset_index()
            fig3 = px.bar(top_hsh, x='Views', y='Hashtag', orientation='h',
                          title="Top 15 Hashtags by Total Views",
                          color='Views', color_continuous_scale='Teal')
            fig3.update_layout(paper_bgcolor='rgba(0,0,0,0)', yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig3, use_container_width=True)
        with hc2:
            reg_eng = filt_h.groupby('Region')[['Views','Likes','Shares']].mean().reset_index()
            fig4 = px.bar(reg_eng, x='Region', y=['Views','Likes','Shares'], barmode='group',
                          title="Avg Views / Likes / Shares by Region")
            fig4.update_layout(paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig4, use_container_width=True)

# ── Tab 3: YouTube ─────────────────────────────────────────────────────────────
with tab3:
    if ts_df is not None:
        st.markdown(f"**{len(ts_df):,} YouTube Videos**")
        st.dataframe(ts_df.head(500), use_container_width=True)
        st.download_button("⬇️ Download CSV", ts_df.to_csv(index=False), "youtube_data.csv", "text/csv")
        
        yc1, yc2 = st.columns(2)
        with yc1:
            fig5 = px.histogram(ts_df, x='view_count', nbins=30,
                                title="Video View Count Distribution",
                                color_discrete_sequence=['#e63946'])
            fig5.update_layout(paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig5, use_container_width=True)
        with yc2:
            if 'category_id' in ts_df.columns:
                cat_views = ts_df.groupby('category_id')['view_count'].mean().reset_index()
                fig6 = px.bar(cat_views, x='category_id', y='view_count',
                              title="Avg Views by Category",
                              color='view_count', color_continuous_scale='Purples')
                fig6.update_layout(paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig6, use_container_width=True)
