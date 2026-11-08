#!/usr/bin/env python3
"""구조 편집 기록 모음 — 편집기(GUI-Structure.html)에서 고친 것을 쌓아 두고, 마지막 업데이트(스킬 6절) 때 반영한다.

기록 모음: <데이터 폴더>/knowledge/structure_edits.json
  {"version": 1, "batches": [{"id", "received", "lecture", "source", "status": "pending|applied|rejected",
                              "ops": [...], "applied": 날짜, "reason": 거절 이유}]}

사용법:
  python3 structure_edits.py add <편집.json>       편집기가 내보낸 JSON을 「반영 대기」로 쌓는다(적용해 보고 오류가 있으면 쌓지 않음)
  python3 structure_edits.py list                  쌓인 묶음과 편집 내용(사람이 읽는 문장)
  python3 structure_edits.py preview               대기 중인 편집을 모두 적용하면 무엇이 바뀌는지 + 검사 결과(파일은 안 바꿈)
  python3 structure_edits.py apply [--yes]         대기 중인 편집을 dimensions.json · questions.json 에 반영하고 「반영됨」으로 표시
                                                   (--yes 없이는 preview 만 보여 주고 끝난다)
  python3 structure_edits.py reject <묶음 id> [이유]  그 묶음을 반영하지 않음으로 표시(기록은 남김)

인터뷰·편집기 페이지(build_interview.py)는 대기 중인 편집을 메모리에서 적용해 보여 준다(파일은 apply 때 바뀐다).
적용 규칙은 structure.py.
"""
import datetime
import json
import pathlib
import sys

sys.dont_write_bytecode = True  # 설치 폴더(플러그인 캐시)에 __pycache__ 를 만들지 않는다
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import store as ST  # noqa: E402
import structure as SX  # noqa: E402


def ledger_path():
    return ST.path('knowledge') / 'structure_edits.json'


def load_ledger():
    p = ledger_path()
    if p.exists():
        return json.loads(p.read_text(encoding='utf-8'))
    return {'version': 1, 'note': '구조 편집 기록 모음 — structure_edits.py 로만 고친다', 'batches': []}


