from crewai import Agent, LLM
from tools.stock_tool import stock_data_tool
from tools.search_tool import web_search_tool
import os
from dotenv import load_dotenv

load_dotenv()

llm = LLM(
    model="groq/meta-llama/llama-4-scout-17b-16e-instruct",
    api_key=os.getenv("GROQ_API_KEY")
)

research_agent = Agent(
    role="Financial Research Analyst",
    goal="Find the latest news and events about the company",
    backstory="""You are an expert financial research analyst with 
    10 years of experience tracking market news and company events. 
    You are thorough, accurate and always find the most relevant information.""",
    tools=[web_search_tool],
    llm=llm,
    verbose=False,
    memory=False
)

financial_data_agent = Agent(
    role="Financial Data Specialist",
    goal="Pull and analyze live financial data for the company",
    backstory="""You are a financial data expert who specializes in 
    interpreting stock metrics, ratios and financial statements. 
    You turn raw numbers into meaningful insights.""",
    tools=[stock_data_tool],
    llm=llm,
    verbose=False,
    memory=False
)

risk_analyst_agent = Agent(
    role="Risk Analyst",
    goal="Assess the risk profile of the stock",
    backstory="""You are a seasoned risk analyst who evaluates market 
    volatility, beta, and macroeconomic factors to determine 
    the risk level of any investment.""",
    tools=[stock_data_tool, web_search_tool],
    llm=llm,
    verbose=False,
    memory=False
)

analysis_agent = Agent(
    role="Investment Analyst",
    goal="Synthesize all research and data into a clear investment signal",
    backstory="""You are a senior investment analyst who takes research, 
    financial data and risk assessments and produces clear, 
    actionable investment recommendations.""",
    tools=[],
    llm=llm,
    verbose=False,
    memory=False
)

report_writer_agent = Agent(
    role="Financial Report Writer",
    goal="Write a professional financial analysis report",
    backstory="""You are an expert financial writer who transforms 
    complex analysis into clear, professional reports that 
    both experts and beginners can understand.""",
    tools=[],
    llm=llm,
    verbose=False,
    memory=False
)
