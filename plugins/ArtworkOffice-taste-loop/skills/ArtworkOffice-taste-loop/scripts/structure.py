#!/usr/bin/env python3
"""인터뷰 구조(목차 → 질문 → 선택지)의 「보이는 조건」과 구조 편집 기록 다시 적용하기.

GUI-Interview.html · GUI-Structure.html 의 JS와 판정·적용 규칙이 같아야 한다(check_structure.js 가 둘을 대조한다).

1) 보이는 조건 — 모든 항목에 같은 방식
   항목: 1부 목차(screens) · 질문(dimensions) · 선택지(values) / 2부 묶음(categories) · 취향 질문(aspects) · 선택지(options)
         / 3부 질문(project_questions) · 선택지(options)
   when: {차원 id: [값 id…], …}  모든 차원이 맞아야 보인다(차원 안에서는 값 하나만 맞아도 된다)
         [{…}, {…}]              묶음 중 하나라도 맞으면 보인다
         위 질문에 아직 답하지 않았으면 숨긴다(엄격).
   옛 표기도 읽는다: ask_when(+ask_strict) · applies_when — 답하지 않은 차원은 "모름 → 보여 줌".
   retired: true — 편집기에서 뺀 항목(기록은 남기고 인터뷰에서는 숨긴다).
   선택지가 하나도 안 보이는 선택형 질문은 질문째 숨긴다. 목차가 숨으면 그 안의 질문도 숨는다.

2) 구조 편집 기록(ops) — 편집기가 만든 목록을 순서대로 적용한다
   노드: {"t": "screen"|"dim"|"value"|"cat"|"sub"|"aspect"|"option"|"pq"|"pqopt", "id": …, 부모 키}
         value → "dim", sub → "cat", option → "aspect", pqopt → "pq"
   {"op": "set",  "node": …, "field": …, "before": …, "after": …}   after 가 null 이면 그 칸을 지운다.
        field "when" 을 바꾸면 옛 표기(ask_when·ask_strict·applies_when)는 지운다.
   {"op": "add",  "node": …, "data": {…}, "parent": 목차 id(질문) | 하위 id(취향 질문), "index": 위치(없으면 끝)}
   {"op": "move", "node": …, "parent": 새 부모(질문 → 목차), "index": 새 위치}  취향 질문은 같은 하위 묶음 안에서만 옮긴다
   빼기는 set retired=true, 되살리기는 set retired=null.
"""
import copy

FIELDS = {
    'screen': ('title', 'when', 'retired'),
    'dim': ('name', 'desc', 'type', 'when', 'retired'),
    'value': ('label', 'when', 'free', 'group', 'retired'),
    'cat': ('name', 'when', 'retired'),
    'sub': ('name',),
    'aspect': ('text', 'type', 'when', 'retired'),
    'option': ('label', 'when', 'group', 'retired'),
    'pq': ('text', 'type', 'when', 'retired'),
    'pqopt': ('label', 'when', 'group', 'retired'),
}
LEGACY = ('ask_when', 'ask_strict', 'applies_when')
T_NAME = {'screen': '목차', 'dim': '질문', 'value': '선택지', 'cat': '취향 묶음', 'sub': '하위 묶음', 'aspect': '취향 질문', 'option': '취향 선택지', 'pq': '3부 질문', 'pqopt': '3부 선택지'}
F_NAME = {'title': '이름', 'name': '이름', 'label': '이름', 'text': '질문 글', 'desc': '설명', 'type': '유형', 'when': '보이는 조건', 'free': '직접 입력 칸', 'group': '묶음 제목', 'retired': '빼기'}
# 손으로 쓰는 「추가」 기록의 모양 — 새 id 는 node.id, 부모는 node 의 부모 키와 parent(질문은 목차 id, 취향 질문은 하위 묶음 id)
ADD_EXAMPLE = {
    'screen': '{"op": "add", "node": {"t": "screen", "id": "S8"}, "data": {"title": "새 목차"}}',
    'dim': '{"op": "add", "node": {"t": "dim", "id": "new_dim"}, "parent": "S4", "data": {"name": "새 질문", "type": "single"}}',
    'value': '{"op": "add", "node": {"t": "value", "dim": "field", "id": "new_value"}, "parent": "field", "data": {"label": "새 선택지"}}',
    'cat': '{"op": "add", "node": {"t": "cat", "id": "P6"}, "data": {"name": "새 취향 묶음"}}',
    'sub': '{"op": "add", "node": {"t": "sub", "cat": "P2", "id": "P2.8"}, "data": {"name": "새 하위 묶음"}}',
    'aspect': '{"op": "add", "node": {"t": "aspect", "id": "P2.4.new_q"}, "parent": "P2.4", "data": {"text": "새 취향 질문?", "type": "single"}}',
    'option': '{"op": "add", "node": {"t": "option", "aspect": "P2.4.density", "id": "medium"}, "parent": "P2.4.density", "index": 2, "data": {"label": "새 선택지"}}',
    'pq': '{"op": "add", "node": {"t": "pq", "id": "new_pq"}, "data": {"text": "새 3부 질문", "type": "text"}}',
    'pqopt': '{"op": "add", "node": {"t": "pqopt", "pq": "delivery", "id": "new_opt"}, "data": {"label": "새 선택지"}}',
}


