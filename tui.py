import threading
import time
from dataclasses import dataclass, field
from typing import Optional

from rich.align import Align
from rich.console import Console, Group
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.prompt import Prompt
from rich.rule import Rule
from rich.table import Table
from rich.text import Text
from rich import box

from config import Settings
from pipeline import run_research_pipeline

console = Console()

STEP_NAMES = ["search", "reader", "writer", "critic"]
STEP_LABELS = {
    "search": "Search Agent",
    "reader": "Reader Agent",
    "writer": "Writer Chain",
    "critic": "Critic Chain",
}
STEP_DESCRIPTIONS = {
    "search": "Gathers recent web information",
    "reader": "Scrapes & extracts deep content",
    "writer": "Drafts the full research report",
    "critic": "Reviews & scores the report",
}


@dataclass
class PipelineState:
    steps: dict = field(default_factory=lambda: {
        name: {"status": "waiting", "output": ""} for name in STEP_NAMES
    })
    report: str = ""
    critique: str = ""
    running: bool = False
    done: bool = False
    topic: str = ""

    def reset(self):
        for s in self.steps.values():
            s["status"] = "waiting"
            s["output"] = ""
        self.report = ""
        self.critique = ""
        self.running = False
        self.done = False
        self.topic = ""

    @property
    def current_step(self) -> Optional[str]:
        for name in STEP_NAMES:
            if self.steps[name]["status"] == "running":
                return name
        return None

    @property
    def recent_output(self) -> str:
        for name in reversed(STEP_NAMES):
            out = self.steps[name]["output"]
            if out:
                return out
        return ""


def make_header() -> Panel:
    header = Group(
        Text("ResearchMesh", style="bold orange1", justify="center"),
        Text("Multi-Agent AI Research System", style="dim white", justify="center"),
    )
    return Panel(header, box=box.ROUNDED, border_style="orange1")


def make_pipeline_table(state: PipelineState) -> Table:
    table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    table.add_column(width=4)
    table.add_column(width=18)
    table.add_column(width=22)
    table.add_column(style="dim")

    for idx, name in enumerate(STEP_NAMES, 1):
        s = state.steps[name]
        status = s["status"]

        if status == "waiting":
            indicator = Text("  ", style="dim")
            label = Text("WAITING", style="dim")
        elif status == "running":
            indicator = Text("● ", style="bold orange1")
            label = Text("RUNNING", style="bold orange1")
        elif status == "done":
            indicator = Text("✓ ", style="bold green")
            label = Text("DONE   ", style="bold green")
        elif status == "error":
            indicator = Text("✗ ", style="bold red")
            label = Text("ERROR  ", style="bold red")

        table.add_row(
            f"0{idx}",
            STEP_LABELS[name],
            Text.assemble(indicator, label),
            STEP_DESCRIPTIONS[name],
        )

    return table


def make_output_panel(state: PipelineState) -> Panel:
    current = state.current_step
    output = state.recent_output

    if not state.running and not state.done:
        content = Text("Type a research topic to begin.", style="dim italic")
    elif not output:
        content = Text("Waiting for output...", style="dim italic")
    else:
        lines = output.split("\n")
        truncated = "\n".join(lines[:15])
        content = Text(truncated[:800])

    title = f"Output — {STEP_LABELS.get(current or '', '')}" if current else "Output"
    return Panel(content, title=title, border_style="bright_black", box=box.ROUNDED)


def make_report_panel(state: PipelineState) -> Panel:
    if not state.report:
        return Panel(
            Text("Report will appear here.", style="dim italic"),
            title="Report",
            border_style="bright_black",
            box=box.ROUNDED,
        )
    lines = state.report.split("\n")
    display = "\n".join(lines[:60])
    return Panel(display[:4000], title="Report", border_style="green", box=box.ROUNDED)


def make_critique_panel(state: PipelineState) -> Panel:
    if not state.critique:
        return Panel(
            Text("Critique will appear here.", style="dim italic"),
            title="Critique",
            border_style="bright_black",
            box=box.ROUNDED,
        )
    lines = state.critique.split("\n")
    display = "\n".join(lines[:30])
    return Panel(display[:2000], title="Critique", border_style="cyan", box=box.ROUNDED)


def make_footer(state: PipelineState) -> Panel:
    if state.running:
        return Panel(
            Text("Pipeline running...", style="bold orange1", justify="center"),
            box=box.ROUNDED,
            border_style="orange1",
        )
    if state.done:
        return Panel(
            Text("Done — type a new topic or /help for commands", style="bold green", justify="center"),
            box=box.ROUNDED,
            border_style="green",
        )
    return Panel(
        Text("Type a topic below or /help", style="dim", justify="center"),
        box=box.ROUNDED,
        border_style="bright_black",
    )


