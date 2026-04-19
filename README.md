<div align="center">

# 📈 Financial Analysis Agent Crew

### An AI-powered multi-agent system that automates the entire stock research workflow
### From live data collection to professional PDF report generation

[![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square&logo=python)](https://python.org)
[![CrewAI](https://img.shields.io/badge/CrewAI-Multi--Agent-purple?style=flat-square)](https://crewai.com)
[![Flask](https://img.shields.io/badge/Flask-Web%20UI-black?style=flat-square&logo=flask)](https://flask.palletsprojects.com)
[![Groq](https://img.shields.io/badge/Groq-LLaMA%204-orange?style=flat-square)](https://groq.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

</div>

---

## 📋 Table of Contents
- [Project Overview](#-project-overview)
- [Features](#-features)
- [Technology Stack](#-technology-stack)
- [Getting Started](#-getting-started)
- [How It Works](#-how-it-works)
- [Disclaimer](#-disclaimer)

---

## 🔍 Project Overview

This project is a fully automated financial research system powered by a crew of **5 specialized AI agents**. You enter a stock ticker (e.g. `AAPL`, `NVDA`, `TSLA`) and the system automatically:

- 🔎 Researches the company using real-time web search
- 📊 Pulls live financial data from Yahoo Finance
- ⚠️ Assesses investment risk
- ✅ Synthesizes a Buy / Hold / Sell recommendation
- 📄 Generates a downloadable professional PDF report

> **All without any human doing the legwork.**

It supports both **single stock analysis** and **multi-stock comparison** with side-by-side charts. All prices are automatically converted to the user's local currency based on their region.

This project demonstrates how AI agents can replace expensive, time-consuming human workflows in financial research — a process that typically costs **thousands of dollars per report** when done manually.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🤖 5 Specialist Agents | Each agent handles one part of the research workflow |
| 📡 Live Financial Data | Real-time prices, P/E ratio, revenue, profit margin, market cap |
| 🔍 Real-Time Web Search | Latest news and events via Serper API |
| ✅ Investment Signal | Buy, Hold, or Sell with confidence score |
| 📄 PDF Report | Professional report with charts and visual analysis |
| 📈 Price History Chart | 12-month line chart showing trend and % change |
| 📏 52-Week Gauge | Visual indicator of where stock sits in its yearly range |
| ⚖️ Multi-Stock Comparison | Side-by-side bar charts and summary table |
| 💱 Currency Conversion | Prices shown in INR, KRW, GBP, EUR, USD etc. based on location |
| 🌐 Flask Web UI | Clean interface with real-time agent progress updates |
| 🛡️ Error Handling | Invalid ticker detection and graceful failure recovery |

---

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| Agent Framework | [CrewAI](https://crewai.com) |
| LLM | LLaMA 4 Scout via [Groq](https://groq.com) |
| LLM Bridge | LiteLLM |
| Stock Data | yfinance (Yahoo Finance) |
| Web Search | [Serper API](https://serper.dev) |
| Charts | Matplotlib |
| PDF Generation | ReportLab |
| Web UI | Flask + HTML/CSS |
| Currency Detection | ipapi.co |
| Language | Python 3.12 |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.12
- A [Groq API key](https://console.groq.com) — free
- A [Serper API key](https://serper.dev) — free tier gives 2,500 searches

### Setup Instructions

**1. Clone the repository**
```bash
git clone https://github.com/arpita-mac/financial-analyst-crew.git
cd financial-analyst-crew
```

**2. Create a virtual environment**
```bash
python -m venv venv

# Mac/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Set up API keys**

Create a `.env` file in the root folder:
```
GROQ_API_KEY=your_groq_key_here
SERPER_API_KEY=your_serper_key_here
```

### How to Run

**Option 1 — Web UI (recommended)**
```bash
python app.py
```
Open `http://localhost:5000` in your browser.

**Option 2 — Command line**
```bash
python main.py
```
Follow the prompts to enter a ticker or compare multiple stocks.

---

## ⚙️ How It Works

The system runs **5 AI agents in sequence**, each passing their output to the next:

```
User Input (ticker)
       ↓
🔍 Research Agent      → Searches latest news and events
       ↓
📊 Financial Data Agent → Pulls live stock data
       ↓
⚠️  Risk Analyst Agent  → Assesses market, business and macro risk
       ↓
✅ Analysis Agent       → Synthesizes Buy / Hold / Sell signal
       ↓
📝 Report Writer Agent  → Writes and formats the final PDF report
       ↓
📄 PDF Report (download)
```

**The PDF report includes:**
1. Executive Summary
2. Recent News & Sentiment
3. Financial Metrics
4. Risk Assessment
5. Investment Recommendation

---

## ⚠️ Disclaimer

This project generates AI-powered analysis for **informational purposes only**. It is **not financial advice**. Always consult a qualified financial advisor before making any investment decisions.

---



</div>