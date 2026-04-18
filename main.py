from crewai import Crew, Process
from tasks.tasks import create_tasks
from pdf_generator import generate_pdf, generate_comparison_pdf
from dotenv import load_dotenv
import os
import time

load_dotenv()

def validate_ticker(ticker: str) -> bool:
    """Check if a ticker is valid before running the full analysis."""
    try:
        import yfinance as yf
        info = yf.Ticker(ticker).info
        return bool(info and (info.get('currentPrice') or info.get('regularMarketPrice')))
    except:
        return False

def run_analysis(ticker: str) -> str:
    """Run the full agent crew analysis for a single ticker."""
    try:
        from agents.agents import (
            research_agent,
            financial_data_agent,
            risk_analyst_agent,
            analysis_agent,
            report_writer_agent
        )

        print(f"\n Starting Financial Analysis for {ticker}...\n")

        tasks = create_tasks(ticker)

        crew = Crew(
            agents=[
                research_agent,
                financial_data_agent,
                risk_analyst_agent,
                analysis_agent,
                report_writer_agent
            ],
            tasks=tasks,
            process=Process.sequential,
            verbose=False
        )

        result = crew.kickoff()
        return str(result)

    except Exception as e:
        return f"Analysis failed for {ticker}: {str(e)}"

if __name__ == "__main__":
    mode = input("Single stock (1) or Compare multiple stocks (2)? Enter 1 or 2: ").strip()

    if mode == "1":
        ticker = input("Enter stock ticker (e.g. AAPL): ").upper().strip()

        if not ticker:
            print("❌ No ticker entered.")
        elif not validate_ticker(ticker):
            print(f"❌ '{ticker}' is not a valid stock ticker. Please check the symbol and try again.")
        else:
            result = run_analysis(ticker)
            if result.startswith("Analysis failed"):
                print(f"\n❌ {result}")
            else:
                generate_pdf(ticker, result)
                print("\n✅ Analysis complete! Check your output folder.")

    elif mode == "2":
        raw     = input("Enter tickers separated by commas (e.g. AAPL, TSLA): ")
        tickers = [t.strip().upper() for t in raw.split(",") if t.strip()]

        if len(tickers) < 2:
            print("❌ Please enter at least 2 tickers separated by commas.")
        else:
            print("\n🔍 Validating tickers...")
            valid_tickers = []
            for ticker in tickers:
                if validate_ticker(ticker):
                    valid_tickers.append(ticker)
                    print(f"  ✅ {ticker} is valid")
                else:
                    print(f"  ❌ {ticker} is not valid — skipping")

            if len(valid_tickers) < 2:
                print("\n❌ Need at least 2 valid tickers to run a comparison.")
            else:
                results = {}
                for i, ticker in enumerate(valid_tickers):
                    print(f"\n🔍 Analyzing {ticker}...")
                    results[ticker] = run_analysis(ticker)
                    if i < len(valid_tickers) - 1:
                        print(f"\n⏳ Waiting 30 seconds before next stock...")
                        time.sleep(30)

                generate_comparison_pdf(results)
                print("\n✅ Comparison complete! Check your output folder.")

    else:
        print("❌ Invalid option. Please enter 1 or 2.")