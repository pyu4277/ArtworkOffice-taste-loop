#!/usr/bin/env python3
"""취향 저장소의 손 정렬 파일(preferences.json · knowledge/choices.json)을 형식 그대로 고친다.

json.load → json.dump 로 다시 쓰면 항목마다 6줄로 맞춘 손 정렬이 풀려 PR 비교가 수천 줄로 불어난다
(2026-11-09 한 프로젝트 마무리: preferences.json 비교 2,804줄 → 형식 복원 커밋을 따로 냄). 이 도구는 고친 항목만 다시 쓰고
나머지 줄은 한 글자도 건드리지 않는다.

사용법:
  python3 store_write.py entry-add <항목.json>                새 취향 항목을 끝에 붙인다(이번 묶음 앞에 빈 줄 하나).
                                                             파일에는 항목 하나 또는 목록. id 가 없으면 <sub>-<오늘 YYMMDD>-<nn> 으로 매긴다
  python3 store_write.py entry-set <id> <바꿀 칸.json>         그 항목의 칸만 바꾼다(그 항목 줄만 다시 씀)
                                                             예: {"status": "confirmed", "last": "2026-11-09"}
  python3 store_write.py choice-add <기록.json>               선택별 진화 기록을 붙인다(키 '<aspect>|<option>', 하나 또는 목록)
  python3 store_write.py choice-set <키> <바꿀 칸.json> [--history "<무엇이 달라졌나>" --project <작업폴더>]
                                                             칸을 바꾼다. --history 를 주면 version +1, updated 오늘, history 한 줄
  python3 store_write.py fmt [--check]                        두 파일을 손 정렬 형식으로 다시 쓴다(json.dump 로 풀린 파일 되돌리기 —
                                                             빈 줄 자리는 git 의 마지막 판을 따른다). --check: 다르면 종료 코드 1
  python3 store_write.py selftest                             지금 두 파일이 이 도구의 형식과 바이트까지 같은지 확인
공통: --dry-run 은 쓰지 않고 바뀔 줄 수만 알린다. <바꿀 칸.json> 자리에 JSON 글을 바로 써도 된다.
쓴 뒤 JSON 을 다시 읽어 확인하고, 줄바꿈은 LF 로 쓴다(실수 기록 E22). 다음 단계: check_store.py (값 · 범위 · 충돌 검증).
"""
import datetime
import json
import pathlib
import re
import subprocess
import sys

sys.dont_write_bytecode = True  # 설치 폴더(플러그인 캐시)에 __pycache__ 를 만들지 않는다
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import store as ST  # noqa: E402

TODAY = datetime.date.today()
# 취향 항목 한 개 = 6줄(칸 묶음). 이 순서에 없는 칸은 마지막 줄 뒤 한 줄에 모은다
ENTRY_LINES = [('id', 'sub', 'aspect', 'value'), ('statement',), ('scope', 'strength', 'reason'), ('examples',), ('source',),
               ('status', 'first', 'last', 'count', 'conflicts')]
ENTRY_KEYS = [k for line in ENTRY_LINES for k in line]
ENTRY_DEFAULTS = {'scope': {}, 'examples': {'liked': [], 'disliked': []}, 'count': 1, 'conflicts': []}
ENTRY_REQUIRED = ('aspect', 'value', 'statement', 'strength', 'reason', 'source', 'status')
CHOICE_HEAD = ('aspect', 'option', 'version', 'updated')
CHOICE_REQUIRED = ('aspect', 'option', 'how', 'source')
ID_RE = re.compile(r'^(P\d+\.\d+)-(\d{6})-(\d{2})$')


class FormatError(Exception):
    pass


def j(v):
    return json.dumps(v, ensure_ascii=False)


def read_text(p):
    return pathlib.Path(p).read_bytes().decode('utf-8').replace('\r\n', '\n')


def write_text(p, text):
    json.loads(text)  # 쓰기 전에 한 번 더: 깨진 JSON 은 쓰지 않는다
    pathlib.Path(p).write_bytes(text.encode('utf-8'))


