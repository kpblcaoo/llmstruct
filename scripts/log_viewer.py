import argparse
import json
from pathlib import Path
from tabulate import tabulate


def load_log(log_path):
    with open(log_path, 'r', encoding='utf-8') as f:
        return [json.loads(line) for line in f if line.strip()]

def filter_log(log, epic=None, event_type=None, author=None, request_id=None):
    result = log
    if epic:
        result = [e for e in result if e.get('epic') == epic]
    if event_type:
        result = [e for e in result if e.get('event_type') == event_type]
    if author:
        result = [e for e in result if e.get('author') == author]
    if request_id:
        result = [e for e in result if e.get('request_id') == request_id]
    return result

def main():
    parser = argparse.ArgumentParser(description='View and filter event_log.jsonl')
    parser.add_argument('--log', type=str, default='data/epic_logs/logging_transparency_audit/event_log.jsonl', help='Path to event_log.jsonl')
    parser.add_argument('--epic', type=str, help='Filter by epic')
    parser.add_argument('--event-type', type=str, help='Filter by event_type')
    parser.add_argument('--author', type=str, help='Filter by author')
    parser.add_argument('--request-id', type=str, help='Filter by request_id')
    parser.add_argument('--format', type=str, choices=['json', 'table'], default='table', help='Output format')
    args = parser.parse_args()

    log = load_log(args.log)
    filtered = filter_log(log, args.epic, args.event_type, args.author, args.request_id)

    if args.format == 'json':
        print(json.dumps(filtered, ensure_ascii=False, indent=2))
    else:
        if not filtered:
            print('No records found.')
            return
        headers = filtered[0].keys()
        rows = [ [e.get(h, '') for h in headers] for e in filtered ]
        print(tabulate(rows, headers=headers, tablefmt='grid'))

if __name__ == '__main__':
    main() 