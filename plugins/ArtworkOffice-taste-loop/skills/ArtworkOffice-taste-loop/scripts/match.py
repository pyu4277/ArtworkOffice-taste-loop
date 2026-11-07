#!/usr/bin/env python3
"""프로젝트의 차원 값에 맞는 취향 항목을 고른다.

사용법:
  python3 match.py --set material_type=video_promo --set purpose=exhibit,report --set venue=kiosk
  python3 match.py --set material_type=slides --lecture <작업폴더> --topic <낱말>
  python3 match.py --answers <인터뷰 답변.json>      답변 JSON의 dimensions 값으로 계산
  옵션: --json (스크립트용 출력) · --all (적용되지 않는 항목도 표시)

판정 규칙(GUI-Interview.html의 JS와 같아야 한다):
  - 항목의 scope 모든 키에서 프로젝트 값과 교집합이 있어야 적용. scope가 비면 전체 적용.
  - lecture·pc 는 문자열 일치, topic 은 프로젝트 topic 문자열에 포함되면 일치.
  - 같은 aspect에 여러 항목이 적용되면 구체성(scope 키 수)이 큰 쪽이 이긴다.
    같으면 confirmed > proposed, 세기 숫자가 작은 쪽, 최근 것 순. 그래도 값이 다른 항목이 남으면 충돌로 표시한다.
  - 세기 5(추론) 항목은 다른 항목이 없을 때만 기본값으로 보이고, '확인 필요'로 표시한다.
"""
import json
import pathlib
import sys

sys.dont_write_bytecode = True  # 설치 폴더(플러그인 캐시)에 __pycache__ 를 만들지 않는다
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import store as ST  # noqa: E402


def load():
    d = json.loads(ST.path('dimensions.json').read_text(encoding='utf-8'))
    q = json.loads(ST.path('questions.json').read_text(encoding='utf-8'))
    p = json.loads(ST.path('preferences.json').read_text(encoding='utf-8'))
    return d, q, p


def applies(entry, project):
    for k, vs in (entry.get('scope') or {}).items():
        pv = project.get(k)
        if pv is None:
            return False
        pv = pv if isinstance(pv, list) else [pv]
        if k == 'topic':
            if not any(any(v in t for t in pv) for v in vs):
                return False
        elif not (set(vs) & set(pv)):
            return False
    return True


def rank_key(e):
    return (-len(e.get('scope') or {}), e.get('status') != 'confirmed', e.get('strength', 9), e.get('last', ''))


def match(project, prefs, all_entries=False):
    by_aspect = {}
    for e in prefs['entries']:
        if e.get('status') not in ('proposed', 'confirmed'):
            continue
        if applies(e, project):
            by_aspect.setdefault(e['aspect'], []).append(e)
        elif all_entries:
            by_aspect.setdefault('(미적용)', []).append(e)
    result = {}
    for aid, group in by_aspect.items():
        if aid == '(미적용)':
            continue
        group.sort(key=lambda e: (e.get('strength') == 5,) + rank_key(e))  # 추론은 맨 뒤
        winner = group[0]
        top = [e for e in group if len(e.get('scope') or {}) == len(winner.get('scope') or {}) and (e.get('strength') == 5) == (winner.get('strength') == 5)]
        values = {json.dumps(e.get('value'), ensure_ascii=False, sort_keys=True) for e in top}
        result[aid] = {
            'winner': winner['id'], 'value': winner.get('value'), 'statement': winner['statement'],
            'specificity': len(winner.get('scope') or {}), 'inferred': winner.get('strength') == 5,
            'conflict': len(values) > 1, 'candidates': [e['id'] for e in group],
        }
    return result, by_aspect.get('(미적용)', [])


def parse_args(argv):
    project, as_json, all_entries, answers = {}, False, False, None
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == '--set':
            k, _, v = argv[i + 1].partition('=')
            project[k] = v.split(',')
            i += 2
        elif a in ('--lecture', '--pc'):
            project[a[2:]] = [argv[i + 1]]
            i += 2
        elif a == '--topic':
            project.setdefault('topic', []).append(argv[i + 1])
            i += 2
        elif a == '--answers':
            answers = pathlib.Path(argv[i + 1])
            i += 2
        elif a == '--json':
            as_json = True
            i += 1
        elif a == '--all':
            all_entries = True
            i += 1
        else:
            print(__doc__, file=sys.stderr)
            sys.exit(2)
    if answers:
        ans = json.loads(answers.read_text(encoding='utf-8'))
        for k, v in (ans.get('dimensions') or {}).items():
            project[k] = v if isinstance(v, list) else [v]
        if ans.get('lecture'):
            project['lecture'] = [ans['lecture']]
    return project, as_json, all_entries


def main(argv):
    project, as_json, all_entries = parse_args(argv)
    if not project:
        print(__doc__, file=sys.stderr)
        return 2
    _, qs, prefs = load()
    result, unused = match(project, prefs, all_entries)
    names = {a['id']: a for a in qs['aspects']}
    if as_json:
        print(json.dumps({'project': project, 'matches': result}, ensure_ascii=False, indent=1))
        return 0
    print('프로젝트:', json.dumps(project, ensure_ascii=False))
    print(f'적용 항목 {len(result)}개 (aspect 기준)')
    for aid in sorted(result):
        r = result[aid]
        flags = []
        if r['conflict']:
            flags.append('⚠충돌: 사용자가 골라야 함')
        if r['inferred']:
            flags.append('⚠추론: 확인 필요')
        extra = f' (후보 {", ".join(r["candidates"])})' if len(r['candidates']) > 1 else ''
        print(f'- {aid} [{names.get(aid, {}).get("text", "")}] → {r["value"]!r} ← {r["winner"]}{extra} {" ".join(flags)}')
        print(f'    {r["statement"]}')
    if all_entries:
        print(f'미적용 {len(unused)}개:', ', '.join(e['id'] for e in unused))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
