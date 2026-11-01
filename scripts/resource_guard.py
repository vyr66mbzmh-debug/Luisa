#!/usr/bin/env python3
"""One local heavy job slot. No processes killed and no automatic stale takeover."""
import argparse
import json
import os
from pathlib import Path
import sys
import time

p = argparse.ArgumentParser()
p.add_argument('action', choices=['acquire', 'release', 'status'])
p.add_argument('owner')
a = p.parse_args()
state = Path(os.environ.get('LUISA_STATE_DIR', Path.home() / '.local/share/luisa-agent-state'))
state.mkdir(parents=True, exist_ok=True)
slot = state / 'heavy.lock'
if a.action == 'acquire':
    try:
        slot.mkdir()
    except FileExistsError:
        raise SystemExit('Heavy slot occupied; inspect status and wait. No automatic stale takeover.')
    (slot / 'owner.json').write_text(json.dumps({'owner': a.owner, 'time': time.time()}))
elif a.action == 'release':
    row = json.loads((slot / 'owner.json').read_text())
    if row['owner'] != a.owner:
        raise SystemExit('Refusing to release another owner slot')
    (slot / 'owner.json').unlink()
    slot.rmdir()
else:
    print((slot / 'owner.json').read_text() if slot.exists() else 'free')
