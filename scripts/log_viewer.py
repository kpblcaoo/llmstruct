import argparse
import json
from pathlib import Path
from tabulate import tabulate
from datetime import datetime
from collections import Counter


def parse_date(date_str):
    # Поддержка форматов YYYY-MM-DD и YYYY-MM-DDTHH:MM:SS
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(date_str, fmt)
        except Exception:
            continue
    raise ValueError(f"Invalid date format: {date_str}")

def load_log(log_path):
    with open(log_path, 'r', encoding='utf-8') as f:
        return [json.loads(line) for line in f if line.strip()]

def filter_log(log, epic=None, event_type=None, author=None, request_id=None, from_date=None, to_date=None):
    result = log
    if epic:
        result = [e for e in result if e.get('epic') == epic]
    if event_type:
        result = [e for e in result if e.get('event_type') == event_type]
    if author:
        result = [e for e in result if e.get('author') == author]
    if request_id:
        result = [e for e in result if e.get('request_id') == request_id]
    if from_date:
        from_dt = parse_date(from_date)
        result = [e for e in result if 'timestamp' in e and parse_date(e['timestamp'][:19]) >= from_dt]
    if to_date:
        to_dt = parse_date(to_date)
        result = [e for e in result if 'timestamp' in e and parse_date(e['timestamp'][:19]) <= to_dt]
    return result

def aggregate_log(log, field='event_type'):
    counter = Counter(e.get(field, 'unknown') for e in log)
    return counter.items()

def main():
    parser = argparse.ArgumentParser(description='View and filter event_log.jsonl')
    parser.add_argument('--log', type=str, default='data/epic_logs/logging_transparency_audit/event_log.jsonl', help='Path to event_log.jsonl')
    parser.add_argument('--epic', type=str, help='Filter by epic')
    parser.add_argument('--event-type', type=str, help='Filter by event_type')
    parser.add_argument('--author', type=str, help='Filter by author')
    parser.add_argument('--request-id', type=str, help='Filter by request_id')
    parser.add_argument('--from-date', type=str, help='Filter from date (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)')
    parser.add_argument('--to-date', type=str, help='Filter to date (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)')
    parser.add_argument('--aggregate', action='store_true', help='Aggregate by event_type')
    parser.add_argument('--format', type=str, choices=['json', 'table'], default='table', help='Output format')
    args = parser.parse_args()

    log = load_log(args.log)
    filtered = filter_log(log, args.epic, args.event_type, args.author, args.request_id, args.from_date, args.to_date)

    if args.aggregate:
        agg = aggregate_log(filtered, field='event_type')
        print(tabulate(agg, headers=['event_type', 'count'], tablefmt='grid'))
        return

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