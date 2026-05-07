# 🔮 Social Media Trend Analyzer

> **AI-powered social media intelligence platform** that combines Machine Learning with **live Google Trends data** to give brands, influencers, and marketers the most accurate, real-time predictions — across every module, for every topic.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.3+-F7931E?style=flat-square&logo=scikit-learn&logoColor=white)
![Google Trends](https://img.shields.io/badge/Google%20Trends-Live%20Data-4285F4?style=flat-square&logo=google&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## ✨ What Makes This Different

Most analytics tools rely on **static, pre-trained data** that goes stale quickly. This platform is built around a **dual-intelligence engine**:

| Layer | What it does |
|---|---|
| 🧠 **ML Models** | Trained on 50K+ historical posts — learns patterns from platform, media type, region, hour |
| 📡 **Live Google Trends** | Fetches real-time interest scores (0–100) for any hashtag/topic/niche via `pytrends` |
| ⚡ **Blended Score** | 70% live data + 30% ML = the most accurate prediction possible, always current |

Results are **cached for 1 hour** for speed, then auto-refreshed — so the app never shows stale predictions.

---

## 🚀 Live Modules

### 🏠 Dashboard
- **Live Market Pulse** — real-time Google Trends scores for 8 content niches (Technology, Fitness, Fashion, Finance, Gaming, Food, Travel, Education)
- **🔥 Trending Now** — live feed of top 10 globally trending topics pulled from Google Trends
- Dataset KPI cards + engagement charts

### 🔮 Trend Predictor
- Type **any hashtag** (e.g. `#AI`, `#ChatGPT`, `#fitness`, `#crypto`)
- Fetches **live Google Trends score** for that exact keyword
- Blends with ML model → outputs **Viral / High / Medium / Low**
- Shows **30-day interest sparkline chart** from Google Trends
- Displays **related rising queries** alongside prediction
- **Trending Now** widget with live topics

### 📊 Post Analyzer & Engagement Forecaster
- Predict engagement rate **before** you post
- Fetches **live trend score for your content category** (e.g. Technology = 92/100 Viral)
- Applies a **real-time trend multiplier** to the ML engagement rate:
  - Viral niche → ×1.4 boost
  - High niche → ×1.2 boost
  - Low niche → ×0.85 dampening
- **Upgrades/downgrades performance bucket** based on live market conditions
- Live **category interest sparkline** embedded in results
- AI Viral Caption & Hook Generator with clipboard copy

### 🔍 Hashtag Clustering Explorer
- **Live Hashtag Trend Check** — type any hashtag and instantly see its Google Trends score + sparkline
- **Trending Now** tab with live Google Trends feed
- **Head-to-Head Hashtag Comparison** — compare up to 3 hashtags with a live 3-month trend chart
- AI K-Means clustering of 10K+ hashtags on an interactive PCA scatter map
- Filter by Platform and Region

### 📋 Data Explorer
- **Live Market Pulse header** — 8 niche trend scores shown above all data tables
- Filter and explore raw engagement, hashtag, and YouTube data
- Download filtered CSVs
- Summary statistics charts

### 🏆 Competitor Benchmarking
- **Live niche trend scores** for both your niche and competitor's niche
- Niche engagement multiplier is **data-driven from Google Trends** (not hardcoded)
- Radar chart + absolute value comparison
- AI-simulated competitor profile

### 🎭 Audience Sentiment Analyzer
- **Live Google Trends score** fetched for any topic before analysis
- Sentiment weights **calibrated by real market momentum** (high-trending topics → more positive sentiment)
- Brand Health Score gauge + Sentiment breakdown pie chart
- Live Comment Feed simulation

### 📄 Report Generator
- **Live Google Trends score displayed** before PDF generation
- PDF report includes a **"Live Google Trends Score"** KPI row
- Fully professional PDF with AI findings, recommendations, and data tables
- One-click download

---

## 🛠️ Technology Stack

| Category | Technologies |
|---|---|
| **UI Framework** | Streamlit 1.30+ |
| **Language** | Python 3.10+ |
| **Live Data** | `pytrends` (Google Trends API — free, no key required) |
| **ML / Data Science** | Scikit-learn, Pandas, NumPy, SciPy |
| **Visualization** | Plotly, Matplotlib, Seaborn |
| **PDF Generation** | fpdf2 |
| **Model Persistence** | joblib |
| **Deployment** | Streamlit Community Cloud |

---

## 📦 Installation & Setup

### Option 1: Run Locally

```bash
# 1. Clone the repository
git clone https://github.com/PrathamKhawani/Social_Media_Trend_Analyzer.git
cd Social_Media_Trend_Analyzer

# 2. Create a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Mac/Linux

# 3. Install all dependencies
pip install -r requirements.txt

# 4. Train the ML models (first time only)
python "Social Media Trend Analyzer/utils/model_trainer.py"

# 5. Launch the app
streamlit run "Social Media Trend Analyzer/Dashboard.py"
```

### Option 2: Deploy on Streamlit Cloud (Free)

1. Fork this repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **New app** → select your fork
4. Set **Main file path** to: `Social Media Trend Analyzer/Dashboard.py`
5. Click **Deploy** — done! ✅

> Streamlit Cloud **auto-redeploys** every time you push to `main`. No manual steps needed.

---

## 📂 Project Structure

```
Social_Media_Trend_Analyzer/
├── requirements.txt                        # All Python dependencies
├── README.md
│
└── Social Media Trend Analyzer/
    ├── Dashboard.py                        # 🏠 Main entry point
    │
    ├── pages/
    │   ├── 1_🔮_Trend_Predictor.py        # Live Google Trends + ML blend
    │   ├── 2_📊_Post_Analyzer.py          # Post simulation + trend multiplier
    │   ├── 3_🔍_Hashtag_Explorer.py       # Live hashtag check + comparison
    │   ├── 4_📋_Data_Explorer.py          # Market pulse + raw data
    │   ├── 5_🏆_Competitor_Benchmarking.py# Live niche scores
    │   ├── 6_🎭_Sentiment_Analyzer.py     # Trend-calibrated sentiment
    │   └── 7_📄_Report_Generator.py       # PDF with live score
    │
    ├── utils/
    │   ├── trend_fetcher.py               # 📡 Live Google Trends engine
    │   ├── model_trainer.py               # ML model training pipeline
    │   ├── data_updater.py                # Synthetic data generator
    │   └── ui.py                          # Global CSS / design system
    │
    ├── models/                            # Pre-trained .pkl model files
    │   ├── trend_predictor.pkl
    │   ├── performance_classifier.pkl
    │   ├── engagement_regressor.pkl
    │   └── hashtag_clustering.pkl
    │
    ├── engagement.csv                     # Instagram engagement dataset
    ├── hashtags.csv                       # Hashtag performance dataset
    └── time_series.csv                    # YouTube trending dataset
```

---

## 🧠 How the Live Data Engine Works

```
User types "#AI"
      ↓
trend_fetcher.py → pytrends → Google Trends API
      ↓
Returns: Interest Score = 92/100 (last 30 days average)
      ↓
Blended Score = (92 × 0.7) + (ML score × 0.3) = 84
      ↓
Final Result: 🔥 VIRAL  |  AI Certainty: 95%
      ↓
Cached for 1 hour → auto-refreshes next load
```

**Graceful fallback:** If Google rate-limits the request, the engine silently falls back to a curated keyword intelligence cache — the app **never crashes**.

---

## 📊 ML Models

| Model | Algorithm | Purpose |
|---|---|---|
| `trend_predictor.pkl` | Random Forest Classifier | Predict Viral/High/Medium/Low for any Platform+Region combo |
| `performance_classifier.pkl` | Gradient Boosting Classifier | Predict post performance bucket |
| `engagement_regressor.pkl` | Random Forest Regressor | Predict exact engagement rate % |
| `hashtag_clustering.pkl` | K-Means + PCA | Group hashtags by behavior similarity |

---

## 🤝 Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request.

1. Fork the repo
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with ❤️ using Python, Streamlit, and Google Trends**

*Turning raw social media data into actionable intelligence — in real time.*

</div>
