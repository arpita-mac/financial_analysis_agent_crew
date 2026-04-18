import yfinance as yf
from crewai.tools import tool

@tool("Stock Data Tool")
def stock_data_tool(ticker: str) -> str:
    """Fetches live stock data for a given ticker symbol."""
    try:
        stock = yf.Ticker(ticker)
        info  = stock.info

        if not info or info.get('regularMarketPrice') is None and info.get('currentPrice') is None:
            return f"Error: '{ticker}' does not appear to be a valid stock ticker. Please check the symbol and try again."

        data = f"""
        Company: {info.get('longName', 'N/A')}
        Sector: {info.get('sector', 'N/A')}
        Current Price: ${info.get('currentPrice', 'N/A')}
        Market Cap: ${info.get('marketCap', 'N/A')}
        P/E Ratio: {info.get('trailingPE', 'N/A')}
        Revenue: ${info.get('totalRevenue', 'N/A')}
        Profit Margin: {info.get('profitMargins', 'N/A')}
        52 Week High: ${info.get('fiftyTwoWeekHigh', 'N/A')}
        52 Week Low: ${info.get('fiftyTwoWeekLow', 'N/A')}
        Analyst Recommendation: {info.get('recommendationKey', 'N/A')}
        """
        return data

    except Exception as e:
        return f"Error fetching data for '{ticker}': {str(e)}. Please verify the ticker symbol is correct."