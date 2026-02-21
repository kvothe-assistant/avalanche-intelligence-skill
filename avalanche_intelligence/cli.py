"""CLI interface for Avalanche Intelligence."""

import asyncio
import click
from rich.console import Console
from rich.table import Table

from .config import ConfigManager
from .engine import IntelligenceEngine

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def main():
    """Avalanche Intelligence - Real-time Avalanche ecosystem monitoring and analysis."""
    pass


@main.command()
@click.option("--hours", type=int, default=24, help="Hours of data to scan")
@click.option("--sources", type=str, default="all", help="Comma-separated list of sources")
def scan(hours: int, sources: str):
    """Scan and collect data from multiple sources."""
    config = ConfigManager.load()

    sources_list = sources.split(",") if sources != "all" else []

    with console.status(f"[bold green]Scanning for last {hours} hours..."):
        engine = IntelligenceEngine(config)
        results = asyncio.run(engine.scan(hours=hours, sources=sources_list))

    if results:
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Source", style="cyan")
        table.add_column("Posts Collected", style="green")
        table.add_column("Signals Found", style="yellow")
        table.add_column("Duration", style="blue")

        for result in results:
            table.add_row(
                result["source"],
                str(result["posts_collected"]),
                str(result["signals_found"]),
                f"{result['duration']:.1f}s"
            )

        console.print(table)

        console.print(f"\n[bold green]✓ Scan complete![/bold white]")
    else:
        console.print("[bold red]No results found.")


@main.command()
@click.option("--daemon", is_flag=True, help="Run as background daemon")
@click.option("--interval", type=int, default=900, help="Check interval in seconds")
def watch(daemon: bool, interval: int):
    """Watch mode - Continuous monitoring with alerts."""
    config = ConfigManager.load()

    if daemon:
        console.print("[bold green]Starting watch daemon...")
        console.print(f"  Check interval: {interval} seconds ({interval//60}m)")
        console.print("[dim]Press Ctrl+C to stop[/dim]")

        engine = IntelligenceEngine(config)
        asyncio.run(engine.watch_daemon(interval=interval))
    else:
        console.print("[bold yellow]Watch mode requires --daemon flag")


@main.command()
@click.option("--timeframe", type=str, default="24h", help="Time period (24h, 7d, 30d)")
@click.option("--format", type=click.Choice(["markdown", "json", "html"]), default="markdown")
def report(timeframe: str, format: str):
    """Generate intelligence report."""
    config = ConfigManager.load()

    with console.status("[bold green]Generating report..."):
        engine = IntelligenceEngine(config)
        report_data = asyncio.run(engine.generate_report(timeframe=timeframe, format=format))

    console.print(f"\n[bold cyan]Report generated:[/bold white] {timeframe}")
    console.print(f"  Sources: {report_data['summary']['total_sources']}")
    console.print(f"  Items: {report_data['summary']['total_items']}")
    console.print(f"  Signals: {report_data['summary']['total_signals']}")


@main.command()
@click.option("--query", type=str, required=True, help="Search query")
@click.option("--source", type=str, default="all", help="Filter by source")
@click.option("--deep", is_flag=True, help="Deep search with more results")
def search(query: str, source: str, deep: bool):
    """Search across all collected data."""
    config = ConfigManager.load()

    with console.status(f"[bold green]Searching:[/bold white] {query}..."):
        engine = IntelligenceEngine(config)
        results = asyncio.run(engine.search(query=query, source=source, deep=deep))

    if results:
        console.print(f"\n[bold cyan]Found {len(results)} results:[/bold white]\n")

        table = Table(show_header=True)
        table.add_column("Relevance", style="magenta")
        table.add_column("Source", style="cyan")
        table.add_column("Content Preview", style="white")
        table.add_column("Date", style="dim")

        for result in results[:20]:  # Show top 20
            content = result.get("content", "")
            preview = content[:50] + "..." if len(content) > 50 else content

            table.add_row(
                f"{result['relevance']:.2f}",
                result["source"],
                preview,
                result.get("timestamp", "")[:19]
            )

        console.print(table)

        if len(results) > 20:
            console.print(f"\n[dim]...and {len(results) - 20} more[/dim]")
    else:
        console.print("[bold red]No results found.")


