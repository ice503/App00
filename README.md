# 📱 Forex Strategy Analyzer

*A mobile-friendly app for backtesting forex trading strategies, deployable entirely from your phone.*

![App Screenshot](https://via.placeholder.com/300x600?text=Mobile+App+Preview)

## 🌟 Features
- **Strategies Included**:
  - SMA Crossover (10/30 default)
  - RSI (14-period default)
- **Data Sources**:
  - Real-time via Yahoo Finance API
  - Daily/Hourly timeframes
- **Metrics**:
  - Sharpe Ratio
  - Max Drawdown
  - Win Rate
  - Portfolio Growth

## 📲 Mobile Deployment Guide

### 1. One-Click Deploy
[![Deploy to Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/deploy?repository=yourusername/forex-strategy-analyzer)

*or*

### 2. Manual Setup
```bash
# Clone repository (in Termux/Terminal)
git clone https://github.com/yourusername/forex-strategy-analyzer

# Install dependencies
pip install -r requirements.txt

# Run locally (if supported)
streamlit run app.py
