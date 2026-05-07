import streamlit as st
import pandas as pd
import numpy as np
import os
import io
from datetime import datetime
from fpdf import FPDF

import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from utils.ui import set_premium_ui
from utils.trend_fetcher import get_live_trend_score, level_emoji

st.set_page_config(page_title="Report Generator", page_icon="📄", layout="wide")

set_premium_ui()

st.markdown("""
<h1>📄 AI Analysis Report Generator</h1>
<p>
Fill in your analysis details below. Our engine will compile all insights into a clean, professional <b>PDF Report</b> you can download in one click.
</p>
""", unsafe_allow_html=True)

with st.expander("📖 How to use the Report Generator", expanded=False):
    st.markdown("""
    1. **Fill in the report details** — enter your name, the topic you analyzed, and the platform.
    2. **Enter your key metrics** from your analysis (you can copy these from the Trend Predictor or Post Analyzer).
    3. **Write an optional executive summary** to add your own professional commentary.
    4. Click **📥 Generate PDF Report** to create and download the PDF instantly!
    """)

# ─── Form Inputs ─────────────────────────────────────────────────────────────
st.markdown("### 📝 Configure Your Report")

col1, col2 = st.columns(2)
with col1:
    analyst_name  = st.text_input("Your Name / Organization", "Social Media Analyst")
    topic         = st.text_input("Topic / Hashtag Analyzed", "#TechTrends2026")
    platform      = st.selectbox("Platform", ["Instagram", "TikTok", "Twitter", "YouTube", "Facebook"])
    region        = st.selectbox("Region", ["Global", "India", "USA", "UK", "Brazil", "Europe"])

with col2:
    predicted_engagement = st.text_input("Predicted Engagement Level", "High")
    ai_confidence        = st.number_input("AI Certainty Score (%)", 0, 100, 85)
    estimated_reach      = st.number_input("Estimated Reach", 0, 10000000, 50000, step=1000)
    sentiment            = st.selectbox("Audience Sentiment", ["Positive", "Neutral", "Negative", "Mixed"])

exec_summary = st.text_area(
    "Executive Summary (optional)",
    "Based on our AI analysis, this topic shows strong potential for viral performance on the selected platform. "
    "We recommend increasing content frequency and leveraging peak posting hours for maximum reach.",
    height=120
)

st.markdown("### 📊 Add Data Snapshot (Optional)")
include_data = st.checkbox("Include dataset statistics in the report", value=True)

submitted = st.button("📥 Generate PDF Report", use_container_width=True)