def save_ledger(led):
    p = ledger_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(led, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def load_base():
    import upgrade_store as UP
    dims, _old = UP.migrate_dims(json.loads(ST.path('dimensions.json').read_text(encoding='utf-8')))
    qs, _oldq = UP.migrate_qs(json.loads(ST.path('questions.json').read_text(encoding='utf-8')))
    return dims, qs


def pending_ops(led=None):
    led = led or load_ledger()
    return [op for b in led.get('batches', []) if b.get('status') == 'pending' for op in b.get('ops', [])]


def with_pending(dims, qs):
    """build_interview.py 용: 대기 중인 편집을 적용한 (dims, qs, 편집 수, 문제)."""
    if not ledger_path().exists():
        return dims, qs, 0, []
    ops = pending_ops()
    if not ops:
        return dims, qs, 0, []
    d2, q2, probs = SX.replay(dims, qs, ops)
    return d2, q2, len(ops), probs


def validate(dims, qs):
    """적용 결과 검사: 조건 + check_store 의 차원·질문 검사 + 취향 항목이 가리키는 것."""
    import check_store as CS
    errors, warnings = SX.check_conditions(dims, qs)
    e2 = []
    dim_values = CS.check_dimensions(dims, e2)
    CS.check_questions(qs, dim_values, e2)
    errors += e2
    prefs = json.loads(ST.path('preferences.json').read_text(encoding='utf-8'))
    asp = {a['id']: a for a in qs.get('aspects', [])}
    for e in prefs.get('entries', []):
        if e.get('status') not in ('proposed', 'confirmed'):
            continue
        a = asp.get(e.get('aspect'))
        if a is None:
            errors.append(f"취향 항목 {e['id']}: 질문 {e.get('aspect')!r} 없음")
        elif a.get('retired'):
            warnings.append(f"취향 항목 {e['id']}: 질문 {a['id']} 를 뺐음(항목은 남지만 인터뷰에서 안 물음)")
        elif a.get('options'):
            vals = e.get('value') if isinstance(e.get('value'), list) else [e.get('value')]
            ret = {o['id'] for o in a['options'] if o.get('retired')}
            if any(v in ret for v in vals):
                warnings.append(f"취향 항목 {e['id']}: 뺀 선택지를 씀({a['id']})")
    return errors, warnings


def summary_lines(ops, dims):
    return [f'  - {SX.describe(op, dims)}' + (f"  — {op['note']}" if op.get('note') else '') for op in ops]


def cmd_add(path):
    data = json.loads(pathlib.Path(path).read_text(encoding='utf-8'))
    ops = data.get('ops') if isinstance(data, dict) else None
    if not isinstance(ops, list) or not ops:
        print('편집 기록(ops)이 없습니다. 편집기에서 내보낸 JSON인지 확인하세요.'); return 1
    led = load_ledger()
    dims, qs = load_base()
    _d, _q, probs = SX.replay(dims, qs, pending_ops(led) + ops)
    if probs:
        print('적용할 수 없는 편집이 있어 쌓지 않았습니다:'); print('\n'.join('  - ' + p for p in probs)); return 1
    today = datetime.date.today().isoformat()
    n = sum(1 for b in led['batches'] if b['id'].startswith(f'SE-{today}')) + 1
    bid = f'SE-{today}-{n:02d}'
    led['batches'].append({'id': bid, 'received': today, 'lecture': data.get('lecture'), 'source': str(path),
                           'note': data.get('note') or '', 'status': 'pending', 'ops': ops})
    save_ledger(led)
    print(f'쌓음: {bid} (편집 {len(ops)}건, 반영 대기). 마지막 업데이트 때 `structure_edits.py apply --yes` 로 반영합니다.')
    print('\n'.join(summary_lines(ops, dims)))
    return 0


def cmd_list():
    led = load_ledger()
    dims, _qs = load_base()
    if not led['batches']:
        print('쌓인 구조 편집이 없습니다.'); return 0
    name = {'pending': '반영 대기', 'applied': '반영됨', 'rejected': '반영 안 함'}
    for b in led['batches']:
        print(f"{b['id']} · {name.get(b['status'], b['status'])} · {b.get('lecture') or '-'} · 편집 {len(b['ops'])}건" + (f" · {b['applied']}" if b.get('applied') else '') + (f" · 이유: {b['reason']}" if b.get('reason') else ''))
        print('\n'.join(summary_lines(b['ops'], dims)))
    return 0


def cmd_preview(quiet=False):
    led = load_ledger()
    ops = pending_ops(led)
    dims, qs = load_base()
    if not ops:
        print('반영 대기 중인 구조 편집이 없습니다.'); return 0, None
    d2, q2, probs = SX.replay(dims, qs, ops)
    errors, warnings = validate(d2, q2)
    if not quiet:
        print(f"반영 대기 {sum(1 for b in led['batches'] if b['status'] == 'pending')}묶음 · 편집 {len(ops)}건:")
        print('\n'.join(summary_lines(ops, dims)))
    for p in probs:
        print('적용 실패:', p)
    for e in errors:
        print('오류:', e)
    for w in warnings:
        print('경고:', w)
    ok = not probs and not errors
    print('검사: ' + ('문제 없음' if ok else '문제 있음 — 반영하지 않습니다') + f' (경고 {len(warnings)}개)')
    return (0 if ok else 1), (d2, q2)


def cmd_apply(yes):
    rc, res = cmd_preview()
    if res is None or rc:
        return rc
    if not yes:
        print('\n반영하려면 `--yes` 를 붙여 다시 실행하세요(사용자 확인 뒤).'); return 0
    d2, q2 = res
    today = datetime.date.today().isoformat()
    d2['updated'] = today
    q2['updated'] = today
    ST.path('dimensions.json').write_text(json.dumps(d2, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    ST.path('questions.json').write_text(json.dumps(q2, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    led = load_ledger()
    dims_before = d2
    done = []
    for b in led['batches']:
        if b['status'] == 'pending':
            b['status'] = 'applied'; b['applied'] = today; done.append(b)
    save_ledger(led)
    ch = ST.path('knowledge') / '02_변경이력.md'
    if ch.exists():  # 변경이력은 표 — 묶음마다 한 줄(편집 문장은 「 / 」로 잇는다)
        rows = []
        for b in done:
            what = ' / '.join(SX.describe(op, dims_before) for op in b['ops']).replace('|', '¦').replace('\n', ' ')
            rows.append(f"| {today} | {b.get('lecture') or '-'} | 구조 편집 {b['id']} (편집 {len(b['ops'])}건): {what} | 구조 편집 반영(structure_edits.py) | {(b.get('note') or '편집기 기록').replace('|', '¦')} | 사용자(반영 확인) |")
        body = ch.read_text(encoding='utf-8').rstrip('\n')
        ch.write_text(body + '\n' + '\n'.join(rows) + '\n', encoding='utf-8')
    print(f"반영함: {', '.join(b['id'] for b in done)}. 다음: check_store.py 로 검증·요약을 다시 만들고, 인터뷰 페이지를 다시 만든다.")
    return 0


def cmd_reject(bid, reason):
    led = load_ledger()
    b = next((x for x in led['batches'] if x['id'] == bid), None)
    if b is None:
        print(f'묶음 {bid} 없음'); return 1
    b['status'] = 'rejected'; b['reason'] = reason or ''
    save_ledger(led)
    print(f'{bid}: 반영 안 함으로 표시했습니다(기록은 남김).')
    return 0


def main(argv):
    if not argv:
        print(__doc__); return 2
    c = argv[0]
    if c == 'add' and len(argv) > 1:
        if not ST.STORE_WRITABLE:
            print('데이터 폴더가 없습니다(starter를 쓰는 중). 먼저 init_store.py 로 만드세요.'); return 1
        return cmd_add(argv[1])
    if c == 'list':
        return cmd_list()
    if c == 'preview':
        return cmd_preview()[0]
    if c == 'apply':
        if not ST.STORE_WRITABLE:
            print('데이터 폴더가 없습니다(starter를 쓰는 중). 먼저 init_store.py 로 만드세요.'); return 1
        return cmd_apply('--yes' in argv)
    if c == 'reject' and len(argv) > 1:
        return cmd_reject(argv[1], ' '.join(argv[2:]))
    print(__doc__); return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