# ---------- 보이는 조건 ----------
def _vals(answers, k):
    v = answers.get(k)
    if v is None or v == '' or v == []:
        return None
    return v if isinstance(v, list) else [v]


def cond_ok(cond, answers, strict):
    for k, vs in (cond or {}).items():
        pv = _vals(answers, k)
        if pv is None:
            if strict:
                return False
            continue
        if not set(vs) & set(pv):
            return False
    return True


def cond_any(c, answers, strict):
    if not c:
        return True
    if isinstance(c, list):
        return any(cond_ok(x, answers, strict) for x in c)
    return cond_ok(c, answers, strict)


def when_ok(x, answers):
    if not x or x.get('retired'):
        return False
    if x.get('ask_when') and not cond_any(x['ask_when'], answers, bool(x.get('ask_strict'))):
        return False
    if x.get('applies_when') and not cond_any(x['applies_when'], answers, False):
        return False
    if x.get('when') and not cond_any(x['when'], answers, True):
        return False
    return True


def vis(lst, answers):
    return [o for o in (lst or []) if when_ok(o, answers)]


def dim_shown(d, answers, screens=None):
    """질문을 물을지. screens 를 주면 그 질문이 든 목차의 조건도 본다(목차가 숨으면 안의 질문도 숨는다)."""
    if screens is not None:
        s = next((s for s in screens if d['id'] in s.get('dimensions', [])), None)
        if s is not None and not when_ok(s, answers):
            return False
    return when_ok(d, answers) and (d.get('type') == 'text' or not d.get('values') or bool(vis(d['values'], answers)))


def asp_shown(a, answers):
    return when_ok(a, answers) and (a.get('type') in ('text', 'scale') or not a.get('options') or bool(vis(a['options'], answers)))


