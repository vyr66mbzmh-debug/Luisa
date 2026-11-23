#!/usr/bin/env python3
"""Sum per-call token usage from session transcripts, for the OPS-063 token log.

Engine-neutral contract: a transcript is a JSON Lines file in which model calls carry
`message.id` and `message.usage` (integer fields such as input_tokens, output_tokens,
cache_creation_input_tokens, cache_read_input_tokens). The last record per call id wins.
Engines that record usage differently should report their own per-call totals; when no counter
is available, say "token counts unavailable" and name what was used instead (scripts/usage.py).

Usage:
  python3 scripts/release/tokens.py baseline --transcript T.jsonl --state <file>   # remember calls so far
  python3 scripts/release/tokens.py since    --transcript T.jsonl --state <file>   # totals after the baseline
  python3 scripts/release/tokens.py total    --transcript A.jsonl [--transcript B.jsonl ...]  # e.g. review agents
  python3 scripts/release/tokens.py total    --transcript T.jsonl --after 2026-11-23T07:35:49Z     # calls after the job started
Transcripts and state files are private (keep them in the private state folder); only totals are published.
"""
import argparse
import json
from pathlib import Path

FIELDS = ('input_tokens', 'cache_creation_input_tokens', 'cache_read_input_tokens', 'output_tokens')


def calls(paths, after=None):
    found = {}
    for path in paths:
        for line in Path(path).open(errors='replace'):
            try:
                record = json.loads(line)
            except ValueError:
                continue
            message = record.get('message')
            if after and str(record.get('timestamp', '')) < after:
                continue
            if isinstance(message, dict) and message.get('id') and isinstance(message.get('usage'), dict):
                found[message['id']] = message['usage']
    return found


def summarise(usages):
    totals = {f: sum(int(u.get(f) or 0) for u in usages) for f in FIELDS}
    totals['calls'] = len(usages)
    totals['total'] = sum(totals[f] for f in FIELDS)
    return totals


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('command', choices=['baseline', 'since', 'total'])
    parser.add_argument('--transcript', action='append', required=True)
    parser.add_argument('--state', type=Path)
    parser.add_argument('--after', help='ISO UTC timestamp; only records at or after it count (records need a timestamp field)')
    args = parser.parse_args()
    found = calls(args.transcript, args.after)
    if args.command == 'baseline':
        args.state.write_text(json.dumps(sorted(found)))
        print(json.dumps({'baselineCalls': len(found)}))
    elif args.command == 'since':
        old = set(json.loads(args.state.read_text()))
        print(json.dumps(summarise([u for k, u in found.items() if k not in old])))
    else:
        print(json.dumps(summarise(list(found.values()))))


if __name__ == '__main__':
    main()
