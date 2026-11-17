#!/usr/bin/env python3
"""구조 편집 기록 모음 — 편집기(GUI-Structure.html)에서 고친 것을 쌓아 두고, 마지막 업데이트(스킬 6절) 때 반영한다.

기록 모음: <데이터 폴더>/knowledge/structure_edits.json
  {"version": 1, "batches": [{"id", "received", "lecture", "source", "status": "pending|applied|rejected",
                              "ops": [...], "applied": 날짜, "reason": 거절 이유}]}

사용법:
  python3 structure_edits.py add <편집.json>       편집기가 내보낸 JSON을 「반영 대기」로 쌓는다(적용해 보고 오류가 있으면 쌓지 않음)
  python3 structure_edits.py list                  쌓인 묶음과 편집 내용(사람이 읽는 문장)
  python3 structure_edits.py preview               대기 중인 편집을 모두 적용하면 무엇이 바뀌는지 + 검사 결과(파일은 안 바꿈)
  python3 structure_edits.py apply [--yes] [--by <확인자>]
                                                   대기 중인 편집을 dimensions.json · questions.json 에 반영하고 「반영됨」으로 표시
                                                   (--yes 없이는 preview 만 보여 주고 끝난다. 변경이력 줄은 표의 마지막 줄 뒤에 넣는다.
                                                    --by 는 변경이력의 확인자 칸 — 없으면 「Claude 판정(자율 반영)」, 사용자가 직접 확인했으면 「사용자 확인」)
  python3 structure_edits.py reject <묶음 id> [이유]  그 묶음을 반영하지 않음으로 표시(기록은 남김)
  python3 structure_edits.py selftest              변경이력 줄 자리 · apply 인자 검사의 자체 시험

인터뷰·편집기 페이지(build_interview.py)는 대기 중인 편집을 메모리에서 적용해 보여 준다(파일은 apply 때 바뀐다).
적용 규칙은 structure.py.
"""
import datetime
import json
import pathlib
import re
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


def write_lf(p, text):
    """줄바꿈을 LF 로 고정해 쓴다. Windows 파이썬의 write_text 는 CRLF 로 써서 PC와 클라우드 결과가 달라진다."""
    p.write_bytes(text.encode('utf-8'))


def save_ledger(led):
    p = ledger_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    write_lf(p, json.dumps(led, ensure_ascii=False, indent=2) + '\n')


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


DEFAULT_BY = 'Claude 판정(자율 반영)'


def _split(line):
    """표 줄을 칸으로 나눈다(칸 안의 \\| 는 글자). 양 끝의 세로줄은 하나씩만 뗀다 — `|a||` 의 빈 끝 칸을 지우지 않는다."""
    s = line.strip()
    if s.startswith('|'):
        s = s[1:]
    if s.endswith('|') and not s.endswith('\\|'):
        s = s[:-1]
    return re.split(r'(?<!\\)\|', s)


def _cells(line):
    """표 줄의 칸 수."""
    return len(_split(line))


_FENCE = re.compile(r'^([ \t]*)(`{3,}|~{3,})(.*)$')
_SEP_CELL = re.compile(r'^\s*:?-+:?\s*$')
CHANGELOG_HEAD = ['| 날짜 | 프로젝트(대화) | 대상 | 조치 | 근거 | 확인자 |', '|---|---|---|---|---|---|']


def _table_line(line):
    """표 줄인가 — 들여쓰기 3칸 이하이고 | 로 시작한다(4칸 이상 들여 쓴 줄은 코드 블록이다)."""
    return re.match(r'^ {0,3}\|', line) is not None


