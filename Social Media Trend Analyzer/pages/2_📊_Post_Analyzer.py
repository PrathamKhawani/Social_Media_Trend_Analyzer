import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import joblib
import numpy as np
import os
import streamlit.components.v1 as components

import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from utils.ui import set_premium_ui
from utils.trend_fetcher import get_live_trend_score, get_niche_score, level_color, level_emoji

st.set_page_config(page_title="Post Analyzer | Social Trend Analyzer", page_icon="📊", layout="wide")
set_premium_ui()

st.markdown("""
<h1>📊 Post Analyzer & Engagement Forecaster</h1>
<p>
Simulate a post before you publish it. Our <b>AI Analyzer</b> combines historical ML patterns with
<b>live Google Trends data</b> for your content category to give the most accurate engagement forecast.
</p>
""", unsafe_allow_html=True)

with st.expander("📖 How to use the Post Analyzer", expanded=False):
    st.markdown("""
    1. **Fill out your post details** (follower count, media type, caption length, etc).
    2. Click **🚀 Analyze Post** — the AI fetches **live trend data** for your chosen category.
    3. Review the **Performance Bucket** (boosted/dampened by live market trends), **Engagement Rate**, and **Reach**.
    4. Check **Best Hours to Post** and grab ready-to-use **AI Viral Captions**.
    """)

@st.cache_resource
def load_models():
    try:
        clf_path = os.path.join(BASE_DIR, 'models', 'performance_classifier.pkl')
        reg_path = os.path.join(BASE_DIR, 'models', 'engagement_regressor.pkl')
        clf = joblib.load(clf_path)
        reg = joblib.load(reg_path)
        return clf, reg
    except Exception as e:
        st.error(f"Error loading models: {e}")
        return None, None

classifier, regressor = load_models()
if classifier is None:
    st.error("Models not found. Run `python utils/model_trainer.py` first.")
    st.stop()

import random

def generate_captions(category, media, cta):
    hooks = {
        "Technology": [
            "Is this the end of smartphones? 📱",
            "I tested the top 3 gadgets so you don't have to.",
            "The hidden feature Apple didn't tell you about 🤫"
        ],
        "Fitness": [
            "Stop doing your squats like this! 🛑",
            "3 exercises for a bulletproof core.",
            "My entire morning routine revealed. ☕"
        ],
        "Beauty": [
            "The $5 drugstore find that beats luxury brands.",
            "My secret to glowing skin in 5 minutes.",
            "GRWM: The ultimate night out look ✨"
        ],
        "Finance": [
            "How I saved $10k in 6 months without trying.",
            "The biggest money mistake you're making right now.",
            "Index funds vs Real Estate: The truth 📈"
        ],
        "Food": [
            "The only pasta recipe you'll ever need 🍝",
            "I tried the viral TikTok recipe so you don't have to.",
            "3-ingredient dessert that takes 5 minutes!"
        ],
        "Travel": [
            "The most underrated city in Europe ✈️",
            "How to pack for 2 weeks in one carry-on.",
            "My honest review of the Maldives 🏝️"
        ],
        "Gaming": [
            "The best loadout for Season 5 🎮",
            "How I beat the hardest boss in under 2 minutes.",
            "This hidden easter egg changes everything!"
        ],
        "Education": [
            "The study hack that got me a 4.0 GPA 📚",
            "Stop studying harder, start studying smarter.",
            "5 websites every student needs to know."
        ],
        "Fashion": [
            "3 ways to style a basic white tee 👕",
            "Trend alert: What's in for Fall 2026.",
            "My honest review of the viral Zara jacket."
        ],
        "Entertainment": [
            "You won't believe what happened at the end 😱",
            "My top 5 favorite movies of all time 🍿",
            "The truth behind the latest drama..."
        ]
    }
    default_hooks = [
        "Wait until the end for this... 👀",
        "I can't believe I'm sharing my secret 🤫",
        "This changes everything!"
    ]
    bodies = [
        "I've been experimenting with this for the past few weeks and the results are mind-blowing. If you want to achieve similar results, you need to be consistent and pay attention to the details. Save this post so you don't forget it!",
        "It took me years of trial and error to finally figure this out. I wish I knew this when I first started! The key is to keep it simple and focus on what actually moves the needle.",
        "A lot of people asked me about this, so here is the complete breakdown! Make sure you watch carefully because I dropped a lot of gems in this one.",
        "Here is the exact strategy I use every single day. It's not always easy, but it is definitely worth it. Double tap if you agree!"
    ]
    ctas = [
        "👇 Let me know what you think in the comments!",
        "💾 Save this for later so you don't lose it!",
        "🚀 Tag a friend who needs to see this!",
        "🔗 Click the link in my bio for the full guide!",
        "✅ Follow me for more tips like this every day!"
    ]
    cat_hooks = hooks.get(category, default_hooks).copy()
    random.shuffle(cat_hooks)
    media_line = f"Watch the {media} to see exactly how it works. " if media != "text" else ""
    opt1 = f"{cat_hooks[0]}\n\n{media_line}Have you ever tried this? Drop a comment below! 👇"
    b_idx = random.randint(0, len(bodies) - 1)
    c_idx = random.randint(0, len(ctas) - 1)
    cta_line = ctas[c_idx] if cta else "Thanks for watching/reading!"
    opt2 = f"{cat_hooks[1]}\n\n{bodies[b_idx]}\n\n{cta_line}"
    opt3 = f"{cat_hooks[2]} 🔥\n\n#trending #{category.lower().replace(' ', '')} #viral"
    return opt1, opt2, opt3