# ---------- 형식 ----------
def fmt_entry(e, last):
    keys = list(e.keys())
    extra = [k for k in keys if k not in ENTRY_KEYS]
    groups = [[k for k in line if k in e] for line in ENTRY_LINES]
    groups = [g for g in groups if g] + ([extra] if extra else [])
    out = []
    for n, g in enumerate(groups):
        body = ', '.join(f'{j(k)}: {j(e[k])}' for k in g)
        head = '    {' if n == 0 else '     '
        tail = ('}' + ('' if last else ',')) if n == len(groups) - 1 else ','
        out.append(head + body + tail)
    return out


def fmt_choice(key, c, last):
    out = [f'    {j(key)}: {{']
    rest = [k for k in c.keys() if k not in CHOICE_HEAD]
    head = [k for k in CHOICE_HEAD if k in c]
    parts = []
    if head:
        parts.append(['      ' + ', '.join(f'{j(k)}: {j(c[k])}' for k in head)])
    for k in rest:
        v = c[k]
        if k == 'how' and isinstance(v, list) and v:
            parts.append([f'      {j(k)}: ['] + [f'        {j(x)}' + (',' if i < len(v) - 1 else '') for i, x in enumerate(v)] + ['      ]'])
        else:
            parts.append([f'      {j(k)}: {j(v)}'])
    for i, p in enumerate(parts):
        if i < len(parts) - 1:
            p[-1] += ','
        out += p
    out.append('    }' + ('' if last else ','))
    return out


# ---------- 나누기: 머리 · 항목 덩이(앞 빈 줄 여부) · 꼬리 ----------
def split_entries(text):
    lines = text.split('\n')
    try:
        s = lines.index('  "entries": [')
        e = max(i for i, l in enumerate(lines) if l == '  ]')
    except ValueError:
        raise FormatError('preferences.json 이 손 정렬 형식이 아님("entries": [ 줄을 못 찾음) — fmt 로 먼저 되돌리세요')
    starts = [i for i in range(s + 1, e) if lines[i].startswith('    {"id": ')]
    blocks = []
    for n, i in enumerate(starts):
        end = starts[n + 1] if n + 1 < len(starts) else e
        body = lines[i:end]
        while body and body[-1] == '':
            body.pop()
        blank = i > s + 1 and lines[i - 1] == ''
        raw = '\n'.join(body).rstrip(',')
        try:
            obj = json.loads(raw)
        except ValueError as ex:
            raise FormatError(f'{i + 1}번째 줄부터의 항목을 읽을 수 없음({ex}) — fmt 로 먼저 되돌리세요')
        blocks.append({'blank': blank, 'lines': body, 'obj': obj})
    inner = [l for l in lines[s + 1:e] if l != '']
    if sum(len(b['lines']) for b in blocks) != len(inner):
        raise FormatError('항목 사이에 알 수 없는 줄이 있음 — fmt 로 먼저 되돌리세요')
    return lines[:s + 1], blocks, lines[e:]


def split_choices(text):
    lines = text.split('\n')
    try:
        s = lines.index('  "choices": {')
        e = max(i for i, l in enumerate(lines) if l == '  }')
    except ValueError:
        raise FormatError('choices.json 이 손 정렬 형식이 아님("choices": { 줄을 못 찾음) — fmt 로 먼저 되돌리세요')
    key_re = re.compile(r'^    ("(?:[^"\\]|\\.)*"): \{$')
    starts = [i for i in range(s + 1, e) if key_re.match(lines[i])]
    blocks = []
    for n, i in enumerate(starts):
        end = starts[n + 1] if n + 1 < len(starts) else e
        body = lines[i:end]
        while body and body[-1] == '':
            body.pop()
        key = json.loads(key_re.match(lines[i]).group(1))
        raw = '{' + '\n'.join(body).rstrip(',') + '}'
        try:
            obj = json.loads(raw)[key]
        except (ValueError, KeyError) as ex:
            raise FormatError(f'{i + 1}번째 줄부터의 기록을 읽을 수 없음({ex}) — fmt 로 먼저 되돌리세요')
        blocks.append({'blank': i > s + 1 and lines[i - 1] == '', 'lines': body, 'key': key, 'obj': obj})
    inner = [l for l in lines[s + 1:e] if l != '']
    if sum(len(b['lines']) for b in blocks) != len(inner):
        raise FormatError('기록 사이에 알 수 없는 줄이 있음 — fmt 로 먼저 되돌리세요')
    return lines[:s + 1], blocks, lines[e:]


