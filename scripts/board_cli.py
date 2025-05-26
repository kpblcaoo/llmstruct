#!/usr/bin/env python3
"""
CLI Kanban Board for llmstruct tasks and ideas
- Reads data/tasks.json and data/ideas.json
- Shows board in terminal: columns by status, rows by priority
- Supports filtering, sorting, and shows links between tasks/ideas
"""
import json
import os
from pathlib import Path
from collections import defaultdict
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

DATA_DIR = Path(__file__).parent / "data"
TASKS_FILE = DATA_DIR / "tasks.json"
IDEAS_FILE = DATA_DIR / "ideas.json"

STATUSES = ["proposed", "in_progress", "completed", "needs_review", "archived"]
PRIORITIES = ["critical", "high", "medium", "low", "unknown"]

console = Console()

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def group_by_status_and_priority(items, kind="task"):
    board = {status: defaultdict(list) for status in STATUSES}
    for item in items:
        status = item.get("status", "proposed")
        priority = item.get("priority", "unknown")
        board[status][priority].append(item)
    return board

def render_board(board, kind="task"):
    for status in STATUSES:
        table = Table(title=f"{kind.capitalize()}s: {status}", box=box.SIMPLE, show_lines=True)
        table.add_column("Priority", style="bold")
        table.add_column("ID", style="cyan")
        table.add_column("Title/Description", style="white")
        table.add_column("Assignee", style="magenta")
        table.add_column("Links", style="yellow")
        for priority in PRIORITIES:
            for item in board[status][priority]:
                id_ = item.get("id", "?")
                desc = item.get("title") or item.get("description", "")
                assignee = item.get("assignee", "")
                # Show links (dependencies, related_idea, etc)
                links = []
                if kind == "task" and item.get("related_idea"):
                    links.append(f"idea:{item['related_idea']}")
                if kind == "idea" and item.get("related_tasks"):
                    links.extend([f"task:{tid}" for tid in item["related_tasks"]])
                if item.get("dependencies"):
                    links.extend([f"dep:{d}" for d in item["dependencies"]])
                if item.get("ai-generated", False):
                    desc = "🤖 " + desc
                if "Placeholder" in desc:
                    desc = "⚠️ " + desc
                table.add_row(priority, id_, desc, assignee, ", ".join(links))
        console.print(Panel(table, title=f"[bold]{kind.capitalize()}s: {status}", expand=False))

def main():
    tasks_data = load_json(TASKS_FILE)
    ideas_data = load_json(IDEAS_FILE)
    tasks = tasks_data.get("tasks", [])
    ideas = ideas_data.get("ideas", [])
    console.rule("[bold green]Tasks Board")
    render_board(group_by_status_and_priority(tasks, "task"), kind="task")
    console.rule("[bold blue]Ideas Board")
    render_board(group_by_status_and_priority(ideas, "idea"), kind="idea")

if __name__ == "__main__":
    main()