def clean_answers(dims_doc, qs_doc, ans):
    """숨은 질문·선택지의 답을 뺀 (dimensions, aspects, project). GUI의 cleanAnswers()와 같다."""
    dims = (dims_doc or {}).get('dimensions', [])
    screens = (dims_doc or {}).get('screens', [])
    cur = copy.deepcopy(ans.get('dimensions') or {})

    def empty(v):
        return v is None or v == '' or v == []
    for _ in range(8):
        nxt = copy.deepcopy(cur)
        ch = False
        for d in dims:
            did = d['id']
            if not dim_shown(d, cur, screens):
                for k in (did, did + '_other', did + '_primary'):
                    if k in nxt:
                        del nxt[k]; ch = True
                continue
            if d.get('type') == 'text' or empty(nxt.get(did)):
                continue
            ok = {v['id'] for v in vis(d.get('values'), cur)}
            v = nxt[did]
            if isinstance(v, list):
                f = [x for x in v if x in ok]
                if len(f) != len(v):
                    nxt[did] = f; ch = True
                    if nxt.get(did + '_primary') and nxt[did + '_primary'] not in f:
                        del nxt[did + '_primary']
            elif v not in ok:
                del nxt[did]; ch = True
            vv = nxt.get(did)
            if 'other' not in (vv if isinstance(vv, list) else [vv]) and (did + '_other') in nxt:
                del nxt[did + '_other']; ch = True
        cur = nxt
        if not ch:
            break
    asp_by = {a['id']: a for a in (qs_doc or {}).get('aspects', [])}
    pq_by = {q['id']: q for q in (qs_doc or {}).get('project_questions', [])}
    asp = {k: v for k, v in (ans.get('aspects') or {}).items() if k not in asp_by or asp_shown(asp_by[k], cur)}
    pj = {k: v for k, v in (ans.get('project') or {}).items() if k not in pq_by or when_ok(pq_by[k], cur)}
    return cur, asp, pj


def cond_text(c, dims_doc):
    """사람이 읽는 조건 문장."""
    if not c:
        return ''
    if isinstance(c, list):
        return ' 또는 '.join(cond_text(x, dims_doc) for x in c)
    by = {d['id']: d for d in (dims_doc or {}).get('dimensions', [])}
    out = []
    for k, vs in c.items():
        d = by.get(k)
        lab = {v['id']: v['label'] for v in (d or {}).get('values', [])}
        out.append(f"「{d['name'] if d else k}」에서 {'·'.join(lab.get(v, v) for v in vs)}")
    return ' 그리고 '.join(out)


# ---------- 구조 편집 기록 적용 ----------
class EditError(Exception):
    pass


def _find(lst, i):
    for x in lst:
        if x.get('id') == i:
            return x
    return None


def _locate(m, node):
    """(대상, 담긴 목록 또는 dict) — 없으면 EditError."""
    t, i = node.get('t'), node.get('id')
    D, Q = m['dims'], m['qs']
    if t == 'screen':
        lst = D.setdefault('screens', [])
    elif t == 'dim':
        lst = D.setdefault('dimensions', [])
    elif t == 'value':
        d = _find(D.get('dimensions', []), node.get('dim'))
        if d is None:
            raise EditError(f"질문 {node.get('dim')!r} 없음")
        lst = d.setdefault('values', [])
    elif t == 'cat':
        lst = Q.setdefault('categories', [])
    elif t == 'sub':
        c = _find(Q.get('categories', []), node.get('cat'))
        if c is None:
            raise EditError(f"취향 묶음 {node.get('cat')!r} 없음")
        subs = c.setdefault('subs', {})
        if i not in subs:
            raise EditError(f'하위 묶음 {i!r} 없음')
        return subs, c
    elif t == 'aspect':
        lst = Q.setdefault('aspects', [])
    elif t == 'option':
        a = _find(Q.get('aspects', []), node.get('aspect'))
        if a is None:
            raise EditError(f"취향 질문 {node.get('aspect')!r} 없음")
        lst = a.setdefault('options', [])
    elif t == 'pq':
        lst = Q.setdefault('project_questions', [])
    elif t == 'pqopt':
        q = _find(Q.get('project_questions', []), node.get('pq'))
        if q is None:
            raise EditError(f"3부 질문 {node.get('pq')!r} 없음")
        lst = q.setdefault('options', [])
    else:
        raise EditError(f'모르는 항목 종류 {t!r}')
    x = _find(lst, i)
    if x is None:
        raise EditError(f'{T_NAME.get(t, t)} {i!r} 없음')
    return x, lst


