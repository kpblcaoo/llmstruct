import argparse
import json
from pathlib import Path

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def show_links(args):
    epic_id = args.epic_id
    link_type = args.type or 'all'
    status_filter = args.status or 'all'
    fmt = args.format or 'markdown'
    base = Path('data/sessions')
    epic_path = base / f'{epic_id}.json'
    if not epic_path.exists():
        print(f"❌ Epic roadmap not found: {epic_path}")
        return
    epic = load_json(epic_path)
    # Словарь: тип → (поле, файл, ключ)
    link_map = {
        'tasks':    ('related_tasks',    '../tasks.json',    'tasks'),
        'ideas':    ('related_ideas',    '../ideas.json',    'ideas'),
        'insights': ('related_insights', '../insights.json', 'insights'),
        'prs':      ('related_prs',      '../prs.json',      'pull_requests'),
    }
    results = {}
    for t, (epic_field, json_file, json_key) in link_map.items():
        if link_type != 'all' and link_type != t:
            continue
        ids = epic.get(epic_field, [])
        if not ids:
            continue
        data = load_json(base / json_file)
        items = data.get(json_key, [])
        found = [item for item in items if item.get('id') in ids]
        if status_filter != 'all':
            found = [item for item in found if str(item.get('status', '')).lower() == status_filter.lower()]
        results[t] = found
    # Вывод
    if fmt == 'json':
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return
    if fmt == 'table':
        for t, items in results.items():
            print(f"\n=== {t.upper()} ===")
            for item in items:
                print(f"{item.get('id'):<10} | {item.get('title', item.get('description', '')):<40} | {item.get('status', ''):<12} | {item.get('priority', '')}")
        return
    # markdown (default)
    for t, items in results.items():
        print(f"\n### Связанные {t}:")
        for item in items:
            title = item.get('title', item.get('description', ''))
            status = item.get('status', '')
            prio = item.get('priority', '')
            print(f"- **{item.get('id')}**: {title} — {status}, priority: {prio}")

def add_epic_cli_subparser(subparsers):
    epic_parser = subparsers.add_parser('epic', help='Epic management commands')
    epic_sub = epic_parser.add_subparsers(dest='epic_cmd')
    show_links_parser = epic_sub.add_parser('show-links', help='Show all linked tasks/ideas/insights/prs for epic')
    show_links_parser.add_argument('epic_id', help='Epic id (example: epic_llmstruct_code_quality)')
    show_links_parser.add_argument('--type', choices=['tasks','ideas','insights','prs','all'], default='all', help='Type of links to show')
    show_links_parser.add_argument('--status', default='all', help='Status filter (open, closed, in_progress, all)')
    show_links_parser.add_argument('--format', choices=['markdown','json','table'], default='markdown', help='Output format')
    show_links_parser.set_defaults(func=show_links) 