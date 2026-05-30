import time
import random
from functools import wraps
from agents import build_search_agent, build_read_agent, writer_chain, critic_chain
from rich import print


def retry(max_attempts=3, base_delay=1.0, backoff=2.0, exceptions=(Exception,)):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts:
                        delay = base_delay * (backoff ** (attempt - 1)) + random.uniform(0, 0.5)
                        print(f"[bold yellow]⚠ Attempt {attempt}/{max_attempts} failed: {e}[/bold yellow]")
                        print(f"[dim]Retrying in {delay:.1f}s...[/dim]")
                        time.sleep(delay)
            raise last_exception
        return wrapper
    return decorator


def run_research_pipeline(query: str) -> dict:
    state = {}

    _retry = retry(max_attempts=3, base_delay=2.0)

    # Step 1: Search Agent
    print("\n" + "=" * 50 + "\n")
    print("[bold blue]Step 1: Search Agent[/bold blue]")
    print("\n" + "=" * 50 + "\n")
    try:
        search_agent = build_search_agent()
        invoke_search = _retry(search_agent.invoke)
        search_results = invoke_search({
            "messages": [
                {"role": "user", "content": f"Search the web for information on the following topic: {query}"}
            ]
        })
        state["search_results"] = search_results["messages"][-1].content
        print("[bold green]Search Results:[/bold green]")
        print(state["search_results"])
    except Exception as e:
        print(f"[bold red]✗ Search Agent failed after 3 attempts: {e}[/bold red]")
        state["search_results"] = f"No search results available due to: {e}"
        return state

    # Step 2: Read Agent
    print("\n" + "=" * 50 + "\n")
    print("[bold blue]Step 2: Read Agent is scraping content....[/bold blue]")
    print("\n" + "=" * 50 + "\n")
    try:
        read_agent = build_read_agent()
        invoke_read = _retry(read_agent.invoke)
        read_results = invoke_read({
            "messages": [
                {"role": "user",
                 "content": f"Given the following search results, scrape the content of the top URLs and summarize the key information found on each page:\n\n{state['search_results']}"}
            ]
        })
        raw = read_results["messages"][-1].content
        state["scraped_results"] = raw.split("\n\n") if raw else []
        print("[bold green]Content Summaries:[/bold green]")
        for idx, summary in enumerate(state["scraped_results"], 1):
            print(f"[bold yellow]Summary {idx}:[/bold yellow]\n{summary}\n")
    except Exception as e:
        print(f"[bold red]✗ Read Agent failed after 3 attempts: {e}[/bold red]")
        state["scraped_results"] = []

    # Step 3: Write Agent
    print("\n" + "=" * 50 + "\n")
    print("[bold blue]Step 3: Write Agent is generating report....[/bold blue]")
    print("\n" + "=" * 50 + "\n")
    try:
        research_combined = (
            f"Topic: {query}\n\n"
            f"Research gathered:\n{state.get('search_results', 'N/A')}\n\n"
            f"Content summaries:\n{state.get('scraped_results', 'N/A')}"
        )
        invoke_write = _retry(writer_chain.invoke)
        report = invoke_write({"topic": query, "research": research_combined})
        state["report"] = report
        print("[bold green]Generated Report:[/bold green]")
        print(state["report"])
    except Exception as e:
        print(f"[bold red]✗ Write Agent failed after 3 attempts: {e}[/bold red]")
        state["report"] = f"Report generation failed due to: {e}"
        return state

    # Step 4: Critic Agent
    print("\n" + "=" * 50 + "\n")
    print("[bold blue]Step 4: Critic Agent is reviewing the report.... [/bold blue]")
    print("\n" + "=" * 50 + "\n")
    try:
        invoke_critic = _retry(critic_chain.invoke)
        critique = invoke_critic({"report": state["report"]})
        state["critique"] = critique
        print("[bold green]Critique:[/bold green]")
        print(state["critique"])
    except Exception as e:
        print(f"[bold red]✗ Critic Agent failed after 3 attempts: {e}[/bold red]")
        state["critique"] = f"Critique generation failed due to: {e}"

    return state


if __name__ == "__main__":
    query = input("Enter a research topic: ")
    run_research_pipeline(query)