def join_blocks(head, blocks, tail, fmt):
    out = list(head)
    for n, b in enumerate(blocks):
        if b['blank']:
            out.append('')
        out += fmt(b, n == len(blocks) - 1)
    return '\n'.join(out + tail)


def comma(lines, last):
    """손대지 않는 덩이는 원래 줄 그대로 — 끝 쉼표만 자리에 맞춘다(새 항목을 붙이면 옛 마지막 항목 뒤에 쉼표가 생긴다)."""
    lines = list(lines)
    if last and lines[-1].endswith(','):
        lines[-1] = lines[-1][:-1]
    elif not last and not lines[-1].endswith(','):
        lines[-1] += ','
    return lines


def keep_or_fmt_entry(b, last):
    return comma(b['lines'], last) if b.get('keep') else fmt_entry(b['obj'], last)


def keep_or_fmt_choice(b, last):
    return comma(b['lines'], last) if b.get('keep') else fmt_choice(b['key'], b['obj'], last)


def set_updated(head):
    return [f'  "updated": {j(TODAY.isoformat())},' if l.startswith('  "updated": ') else l for l in head]


# ---------- 명령 ----------
def load_arg(s):
    p = pathlib.Path(s)
    try:
        if p.exists():
            return json.loads(read_text(p))
    except OSError:
        pass
    return json.loads(s)


def next_id(sub, used):
    stamp = TODAY.strftime('%y%m%d')
    n = 1
    while f'{sub}-{stamp}-{n:02d}' in used:
        n += 1
    return f'{sub}-{stamp}-{n:02d}'


def cmd_entry_add(arg, dry):
    path = ST.path('preferences.json')
    head, blocks, tail = split_entries(read_text(path))
    new = load_arg(arg)
    new = new if isinstance(new, list) else [new]
    used = {b['obj'].get('id') for b in blocks}
    added = []
    for k, e in enumerate(new):
        if not isinstance(e, dict):
            raise FormatError(f'{k + 1}번째 항목이 객체가 아님')
        miss = [x for x in ENTRY_REQUIRED if x not in e]
        if miss:
            raise FormatError(f'{k + 1}번째 항목에 칸이 없음: {", ".join(miss)} (형식은 SKILL.md 6절 · preferences.json 머리말)')
        sub = e.get('sub') or '.'.join(str(e['aspect']).split('.')[:2])
        eid = e.get('id') or next_id(sub, used)
        m = ID_RE.match(eid)
        if not m or m.group(1) != sub:
            raise FormatError(f'id {eid!r} 는 <sub>-<YYMMDD>-<nn> 꼴이어야 함(sub {sub})')
        if eid in used:
            raise FormatError(f'id {eid!r} 가 이미 있음')
        used.add(eid)
        obj = {'id': eid, 'sub': sub}
        for key in ENTRY_KEYS[2:]:
            if key in e:
                obj[key] = e[key]
            elif key in ENTRY_DEFAULTS:
                obj[key] = json.loads(j(ENTRY_DEFAULTS[key]))
            elif key in ('first', 'last'):
                obj[key] = TODAY.isoformat()
        for key in e:
            if key not in obj:
                obj[key] = e[key]
        blocks.append({'blank': k == 0, 'obj': obj})
        added.append(eid)
    for b in blocks:
        b.setdefault('keep', 'lines' in b)
    text = join_blocks(set_updated(head), blocks, tail, keep_or_fmt_entry)
    return finish(path, text, f'항목 {len(added)}개 붙임: {", ".join(added)}', dry)


def cmd_entry_set(eid, arg, dry):
    path = ST.path('preferences.json')
    head, blocks, tail = split_entries(read_text(path))
    patch = load_arg(arg)
    b = next((x for x in blocks if x['obj'].get('id') == eid), None)
    if not b:
        raise FormatError(f'항목 {eid!r} 없음')
    if 'id' in patch and patch['id'] != eid:
        raise FormatError('id 는 바꿀 수 없음(새 항목을 붙이고 옛 항목은 status retired)')
    for k, v in patch.items():
        if v is None:
            b['obj'].pop(k, None)
        else:
            b['obj'][k] = v
    for x in blocks:
        x['keep'] = x is not b
    text = join_blocks(set_updated(head), blocks, tail, keep_or_fmt_entry)
    return finish(path, text, f'항목 {eid} 칸 {len(patch)}개 바꿈: {", ".join(patch)}', dry)


