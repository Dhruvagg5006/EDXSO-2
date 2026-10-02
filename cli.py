"""
Command-Line Interface for Scholarship Intelligence Crawler.
Provides commands to run crawls, inspect evidence, view changes, and check system metrics.
"""

import argparse
import sys
import json
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

# Add current directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.crawler.crawler_engine import CrawlerEngine
from src.database.repository import ScholarshipRepository
import config

import os
import sys

# Ensure UTF-8 output on Windows
if sys.platform.startswith("win"):
    os.system("")  # Enable VT100
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

console = Console(highlight=False)


def run_crawl(run_number: int):
    engine = CrawlerEngine()
    if run_number == 1:
        console.print("[bold cyan]>>> Launching Run 1 (Initial Base Crawl)...[/bold cyan]")
        run_record = engine.run_initial_crawl()
        console.print(Panel(
            f"[bold green][SUCCESS] Run 1 Finished Successfully![/bold green]\n"
            f"Run ID: {run_record.run_id}\n"
            f"Total Discovered: {run_record.total_discovered}\n"
            f"Total Verified (>=95%): {run_record.total_verified}\n"
            f"Review Required (<95%): {run_record.total_review_required}\n"
            f"Expired Tracked: {run_record.total_expired_detected}\n"
            f"Database: {config.DATABASE_PATH}",
            title="Crawler Execution Summary",
            border_style="green"
        ))
    elif run_number == 2:
        console.print("[bold yellow]>>> Launching Run 2 (Consecutive Crawl with Change Detection)...[/bold yellow]")
        run_record, changes = engine.run_consecutive_crawl()
        console.print(Panel(
            f"[bold green][SUCCESS] Run 2 Finished Successfully![/bold green]\n"
            f"Run ID: {run_record.run_id}\n"
            f"Total Re-crawled: {run_record.total_discovered}\n"
            f"Changes Detected: [bold magenta]{len(changes)}[/bold magenta]\n"
            f"Expired Records Tracked: {run_record.total_expired_detected}",
            title="Consecutive Crawl & Change Detection Summary",
            border_style="yellow"
        ))
        if changes:
            table = Table(title="Detected Field-Level Changes (Audit Trail)", border_style="magenta")
            table.add_column("Scholarship ID", style="cyan")
            table.add_column("Field", style="yellow")
            table.add_column("Old Value", style="red")
            table.add_column("New Value", style="green")
            table.add_column("Detected At", style="dim")
            for c in changes:
                table.add_row(
                    c["scholarship_id"],
                    c["field_name"],
                    str(c["old_value"])[:45],
                    str(c["new_value"])[:45],
                    c["detected_at"][:19]
                )
            console.print(table)
    else:
        console.print(f"[red]Invalid run number: {run_number}. Choose 1 or 2.[/red]")


def list_scholarships():
    repo = ScholarshipRepository()
    records = repo.list_scholarships()
    if not records:
        console.print("[yellow]No scholarships in database. Run 'python cli.py crawl --run 1' first.[/yellow]")
        return

    table = Table(title=f"Indexed Scholarships ({len(records)} Records)", border_style="cyan")
    table.add_column("Name", style="bold white", width=36)
    table.add_column("Provider Type", style="cyan", width=22)
    table.add_column("Amount", style="green", width=24)
    table.add_column("Deadline", style="yellow", width=12)
    table.add_column("Status", width=15)
    table.add_column("Confidence", justify="right", style="bold magenta", width=12)
    table.add_column("Verification", width=16)

    for r in records:
        status_color = "green" if r.status.value == "ACTIVE" else ("red" if r.status.value == "EXPIRED" else "yellow")
        v_color = "bold green" if r.verification_status.value == "VERIFIED" else "bold yellow"
        table.add_row(
            r.scholarship_name[:35],
            r.provider_type.value[:20],
            r.amount_benefit[:22],
            r.closing_date,
            f"[{status_color}]{r.status.value}[/{status_color}]",
            f"{r.confidence_score:.1f}%",
            f"[{v_color}]{r.verification_status.value}[/{v_color}]"
        )
    console.print(table)