# ── Live Trend Score for the Topic ─────────────────────────────────────────────
if topic:
    with st.spinner(f"📡 Fetching live trend score for **{topic}**…"):
        live_data   = get_live_trend_score(topic)
    live_score  = live_data["score"]
    live_level  = live_data["level"]
    live_src    = live_data["source"]
    live_emoji  = level_emoji(live_level)
    live_color  = {"Viral": "#ff6b35", "High": "#00e676", "Medium": "#fca311", "Low": "#e63946"}.get(live_level, "#fca311")
    src_label   = "📡 Live Google Trends" if live_src == "google_trends" else "🧠 Cached Intelligence"

    st.markdown(f"""
    <div style="background:{live_color}12; border:1px solid {live_color}44; border-left:4px solid {live_color};
                border-radius:8px; padding:12px 20px; margin:12px 0; display:flex; align-items:center; gap:16px;">
        <div><span style="font-size:2rem;">{live_emoji}</span></div>
        <div>
            <div style="font-weight:700; color:{live_color}; font-size:1rem;">
                {topic} — Live Google Trends Score: {live_score}/100 ({live_level})
            </div>
            <div style="font-size:0.8rem; opacity:0.7;">Source: {src_label} · This live score will be included in your PDF report.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    live_score, live_level, live_emoji = 50, "Medium", "📊"


# ─── PDF Generation ──────────────────────────────────────────────────────────
def generate_pdf(analyst, topic, platform, region, pred_eng, confidence, reach, sentiment, summary, include_data, live_score=50, live_level="Medium"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # ── Header Bar ──
    pdf.set_fill_color(12, 18, 40)  # dark navy
    pdf.rect(0, 0, 210, 30, 'F')
    pdf.set_text_color(252, 163, 17)  # golden
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_xy(10, 8)
    pdf.cell(0, 14, "Social Media Trend Analyzer", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(180, 180, 180)
    pdf.set_xy(10, 20)
    pdf.cell(0, 8, "AI-Powered Social Media Performance Report", ln=True)
    pdf.ln(10)

    # ── Meta Info ──
    pdf.set_fill_color(230, 235, 245)
    pdf.set_text_color(30, 30, 60)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 8, f"Report Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 7, f"Prepared By: {analyst}", ln=True)
    pdf.cell(0, 7, f"Topic Analyzed: {topic}   |   Platform: {platform}   |   Region: {region}", ln=True)
    pdf.ln(5)

    # ── Divider ──
    pdf.set_draw_color(252, 163, 17)
    pdf.set_line_width(0.8)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)

    # ── Executive Summary ──
    pdf.set_text_color(252, 163, 17)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 9, "Executive Summary", ln=True)
    pdf.set_text_color(40, 40, 40)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 7, summary)
    pdf.ln(5)

    # ── Key Findings ──
    pdf.set_text_color(252, 163, 17)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 9, "Key AI Findings", ln=True)
    pdf.ln(2)

    def kpi_row(label, value, fill=False):
        if fill:
            pdf.set_fill_color(240, 243, 250)
        else:
            pdf.set_fill_color(255, 255, 255)
        pdf.set_text_color(60, 60, 60)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(90, 9, f"  {label}", fill=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(100, 9, str(value), fill=True, ln=True)

    kpi_row("Predicted Engagement Level", pred_eng.upper(), fill=False)
    kpi_row("AI Certainty Score", f"{confidence}%", fill=True)
    kpi_row("Live Google Trends Score", f"{live_score}/100 ({live_level})", fill=False)
    kpi_row("Estimated Audience Reach", f"{reach:,} people", fill=True)
    kpi_row("Audience Sentiment", sentiment, fill=False)
    kpi_row("Best Platform for Content", platform, fill=True)
    kpi_row("Best Time to Post", "6PM - 9PM (local time)", fill=False)
    pdf.ln(5)

    # ── Recommendations ──
    pdf.set_draw_color(252, 163, 17)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    pdf.set_text_color(252, 163, 17)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 9, "AI Recommendations", ln=True)
    pdf.set_text_color(40, 40, 40)
    pdf.set_font("Helvetica", "", 10)

    recommendations = [
        f"1. Post consistently 3-5 times per week on {platform} for sustained engagement.",
        f"2. Target audience in {region} during peak hours (6PM - 9PM local time).",
        f"3. Use 7-15 relevant hashtags per post for maximum discoverability.",
        f"4. Include a clear Call-to-Action (e.g., 'Save this', 'Tag a friend') to boost interaction.",
        f"5. Capitalize on the {sentiment.lower()} sentiment by responding to comments promptly.",
        f"6. Monitor competitor performance regularly using the Benchmarking module.",
    ]
    for rec in recommendations:
        pdf.multi_cell(0, 7, rec)
        pdf.ln(1)
    pdf.ln(5)

    # ── Dataset Stats (optional) ──
    if include_data:
        try:
            eng_df  = pd.read_csv(os.path.join(BASE_DIR, 'engagement.csv'))
            hash_df = pd.read_csv(os.path.join(BASE_DIR, 'hashtags.csv'))
            ts_df   = pd.read_csv(os.path.join(BASE_DIR, 'time_series.csv'))

            pdf.set_draw_color(252, 163, 17)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(5)
            pdf.set_text_color(252, 163, 17)
            pdf.set_font("Helvetica", "B", 13)
            pdf.cell(0, 9, "Live Dataset Snapshot", ln=True)
            pdf.set_text_color(40, 40, 40)
            pdf.set_font("Helvetica", "", 10)
            pdf.cell(0, 7, f"Instagram Posts Analyzed:  {len(eng_df):,}", ln=True)
            pdf.cell(0, 7, f"Hashtag Records Tracked:   {len(hash_df):,}", ln=True)
            pdf.cell(0, 7, f"YouTube Videos Analyzed:   {len(ts_df):,}", ln=True)

            if 'engagement_rate' in eng_df.columns:
                avg_eng = eng_df['engagement_rate'].mean()
                pdf.cell(0, 7, f"Average Dataset Engagement Rate: {avg_eng:.4f}", ln=True)
        except Exception:
            pass

    # ── Footer ──
    pdf.set_y(-20)
    pdf.set_draw_color(252, 163, 17)
    pdf.set_line_width(0.5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 8, f"Social Media Trend Analyzer · AI-Powered Report · Confidential · {datetime.now().year}", align="C", ln=True)

    return bytes(pdf.output())


if submitted:
    with st.spinner("Building your professional PDF report..."):
        pdf_bytes = generate_pdf(
            analyst_name, topic, platform, region,
            predicted_engagement, ai_confidence,
            estimated_reach, sentiment, exec_summary, include_data,
            live_score=live_score, live_level=live_level
        )

    st.success("✅ Report generated successfully! Click below to download.")

    st.download_button(
        label="📥 Download PDF Report",
        data=pdf_bytes,
        file_name=f"social_media_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

    st.markdown("---")
    st.markdown("### 👁️ Report Preview")

    st.markdown(f"""
    <div class='preview-box'>
        <div class='preview-title'>📌 Report Metadata</div>
        <div class='preview-text'>
            <b>Analyst:</b> {analyst_name} &nbsp;&nbsp;|&nbsp;&nbsp;
            <b>Topic:</b> {topic} &nbsp;&nbsp;|&nbsp;&nbsp;
            <b>Platform:</b> {platform} &nbsp;&nbsp;|&nbsp;&nbsp;
            <b>Region:</b> {region}<br>
            <b>Generated:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
        </div>
    </div>
    <div class='preview-box'>
        <div class='preview-title'>📊 Key AI Findings</div>
        <div class='preview-text'>
            <b>Predicted Engagement Level:</b> {predicted_engagement.upper()}<br>
            <b>AI Certainty Score:</b> {ai_confidence}%<br>
            <b>Estimated Reach:</b> {estimated_reach:,} people<br>
            <b>Audience Sentiment:</b> {sentiment}<br>
            <b>Best Posting Time:</b> 6PM – 9PM (local time)
        </div>
    </div>
    <div class='preview-box'>
        <div class='preview-title'>✍️ Executive Summary</div>
        <div class='preview-text'>{exec_summary}</div>
    </div>
    """, unsafe_allow_html=True)