def make_layout(state: PipelineState) -> Layout:
    layout = Layout()
    layout.split_column(
        Layout(make_header(), size=5),
        Layout(name="body"),
        Layout(make_footer(state), size=3),
    )

    body = Layout()
    body.split_row(
        Layout(name="left", ratio=2),
        Layout(name="right", ratio=3),
    )

    pipeline_panel = Panel(
        make_pipeline_table(state),
        title="Pipeline",
        border_style="bright_black",
        box=box.ROUNDED,
    )

    left_content = Layout()
    left_content.split_column(
        Layout(pipeline_panel),
        Layout(make_output_panel(state)),
    )
    body["left"].update(left_content)

    right_content = Layout()
    right_content.split_column(
        Layout(make_report_panel(state)),
        Layout(make_critique_panel(state)),
    )
    body["right"].update(right_content)

    layout["body"].update(body)
    return layout


def print_welcome():
    console.clear()
    console.print()
    console.print(Panel(
        Align(Group(
            Text("⚡  ResearchMesh", style="bold orange1"),
            Text(""),
            Text("Four specialized AI agents collaborate —", style="dim"),
            Text("searching, scraping, writing, and critiquing", style="dim"),
            Text("— to deliver a polished research report.", style="dim"),
        ), align="center"),
        box=box.DOUBLE_EDGE,
        border_style="orange1",
        padding=(1, 2),
    ))
    console.print()


def print_results(state: PipelineState):
    if state.report:
        console.print()
        console.print(Rule(style="green"))
        console.print(Panel(
            state.report,
            title=" Report ",
            border_style="green",
            box=box.ROUNDED,
            subtitle=f"Topic: {state.topic}",
        ))
    if state.critique:
        console.print(Panel(
            state.critique,
            title=" Critique ",
            border_style="cyan",
            box=box.ROUNDED,
        ))


def show_help():
    console.print(Panel(
        "\n"
        "  [bold]Commands:[/bold]\n"
        "    [bold]/help[/bold]    Show this help\n"
        "    [bold]/quit[/bold]    Exit ResearchMesh\n"
        "    [bold]/clear[/bold]   Clear the screen\n"
        "    [bold]/save[/bold]    Save report to research_report.md\n"
        "\n"
        "  [bold]Usage:[/bold]\n"
        "    Just type a research topic and press Enter.\n"
        "    The pipeline runs four agents to produce a report.\n"
        ,
        title=" Help ",
        border_style="orange1",
        box=box.ROUNDED,
    ))


def make_callbacks(state: PipelineState):
    def on_step_start(name: str):
        state.steps[name]["status"] = "running"

    def on_step_complete(name: str, result: str):
        state.steps[name]["status"] = "done"
        state.steps[name]["output"] = result[:600]
        if name == "writer":
            state.report = result
        elif name == "critic":
            state.critique = result

    def on_error(name: str, error: str):
        state.steps[name]["status"] = "error"
        state.steps[name]["output"] = str(error)[:600]

    return on_step_start, on_step_complete, on_error


def run_tui():
    settings = Settings.load()
    missing = settings.validate()
    if missing:
        console.print(f"[bold red]Error:[/bold red] Missing environment variables: {', '.join(missing)}")
        console.print("[yellow]Tip:[/yellow] Create a .env file (see .env.example)")
        return

    print_welcome()
    state = PipelineState()

    while True:
        raw = Prompt.ask("[bold]Research topic[/bold]")
        raw = raw.strip()

        if not raw:
            continue

        if raw.startswith("/"):
            parts = raw.lower().split(maxsplit=1)
            cmd = parts[0]

            if cmd == "/quit":
                console.print("[dim]Goodbye![/dim]")
                break

            elif cmd == "/help":
                show_help()
                continue

            elif cmd == "/clear":
                console.clear()
                continue

            elif cmd == "/save":
                filename = parts[1] if len(parts) > 1 else "research_report.md"
                if not state.report:
                    console.print("[yellow]No report to save yet. Run a topic first.[/yellow]")
                    continue
                try:
                    with open(filename, "w") as f:
                        f.write(state.report)
                    console.print(f"[green]Report saved to {filename}[/green]")
                except OSError as e:
                    console.print(f"[red]Failed to save: {e}[/red]")
                continue

            else:
                console.print(f"[red]Unknown command: {cmd}. Try /help[/red]")
                continue

        # ---- Run pipeline ----
        state.reset()
        state.topic = raw
        on_step_start, on_step_complete, on_error = make_callbacks(state)
        state.running = True

        thread = threading.Thread(
            target=run_research_pipeline,
            args=(raw, on_step_start, on_step_complete, on_error),
            daemon=True,
        )
        thread.start()

        try:
            with Live(make_layout(state), refresh_per_second=10, screen=False) as live:
                while thread.is_alive():
                    live.update(make_layout(state))
                    time.sleep(0.1)
                thread.join()
        except KeyboardInterrupt:
            state.running = False
            console.print("\n[yellow]Interrupted.[/yellow]")
            continue

        state.running = False
        state.done = True

        # Show results after Live exits
        print_results(state)


if __name__ == "__main__":
    run_tui()