def _list_of(m, node):
    """새 항목이 들어갈 목록."""
    t = node.get('t')
    D, Q = m['dims'], m['qs']
    if t == 'screen':
        return D.setdefault('screens', [])
    if t == 'dim':
        return D.setdefault('dimensions', [])
    if t == 'value':
        d = _find(D.get('dimensions', []), node.get('dim'))
        if d is None:
            raise EditError(f"질문 {node.get('dim')!r} 없음")
        return d.setdefault('values', [])
    if t == 'cat':
        return Q.setdefault('categories', [])
    if t == 'aspect':
        return Q.setdefault('aspects', [])
    if t == 'option':
        a = _find(Q.get('aspects', []), node.get('aspect'))
        if a is None:
            raise EditError(f"취향 질문 {node.get('aspect')!r} 없음")
        return a.setdefault('options', [])
    if t == 'pq':
        return Q.setdefault('project_questions', [])
    if t == 'pqopt':
        q = _find(Q.get('project_questions', []), node.get('pq'))
        if q is None:
            raise EditError(f"3부 질문 {node.get('pq')!r} 없음")
        return q.setdefault('options', [])
    raise EditError(f'모르는 항목 종류 {t!r}')


def _ins(lst, x, index):
    if index is None or index < 0 or index > len(lst):
        lst.append(x)
    else:
        lst.insert(index, x)


def _sub_cat(m, sub):
    for c in m['qs'].get('categories', []):
        if sub in (c.get('subs') or {}):
            return c
    return None


def _aspect_place(m, aid, sub, index):
    """취향 질문 aid 를 하위 sub 안의 index 번째에 둔다(전체 목록 순서로)."""
    A = m['qs']['aspects']
    a = _find(A, aid)
    A.remove(a)
    a['sub'] = sub
    same = [x for x in A if x.get('sub') == sub]
    if not same:
        # 같은 묶음의 앞 하위 묶음 뒤에 둔다
        c = _sub_cat(m, sub)
        order = list((c or {}).get('subs', {}).keys())
        pos = len(A)
        if sub in order:
            before = order[:order.index(sub)]
            idxs = [k for k, x in enumerate(A) if x.get('sub') in before]
            if idxs:
                pos = idxs[-1] + 1
            else:
                cat_idxs = [k for k, x in enumerate(A) if c and str(x.get('sub', '')).startswith(c['id'] + '.')]
                pos = cat_idxs[0] if cat_idxs else len(A)
        A.insert(pos, a)
        return
    if index is None or index >= len(same):
        A.insert(A.index(same[-1]) + 1, a)
    else:
        A.insert(A.index(same[max(0, index)]), a)