def cmd_choice_add(arg, dry):
    path = ST.path('knowledge/choices.json')
    head, blocks, tail = split_choices(read_text(path))
    new = load_arg(arg)
    new = new if isinstance(new, list) else [new]
    have = {b['key'] for b in blocks}
    added = []
    for k, c in enumerate(new):
        miss = [x for x in CHOICE_REQUIRED if x not in c]
        if miss:
            raise FormatError(f'{k + 1}번째 기록에 칸이 없음: {", ".join(miss)}')
        key = f"{c['aspect']}|{c['option']}"
        if key in have:
            raise FormatError(f'기록 {key!r} 가 이미 있음 — choice-set 으로 고치세요')
        have.add(key)
        obj = {'aspect': c['aspect'], 'option': c['option'], 'version': c.get('version', 1), 'updated': c.get('updated', TODAY.isoformat())}
        for x in c:
            if x not in obj:
                obj[x] = c[x]
        obj.setdefault('history', [{'date': TODAY.isoformat(), 'project': c.get('project', ''), 'change': '처음 기록'}])
        obj.pop('project', None)
        blocks.append({'blank': False, 'key': key, 'obj': obj})
        added.append(key)
    for b in blocks:
        b.setdefault('keep', 'lines' in b)
    text = join_blocks(set_updated(head), blocks, tail, keep_or_fmt_choice)
    return finish(path, text, f'선택 기록 {len(added)}개 붙임: {", ".join(added)}', dry)


def cmd_choice_set(key, arg, history, project, dry):
    path = ST.path('knowledge/choices.json')
    head, blocks, tail = split_choices(read_text(path))
    patch = load_arg(arg)
    b = next((x for x in blocks if x['key'] == key), None)
    if not b:
        raise FormatError(f'선택 기록 {key!r} 없음')
    for k, v in patch.items():
        if v is None:
            b['obj'].pop(k, None)
        else:
            b['obj'][k] = v
    if history:
        b['obj']['version'] = int(b['obj'].get('version', 1)) + 1
        b['obj']['updated'] = TODAY.isoformat()
        b['obj'].setdefault('history', []).append({'date': TODAY.isoformat(), 'project': project or '', 'change': history})
        lf = b['obj'].setdefault('learned_from', [])
        if project and project not in lf:
            lf.append(project)
    for x in blocks:
        x['keep'] = x is not b
    text = join_blocks(set_updated(head), blocks, tail, keep_or_fmt_choice)
    return finish(path, text, f'선택 기록 {key} 바꿈' + (f' → v{b["obj"]["version"]}' if history else ''), dry)


def git_blank_flags(path, kind):
    """git 의 마지막 판에서 항목(또는 기록)마다 앞에 빈 줄이 있었는지 — fmt 가 json.dump 로 풀린 파일을 되돌릴 때 쓴다."""
    try:
        root = ST.project_root()
        rel = pathlib.Path(path).resolve().relative_to(root).as_posix()
        r = subprocess.run(['git', '-C', str(root), 'show', f'HEAD:{rel}'], capture_output=True, timeout=10)
        if r.returncode != 0:
            return {}
        old = r.stdout.decode('utf-8', 'replace').replace('\r\n', '\n')
        _h, blocks, _t = (split_entries if kind == 'entries' else split_choices)(old)
        return {(b['obj'].get('id') if kind == 'entries' else b['key']): b['blank'] for b in blocks}
    except Exception:  # noqa: BLE001
        return {}


def fmt_file(path, kind):
    """파일 전체를 손 정렬 형식으로 만든 글(빈 줄: 지금 파일 → git 마지막 판 → 없으면 빈 줄 없음)."""
    text = read_text(path)
    try:
        head, blocks, tail = (split_entries if kind == 'entries' else split_choices)(text)
        flags = {(b['obj'].get('id') if kind == 'entries' else b['key']): b['blank'] for b in blocks}
    except FormatError:
        flags = {}
    if not flags or not any(flags.values()):
        flags = git_blank_flags(path, kind) or flags
    data = json.loads(text)
    top = [k for k in data if k not in ('entries', 'choices')]
    head = ['{'] + [f'  {j(k)}: {j(data[k])},' for k in top] + (['  "entries": ['] if kind == 'entries' else ['  "choices": {'])
    if kind == 'entries':
        blocks = [{'blank': bool(flags.get(e.get('id'))), 'obj': e} for e in data['entries']]
        return join_blocks(head, blocks, ['  ]', '}', ''], lambda b, last: fmt_entry(b['obj'], last))
    blocks = [{'blank': bool(flags.get(k)), 'key': k, 'obj': v} for k, v in data['choices'].items()]
    return join_blocks(head, blocks, ['  }', '}', ''], lambda b, last: fmt_choice(b['key'], b['obj'], last))


