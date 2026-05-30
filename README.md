# ResearchMesh

**A Multi-Agent AI Research System**

ResearchMesh is an experimental multi-agent pipeline that processes user queries through a chain of specialized AI agents. Each agent plays a distinct role — searching the web, reading and extracting content, storing data, and refining results into structured research.

This is a personal project exploring multi-agent orchestration using LangChain, Mistral AI, and Tavily.

## Architecture

```
User Query
    │
    ▼
┌─────────────┐
│  Search     │  Searches web using Tavily API
│  Agent      │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Read       │  Scrapes and extracts page content
│  Agent      │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Store      │  Stores raw research data
│  Agent      │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Refine     │  Synthesizes findings into final output
│  Agent      │
└──────┬──────┘
       │
       ▼
    Response
```

## Tools

| Tool | Description | Powered By |
|------|-------------|------------|
| `web_search` | Searches the web and returns top results with snippets | Tavily API |
| `web_scrape` | Extracts readable content from a given URL | requests + BeautifulSoup |

## Tech Stack

- **Orchestration**: LangChain
- **LLM**: Mistral AI
- **Search**: Tavily
- **Scraping**: requests, BeautifulSoup, lxml
- **Language**: Python 3.14

## Getting Started

```bash
# Clone the repo
git clone https://github.com/souravkumardubey/researchmesh.git
cd researchmesh

# Create virtual environment and install deps
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Add your API keys to .env

# Run tools
python tools.py
```

## Environment Variables

```
TAVILY_API_KEY=your_tavily_api_key
MISTRAL_API_KEY=your_mistral_api_key
```
