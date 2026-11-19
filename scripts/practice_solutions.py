#!/usr/bin/env python3
"""Validate authored practice solutions without accepting answer-only rows.

The JSON files are deliberately separate from the question extraction catalogue.
Run with --catalogue to require an exact source-question match. SymPy checks use
the optional local authoring environment, never the shipped browser runtime.
"""
import argparse
import json
from pathlib import Path


def validate(path, known_ids=None):
    data = json.loads(path.read_text())
    ids = set()
    for row in data['solutions']:
        ident = row['id']
        if ident in ids:
            raise ValueError(f'Duplicate solution: {ident}')
        ids.add(ident)
        if known_ids is not None and ident not in known_ids:
            raise ValueError(f'No source question: {ident}')
        if row['status'] != 'worked' or not row['solutionHtml'].strip():
            raise ValueError(f'Not a worked solution: {ident}')
        if not row.get('method') or not row.get('steps'):
            raise ValueError(f'Missing explicit method or steps: {ident}')
        if row['answerCheck'] not in ('matches', 'domain-qualified', 'source-discrepancy'):
            raise ValueError(f'No answer comparison: {ident}')
        for part in row['steps']:
            if not part.get('latex') and not part.get('explanation'):
                raise ValueError(f'Empty working: {ident}')
    return len(ids)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('paths', nargs='+', type=Path)
    parser.add_argument('--catalogue', type=Path)
    args = parser.parse_args()
    ids = None
    if args.catalogue:
        catalogue = json.loads(args.catalogue.read_text())
        rows = catalogue if isinstance(catalogue, list) else catalogue['questions']
        if rows and 'questions' in rows[0]:
            rows = [question for chapter in rows for question in chapter['questions']]
        ids = {row['id'] for row in rows}
    count = sum(validate(path, ids) for path in args.paths)
    print(f'{count} authored worked solutions: structure and source IDs checked.'
          if ids is not None else f'{count} authored worked solutions: structure checked; catalogue mapping pending.')


if __name__ == '__main__':
    main()