def files():
    return [(ST.path('preferences.json'), 'entries'), (ST.path('knowledge/choices.json'), 'choices')]


def cmd_fmt(check, dry):
    bad = 0
    for path, kind in files():
        if not path.exists():
            continue
        text, want = read_text(path), fmt_file(path, kind)
        if json.loads(text) != json.loads(want):
            print(f'오류: {path.name} 형식을 맞추다 내용이 달라짐 — 쓰지 않음'); return 1
        if text == want:
            print(f'{path.name}: 손 정렬 형식 그대로'); continue
        bad += 1
        if check or dry:
            print(f'{path.name}: 형식이 다름(바꿀 줄 {diff_count(text, want)}개)')
        else:
            write_text(path, want)
            print(f'{path.name}: 손 정렬 형식으로 다시 씀(바꾼 줄 {diff_count(text, want)}개, 내용 같음)')
    return 1 if (check and bad) else 0


def cmd_selftest():
    ok = True
    for path, kind in files():
        if not path.exists():
            continue
        text = read_text(path)
        try:
            head, blocks, tail = (split_entries if kind == 'entries' else split_choices)(text)
        except FormatError as e:
            print(f'FAIL {path.name}: {e}'); ok = False; continue
        for b in blocks:
            b['keep'] = False
        again = join_blocks(head, blocks, tail, keep_or_fmt_entry if kind == 'entries' else keep_or_fmt_choice)
        same = again == text
        ok &= same
        print(f'{"OK  " if same else "FAIL"} {path.name}: {len(blocks)}개를 이 도구의 형식으로 다시 써도 글자까지 같음(줄바꿈은 LF 로 봄)' if same else
              f'FAIL {path.name}: 다시 쓰면 {diff_count(text, again)}줄이 달라짐(이 도구의 형식과 다름 — fmt --check 로 확인)')
    return 0 if ok else 1


def diff_count(a, b):
    import difflib
    return sum(1 for l in difflib.unified_diff(a.split('\n'), b.split('\n'), lineterm='', n=0) if l[:1] in '+-' and not l.startswith(('+++', '---')))


def finish(path, text, msg, dry):
    old = read_text(path)
    n = diff_count(old, text)
    if dry:
        print(f'(쓰지 않음) {msg} — 바뀔 줄 {n}개'); return 0
    write_text(path, text)
    json.loads(read_text(path))
    print(f'{msg} — 바뀐 줄 {n}개 ({path}). 다음: check_store.py')
    return 0


def main(argv):
    dry = '--dry-run' in argv
    argv = [a for a in argv if a != '--dry-run']
    opt = {}
    for k in ('--history', '--project'):
        if k in argv:
            i = argv.index(k)
            opt[k] = argv[i + 1]
            del argv[i:i + 2]
    if not argv:
        print(__doc__); return 2
    if not ST.STORE_WRITABLE and argv[0] not in ('selftest',):
        print(f'데이터 폴더가 없습니다(starter 는 읽기 전용). 먼저 init_store.py: {ST.STORE}'); return 1
    c = argv[0]
    try:
        if c == 'entry-add' and len(argv) == 2:
            return cmd_entry_add(argv[1], dry)
        if c == 'entry-set' and len(argv) == 3:
            return cmd_entry_set(argv[1], argv[2], dry)
        if c == 'choice-add' and len(argv) == 2:
            return cmd_choice_add(argv[1], dry)
        if c == 'choice-set' and len(argv) == 3:
            return cmd_choice_set(argv[1], argv[2], opt.get('--history'), opt.get('--project'), dry)
        if c == 'fmt':
            return cmd_fmt('--check' in argv, dry)
        if c == 'selftest':
            return cmd_selftest()
    except (FormatError, ValueError) as e:
        print(f'오류: {e}'); return 1
    print(__doc__); return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