def _scan(lines):
    """글을 훑어 (표 목록 [(첫 줄, 끝 줄)], 글 끝에서 열려 있는 울타리 (글자, 길이, 들여쓰기) 또는 None)를 돌려준다.

    울타리(``` · ~~~)는 연 글자와 길이를 기억해, 같은 글자가 그 길이 이상이고 뒤에 글이 없는 줄에서만 닫는다.
    목록 항목 안처럼 들여 쓴 울타리도 울타리로 본다(그 안의 표 꼴 줄을 표로 잡지 않게).
    표는 울타리 밖에서 표 줄이 이어진 덩어리이고, 둘째 줄의 모든 칸이 구분 꼴(:---: 등)이며 칸 수가 머리 줄과 같은 것."""
    tables, i, fence, n = [], 0, None, len(lines)
    while i < n:
        m = _FENCE.match(lines[i])
        if fence is not None:
            if m and m.group(2)[0] == fence[0] and len(m.group(2)) >= fence[1] and not m.group(3).strip():
                fence = None
            i += 1
            continue
        if m and not (m.group(2)[0] == '`' and '`' in m.group(3)):
            fence = (m.group(2)[0], len(m.group(2)), m.group(1))
            i += 1
            continue
        if _table_line(lines[i]):
            j = i
            while j < n and _table_line(lines[j]):
                j += 1
            if j - i >= 2:
                sep = _split(lines[i + 1])
                if len(sep) == _cells(lines[i]) and all(_SEP_CELL.match(c) for c in sep):
                    tables.append((i, j - 1))
            i = j
            continue
        i += 1
    return tables, fence


def insert_after_table(text, rows):
    """변경이력 글에서 **변경이력 표**(넣을 줄과 칸 수가 같은 첫 표)의 마지막 줄 바로 뒤에 rows 를 넣는다.

    표 아래에 다른 절 · 다른 표 · 코드 블록이 있어도 그쪽에 들어가지 않는다(코드 블록 안 · 들여 쓴 코드 · 구분 줄이 틀린 덩어리는 표가 아니다).
    칸 수가 맞는 표가 없으면 글 끝에 새 표를 만든다 — 글이 코드 블록 안에서 끝났으면 먼저 닫는다(안 닫으면 새 줄이 코드로 보인다)."""
    if not rows:
        return text
    lines = text.rstrip('\n').split('\n') if text.strip('\n') else []
    tables, fence = _scan(lines)
    want = _cells(rows[0]) if rows else None
    hit = next((t for t in tables if _cells(lines[t[0]]) == want), None)
    if hit is not None:
        last = hit[1]
        return '\n'.join(lines[:last + 1] + rows + lines[last + 1:]) + '\n'
    tail = []
    if fence is not None:
        tail.append(fence[2] + fence[0] * fence[1])
    if lines:
        tail.append('')
    if want == _cells(CHANGELOG_HEAD[0]):
        tail += CHANGELOG_HEAD
    return '\n'.join(lines + tail + rows) + '\n'


def parse_apply_args(argv):
    """apply 뒤의 인자 → (yes, by, 오류 글). 값 없는 --by · 다른 옵션을 값으로 받은 --by · 모르는 옵션은 오류(반영하지 않는다)."""
    yes, by, i = False, None, 0
    while i < len(argv):
        a = argv[i]
        if a == '--yes':
            yes = True
        elif a.startswith('--by='):
            by = a[len('--by='):]
            if not by.strip():
                return yes, None, '--by 값이 비었습니다(예: --by "사용자 확인")'
        elif a == '--by':
            if i + 1 >= len(argv) or argv[i + 1].startswith('--') or not argv[i + 1].strip():
                return yes, None, '--by 뒤에 확인자 글이 없습니다(예: --by "사용자 확인")'
            by = argv[i + 1]
            i += 1
        else:
            return yes, None, f'모르는 인자: {a} (apply [--yes] [--by <확인자>])'
        i += 1
    return yes, by, None


