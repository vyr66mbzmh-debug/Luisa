#!/usr/bin/env python3
"""Provider-independent private, append-only usage observations. No credentials."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sys


def record(args, state):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,79}', args.task):
        raise ValueError('Use a simple task ID')
    if args.remaining is not None and not 0 <= args.remaining <= 100:
        raise ValueError('Remaining percentage must be between 0 and 100')
    path = state / 'usage.jsonl'
    previous = [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []
    last = next((r for r in reversed(previous) if r['task'] == args.task), None)
    if args.action == 'start' and last and last['event'] == 'start':
        raise ValueError('Task already started; end it or use a new task ID')
    if args.action == 'end' and (not last or last['event'] != 'start'):
        raise ValueError('No active start event for task')
    now = datetime.now(timezone.utc)
    row = dict(event=args.action, task=args.task, timestamp=now.isoformat(), provider=args.provider or (last or {}).get('provider'), model=args.model or (last or {}).get('model'), remainingPercent=args.remaining, resetAt=args.reset_at, reportedTaskTokens=args.tokens, artifacts=args.artifacts, rework=args.rework, elapsedSeconds=None, accountObservedDeltaPP=None, attribution='Unavailable; shared-account deltas are not exact task costs.')
    if args.action == 'end':
        row['elapsedSeconds'] = round((now - datetime.fromisoformat(last['timestamp'])).total_seconds(), 1)
        if args.reset_at and args.reset_at == last['resetAt'] and args.remaining is not None and last['remainingPercent'] is not None and args.remaining <= last['remainingPercent']:
            row['accountObservedDeltaPP'] = round(last['remainingPercent'] - args.remaining, 1)
    state.mkdir(parents=True, exist_ok=True)
    with path.open('a') as f:
        f.write(json.dumps(row, sort_keys=True) + '\n')
    os.chmod(path, 0o600)
    return row


def main():
    p = argparse.ArgumentParser()
    p.add_argument('action', choices=['start', 'end'])
    p.add_argument('task')
    p.add_argument('--provider')
    p.add_argument('--model')
    p.add_argument('--remaining', type=float)
    p.add_argument('--reset-at')
    p.add_argument('--tokens', type=int)
    p.add_argument('--artifacts', type=int)
    p.add_argument('--rework', type=int)
    args = p.parse_args()
    for n in ('tokens', 'artifacts', 'rework'):
        if getattr(args, n) is not None and getattr(args, n) < 0:
            p.error(n + ' must not be negative')
    state = Path(os.environ.get('LUISA_STATE_DIR', Path.home() / '.local/share/luisa-agent-state'))
    # Refuse a state folder inside this public repository.
    if state.resolve().is_relative_to(Path(__file__).resolve().parents[1]):
        p.error('Usage state must remain outside the public repository')
    try:
        row = record(args, state)
    except ValueError as e:
        p.error(str(e))
    print(json.dumps(row))


if __name__ == '__main__':
    main()
