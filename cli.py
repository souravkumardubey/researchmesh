import typer
from typing import Optional

from config import Settings
from pipeline import run_research_pipeline

app = typer.Typer(
    name="researchmesh",
    help="Multi-Agent AI Research System — Search, scrape, write, and critique on any topic.",
    no_args_is_help=True,
)


@app.command()
def run(
    topic: Optional[str] = typer.Argument(
        None, help="Research topic. Omit to launch the interactive TUI."
    ),
    output: Optional[str] = typer.Option(
        None, "-o", "--output", help="Save report to a file (markdown)."
    ),
    verbose: bool = typer.Option(
        False, "-v", "--verbose", help="Show pipeline step output in terminal."
    ),
):
    """Research a topic through the multi-agent pipeline.

    Provide a topic as an argument for a single-shot run,
    or omit it to launch the interactive terminal UI.
    """
    if not topic:
        from tui import run_tui
        run_tui()
        return

    settings = Settings.load()
    missing = settings.validate()
    if missing:
        typer.echo(f"Missing environment variables: {', '.join(missing)}", err=True)
        typer.echo("Create a .env file (see .env.example)", err=True)
        raise typer.Exit(1)

    result = run_research_pipeline(topic)

    if output:
        content = result.get("report", "")
        if content:
            with open(output, "w") as f:
                f.write(content)
            typer.echo(f"Report saved to {output}")
        else:
            typer.echo("No report generated.", err=True)
    elif verbose:
        typer.echo(result.get("report", "No report generated."))
    else:
        typer.echo("Done. Use --verbose to see the report, or -o to save it.")


@app.command()
def version():
    """Show the installed version."""
    typer.echo("ResearchMesh v0.1.0")


if __name__ == "__main__":
    app()
