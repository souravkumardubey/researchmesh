import os
import warnings
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
from langchain.tools import tool
from dotenv import load_dotenv
from rich import print

import urllib3
warnings.filterwarnings("ignore", category=urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

session = requests.Session()
session.verify = False

tavily_api_key = os.getenv("TAVILY_API_KEY")
mistral_api_key = os.getenv("MISTRAL_API_KEY")

tavily_client = TavilyClient(api_key=tavily_api_key, session=session)

@tool("web_search", return_direct=True)
def web_search(query: str) -> str:
    """Search the web for most accurate and reliable information on a topic. Returns titles, URLs and snippets of the top results."""
    results = tavily_client.search(query, num_results=5)
    
    output = []

    for r in results["results"]:
        title = r.get("title", "No title")
        url = r.get("url", "No URL")
        content = r.get("content", "No content")[:300]
        output.append(f"Title: {title}\nURL: {url}\nSnippet: {content}\n")

    return "\n---\n".join(output)


@tool("web_scrape", return_direct=True)
def web_scrape(url: str) -> str:
    """Scrape the content of a web page. Returns the main text content."""
    try:
        response = session.get(url, timeout=10, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        })
        soup = BeautifulSoup(response.text, 'html.parser')
        for tag in soup(["script", "style", "header", "footer", "nav", "textarea", "p", "a"]):
            tag.decompose()
        text = soup.get_text(separator="\n", strip=True)
        return text[:3000] if text else "No content found"
    except Exception as e:
        return f"Error scraping {url}: {e}"

# print(web_search.invoke("recipe for gobi manchurian"))
print(web_scrape.invoke("https://resumeworded.com/resume-scanner"))