def clipboard_button(text: str, button_label: str, key: str):
    """Render a real clipboard copy button using JavaScript."""
    escaped = text.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")
    components.html(
        f"""
        <button onclick="copyText()" style="
            background: linear-gradient(135deg, #0070F3, #00b4d8);
            color: white; border: none; padding: 8px 18px; border-radius: 6px;
            cursor: pointer; font-size: 0.85rem; font-weight: 600;
            font-family: Inter, sans-serif; width: 100%; transition: opacity 0.2s;
        " id="btn_{key}" onmouseover="this.style.opacity=0.85" onmouseout="this.style.opacity=1">
            {button_label}
        </button>
        <span id="msg_{key}" style="font-size:0.75rem; color:#00e676; display:none; margin-left:8px;">✅ Copied!</span>
        <script>
        function copyText() {{
            const text = `{escaped}`;
            navigator.clipboard.writeText(text).then(function() {{
                var msg = document.getElementById('msg_{key}');
                msg.style.display = 'inline';
                setTimeout(function() {{ msg.style.display = 'none'; }}, 2000);
            }}).catch(function() {{
                const el = document.createElement('textarea');
                el.value = text;
                document.body.appendChild(el);
                el.select();
                document.execCommand('copy');
                document.body.removeChild(el);
                var msg = document.getElementById('msg_{key}');
                msg.style.display = 'inline';
                setTimeout(function() {{ msg.style.display = 'none'; }}, 2000);
            }});
        }}
        </script>
        """,
        height=50,
    )