def apply_op(m, op):
    kind, node = op.get('op'), op.get('node') or {}
    t = node.get('t')
    if kind == 'set':
        f = op.get('field')
        if f not in FIELDS.get(t, ()):
            raise EditError(f'{T_NAME.get(t, t)}의 {f!r} 칸은 바꿀 수 없음')
        if t == 'sub':
            subs, _c = _locate(m, node)
            if op.get('after') in (None, ''):
                raise EditError('하위 묶음 이름은 비울 수 없음')
            subs[node['id']] = op['after']
            return
        x, _lst = _locate(m, node)
        if op.get('after') is None or op.get('after') == '' or op.get('after') == [] or op.get('after') is False:
            x.pop(f, None)
        else:
            x[f] = copy.deepcopy(op['after'])
        if f == 'when':
            for k in LEGACY:
                x.pop(k, None)
        return
    if kind == 'add':
        data = copy.deepcopy(op.get('data') or {})
        # 새 id 는 node.id 에 둔다(편집기가 그렇게 내보낸다). 손으로 쓴 기록이 data.id 에만 두었으면 그것을 쓴다.
        if node.get('id') and data.get('id') and node['id'] != data['id']:
            raise EditError(f"새 항목의 id 가 두 곳에서 다름(node.id {node['id']!r} ≠ data.id {data['id']!r}) — 한 값으로 맞추세요")
        data['id'] = node.get('id') or data.get('id')
        if not data['id']:
            raise EditError('새 항목에 id 가 없음 — 새 id 는 node 안에 넣는다: ' + ADD_EXAMPLE.get(t, ADD_EXAMPLE['option']))
        if t == 'sub':
            c = _find(m['qs'].get('categories', []), node.get('cat'))
            if c is None:
                raise EditError(f"취향 묶음 {node.get('cat')!r} 없음")
            subs = c.setdefault('subs', {})
            if data['id'] in subs:
                raise EditError(f"하위 묶음 {data['id']!r} 이미 있음")
            items = list(subs.items())
            idx = op.get('index')
            items.insert(len(items) if idx is None else max(0, min(idx, len(items))), (data['id'], data.get('name') or data['id']))
            c['subs'] = dict(items)
            return
        lst = _list_of(m, node)
        if _find(lst, data['id']) is not None:
            raise EditError(f"{T_NAME.get(t, t)} {data['id']!r} 이미 있음")
        if t == 'screen':
            data.setdefault('dimensions', [])
            _ins(lst, data, op.get('index'))
        elif t == 'dim':
            scr = _find(m['dims'].get('screens', []), op.get('parent'))
            if scr is None:
                raise EditError(f"목차 {op.get('parent')!r} 없음")
            data.setdefault('type', 'single')
            if data['type'] != 'text':
                data.setdefault('values', [])
            lst.append(data)
            _ins(scr.setdefault('dimensions', []), data['id'], op.get('index'))
        elif t == 'aspect':
            sub = op.get('parent') or data.get('sub')
            if not _sub_cat(m, sub):
                raise EditError(f'하위 묶음 {sub!r} 없음')
            if not str(data['id']).startswith(sub + '.'):
                raise EditError(f"취향 질문 id 는 하위 묶음 이름으로 시작해야 함({sub}.…)")
            data.setdefault('type', 'single')
            if data['type'] in ('single', 'multi'):
                data.setdefault('options', [])
            lst.append(data)
            _aspect_place(m, data['id'], sub, op.get('index'))
        elif t == 'cat':
            data.setdefault('subs', {})
            _ins(lst, data, op.get('index'))
        else:
            _ins(lst, data, op.get('index'))
        return
    if kind == 'move':
        idx = op.get('index')
        if t == 'sub':
            subs, c = _locate(m, node)
            items = [(k, v) for k, v in subs.items() if k != node['id']]
            items.insert(len(items) if idx is None else max(0, min(idx, len(items))), (node['id'], subs[node['id']]))
            c['subs'] = dict(items)
            return
        x, lst = _locate(m, node)
        if t == 'dim':
            scrs = m['dims'].get('screens', [])
            src = next((s for s in scrs if x['id'] in s.get('dimensions', [])), None)
            dst = _find(scrs, op.get('parent')) if op.get('parent') else src
            if dst is None:
                raise EditError(f"목차 {op.get('parent')!r} 없음")
            if src is not None:
                src['dimensions'].remove(x['id'])
            _ins(dst.setdefault('dimensions', []), x['id'], idx)
            return
        if t == 'aspect':
            sub = op.get('parent') or x.get('sub')
            if sub != x.get('sub'):  # id 가 하위 묶음으로 시작해야 하고(check_store), 취향 항목이 그 id 를 가리키므로 다른 하위 묶음으로는 못 옮긴다
                raise EditError(f"취향 질문은 다른 하위 묶음으로 옮길 수 없음({x.get('sub')} → {sub}) — 새 질문을 만들고 옛 질문은 빼기")
            _aspect_place(m, x['id'], sub, idx)
            return
        lst.remove(x)
        _ins(lst, x, idx)
        return
    raise EditError(f'모르는 편집 {kind!r}')


def replay(dims_doc, qs_doc, ops):
    """기록을 순서대로 적용한 (dims, qs, 문제 목록). 실패한 기록은 건너뛰고 문제에 적는다."""
    m = {'dims': copy.deepcopy(dims_doc), 'qs': copy.deepcopy(qs_doc)}
    problems = []
    for k, op in enumerate(ops or []):
        try:
            apply_op(m, op)
        except EditError as e:
            problems.append(f'{k + 1}번째 편집({describe(op)}): {e}')
    return m['dims'], m['qs'], problems