def selftest():
    fails = []

    def ok(c, m):
        print(('OK   ' if c else 'FAIL ') + m)
        if not c:
            fails.append(m)

    head = '# 이력\n\n| 날짜 | 프로젝트 | 대상 | 조치 | 근거 | 확인자 |\n|---|---|---|---|---|---|\n| 1 | a | b | c | d | e |\n'
    row = '| 2 | a | b | c | d | e |'
    at = lambda t: insert_after_table(t, [row]).split('\n').index(row)
    ok(at(head) == 5, '표만 있는 글: 표의 마지막 줄 뒤')
    r = insert_after_table(head + '\n### 뒤 절\n- 글\n', [row])
    ok(r.split('\n').index(row) == 5 and r.endswith('### 뒤 절\n- 글\n'), '표 아래에 절이 있어도 표 안에(절은 그대로)')
    r = insert_after_table(head + '\n```\n| example |\n```\n', [row])
    ok(r.split('\n').index(row) == 5 and '```\n| example |\n```' in r, '뒤쪽 코드 블록 안의 | 줄에는 넣지 않음')
    r = insert_after_table(head + '\n### 다른 표\n\n| x | y |\n|---|---|\n| 1 | 2 |\n', [row])
    ok(r.split('\n').index(row) == 5 and r.endswith('| 1 | 2 |\n'), '뒤쪽에 다른 표가 있어도 변경이력 표에')
    r = insert_after_table('```\n| a | b | c | d | e | f |\n|---|---|---|---|---|---|\n```\n\n' + head, [row])
    ok(r.split('\n').index(row) == 10, '앞쪽 코드 블록 안의 표 꼴은 표로 보지 않음')
    r = insert_after_table('| x | y |\n|---|---|\n| 1 | 2 |\n\n' + head, [row])
    ok(r.split('\n').index(row) == 9, '칸 수가 같은 표를 고름(앞의 다른 표가 아니라)')
    ok(insert_after_table('글만\n', [row]) == '글만\n\n' + '\n'.join(CHANGELOG_HEAD) + '\n' + row + '\n', '표가 없으면 글 끝에 새 변경이력 표')
    ok(insert_after_table('', [row]) == '\n'.join(CHANGELOG_HEAD) + '\n' + row + '\n', '빈 글: 표만')
    r = insert_after_table('````\n```\n| a | b | c | d | e | f |\n|---|---|---|---|---|---|\n```\n````\n\n' + head, [row])
    ok(r.split('\n').index(row) == 12, '네 개짜리 울타리 안의 세 개짜리 줄은 울타리를 닫지 않음(안쪽 표 꼴에 넣지 않음)')
    r = insert_after_table('    | a | b | c | d | e | f |\n    |---|---|---|---|---|---|\n\n' + head, [row])
    ok(r.split('\n').index(row) == 8, '네 칸 들여 쓴 표 꼴(코드)은 표가 아님')
    r = insert_after_table('| a | b | c | d | e | f |\n|---oops|text|x|y|z|w|\n\n' + head, [row])
    ok(r.split('\n').index(row) == 8, '구분 줄이 틀린 덩어리는 표가 아님')
    r = insert_after_table('| x | y |\n|---|---|\n| 1 | 2 |\n', [row])
    ok(r == '| x | y |\n|---|---|\n| 1 | 2 |\n\n' + '\n'.join(CHANGELOG_HEAD) + '\n' + row + '\n', '칸 수가 맞는 표가 없으면 다른 표에 넣지 않고 새 표')
    r = insert_after_table('```\nexample\n', [row])
    ok(r == '```\nexample\n```\n\n' + '\n'.join(CHANGELOG_HEAD) + '\n' + row + '\n', '글이 열린 코드 블록에서 끝나면 닫고 나서 새 표(줄이 코드로 묻히지 않음)')
    r = insert_after_table('- 항목\n\n    ```\n  | a | b | c | d | e | f |\n  |---|---|---|---|---|---|\n    ```\n\n' + head, [row])
    ok(r.split('\n').index(row) == 12 and r.split('\n')[5] == '    ```', '목록 안에 들여 쓴 울타리도 울타리(그 안의 표 꼴에 넣지 않음)')
    r = insert_after_table('# 이력\n\n|a|b|c|d|e||\n|---|---|---|---|---|---|\n|1|2|3|4|5||\n', [row])
    ok(r.split('\n').index(row) == 5 and '| 날짜 |' not in r and r.count('|---|---|---|---|---|---|') == 1, '끝 칸이 빈 여섯 칸 표도 여섯 칸(새 표를 또 만들지 않음)')
    ok(insert_after_table('```\nx\n', []) == '```\nx\n' and insert_after_table(head, []) == head, '넣을 줄이 없으면 글을 그대로')
    r = insert_after_table('- 항목\n\n    ```\n    x\n', [row])
    ok(r.startswith('- 항목\n\n    ```\n    x\n    ```\n\n| 날짜 |'), '들여 쓴 울타리가 열린 채 끝나면 같은 들여쓰기로 닫음')
    r = insert_after_table(head.replace('| 1 | a |', '| 1 \\| 2 | a |'), [row])
    ok(r.split('\n').index(row) == 5, '칸 안의 \\| 는 칸 구분이 아님')
    ok(parse_apply_args(['--yes']) == (True, None, None), 'apply --yes: 확인자 기본값')
    ok(parse_apply_args(['--yes', '--by', '사용자 확인']) == (True, '사용자 확인', None) and parse_apply_args(['--by=사용자 확인', '--yes']) == (True, '사용자 확인', None), '--by 값 · --by=값')
    ok(parse_apply_args(['--by', '--yes'])[2] and parse_apply_args(['--yes', '--by'])[2] and parse_apply_args(['--by='])[2], '값 없는 --by 는 오류(반영하지 않음)')
    ok(parse_apply_args(['--yes', '--by', ''])[2] and parse_apply_args(['--yes', '--by', '   '])[2] and parse_apply_args(['--by=  '])[2], '빈 글 · 빈칸뿐인 --by 도 오류')
    ok(parse_apply_args(['--yse'])[2] is not None, '모르는 인자는 오류')
    print('자체 시험 통과' if not fails else f'자체 시험 실패 {len(fails)}개')
    return 1 if fails else 0