# ─── Input Form ──────────────────────────────────────────────────────────────
with st.form("post_form"):
    st.markdown("### 📝 Configure Your Post")
    c1, c2, c3 = st.columns(3)
    with c1:
        follower_count = st.number_input("Follower Count", 0, 10_000_000, 15_000, step=1000)
        media_type     = st.selectbox("Media Type", ["reel", "image", "video", "carousel", "text"])
        caption_length = st.slider("Caption Length (chars)", 0, 2200, 150)
    with c2:
        content_cat    = st.selectbox("Content Category", ["Technology","Fitness","Beauty","Fashion","Gaming","Education","Food","Travel","Finance","Entertainment"])
        post_hour      = st.slider("Post Hour (24h)", 0, 23, 18)
        hashtags_count = st.slider("Number of Hashtags", 0, 30, 5)
    with c3:
        day_of_week    = st.selectbox("Day of Week", ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"])
        has_cta_r      = st.radio("Has Call to Action?", ["Yes","No"])
    submitted = st.form_submit_button("🚀 Analyze Post", use_container_width=True)

if submitted:
    has_cta = 1 if has_cta_r == "Yes" else 0
    input_df = pd.DataFrame({
        'follower_count':    [follower_count],
        'media_type':        [media_type],
        'content_category':  [content_cat],
        'post_hour':         [post_hour],
        'day_of_week':       [day_of_week],
        'hashtags_count':    [hashtags_count],
        'caption_length':    [caption_length],
        'has_call_to_action':[has_cta]
    })

    # ── Fetch live category trend score ───────────────────────────────────────
    with st.spinner(f"📡 Fetching live market data for **{content_cat}** category…"):
        niche_score = get_niche_score(content_cat)        # 0–100 live Google Trends score
        cat_data    = get_live_trend_score(content_cat)   # full data for display
        cat_level   = cat_data["level"]
        cat_color   = level_color(cat_level)
        cat_emoji   = level_emoji(cat_level)
        cat_src     = cat_data["source"]

    # ── ML predictions ────────────────────────────────────────────────────────
    with st.spinner("AI is analyzing your post configuration…"):
        try:
            bucket   = classifier.predict(input_df)[0]
            eng_rate = max(0, float(regressor.predict(input_df)[0]))
        except Exception as e:
            st.error("ML Prediction Failed!")
            st.exception(e)
            st.stop()

    # ── Apply live trend multiplier to engagement rate ────────────────────────
    # If the niche is hot right now, posts in this category get a real boost
    # Multiplier: score 75+ → 1.4x, 50–74 → 1.2x, 25–49 → 1.0x, <25 → 0.85x
    if niche_score >= 75:
        trend_mult = 1.4
        trend_note = f"🔥 Your niche ({content_cat}) is trending VIRAL right now! +40% engagement boost applied."
    elif niche_score >= 50:
        trend_mult = 1.2
        trend_note = f"📈 Your niche ({content_cat}) is HIGH in demand. +20% engagement boost applied."
    elif niche_score >= 25:
        trend_mult = 1.0
        trend_note = f"📊 Your niche ({content_cat}) has MEDIUM market activity. No boost or dampening."
    else:
        trend_mult = 0.85
        trend_note = f"📉 Your niche ({content_cat}) has LOW market activity. Predictions adjusted accordingly."

    adjusted_eng_rate = eng_rate * trend_mult

    # ── Upgrade bucket based on trend if ML underestimates ───────────────────
    bucket_upgrade_map = {"low": "medium", "medium": "high", "high": "viral"}
    final_bucket = bucket
    if niche_score >= 75 and bucket in ["low", "medium"]:
        final_bucket = bucket_upgrade_map.get(bucket, bucket)
    elif niche_score < 20 and bucket in ["high", "viral"]:
        final_bucket = "medium"

    bucket_color = {
        'viral': '#ff6b35', 'high': '#00e676',
        'medium': '#fca311', 'low': '#e63946'
    }.get(final_bucket.lower(), '#fca311')

    st.markdown("---")

    # ── Live Trend Context Banner ─────────────────────────────────────────────
    src_label = "📡 Live Google Trends" if cat_src == "google_trends" else "🧠 Cached Intelligence"
    st.markdown(f"""
    <div style="background:{cat_color}12; border:1px solid {cat_color}44; border-left:4px solid {cat_color};
                border-radius:8px; padding:12px 20px; margin-bottom:16px; display:flex; align-items:center; gap:16px;">
        <div><span style="font-size:2rem;">{cat_emoji}</span></div>
        <div>
            <div style="font-weight:700; color:{cat_color}; font-size:1rem;">
                {content_cat} Niche — Google Trends Score: {niche_score}/100 ({cat_level})
            </div>
            <div style="font-size:0.8rem; opacity:0.7;">
                Source: {src_label} · {trend_note}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🎯 Prediction Results")
    r1, r2, r3, r4 = st.columns(4)

    with r1:
        st.markdown(f"""
        <div class='result-card'>
            <div class='result-label'>Performance Bucket</div>
            <div class='result-value' style='color:{bucket_color};'>{final_bucket.upper()}</div>
            <span style="font-size:0.75rem; opacity:0.6;">Trend-adjusted</span>
        </div>""", unsafe_allow_html=True)
    with r2:
        st.markdown(f"""
        <div class='result-card'>
            <div class='result-label'>Predicted Engagement Rate</div>
            <div class='result-value' style='color:#00b4d8;'>{adjusted_eng_rate:.3f}%</div>
            <span style="font-size:0.75rem; opacity:0.6;">×{trend_mult} trend boost</span>
        </div>""", unsafe_allow_html=True)
    with r3:
        reach_est = int(follower_count * adjusted_eng_rate * 3.5)
        st.markdown(f"""
        <div class='result-card'>
            <div class='result-label'>Estimated Reach</div>
            <div class='result-value' style='color:#a78bfa;'>{reach_est:,}</div>
            <span style="font-size:0.75rem; opacity:0.6;">People</span>
        </div>""", unsafe_allow_html=True)
    with r4:
        st.markdown(f"""
        <div class='result-card'>
            <div class='result-label'>Niche Trend Score</div>
            <div class='result-value' style='color:{cat_color};'>{niche_score}<span style="font-size:1rem; opacity:0.6;">/100</span></div>
            <span style="font-size:0.75rem; opacity:0.6;">Live market data</span>
        </div>""", unsafe_allow_html=True)

    # ── Gauge chart ───────────────────────────────────────────────────────────
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=adjusted_eng_rate * 100,
        title={'text': "Engagement Rate Score (Trend-Adjusted)"},
        delta={'reference': 5.0, 'increasing': {'color': '#00e676'}, 'decreasing': {'color': '#e63946'}},
        gauge={
            'axis':  {'range': [0, 20]},
            'bar':   {'color': bucket_color},
            'bgcolor': '#1a1f35',
            'steps': [
                {'range': [0,  3],  'color': '#1a1f1f'},
                {'range': [3,  8],  'color': '#1a2a1a'},
                {'range': [8,  20], 'color': '#1a2a2a'}
            ],
            'threshold': {'line': {'color': '#fca311', 'width': 3}, 'thickness': 0.75, 'value': adjusted_eng_rate * 100}
        }
    ))
    fig_gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', height=300)
    st.plotly_chart(fig_gauge, use_container_width=True)

    # ── Live Trend Sparkline for the chosen category ──────────────────────────
    if cat_data.get("interest_df") is not None:
        st.markdown(f"### 📈 {content_cat} Category — Live Interest (Google Trends, Last 30 Days)")
        fig_spark = px.area(
            cat_data["interest_df"], x='date', y='interest',
            labels={'interest': 'Search Interest (0–100)', 'date': 'Date'},
            template='plotly_dark', color_discrete_sequence=[cat_color]
        )
        fig_spark.update_traces(fill='tozeroy', fillcolor=f"{cat_color}30")
        fig_spark.update_layout(
            paper_bgcolor='rgba(14,21,32,0.9)', plot_bgcolor='rgba(0,0,0,0)',
            height=220, margin=dict(t=10, b=10),
            xaxis=dict(showgrid=False),
            yaxis=dict(range=[0, 100], showgrid=True, gridcolor='rgba(255,255,255,0.05)')
        )
        st.plotly_chart(fig_spark, use_container_width=True)

    # ── Best hour recommendation ──────────────────────────────────────────────
    st.markdown("### ⏰ Best Hours to Post (Historical Avg Engagement)")
    try:
        eng_df = pd.read_csv(os.path.join(BASE_DIR, 'engagement.csv'))
        hour_rate = eng_df.groupby('post_hour')['engagement_rate'].mean().reset_index()
        fig_hour = px.bar(hour_rate, x='post_hour', y='engagement_rate',
                          color='engagement_rate', color_continuous_scale='Oranges',
                          labels={'post_hour':'Hour of Day','engagement_rate':'Avg Engagement Rate'},
                          title="Avg Engagement Rate by Posting Hour")
        fig_hour.add_vline(x=post_hour, line_color='#00e676', line_dash='dash',
                           annotation_text=f"Your hour ({post_hour}:00)", annotation_font_color='#00e676')
        fig_hour.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_hour, use_container_width=True)
    except Exception:
        pass

    best_hours = "6PM – 9PM" if media_type in ["reel","video"] else "8AM – 11AM"
    st.markdown(f"""
    <div class='tip-box'>
        💡 <b>Pro Tip:</b> {media_type.capitalize()}s in the <b>{content_cat}</b> niche (currently <b style="color:{cat_color};">{cat_level}</b>
        on Google Trends) perform best between <b>{best_hours}</b>.
        Adding a CTA can increase engagement by up to <b>23%</b>.
        Aim for <b>{hashtags_count + 3} – {hashtags_count + 7}</b> hashtags for optimal reach.
    </div>""", unsafe_allow_html=True)

    # ── AI Viral Caption Generator ────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### ✍️ AI Viral Caption & Hook Generator")
    st.markdown(f"<p>Crafted for <b>{content_cat}</b> <b>{media_type}</b> content. Click <b>Copy</b> to instantly use any caption.</p>", unsafe_allow_html=True)

    with st.spinner("Generating viral hooks and captions..."):
        cap1, cap2, cap3 = generate_captions(content_cat, media_type, has_cta)

    c_gen1, c_gen2, c_gen3 = st.columns(3)
    with c_gen1:
        st.markdown("**Option 1: 🎯 Engagement Bait**")
        st.text_area("Caption 1", cap1, height=160, key="ta_cap1", label_visibility="collapsed")
        clipboard_button(cap1, "📋 Copy Option 1", "copy1")
    with c_gen2:
        st.markdown("**Option 2: 📖 The Storyteller**")
        st.text_area("Caption 2", cap2, height=160, key="ta_cap2", label_visibility="collapsed")
        clipboard_button(cap2, "📋 Copy Option 2", "copy2")
    with c_gen3:
        st.markdown("**Option 3: ⚡ Short & Punchy**")
        st.text_area("Caption 3", cap3, height=160, key="ta_cap3", label_visibility="collapsed")
        clipboard_button(cap3, "📋 Copy Option 3", "copy3")

    st.markdown("""
    <div class='tip-box' style='margin-top:12px;'>
        💡 <b>Tip:</b> Click inside any caption box and press <b>Ctrl+A</b> then <b>Ctrl+C</b> to copy, or use the Copy button above.
    </div>""", unsafe_allow_html=True)
