"""Search the bundled skill index locally. Never executes a skill."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re


ALIASES = {
    '설계': 'architecture design', '아키텍처': 'architecture system design',
    '명세': 'spec requirements', '리뷰': 'review', '테스트': 'test testing tdd',
    '디버깅': 'debug bug', '데이터': 'data database', '문서': 'documentation adr',
    '프론트엔드': 'frontend react ui', '백엔드': 'backend api',
    '보안': 'security', '성능': 'performance', '접근성': 'accessibility',
}


def search(entries, query, include_reference=False, limit=8):
    words = re.findall(r'[\w-]+', query.lower())
    terms = set(words)
    for word in words:
        terms.update(ALIASES.get(word, '').split())
    results = []
    for item in entries:
        if item.get('alias_of'):
            continue
        if item['mode'] == 'reference-only' and not include_reference:
            continue
        name = item['name'].lower()
        desc = item['description'].lower()
        score = sum(5 * (term in name) + (term in desc) for term in terms)
        if score:
            results.append((score, item))
    results.sort(key=lambda pair: (-pair[0], pair[1]['path']))
    return [item for _, item in results[:limit]]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('query')
    parser.add_argument('--limit', type=int, default=8)
    parser.add_argument('--include-reference', action='store_true')
    args = parser.parse_args()
    if not 1 <= args.limit <= 100:
        parser.error('--limit must be between 1 and 100')
    root = Path(__file__).resolve().parents[1]
    index = json.loads((root / 'docs/external-library.json').read_text(encoding='utf-8'))
    matches = search(index['skills'], args.query, args.include_reference, args.limit)
    for match in matches:
        match['local_path'] = str(root / match['path'])
    print(json.dumps({'query': args.query, 'matches': matches,
                     'ranking': 'lexical relevance, not quality or execution permission'},
                    ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
