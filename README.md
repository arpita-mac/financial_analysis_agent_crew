Financial Analysis Agent Crew
An AI-powered multi-agent system that automates the entire stock research workflow — from live data collection to professional PDF report generation.
Table of Contents

Project Overview
Features
Technology Stack
Getting Started

Prerequisites
Setup Instructions
How to Run


How It Works
Disclaimer

Project Overview
This project is a fully automated financial research system powered by a crew of 5 specialized AI agents. You enter a stock ticker (e.g. AAPL, NVDA, TSLA) and the system automatically researches the company, pulls live financial data, assesses risk, synthesizes an investment recommendation, and generates a downloadable PDF report — all without any human doing the legwork.
It supports both single stock analysis and multi-stock comparison with side-by-side charts. All prices are automatically converted to the user's local currency based on their region.
This project demonstrates how AI agents can replace expensive, time-consuming human workflows in financial research — a process that typically costs thousands of dollars per report when done manually.
Features

5 specialist AI agents — each handling one part of the research workflow
Live financial data — real-time stock prices, P/E ratio, revenue, profit margin, market cap
Real-time web search — latest news and events via Serper API
Investment recommendation — Buy, Hold, or Sell with confidence score
Professional PDF report — with charts, analysis, and visual signals
12-month price history chart — line chart showing trend and % change
52-week price range gauge — visual indicator of where stock sits in its range
Multi-stock comparison — side-by-side bar charts and summary table
Local currency conversion — prices shown in INR, KRW, GBP, EUR, USD etc. based on user location
Flask web UI — clean, professional interface with real-time progress updates
Error handling — invalid ticker detection and graceful failure recovery

Technology Stack
ComponentTechnologyAgent FrameworkCrewAILLMLLaMA 4 Scout via GroqLLM BridgeLiteLLMStock Datayfinance (Yahoo Finance)Web SearchSerper APIChartsMatplotlibPDF GenerationReportLabWeb UIFlask + HTML/CSSCurrency Detectionipapi.coLanguagePython 3.12
Getting Started
Prerequisites

Python 3.12
A Groq API key (free)
A Serper API key (free tier: 2,500 searches)

Setup Instructions
1. Clone the repository
bashgit clone https://github.com/yourusername/financial-analyst-crew.git
cd financial-analyst-crew
2. Create a virtual environment
bashpython -m venv venv

# Mac/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
3. Install dependencies
bashpip install -r requirements.txt
4. Set up API keys
Create a .env file in the root folder:
GROQ_API_KEY=your_groq_key_here
SERPER_API_KEY=your_serper_key_here
How to Run
Option 1 — Web UI (recommended)
bashpython app.py
Open http://localhost:5000 in your browser.
Option 2 — Command line
bashpython main.py
Follow the prompts to enter a ticker or compare multiple stocks.
How It Works
The system runs 5 AI agents in sequence, each passing their output to the next:
AgentRoleResearch AgentSearches the web for latest news, earnings, and eventsFinancial Data AgentPulls live stock data from Yahoo FinanceRisk Analyst AgentAssesses market, business, and macro riskAnalysis AgentSynthesizes everything into a Buy/Hold/Sell signalReport Writer AgentWrites and formats the final professional report
The PDF report includes:

Executive Summary
Recent News
Financial Metrics
Risk Assessment
Investment Recommendation

Disclaimer
This project is AI-generated analysis for informational purposes only. It is not financial advice. Always consult a qualified financial advisor before making investment decisions.