def inspect_scholarship(slug_id: str):
    repo = ScholarshipRepository()
    rec = repo.get_scholarship(slug_id)
    if not rec:
        console.print(f"[red]Scholarship '{slug_id}' not found in database.[/red]")
        return

    console.print(Panel(
        f"[bold cyan]{rec.scholarship_name}[/bold cyan]\n"
        f"[dim]Provider:[/dim] {rec.provider} ({rec.provider_type.value})\n"
        f"[dim]Official Source:[/dim] {rec.official_source_url}\n"
        f"[dim]Application URL:[/dim] {rec.application_url}\n"
        f"[dim]Amount / Benefit:[/dim] {rec.amount_benefit}\n"
        f"[dim]Academic Requirements:[/dim] {rec.academic_requirements}\n"
        f"[dim]Income Criteria:[/dim] {rec.income_criteria}\n"
        f"[dim]Gender / Category:[/dim] {rec.gender_criteria.value if hasattr(rec.gender_criteria, 'value') else rec.gender_criteria} | {rec.category_criteria}\n"
        f"[dim]Domicile / Institution:[/dim] {rec.domicile_state} | {rec.institution_requirements}\n"
        f"[dim]Closing Deadline:[/dim] {rec.closing_date} ({rec.status.value})\n"
        f"[dim]Confidence Score:[/dim] [bold magenta]{rec.confidence_score:.1f}%[/bold magenta] ([bold]{rec.verification_status.value}[/bold])",
        title="Scholarship Universal Record",
        border_style="cyan"
    ))

    # Evidence Breakdown
    if rec.evidence_items:
        ev_table = Table(title="Field-Level Grounded Evidence Audit Trail", border_style="green")
        ev_table.add_column("Field", style="cyan", width=22)
        ev_table.add_column("Extracted Value", style="white", width=30)
        ev_table.add_column("Verbatim Evidence Quote from Official DOM", style="yellow")
        for ev in rec.evidence_items:
            ev_table.add_row(ev.field_name, ev.extracted_value[:28], ev.evidence_text[:85])
        console.print(ev_table)

    # Why this score?
    if rec.score_breakdown:
        score_table = Table(title="Explainable 6-Pillar Confidence Scorecard (Why this score?)", border_style="magenta")
        score_table.add_column("Pillar Evaluation Item", style="white")
        for r in rec.score_breakdown.reasons:
            score_table.add_row(r)
        console.print(score_table)


def show_history():
    repo = ScholarshipRepository()
    history = repo.get_history()
    if not history:
        console.print("[yellow]No changes logged yet. Run 'python cli.py crawl --run 2' to test change detection.[/yellow]")
        return

    table = Table(title=f"Change Detection Audit Log ({len(history)} Changes Tracked)", border_style="magenta")
    table.add_column("Scholarship", style="cyan", width=30)
    table.add_column("Field", style="yellow", width=18)
    table.add_column("Previous (Old) Value", style="red", width=30)
    table.add_column("Detected New Value", style="green", width=30)
    table.add_column("Detected At", style="dim", width=20)
    for h in history:
        table.add_row(
            h["scholarship_name"][:28],
            h["field_name"],
            h["old_value"][:28],
            h["new_value"][:28],
            h["detected_at"][:19]
        )
    console.print(table)


def show_metrics():
    repo = ScholarshipRepository()
    m = repo.get_analytics_metrics()
    console.print(Panel(
        f"[bold white]Total Discovered Scholarships:[/bold white] {m['total_discovered']}\n"
        f"[bold green]Verified (>=95%):[/bold green] {m['total_verified']}\n"
        f"[bold yellow]Review Required (<95%):[/bold yellow] {m['total_review_required']}\n"
        f"[bold blue]Active Scholarships:[/bold blue] {m['total_active']}\n"
        f"[bold red]Expired Scholarships:[/bold red] {m['total_expired']}\n"
        f"[bold magenta]Average Confidence:[/bold magenta] {m['avg_confidence']}%\n"
        f"[bold cyan]Historical Changes Detected:[/bold cyan] {m['total_changes']}\n"
        f"[bold white]Distinct Source Types:[/bold white] {m['source_types_count']} ({', '.join(m['source_types'])})",
        title="Scholarship Intelligence KPI Metrics",
        border_style="blue"
    ))


def main():
    parser = argparse.ArgumentParser(description="Scholarship Intelligence Engine CLI")
    subparsers = parser.add_subparsers(dest="command")

    crawl_parser = subparsers.add_parser("crawl", help="Run crawler cycle")
    crawl_parser.add_argument("--run", type=int, choices=[1, 2], default=1, help="1 for Base Crawl, 2 for Consecutive Crawl")

    subparsers.add_parser("list", help="List all indexed scholarships")

    inspect_parser = subparsers.add_parser("inspect", help="Inspect a scholarship record")
    inspect_parser.add_argument("slug_id", type=str, help="Scholarship slug id (e.g., reliance-foundation-ug-scholarship)")

    subparsers.add_parser("history", help="View change detection audit log")
    subparsers.add_parser("metrics", help="View intelligence KPI metrics")

    args = parser.parse_args()

    if args.command == "crawl":
        run_crawl(args.run)
    elif args.command == "list":
        list_scholarships()
    elif args.command == "inspect":
        inspect_scholarship(args.slug_id)
    elif args.command == "history":
        show_history()
    elif args.command == "metrics":
        show_metrics()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
