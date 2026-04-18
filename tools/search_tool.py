import requests
import os
from crewai.tools import tool

@tool("Web Search Tool")
def web_search_tool(query: str) -> str:
    """Searches the web for recent news and information about a company."""
    try:
        api_key = os.getenv("SERPER_API_KEY")

        if not api_key:
            return "Error: SERPER_API_KEY not found. Please check your .env file."

        url     = "https://google.serper.dev/search"
        payload = {"q": query, "num": 5}
        headers = {
            "X-API-KEY": api_key,
            "Content-Type": "application/json"
        }

        response = requests.post(url, json=payload, headers=headers, timeout=10)

        if response.status_code != 200:
            return f"Search API error: status code {response.status_code}. Proceeding with available data."

        results = response.json()
        output  = ""

        for item in results.get("organic", []):
            output += f"Title: {item.get('title')}\n"
            output += f"Summary: {item.get('snippet')}\n"
            output += f"Link: {item.get('link')}\n\n"

        return output if output else "No search results found. Proceeding with available data."

    except requests.exceptions.Timeout:
        return "Search timed out. Proceeding with available data."
    except requests.exceptions.ConnectionError:
        return "No internet connection for search. Proceeding with available data."
    except Exception as e:
        return f"Search error: {str(e)}. Proceeding with available data."