def _label_of(node):
    return node.get('label') or node.get('id')


def describe(op, dims_doc=None):
    """편집 한 건을 사람이 읽는 문장으로."""
    node = op.get('node') or {}
    t = T_NAME.get(node.get('t'), node.get('t'))
    nm = f"{t} 「{op.get('label') or node.get('id')}」"
    k = op.get('op')
    if k == 'set':
        f = op.get('field')
        if f == 'retired':
            return f'{nm} 빼기' if op.get('after') else f'{nm} 되살리기'
        if f == 'when':
            return f"{nm} 보이는 조건: {cond_text(op.get('after'), dims_doc) or '항상 보임'}"
        return f"{nm} {F_NAME.get(f, f)}: {op.get('before')!r} → {op.get('after')!r}"
    if k == 'add':
        d = op.get('data') or {}
        where = f" (위치: {op.get('parent')})" if op.get('parent') else ''
        return f"{t} 추가 「{d.get('label') or d.get('name') or d.get('title') or d.get('text') or node.get('id')}」{where}"
    if k == 'move':
        return f"{nm} 옮기기 → {op.get('parent') or '같은 곳'} {'' if op.get('index') is None else str(op['index'] + 1) + '번째'}"
    return f'{k} {nm}'


def check_conditions(dims_doc, qs_doc):
    """보이는 조건이 있는 차원·값을 가리키는지 (오류, 경고)."""
    errors, warnings = [], []
    dims = dims_doc.get('dimensions', [])
    values = {d['id']: {v['id'] for v in d.get('values', [])} for d in dims}
    order = [did for s in dims_doc.get('screens', []) for did in s.get('dimensions', [])]
    pos = {did: k for k, did in enumerate(order)}

    def chk(where, c, self_dim=None):
        for k in ([x for g in c for x in g.items()] if isinstance(c, list) else list((c or {}).items())):
            dk, vs = k
            if dk not in values:
                errors.append(f'{where}: 조건의 질문 {dk!r} 없음')
                continue
            if not isinstance(vs, list) or not vs:
                errors.append(f'{where}: 조건 {dk} 의 값 목록이 비었음')
                continue
            for v in vs:
                if v not in values[dk]:
                    errors.append(f'{where}: 조건 {dk} 에 값 {v!r} 없음')
            if self_dim is not None:
                if dk == self_dim:
                    errors.append(f'{where}: 자기 자신을 조건으로 씀')
                elif dk in pos and self_dim in pos and pos[dk] > pos[self_dim]:
                    warnings.append(f'{where}: 조건의 질문 {dk} 가 이 질문보다 뒤에 있음(앞에 두기를 권함)')
    for s in dims_doc.get('screens', []):
        if s.get('when'):
            chk(f"목차 {s['id']}", s['when'])
    for d in dims:
        for key in ('when', 'ask_when'):
            if d.get(key):
                chk(f"질문 {d['id']}", d[key], d['id'])
        for v in d.get('values', []):
            if v.get('when'):
                chk(f"선택지 {d['id']}.{v['id']}", v['when'], d['id'])
    for c in qs_doc.get('categories', []):
        if c.get('when'):
            chk(f"취향 묶음 {c['id']}", c['when'])
    for a in qs_doc.get('aspects', []):
        for key in ('when', 'applies_when'):
            if a.get(key):
                chk(f"취향 질문 {a['id']}", a[key])
        for o in a.get('options', []) or []:
            if o.get('when'):
                chk(f"취향 선택지 {a['id']}.{o['id']}", o['when'])
    for q in qs_doc.get('project_questions', []):
        if q.get('when'):
            chk(f"3부 질문 {q['id']}", q['when'])
        for o in q.get('options', []) or []:
            if o.get('when'):
                chk(f"3부 선택지 {q['id']}.{o['id']}", o['when'])
    return errors, warnings
