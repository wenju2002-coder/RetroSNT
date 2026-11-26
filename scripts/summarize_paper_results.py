"""Audit the two selected single-seed RetroSNT results.

No Torch, RDKit, model weights or raw reactions are needed for this audit.
Selection is by calibrated test Top-1 among the manuscript's seeds 41,43,44.
These two single best runs are NOT the manuscript's three-seed mean and SD.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path


METRICS = ('retro_mtgr_top1', 'retro_mtgr_top3', 'retro_mtgr_top5')
SEEDS = (41, 43, 44)


def summarize(records):
    if len(records) != 1 or records[0]['seed'] not in SEEDS:
        raise ValueError('Expected exactly one selected run from seeds 41, 43, 44')
    result = {}
    for key in METRICS:
        values = [r['metrics'][key] for r in records]
        if not all(isinstance(v, (int, float)) and not isinstance(v, bool)
                   and math.isfinite(v) and 0 <= v <= 1 for v in values):
            raise ValueError(f'{key} must contain finite fractions between 0 and 1')
        value = values[0]
        result[key] = {
            'fraction': value,
            'percent': 100 * value,
            'display_percent': f'{100 * value:.2f}',
        }
    return result


def collect(root):
    manifest = json.loads((root / 'reproducibility/source_manifest.json').read_text(encoding='utf-8'))
    output = {}
    for group in ('with_class', 'without_class'):
        candidates = [r for r in manifest['selection']['candidates'] if r['group'] == group]
        if sorted(r['seed'] for r in candidates) != list(SEEDS):
            raise ValueError(f'Invalid selection seed pool for {group}')
        chosen = [r for r in manifest['paper_runs'] if r['group'] == group]
        winner = max(candidates, key=lambda r: r['calibrated_test_top1'])
        if len(chosen) != 1 or chosen[0]['run'] != winner['run']:
            raise ValueError(f'Selected run does not maximize calibrated test Top-1: {group}')
        by_checkpoint = {}
        for checkpoint, filename in [('calibrated', 'evaluation_test_calibrated.json'),
                                     ('best', 'evaluation_test.json')]:
            records = []
            for run in sorted(manifest['paper_runs'], key=lambda x: x['seed']):
                if run['group'] != group:
                    continue
                path = root / 'runs' / group / run['run'] / filename
                if hashlib.sha256(path.read_bytes()).hexdigest() != run['files'][filename]:
                    raise ValueError(f'Archived evaluation checksum mismatch: {path}')
                metrics = json.loads(path.read_text(encoding='utf-8'))
                config = json.loads((path.parent / 'config.json').read_text(encoding='utf-8'))
                if metrics.get('split') != 'test':
                    raise ValueError(f'Not a test evaluation: {path}')
                if config['seed'] != run['seed'] or bool(config['model']['use_reaction_class']) != (group == 'with_class'):
                    raise ValueError(f'Run configuration/group mismatch: {path.parent}')
                records.append({'seed': run['seed'],
                                'run_directory': f"runs/{group}/{run['run']}",
                                'evaluation_file': filename,
                                'evaluation_sha256': run['files'][filename],
                                'metrics': {key: metrics[key] for key in METRICS}})
            by_checkpoint[checkpoint] = {'seeds': records, 'topk': summarize(records)}
        output[group] = {
            'model': 'RetroSNT', 'reaction_class_given': group == 'with_class',
            'report_scope': 'single best run from the manuscript seed cohort; not the Table 3 mean',
            'reported_checkpoint': 'calibrated',
            'selected_seed': by_checkpoint['calibrated']['seeds'][0]['seed'],
            'selection_seed_pool': list(SEEDS),
            'selection_metric': 'calibrated test retro_mtgr_top1 (post-hoc test selection)',
            'test_reactions': 3537, 'split_seed': 42,
            'metric': 'local ordered centre-bond/left-label/right-label triple exact match',
            'uncertainty': 'not estimated from one selected run',
            'split_identity_basis': 'author-confirmed for neural runs; seed42 snapshot supplied separately',
            'checkpoints': by_checkpoint,
        }
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--write', action='store_true', help='Write runs/<group>/selected_result.json')
    mode.add_argument('--check', action='store_true', help='Check stored summaries without changing files')
    args = parser.parse_args()
    root = args.root.resolve()
    results = collect(root)
    for group, result in results.items():
        path = root / 'runs' / group / 'selected_result.json'
        if args.write:
            path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        if args.check:
            if json.loads(path.read_text(encoding='utf-8')) != result:
                raise ValueError(f'Selected result summary is stale or modified: {path}')
        scores = result['checkpoints']['calibrated']['topk']
        print(group + ': ' + ' | '.join(scores[k]['display_percent'] for k in METRICS))
    if args.check:
        print('PASS: archived evaluation hashes and both selected-result summaries match.')


if __name__ == '__main__':
    main()
