from agents import build_search_agent, build_read_agent, writer_chain, critic_chain
from rich import print

def run_research_pipeline(query: str) -> dict:

    state = {}

    # Step 1: Search Agent
    print("\n" + "="*50 + "\n")
    print("[bold blue]Step 1: Search Agent[/bold blue]")
    print("\n" + "="*50 + "\n")
    search_agent = build_search_agent()
    search_results = search_agent.invoke({
        "messages": [
            {"role": "user", "content": f"Search the web for information on the following topic: {query}"}
        ]
    })
    
    state["search_results"] = search_results["messages"][-1].content

    print("[bold green]Search Results:[/bold green]")
    print(state["search_results"])

    # Step 2: Read Agent
    print("\n" + "="*50 + "\n")
    print("[bold blue]Step 2: Read Agent is scraping content....[/bold blue]")
    print("\n" + "="*50 + "\n")
    read_agent = build_read_agent() 
    read_results = read_agent.invoke({
        "messages": [
            {"role": "user", "content": f"Given the following search results, scrape the content of the top URLs and summarize the key information found on each page:\n\n{state['search_results']}"}
        ]
    })
    
    content_summaries = read_results["messages"][-1].content.split("\n\n")
    state["scraped_results"] = content_summaries
    print("[bold green]Content Summaries:[/bold green]")
    for idx, summary in enumerate(content_summaries, 1):
        print(f"[bold yellow]Summary {idx}:[/bold yellow]\n{summary}\n")
         
    # Step 3: Write Agent
    print("\n" + "="*50 + "\n")
    print("[bold blue]Step 3: Write Agent is generating report....[/bold blue]")
    print("\n" + "="*50 + "\n")
    research_combined = (
        f"Topic: {query}\n\n"
        f"Research gathered:\n{state['search_results']}\n\n"
        f"Content summaries:\n{state['scraped_results']}"
    )
    report = writer_chain.invoke({"topic": query, "research": research_combined})
    state["report"] = report
    print("[bold green]Generated Report:[/bold green]")
    print(state["report"])

    # Step 4: Critic Agent
    print("\n" + "="*50 + "\n")
    print("[bold blue]Step 4: Critic Agent is reviewing the report.... [/bold blue]")
    print("\n" + "="*50 + "\n")
    critique = critic_chain.invoke({"report": state["report"]})
    state["critique"] = critique
    print("[bold green]Critique:[/bold green]")
    print(state["critique"])
    
    return state

if __name__ == "__main__":
    query = input("Enter a research topic: ")
    run_research_pipeline(query)