from crewai import Task
from agents.agents import (
    research_agent,
    financial_data_agent,
    risk_analyst_agent,
    analysis_agent,
    report_writer_agent
)

def create_tasks(ticker: str):

    research_task = Task(
        description=f"""Search for the latest news, events, and developments 
        about {ticker}. Look for earnings reports, product launches, 
        management changes, and market sentiment.
        Be concise. Do NOT describe what the company does — focus only on 
        recent events and news from the last 3 months.""",
        expected_output="""A concise bullet point summary of the 5 most 
        important recent news items with dates and their potential 
        impact on the stock price. No company background.""",
        agent=research_agent
    )

    financial_data_task = Task(
        description=f"""Pull the live financial data for {ticker} and analyze 
        the key metrics. Focus only on the numbers and what they mean.
        Do NOT describe the company background.
        Compare each metric to industry averages where possible.""",
        expected_output="""A clean table of key metrics with a one line 
        interpretation of each number. Include:
        Price, Market Cap, P/E Ratio, Revenue, Profit Margin, 
        52 Week High/Low, and one sentence verdict on financial health.""",
        agent=financial_data_agent
    )

    risk_task = Task(
        description=f"""Assess the risk profile of {ticker} in 3 clear areas:
        1. Market Risk — volatility and beta
        2. Business Risk — competitive threats and operational risks  
        3. Macro Risk — economic and regulatory factors
        Do NOT repeat financial metrics already covered. 
        Do NOT describe what the company does.""",
        expected_output="""Three short paragraphs covering each risk area.
        End with an overall risk rating: LOW, MEDIUM, or HIGH 
        with one sentence justification.""",
        agent=risk_analyst_agent
    )

    analysis_task = Task(
        description=f"""Based on the research, financial data and risk assessment 
        for {ticker}, produce a final investment recommendation.
        Do NOT repeat any data or news already mentioned.
        Focus only on your synthesis and conclusion.""",
        expected_output="""A recommendation of BUY, HOLD, or SELL.
        A confidence score from 1-10.
        Three bullet points: key reasons FOR the recommendation.
        Two bullet points: key risks AGAINST the recommendation.""",
        agent=analysis_agent
    )

    report_task = Task(
        description=f"""Write a professional financial report for {ticker}.
        Use the outputs from previous agents.
        
        STRICT RULES:
        - Do NOT repeat the company description more than once
        - Each section must contain ONLY new information
        - Keep each section under 150 words
        - Use bullet points instead of long paragraphs
        - Start with a one paragraph executive summary only
        
        Structure:
        1. Executive Summary (1 short paragraph)
        2. Recent News (bullet points only)
        3. Financial Metrics (key numbers only)
        4. Risk Assessment (3 bullet points)
        5. Investment Recommendation (BUY/HOLD/SELL + reasoning)""",
        expected_output="""A structured report with exactly 5 sections.
        Each section clearly labeled.
        Bullet points used throughout.
        No repetition between sections.
        Total length under 600 words.""",
        agent=report_writer_agent
    )

    return [
        research_task,
        financial_data_task,
        risk_task,
        analysis_task,
        report_task
    ]