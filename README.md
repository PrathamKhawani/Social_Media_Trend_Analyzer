# 🔮 Social Media Trend Analyzer

An advanced, AI-powered analytics dashboard designed to help brands, influencers, and marketers understand social media trends, predict engagement, and optimize their content strategy.

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Machine Learning](https://img.shields.io/badge/Scikit--Learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)

---

## 🚀 Key Features

- **🔮 Trend Predictor**: Forecast future trends using machine learning models trained on historical social media data.
- **📊 Post Analyzer**: Deep dive into individual post performance metrics like likes, shares, and comments.
- **🔍 Hashtag Explorer**: Identify high-velocity hashtags and discover related keywords to boost reach.
- **🏆 Competitor Benchmarking**: Compare your performance against industry rivals to identify gaps and opportunities.
- **🎭 Sentiment Analyzer**: Understand the emotional tone of audience comments and mentions.
- **📋 Data Explorer**: Interactive data tables to filter and export raw performance data.
- **📄 Report Generator**: Export professional PDF/CSV reports with one click.

---

## 🛠️ Technology Stack

- **Frontend**: [Streamlit](https://streamlit.io/) (Modern, responsive web UI)
- **Backend**: Python 3.x
- **Data Science**: Pandas, NumPy
- **Machine Learning**: Scikit-learn (Random Forest, Clustering)
- **Visualization**: Plotly, Matplotlib, Seaborn

---

## 📦 Installation & Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/PrathamKhawani/Social_Media_Trend_Analyzer.git
   cd Social_Media_Trend_Analyzer
   ```

2. **Create a Virtual Environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**
   ```bash
   streamlit run Dashboard.py
   ```

---

## 📂 Project Structure

```text
Social Media Trend Analyzer/
├── Dashboard.py              # Main entry point
├── pages/                    # Multi-page application modules
│   ├── 1_🔮_Trend_Predictor.py
│   ├── 2_📊_Post_Analyzer.py
│   └── ...
├── utils/                    # Shared logic & UI components
├── models/                   # Pre-trained ML models (.pkl)
└── data/                     # Sample datasets (.csv)
```

---

## 🤝 Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request if you have ideas for new features or improvements.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