@main.command()
def init():
    """Initialize Avalanche Intelligence configuration."""
    console.print("[bold green]Initializing Avalanche Intelligence...\n")

    try:
        config_path = ConfigManager.create_default()
        console.print(f"\n[bold green]✓ Initialization complete![/bold white]")
        console.print(f"\nConfiguration created: {config_path}")
        console.print("\nNext steps:")
        console.print("  1. Edit [cyan]config/config.yaml[/cyan] with your API keys")
        console.print("  2. Run [cyan]avalanche-intelligence scan --hours 24[/cyan]")
        console.print("  3. Run [cyan]avalanche-intelligence watch --daemon[/cyan]")
    except Exception as e:
        console.print(f"[bold red]Error initializing:[/bold white] {e}")


@main.command()
def status():
    """Show current system status."""
    config = ConfigManager.load()

    engine = IntelligenceEngine(config)
    status_info = asyncio.run(engine.get_status())

    console.print("\n[bold green]Avalanche Intelligence Status[/bold green]\n")

    # System status
    console.print("📊 System:")
    console.print(f"  Active Sources: [cyan]{status_info['sources_count']}[/cyan]")
    console.print(f"  Total Posts: [cyan]{status_info['total_posts']}[/cyan]")
    console.print(f"  Signals Found: [cyan]{status_info['total_signals']}[/cyan]")

    # Storage status
    console.print("\n💾 Storage:")
    console.print(f"  Raw Data: [cyan]{status_info['storage_raw_size_mb']:.1f} MB[/cyan]")
    console.print(f"  Processed: [cyan]{status_info['storage_processed_size_mb']:.1f} MB[/cyan]")
    console.print(f"  Vector DB: [cyan]{status_info['vector_db_status']}[/cyan]")

    # Collector status
    if status_info.get('collectors'):
        console.print("\n🔍 Collectors:")
        for name, active in status_info['collectors'].items():
            status_icon = "[green]✓[/green]" if active else "[red]✗[/red]"
            console.print(f"  {status_icon} {name}: {'Active' if active else 'Inactive'}")


@main.command()
def test():
    """Test the installation."""
    console.print("[bold green]Testing Avalanche Intelligence installation...\n")

    errors = []

    # Check dependencies
    try:
        import aiohttp
        console.print("[green]✓[/green] aiohttp installed")
    except ImportError:
        console.print("[red]✗[/red] aiohttp not installed")
        errors.append("aiohttp")

    try:
        import yaml
        console.print("[green]✓[/green] pyyaml installed")
    except ImportError:
        console.print("[red]✗[/red] pyyaml not installed")
        errors.append("pyyaml")

    try:
        from rich.console import Console
        console.print("[green]✓[/green] rich installed")
    except ImportError:
        console.print("[red]✗[/red] rich not installed")
        errors.append("rich")

    # Check optional dependencies
    try:
        import praw
        console.print("[green]✓[/green] praw installed (Reddit)")
    except ImportError:
        console.print("[yellow]−[/yellow] praw not installed (Reddit support disabled)")

    try:
        import vaderSentiment
        console.print("[green]✓[/green] vaderSentiment installed (Sentiment)")
    except ImportError:
        console.print("[yellow]−[/yellow] vaderSentiment not installed (Sentiment disabled)")

    # Check config
    try:
        config = ConfigManager.load()
        console.print("[green]✓[/green] Configuration loaded")

        # Show enabled sources
        enabled = []
        if config.twitter.enabled:
            enabled.append("Twitter")
        if config.reddit.enabled:
            enabled.append("Reddit")
        if enabled:
            console.print(f"  Enabled sources: {', '.join(enabled)}")
        else:
            console.print("  [yellow]No sources enabled (edit config.yaml)[/yellow]")
    except Exception as e:
        console.print(f"[red]✗[/red] Configuration error: {e}")
        errors.append("config")

    console.print()
    if not errors:
        console.print("[bold green]✓ All tests passed![/bold white]")
        console.print("\nRun 'avalanche-intelligence init' to create a config file.")
    else:
        console.print(f"[bold red]✗ Missing dependencies: {', '.join(errors)}[/bold white]")
        console.print("\nInstall with: pip install -r requirements.txt")


if __name__ == "__main__":
    main()