def cmd_apply(yes, by=None):
    rc, res = cmd_preview()
    if res is None or rc:
        return rc
    if not yes:
        print('\n반영하려면 `--yes` 를 붙여 다시 실행하세요(스킬 6절 판정표대로 — 사용자가 직접 확인했으면 `--by "사용자 확인"`).'); return 0
    d2, q2 = res
    today = datetime.date.today().isoformat()
    d2['updated'] = today
    q2['updated'] = today
    write_lf(ST.path('dimensions.json'), json.dumps(d2, ensure_ascii=False, indent=2) + '\n')
    write_lf(ST.path('questions.json'), json.dumps(q2, ensure_ascii=False, indent=2) + '\n')
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
        who = (by or DEFAULT_BY).replace('|', '¦').replace('\n', ' ')
        for b in done:
            what = ' / '.join(SX.describe(op, dims_before) for op in b['ops']).replace('|', '¦').replace('\n', ' ')
            rows.append(f"| {today} | {b.get('lecture') or '-'} | 구조 편집 {b['id']} (편집 {len(b['ops'])}건): {what} | 구조 편집 반영(structure_edits.py) | {(b.get('note') or '편집기 기록').replace('|', '¦')} | {who} |")
        write_lf(ch, insert_after_table(ch.read_text(encoding='utf-8'), rows))
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
        yes, by, err = parse_apply_args(argv[1:])
        if err:
            print(err + ' — 반영하지 않았습니다.', file=sys.stderr)
            return 2
        return cmd_apply(yes, by)
    if c == 'selftest':
        return selftest()
    if c == 'reject' and len(argv) > 1:
        return cmd_reject(argv[1], ' '.join(argv[2:]))
    print(__doc__); return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
