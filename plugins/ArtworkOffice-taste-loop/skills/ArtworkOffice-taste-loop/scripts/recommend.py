#!/usr/bin/env python3
"""대화 추천 — 기록하고 스스로 진화한다 (엔진 1.4.0, 사용자 결정 2026-11-09).

흐름
  1. Claude가 인터뷰 페이지를 만들기 전에 대화로 「무엇을 · 누구에게 · 왜 · 어떻게」를 알아본다.
     대화 요약은 <작업폴더>/materials/인터뷰/00_대화요약.md, 추천은 00_추천.json 에 쓴다(형식은 아래).
  2. `recommend.py suggest --from 00_추천.json --write` — 지난 기록에서 배운 규칙으로 대화가 정하지 않은 칸을 채운다.
     (대화에서 사용자가 직접 말한 것 basis "said" 는 규칙이 바꾸지 않는다. Claude가 짐작한 것 "inferred" 는
     수정 요청이 섞인 강한 규칙이 다르면 규칙이 이긴다.)
  3. `build_interview.py … --recommend 00_추천.json` — 인터뷰가 추천 답이 골라진 채로 열린다(「대화 추천」 표시 · 이유 · 요약판).
  4. 사용자가 제출하면 `recommend.py record <답변.json>` — 추천과 최종 답의 차이(그대로 · 바꿈 · 지움)와
     추천 없이 답한 것까지 상황 신호와 함께 기록하고 규칙을 다시 배운다.
  5. 제작 중이든 끝난 뒤든 사용자가 「이건 ○○로 바꿔」라고 고치면 `recommend.py correct …` — 가중치 5(보통 기록의 5배)로
     기록한다. 사용자 결정(2026-11-09): 수정 요청은 보상 점수가 훨씬 높아 보정이 더 잘 되게.
  사용자에게 확인 질문을 하지 않는다. 같은 상황인데 다르게 끝난 칸(「갈린 칸」, 기록 파일의 shaky)은 두 갈래로 나눈다(사용자 결정 2026-11-09):
    ① 작업 여건·상황이 조금이라도 달랐다는 단서가 **확실하면** 「단서 규칙」 두 개(단서 있음 → 값1 · 없음 → 값2)로 반영한다.
       확실함 = 단서가 있을 때·없을 때 각각 2번 이상, 양쪽 모두 80% 이상 한 값, 우연히 그렇게 갈릴 확률(피셔 정확 검정) 10% 이하.
       단서 후보: 대화의 tag: · 1부 답 dim. · 페이지가 제출 때 보낸 작업 여건 ctx:(기기 · 시간대 · 요일 · 여는 방식).
    ② 애매하면 「그때그때 취향」으로 보고 기록만 쌓는다. 쌓일수록 어느 쪽으로 기우는지(기울 확률 = 베타 분포에서 그 값이 더 자주
       고르는 쪽일 확률)를 계산해 80% 이상이면 그 값을 미리 고르고(「그때그때 갈림 — ○ 쪽으로 기움」), 아직 반반이면 고르지 않는다.
       수정 요청이 든 쪽은 기록이 적어도 바로 보정한다. 나중에 확실한 단서가 생기면 다음 learn 에서 ①로 바뀌고 history 에 남는다.
    작업 여건(ctx:) 규칙은 인터뷰 페이지가 열릴 때 그 자리의 여건으로 판정한다(build_interview.py 가 ctx_rules 로 넣는다).

파일(데이터 폴더 knowledge/)
  recommend_log.json    기록(손으로 고치지 않는다 — 한 줄에 한 건). {"version":1, "events":[…]}
  recommend_rules.json  배운 규칙(kind: split 단서 · plain 보통 · mood 그때그때 기울기) · 갈린 칸(shaky: condition 단서로 풂 · mood 그때그때) ·
                        적중률 · history(바뀐 판단 — 생김 · 사라짐 · 그때그때 → 단서). learn 이 매번 기록 전체에서 다시 만든다
신호(상황) 하나 더: "ctx:<여건>=<값>" (인터뷰 페이지가 제출 때 자동으로 — 손으로 쓰지 않는다)

키: dim.<1부 질문 id> · asp.<취향 질문 id> · pq.<3부 질문 id>
신호(상황): "dim.<질문>=<값>" (1부 답·대화에서 정해진 것) · "tag:<낱말>" (대화에서 나온 특징 — 예: tag:공모전, tag:마감임박)

00_추천.json
  {"id": "<판 이름>", "source": "conversation", "summary": "materials/인터뷰/00_대화요약.md",
   "signals": ["tag:…", …],
   "dimensions": {"<질문>": {"value": 값, "reason": "<한 줄 근거>", "basis": "said|inferred|rule:<id>"}},
   "aspects":    {"<취향 질문>": {…같은 꼴}},
   "project":    {"<3부 질문>": {…같은 꼴}}}

사용법
  python3 recommend.py check <00_추천.json>                     질문 은행과 맞는지 검사(없는 질문·선택지를 알린다)
  python3 recommend.py suggest (--from <00_추천.json> [--write] | --signals "<신호>,<신호>")
  python3 recommend.py record <답변.json> [--project <작업폴더>]  (같은 제출은 두 번 기록하지 않는다)
  python3 recommend.py correct --project <작업폴더> --key <키> --value '<JSON 값>' --said "<사용자 원문>" [--signals "<신호>,…"]
  python3 recommend.py learn                                    규칙 다시 만들기
  python3 recommend.py stats                                    적중률 · 규칙 · 갈린 칸(단서 / 그때그때) · 최근 바뀐 판단
  python3 recommend.py selftest
"""
import collections
import datetime
import hashlib
import json
import math
import pathlib
import re
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import store as ST  # noqa: E402

VERSION = 1
CORRECTION_WEIGHT = 5.0   # 사용자가 직접 고치라고 한 것(보통 기록의 5배)
ANSWER_WEIGHT = 1.0       # 인터뷰에서 그대로 두거나 바꾼 것
DECAY = 0.85              # 프로젝트가 하나 지날 때마다 옛 기록의 무게(최근 취향이 이긴다)
MIN_SUPPORT = 2.0         # 규칙이 되려면 이 값만큼 가중치(감쇠 전)가 모여야 한다 — 수정 요청 한 번(5)이면 바로 규칙
MIN_CONF = 0.7            # 그 값의 몫(감쇠 뒤)
REFINE_CONF = 0.8         # 단서로 나눈 양쪽이 각각 한 값으로 모인 몫
SPLIT_P = 0.1             # 단서가 확실하다고 볼 우연 확률의 상한(피셔 정확 검정) — 2번 대 2번 완전 갈림(17%)은 아직 우연일 수 있다
MIN_SIDE = 2              # 단서가 있을 때·없을 때 각각 최소 기록 수
LEAN_PROB = 0.8           # 그때그때 취향: 한쪽으로 기울 확률이 이만큼 되면 그 값을 미리 고른다
MIN_MOOD_EVENTS = 3       # 그때그때 취향의 기울기를 쓰려면 최소 기록 수
NONE = '∅'                # 「미리 고르지 않음」(지움 · 제외)
KEY_RE = re.compile(r'^(dim|asp|pq)\.[A-Za-z0-9_.\-]+$')
SIG_RE = re.compile(r'^(dim\.[A-Za-z0-9_.\-]+=.+|tag:.+|ctx:[^=]+=.+)$')  # ctx: 작업 여건(페이지가 제출 때 자동으로 — 기기·시간대·요일·여는 방식)
BASES = ('said', 'inferred')
OUTCOMES = ('kept', 'changed', 'cleared', 'answered', 'corrected')
SECTIONS = (('dimensions', 'dim'), ('aspects', 'asp'), ('project', 'pq'))


# ---------- 공통 ----------
def know_dir():
    return ST.KNOW


def log_path(know=None):
    return pathlib.Path(know or know_dir()) / 'recommend_log.json'


def rules_path(know=None):
    return pathlib.Path(know or know_dir()) / 'recommend_rules.json'


def load_json(p):
    return json.loads(pathlib.Path(p).read_text(encoding='utf-8-sig'))


def norm(v):
    """값 비교용 문자열. 목록은 순서 무시. 없음(None·빈 값)은 NONE."""
    if v is None or v == '' or (isinstance(v, list) and not v):
        return NONE
    if isinstance(v, list):
        return json.dumps(sorted(v, key=lambda x: json.dumps(x, ensure_ascii=False)), ensure_ascii=False)
    return json.dumps(v, ensure_ascii=False)


def unnorm(s):
    return None if s == NONE else json.loads(s)


def bank():
    """(1부 질문 {id: d}, 취향 질문 {id: a}, 3부 질문 {id: q}) — 이관·반영 대기 편집을 적용한 지금 모습."""
    import upgrade_store as UP
    import structure_edits as SE
    dims, _ = UP.migrate_dims(load_json(ST.path('dimensions.json')))
    qs, _ = UP.migrate_qs(load_json(ST.path('questions.json')))
    try:
        dims, qs, _n, _p = SE.with_pending(dims, qs)
    except Exception:  # noqa: BLE001  편집 기록이 없거나 깨져도 추천은 원본 은행으로
        pass
    return ({d['id']: d for d in dims.get('dimensions', [])},
            {a['id']: a for a in qs.get('aspects', [])},
            {q['id']: q for q in qs.get('project_questions', [])})


def item_of(key, B):
    kind, _, qid = key.partition('.')
    return {'dim': B[0], 'asp': B[1], 'pq': B[2]}[kind].get(qid)


def opts_of(item):
    return {o['id'] for o in (item.get('values') or item.get('options') or [])}


def learnable(item):
    """고르는 질문만 배운다(자유 입력은 다음 자료에 그대로 쓸 수 없다)."""
    return bool(item) and item.get('type') in ('single', 'multi', None) and bool(opts_of(item))


def check_value(key, v, B):
    """(정리한 값, 문제 문장 또는 None)"""
    it = item_of(key, B)
    if not it:
        return None, f'{key}: 질문 은행에 없는 질문'
    if v is None:
        return None, None
    if it.get('type') in ('text', 'scale') or not opts_of(it):
        return v, None
    vs = v if isinstance(v, list) else [v]
    bad = [x for x in vs if x not in opts_of(it)]
    if bad:
        return None, f'{key}: 선택지에 없는 값 {bad}'
    if it.get('type') == 'multi' and not isinstance(v, list):
        v = [v]
    if it.get('type') == 'single' and isinstance(v, list):
        if len(v) != 1:
            return None, f'{key}: 하나만 고르는 질문에 값 {len(v)}개'
        v = v[0]
    return v, None


def clean_reco(reco, B=None):
    """00_추천.json 검사·정리. (정리한 것, 알림 목록). build_interview.py 도 쓴다."""
    B = B or bank()
    notes = []
    if not isinstance(reco, dict):
        return None, ['추천 파일은 JSON 객체여야 합니다']
    out = {k: reco[k] for k in ('id', 'source', 'summary') if reco.get(k)}
    out.setdefault('source', 'conversation')
    sig = []
    for s in reco.get('signals') or []:
        if isinstance(s, str) and SIG_RE.match(s.strip()):
            sig.append(s.strip())
        else:
            notes.append(f'신호 {s!r}: 형식은 dim.<질문>=<값> 또는 tag:<낱말> — 뺌')
    out['signals'] = sig
    for sec, kind in SECTIONS:
        out[sec] = {}
        for qid, s in (reco.get(sec) or {}).items():
            if not isinstance(s, dict) or 'value' not in s:
                s = {'value': s}
            base = re.sub(r'_(other|primary)$', '', qid) if kind == 'dim' else qid
            if kind == 'dim' and base != qid:  # 기타 내용 · 주 대상은 값 검사 없이(주 대상은 고른 값 중 하나여야 한다)
                if not item_of('dim.' + base, B):
                    notes.append(f'dim.{qid}: 질문 은행에 없는 질문 — 뺌'); continue
                out[sec][qid] = {'value': s.get('value'), 'reason': str(s.get('reason') or ''), 'basis': s.get('basis') or 'inferred'}
                continue
            v, prob = check_value(f'{kind}.{qid}', s.get('value'), B)
            if prob:
                notes.append(prob + ' — 뺌'); continue
            if v is None:
                notes.append(f'{kind}.{qid}: 값 없음 — 뺌'); continue
            basis = str(s.get('basis') or 'inferred')
            if basis not in BASES and not basis.startswith('rule:'):
                notes.append(f'{kind}.{qid}: basis {basis!r} → inferred'); basis = 'inferred'
            out[sec][qid] = {'value': v, 'reason': str(s.get('reason') or ''), 'basis': basis}
    return out, notes


def reco_signals(reco):
    """추천 파일의 신호 + 추천한 1부 값(그 자체가 상황이다)."""
    sig = set(reco.get('signals') or [])
    for qid, s in (reco.get('dimensions') or {}).items():
        if re.search(r'_(other|primary)$', qid):
            continue
        v = s.get('value') if isinstance(s, dict) else s
        for x in (v if isinstance(v, list) else [v]):
            if x is not None and not isinstance(x, (dict, list)):
                sig.add(f'dim.{qid}={x}')
    return sig


# ---------- 기록 읽기·쓰기 ----------
def read_log(know=None):
    p = log_path(know)
    if not p.exists():
        return {'version': VERSION, 'note': '대화 추천 기록 — recommend.py 로만 쓴다(한 줄에 한 건). 지우지 않는다', 'events': []}
    d = load_json(p)
    d.setdefault('events', [])
    return d


def write_log(d, know=None):
    p = log_path(know)
    p.parent.mkdir(parents=True, exist_ok=True)
    head = {k: v for k, v in d.items() if k != 'events'}
    lines = [json.dumps(e, ensure_ascii=False, sort_keys=False) for e in d['events']]
    text = json.dumps(head, ensure_ascii=False, indent=2)[:-2] + ',\n  "events": [' + ('\n    ' + ',\n    '.join(lines) + '\n  ' if lines else '') + ']\n}\n'
    json.loads(text)  # 쓰기 전에 다시 읽혀야 한다
    p.write_bytes(text.encode('utf-8'))


def write_rules(r, know=None):
    p = rules_path(know)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes((json.dumps(r, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))


# ---------- 배우기 ----------
def _same_key(sig, key):
    kind, _, qid = key.partition('.')
    return kind == 'dim' and (sig.startswith(f'dim.{qid}=') or sig.startswith(f'dim.{qid}_'))


def _rid(when, key, kind='plain'):
    base = [sorted(when), key] + ([kind] if kind != 'plain' else [])  # 같은 조건의 보통 규칙과 단서·기울기 규칙이 겹치지 않게
    return 'R-' + hashlib.sha1(json.dumps(base, ensure_ascii=False).encode('utf-8')).hexdigest()[:8]


def _when_text(when):
    return ' 그리고 '.join(w[1:] + ' 아님' if w.startswith('!') else w for w in when) if when else '모든 상황'


def _match(when, sig):
    """조건 목록이 신호에 맞는가. '!<신호>' 는 「그 신호가 없을 때」."""
    return all((w[1:] not in sig) if w.startswith('!') else (w in sig) for w in when)


def _fisher(a, b, c, d):
    """2×2 표의 한쪽 피셔 정확 검정: 단서가 있는 쪽에 그 값이 a번 이상 몰릴 확률(우연이라면). 작을수록 확실하다."""
    n1, k, n = a + b, a + c, a + b + c + d
    tot = math.comb(n, n1)
    return sum(math.comb(k, x) * math.comb(n - k, n1 - x) for x in range(a, min(n1, k) + 1)) / tot


def _lean_prob(w1, w2):
    """그때그때 갈리는 칸: 두 값의 (감쇠·가중) 기록이 w1·w2 일 때 1번 값이 실제로 더 자주 고르는 쪽일 확률.
    베타 분포 Beta(w1+1, w2+1)에서 p > 0.5 일 확률(심프슨 적분, 난수 없음 — 같은 기록이면 같은 결과)."""
    a, b = w1 + 1.0, w2 + 1.0
    lb = math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)
    f = lambda x: math.exp((a - 1) * math.log(x) + (b - 1) * math.log(1 - x) - lb)
    n, lo, hi = 2000, 0.5, 1 - 1e-12
    h = (hi - lo) / n
    s = f(lo) + f(hi) + sum((4 if i % 2 else 2) * f(lo + i * h) for i in range(1, n))
    return max(0.0, min(1.0, s * h / 3))


KIND_RANK = {'split': 2, 'plain': 1, 'mood': 0}  # 추천을 고를 때: 확실한 단서 규칙 > 보통 규칙 > 그때그때 취향의 기울기


def learn(events):
    """기록 전체 → 규칙 · 흔들림(갈린 칸) · 적중률. 결정적(같은 기록이면 같은 결과).

    같은 상황인데 다르게 끝난 칸은 두 갈래로 나눈다(사용자 결정 2026-11-09):
      ① 작업 여건 · 상황이 조금이라도 달랐다는 단서가 **확실하면**(단서가 있을 때·없을 때 각각 2번 이상, 양쪽 모두 한 값으로 모이고
         ≥ REFINE_CONF, 우연히 그렇게 갈릴 확률 ≤ SPLIT_P) → 「단서 규칙」 두 개(단서 있음 → 값1 · 단서 없음 → 값2)로 반영한다.
      ② 애매하면 → 「그때그때 취향」으로 보고 기록만 쌓는다. 쌓일수록 어느 쪽으로 기우는지(기울 확률)를 계산해,
         LEAN_PROB 이상 확실해지면 그 값을 미리 고른다(「그때그때 갈림 — ○ 쪽으로 기움」). 아직 반반이면 미리 고르지 않는다.
      나중에 확실한 단서가 생기면 다음 learn 에서 ①로 바뀐다(기록 전체에서 매번 다시 배우므로).
    """
    first = {}
    for e in events:
        p = e.get('project') or ''
        first[p] = min(first.get(p, '9999'), e.get('date') or '9999')
    order = sorted(first, key=lambda p: (first[p], p))
    rank = {p: i for i, p in enumerate(order)}
    n = len(order)
    use = [e for e in events if e.get('outcome') in OUTCOMES and KEY_RE.match(e.get('key') or '')]
    score = collections.defaultdict(lambda: collections.defaultdict(float))    # 감쇠 뒤
    support = collections.defaultdict(lambda: collections.defaultdict(float))  # 감쇠 전
    count = collections.defaultdict(lambda: collections.defaultdict(int))
    corr = collections.defaultdict(lambda: collections.defaultdict(int))
    by_key = collections.defaultdict(list)  # 키 → [(신호 집합, 값, 가중, 감쇠 가중, 수정 요청인가)]
    for e in use:
        w = float(e.get('weight', ANSWER_WEIGHT))
        dw = w * DECAY ** (n - 1 - rank[e.get('project') or ''])
        fv = e.get('final_n') or norm(e.get('final'))
        sig = frozenset(s for s in e.get('signals') or [] if not _same_key(s, e['key']))
        by_key[e['key']].append((sig, fv, w, dw, e.get('kind') == 'correction'))
        for cond in [()] + [(s,) for s in sorted(sig)]:
            ck = (cond, e['key'])
            score[ck][fv] += dw; support[ck][fv] += w; count[ck][fv] += 1
            corr[ck][fv] += e.get('kind') == 'correction'

    def tally(rows):
        sc, su, cn, co = (collections.defaultdict(float), collections.defaultdict(float), collections.defaultdict(int), collections.defaultdict(int))
        for _sig, fv, w, dw, isc in rows:
            sc[fv] += dw; su[fv] += w; cn[fv] += 1; co[fv] += isc
        return sc, su, cn, co

    def make_rule(when, key, sc, su, cn, co, kind='plain', extra=None):
        top = max(sc, key=lambda v: (sc[v], su[v], v))
        tot = sum(sc.values())
        conf = sc[top] / tot if tot else 0
        if kind != 'mood' and (su[top] < MIN_SUPPORT or conf < MIN_CONF):
            return None
        r = {'id': _rid(when, key, kind), 'kind': kind, 'when': list(when), 'key': key, 'value': unnorm(top), 'no_preselect': top == NONE,
             'confidence': round(conf, 3), 'score': round(sc[top], 3), 'total': round(tot, 3), 'support': round(su[top], 3),
             'records': cn[top], 'corrections': co[top]}
        r.update(extra or {})
        head = {'split': '단서 규칙', 'plain': '규칙', 'mood': '그때그때 취향의 기울기'}[kind]
        r['reason'] = (f"{head} — {_when_text(when)}: {key} = {'미리 고르지 않음' if top == NONE else top} · 기록 {cn[top]}건"
                       + (f' (수정 요청 {co[top]}건)' if co[top] else '') + f', 몫 {conf:.0%}' + (r.get('why') and ' · ' + r['why'] or ''))
        return r

    rules, shaky = [], []
    for (cond, key) in sorted(score, key=lambda ck: (ck[1], len(ck[0]), ck[0])):
        r = make_rule(cond, key, score[(cond, key)], support[(cond, key)], count[(cond, key)], corr[(cond, key)])
        # 신호 하나를 조건으로 한 보통 규칙은 수정 요청이 든 것만 둔다 — 나머지는 우연히 겹친 신호일 수 있어
        # 아래 「확실한 단서」 검사를 통과해야 규칙이 된다(애매한 단서로 미리 고르지 않는다)
        # 모든 상황(조건 없음) 규칙은 기록이 한 값으로만 끝났을 때만 — 갈렸으면 아래에서 「단서」 또는 「그때그때 취향」으로 판단한다
        if r and ((not cond and len(score[((), key)]) == 1) or (cond and r['corrections'] and not cond[0].startswith('ctx:'))):  # 수정 요청이 든 신호 규칙(작업 여건 신호는 빼고 — 고친 자리의 기기·시간이 까닭이라는 근거가 없다)
            rules.append(r)
    for key in sorted(by_key):
        rows = by_key[key]
        vals = {fv for _s, fv, *_ in rows}
        if len(vals) < 2:
            continue
        sc, su, cn, co = tally(rows)
        tot = sum(sc.values())
        top = max(sc, key=lambda v: (sc[v], su[v], v))
        conf = sc[top] / tot if tot else 0
        # ① 확실한 단서 찾기: 그 신호가 있을 때와 없을 때 서로 다른 한 값으로 모이고, 우연일 확률이 작아야 한다
        cands = []
        for t in sorted({s for sig, *_ in rows for s in sig}):
            W = [x for x in rows if t in x[0]]
            O = [x for x in rows if t not in x[0]]
            if len(W) < MIN_SIDE or len(O) < MIN_SIDE:
                continue
            swc, _, _, _ = tally(W); soc, _, _, _ = tally(O)
            vw = max(swc, key=lambda v: (swc[v], v)); vo = max(soc, key=lambda v: (soc[v], v))
            if vw == vo or swc[vw] / sum(swc.values()) < REFINE_CONF or soc[vo] / sum(soc.values()) < REFINE_CONF:
                continue
            a = sum(1 for x in W if x[1] == vw); b = len(W) - a
            c = sum(1 for x in O if x[1] == vw); d = len(O) - c
            p = _fisher(a, b, c, d)
            if p <= SPLIT_P:
                cands.append((p, t, frozenset(id(x) for x in W), W, O))
        entry = {'id': _rid((), key), 'key': key, 'events': len(rows),
                 'values': {('미리 고르지 않음' if v == NONE else v): round(s, 3) for v, s in sorted(sc.items(), key=lambda kv: -kv[1])},
                 'top_share': round(conf, 3)}
        if cands:
            cands.sort(key=lambda c: (c[0], c[1]))
            p, t, wset, W, O = cands[0]
            same = [c[1] for c in cands[1:] if c[2] == wset]  # 늘 같이 움직이는 단서(어느 것이 진짜 까닭인지는 아직 모름)
            why = f'단서 {t}: 있을 때 {len(W)}번 · 없을 때 {len(O)}번이 서로 다른 값으로 모임, 우연일 확률 {p:.0%}' + (f' · 같이 움직이는 단서 {", ".join(same)}' if same else '')
            made = []
            for when, part in (((t,), W), (('!' + t,), O)):
                r2 = make_rule(when, key, *tally(part), kind='split', extra={'why': why, 'p': round(p, 4), 'together': same})
                if r2:
                    made.append(r2)
            rules.extend(made)
            entry.update(kind='condition', clue=t, together=same, p=round(p, 4), resolved_by=[r2['id'] for r2 in made],
                         note=f'{key}: 같은 칸이 {len(vals)}가지로 끝남 → 작업 여건·상황 차이로 판단 — {why}')
        else:
            # ② 애매 → 그때그때 취향. 기록이 쌓일수록 기우는 쪽을 계산
            order2 = sorted(sc, key=lambda v: (-sc[v], v))
            lp = _lean_prob(sc[order2[0]], sc[order2[1]])
            entry.update(kind='mood', lean=('미리 고르지 않음' if order2[0] == NONE else order2[0]), lean_prob=round(lp, 3))
            if lp >= LEAN_PROB and (len(rows) >= MIN_MOOD_EVENTS or co[order2[0]]):  # 수정 요청이 든 쪽은 기록이 적어도 바로 보정
                rm = make_rule((), key, sc, su, cn, co, kind='mood', extra={'lean_prob': round(lp, 3), 'why': f'확실한 단서 없음 → 기록 {len(rows)}건에서 이쪽으로 기울 확률 {lp:.0%}'})
                rules.append(rm)
                entry['resolved_by'] = [rm['id']]
                entry['note'] = f"{key}: 그때그때 갈림(확실한 단서 없음) — {entry['lean']} 쪽으로 기울 확률 {lp:.0%} → 미리 고름"
            else:
                entry['resolved_by'] = []
                entry['note'] = f"{key}: 그때그때 갈림(확실한 단서 없음) — {entry['lean']} 쪽 {lp:.0%}, 아직 반반이라 미리 고르지 않고 기록만 쌓음"
        shaky.append(entry)
    return {'version': VERSION, 'updated': datetime.date.today().isoformat(),
            'params': {'correction_weight': CORRECTION_WEIGHT, 'answer_weight': ANSWER_WEIGHT, 'decay_per_project': DECAY,
                       'min_support': MIN_SUPPORT, 'min_confidence': MIN_CONF, 'refine_confidence': REFINE_CONF,
                       'split_p': SPLIT_P, 'min_side': MIN_SIDE, 'lean_prob': LEAN_PROB, 'min_mood_events': MIN_MOOD_EVENTS},
            'stats': stats(events), 'rules': rules, 'shaky': shaky}


def stats(events):
    runs = collections.OrderedDict()
    for e in events:
        if e.get('kind') != 'interview':
            continue
        r = runs.setdefault(e.get('run'), {'run': e.get('run'), 'project': e.get('project'), 'date': e.get('date'), 'recommended': 0, 'kept': 0, 'changed': 0, 'cleared': 0, 'answered': 0})
        o = e.get('outcome')
        if o in ('kept', 'changed', 'cleared'):
            r['recommended'] += 1; r[o] += 1
        elif o == 'answered':
            r['answered'] += 1
    for r in runs.values():
        r['hit_rate'] = round(r['kept'] / r['recommended'], 3) if r['recommended'] else None
    rec = sum(r['recommended'] for r in runs.values())
    kept = sum(r['kept'] for r in runs.values())
    corr = [e for e in events if e.get('kind') == 'correction']
    return {'events': len(events), 'interviews': len(runs), 'recommended': rec, 'kept': kept,
            'hit_rate': round(kept / rec, 3) if rec else None, 'corrections': len(corr),
            'runs': list(runs.values())[-10:],
            'recent_corrections': [{k: e.get(k) for k in ('date', 'project', 'key', 'final', 'said')} for e in corr[-5:]]}


def relearn(know=None):
    """다시 배우고, 지난번과 달라진 규칙·판단(생김 · 사라짐 · 그때그때 → 단서 등)을 history 에 남긴다(최근 100건)."""
    old = {}
    p = rules_path(know)
    if p.exists():
        try:
            old = load_json(p)
        except ValueError:
            old = {}
    r = learn(read_log(know)['events'])
    before = {x['id']: x for x in old.get('rules') or []}
    after = {x['id']: x for x in r['rules']}
    sk_b = {x['key']: x.get('kind') for x in old.get('shaky') or []}
    sk_a = {x['key']: x.get('kind') for x in r['shaky']}
    lines = [f"생김: {after[i]['reason']}" for i in sorted(set(after) - set(before))]
    lines += [f"사라짐: {before[i]['reason']}" for i in sorted(set(before) - set(after))]
    lines += [f"{k}: {('그때그때' if sk_b.get(k) == 'mood' else '단서' if sk_b.get(k) == 'condition' else '갈림 없음')} → {('그때그때' if sk_a.get(k) == 'mood' else '단서' if sk_a.get(k) == 'condition' else '갈림 없음')}"
              for k in sorted(set(sk_a) | set(sk_b)) if sk_a.get(k) != sk_b.get(k)]
    hist = list(old.get('history') or [])
    if lines:
        hist.append({'date': r['updated'], 'events': r['stats']['events'], 'changes': lines})
    r['history'] = hist[-100:]
    write_rules(r, know)
    return r


# ---------- 추천하기 ----------
def rule_key(r):
    return (KIND_RANK.get(r.get('kind', 'plain'), 1), len(r['when']), r['confidence'], r['support'])


def suggest(signals, rules):
    """신호 → {키: 규칙}. 확실한 단서 규칙 > 보통 규칙 > 그때그때 취향의 기울기, 같으면 구체적인(조건이 많은) 것 · 몫이 큰 것.
    작업 여건(ctx:) 조건이 든 규칙은 여기서 쓰지 않는다 — 인터뷰 페이지가 열릴 때 그 자리의 여건으로 판정한다(ctx_rules).
    추천한 1부 값은 신호에 더해 다시 본다."""
    sig = set(signals)
    picked = {}
    for _ in range(3):
        best = {}
        for r in rules:
            if any(w.lstrip('!').startswith('ctx:') for w in r['when']) or not _match(r['when'], sig):
                continue
            k = rule_key(r)
            if r['key'] not in best or k > best[r['key']][0]:
                best[r['key']] = (k, r)
        picked = {key: r for key, (_, r) in best.items()}
        new = set(sig)
        for key, r in picked.items():
            if key.startswith('dim.') and not r['no_preselect']:
                for x in (r['value'] if isinstance(r['value'], list) else [r['value']]):
                    new.add(f'{key}={x}')
        if new == sig:
            break
        sig = new
    return picked


def ctx_rules(signals, rules):
    """인터뷰 페이지로 보낼 작업 여건 규칙: ctx: 조건이 있고, 나머지 조건은 지금 신호에 맞는 것."""
    sig = set(signals)
    out = []
    for r in rules:
        cx = [w for w in r['when'] if w.lstrip('!').startswith('ctx:')]
        rest = [w for w in r['when'] if w not in cx]
        if cx and _match(rest, sig):
            out.append(dict({k: r[k] for k in ('id', 'kind', 'key', 'value', 'no_preselect', 'reason', 'confidence', 'support')}, when=cx, rank=list(rule_key(r))))
    return out


def merge(reco, picked):
    """규칙 추천을 추천 파일에 합친다. (합친 것, 바뀐 줄 목록)"""
    out = json.loads(json.dumps(reco, ensure_ascii=False))
    lines = []
    for key, r in sorted(picked.items()):
        kind, _, qid = key.partition('.')
        sec = {'dim': 'dimensions', 'asp': 'aspects', 'pq': 'project'}[kind]
        out.setdefault(sec, {})
        cur = out[sec].get(qid)
        strong = r['corrections'] > 0 or r['support'] >= 3
        if cur and cur.get('basis') == 'said':
            if not r['no_preselect'] and norm(cur.get('value')) != norm(r['value']):
                lines.append(f'{key}: 대화에서 직접 말한 값 유지 (규칙 {r["id"]} 은 {r["value"]!r})')
            continue
        if cur and not (strong and (r['no_preselect'] or norm(cur.get('value')) != norm(r['value']))):
            continue
        if r['no_preselect']:
            if cur:
                del out[sec][qid]
                lines.append(f'{key}: 짐작한 값을 뺌 — {r["reason"]}')
            continue
        out[sec][qid] = {'value': r['value'], 'reason': '지난 기록: ' + r['reason'], 'basis': 'rule:' + r['id']}
        lines.append(f"{key}: {'짐작한 값 대신 ' if cur else ''}{r['value']!r} — {r['reason']}")
    return out, lines


# ---------- 기록하기 ----------
def context_signals(cx):
    """제출 때 인터뷰 페이지가 보낸 작업 여건 → ctx: 신호. 같은 상황인데 다르게 고른 까닭이 여건(기기·시간·여는 방식) 차이인지 가려내는 단서."""
    out = set()
    if not isinstance(cx, dict):
        return out
    if cx.get('device') in ('휴대폰', '넓은화면'):
        out.add('ctx:기기=' + cx['device'])
    h = cx.get('local_hour')
    if isinstance(h, int) and 0 <= h <= 23:
        out.add('ctx:시간대=' + ('새벽' if h < 6 else '오전' if h < 12 else '오후' if h < 18 else '저녁'))
    wd = cx.get('weekday')
    if isinstance(wd, int) and 0 <= wd <= 6:
        out.add('ctx:요일=' + ('주말' if wd in (0, 6) else '주중'))
    if cx.get('client') in ('artifact', 'file'):
        out.add('ctx:열기=' + ('게시페이지' if cx['client'] == 'artifact' else '파일'))
    return out


def events_from_answers(p, project, B):
    """답변 JSON(payload) → 기록. 추천한 칸은 결과(그대로·바꿈·지움), 추천 없이 답한 칸은 answered."""
    if not isinstance(p, dict) or p.get('mode') not in (None, 'interview'):
        raise ValueError('인터뷰 답변 JSON 이 아닙니다')
    if p.get('stage') == 'references':
        raise ValueError('「레퍼런스만 먼저 보내기」 중간 답은 기록하지 않습니다(마지막 제출을 기록)')
    project = project or p.get('lecture') or ''
    run = f"{project}@{p.get('submitted_at') or ''}"
    date = (p.get('submitted_at') or datetime.date.today().isoformat())[:10]
    rec = p.get('recommend') or {}
    sig = set(rec.get('signals') or [])
    for qid, v in (p.get('dimensions') or {}).items():
        if re.search(r'_(other|primary)$', qid):
            continue
        for x in (v if isinstance(v, list) else [v]):
            if x is not None and x != '' and not isinstance(x, (dict, list)):
                sig.add(f'dim.{qid}={x}')
    sig |= context_signals(p.get('context'))
    sig = sorted(s for s in sig if SIG_RE.match(s))
    ev, done = [], set()
    base = {'run': run, 'date': date, 'project': project, 'kind': 'interview', 'signals': sig, 'weight': ANSWER_WEIGHT}
    for it in rec.get('items') or []:
        key, o = it.get('key'), it.get('outcome')
        if not KEY_RE.match(key or '') or o not in ('kept', 'changed', 'cleared'):
            done.add(key); continue  # hidden(조건이 바뀌어 숨음)은 배우지 않는다
        if not learnable(item_of(key, B)):
            done.add(key); continue
        ev.append(dict(base, key=key, recommended=it.get('recommended'), final=None if o == 'cleared' else it.get('final'), outcome=o, basis=it.get('basis')))
        done.add(key)
    for sec, kind in SECTIONS:
        for qid, v in (p.get(sec) or {}).items():
            key = f'{kind}.{qid}'
            if key in done or not KEY_RE.match(key) or not learnable(item_of(key, B)):
                continue
            if kind == 'asp':
                if not isinstance(v, dict) or not v.get('choice'):
                    continue
                if v['choice'] == 'ref' and v.get('value') is None:
                    continue  # 레퍼런스로 정할 칸 — 값이 아직 없다
                fv = None if v['choice'] == 'skip' else v.get('value')
            else:
                fv = v
            if kind != 'asp' and norm(fv) == NONE:
                continue
            ev.append(dict(base, key=key, recommended=None, final=fv, outcome='answered'))
    return ev


def cmd_record(argv):
    if not argv:
        print(__doc__); return 2
    project = None
    if '--project' in argv:
        i = argv.index('--project'); project = argv[i + 1]; argv = argv[:i] + argv[i + 2:]
    if not ST.STORE_WRITABLE:
        print('데이터 폴더가 없습니다(starter 를 쓰는 중). init_store.py 로 먼저 만드세요.'); return 1
    p = load_json(argv[0])
    try:
        ev = events_from_answers(p, project, bank())
    except ValueError as e:
        print(e); return 1
    log = read_log()
    run = ev[0]['run'] if ev else None
    if run and any(e.get('run') == run for e in log['events']):
        print(f'이미 기록한 제출입니다: {run} — 다시 기록하지 않습니다(이중 기록 방지).'); return 0
    log['events'].extend(ev)
    write_log(log)
    r = relearn()
    c = collections.Counter(e['outcome'] for e in ev)
    s = next((x for x in r['stats']['runs'] if x['run'] == run), None)
    print(f"기록 {len(ev)}건: 추천 그대로 {c['kept']} · 바꿈 {c['changed']} · 지움 {c['cleared']} · 추천 없이 답함 {c['answered']}"
          + (f" · 이번 적중률 {s['hit_rate']:.0%}" if s and s['hit_rate'] is not None else ''))
    print(f"규칙 {len(r['rules'])}개 · 갈린 칸 {len(r['shaky'])}개(단서 {sum(1 for x in r['shaky'] if x.get('kind') == 'condition')} · 그때그때 {sum(1 for x in r['shaky'] if x.get('kind') == 'mood')}) · 전체 적중률 {fmt_rate(r['stats']['hit_rate'])}")
    return 0


def cmd_correct(argv):
    opt = {}
    i = 0
    while i < len(argv):
        if argv[i] in ('--project', '--key', '--value', '--said', '--signals', '--date') and i + 1 < len(argv):
            opt[argv[i][2:]] = argv[i + 1]; i += 2
        else:
            print(f'모르는 인자 {argv[i]}'); return 2
    for k in ('project', 'key', 'value', 'said'):
        if not opt.get(k):
            print(f'--{k} 가 필요합니다(--said 는 사용자 원문 — 무엇을 왜 고쳤는지 남긴다).'); return 2
    if not KEY_RE.match(opt['key']):
        print('키 형식: dim.<질문> · asp.<취향 질문> · pq.<3부 질문>'); return 2
    if not ST.STORE_WRITABLE:
        print('데이터 폴더가 없습니다(starter 를 쓰는 중).'); return 1
    try:
        val = json.loads(opt['value'])
    except ValueError:
        val = opt['value']  # 따옴표 없이 쓴 한 낱말 값
    B = bank()
    val, prob = check_value(opt['key'], val, B)
    if prob:
        print(prob); return 1
    log = read_log()
    prev = [e for e in log['events'] if e.get('project') == opt['project']]
    if opt.get('signals'):
        sig = [s.strip() for s in opt['signals'].split(',') if s.strip()]
        bad = [s for s in sig if not SIG_RE.match(s)]
        if bad:
            print(f'신호 형식이 틀림: {bad}'); return 2
    else:
        runs = [e for e in prev if e.get('kind') == 'interview']
        sig = runs[-1]['signals'] if runs else []
        if not runs:
            print('알림: 이 프로젝트의 인터뷰 기록이 없어 신호 없이(모든 상황) 기록합니다. --signals 로 상황을 주면 더 좁게 배웁니다.')
    before = next((e.get('final') for e in reversed(prev) if e.get('key') == opt['key']), None)
    log['events'].append({'run': f"{opt['project']}@correct", 'date': opt.get('date') or datetime.date.today().isoformat(), 'project': opt['project'],
                          'kind': 'correction', 'signals': sorted(set(sig)), 'weight': CORRECTION_WEIGHT, 'key': opt['key'],
                          'recommended': before, 'final': val, 'outcome': 'corrected', 'said': opt['said']})
    write_log(log)
    r = relearn()
    hit = [x for x in r['rules'] if x['key'] == opt['key'] and set(x['when']) <= set(sig)]
    print(f"수정 요청 기록(가중치 {CORRECTION_WEIGHT:g}): {opt['key']} = {val!r}" + (f" (전에는 {before!r})" if before is not None else ''))
    for x in sorted(hit, key=lambda x: -len(x['when']))[:3]:
        print('  규칙 ' + x['id'] + ': ' + x['reason'])
    return 0


def fmt_rate(x):
    return '기록 없음' if x is None else f'{x:.0%}'


def cmd_stats():
    r = load_json(rules_path()) if rules_path().exists() else relearn() if ST.STORE_WRITABLE else learn([])
    s = r['stats']
    print(f"기록 {s['events']}건 · 인터뷰 {s['interviews']}번 · 추천 {s['recommended']}칸 중 그대로 {s['kept']} → 적중률 {fmt_rate(s['hit_rate'])} · 수정 요청 {s['corrections']}건")
    for x in s['runs']:
        print(f"  {x['date']} {x['project']}: 추천 {x['recommended']} · 그대로 {x['kept']} · 바꿈 {x['changed']} · 지움 {x['cleared']} → {fmt_rate(x['hit_rate'])}")
    print(f"규칙 {len(r['rules'])}개")
    for x in r['rules'][:30]:
        print('  ' + x['id'] + ' ' + x['reason'])
    print(f"갈린 칸 {len(r['shaky'])}개 — 작업 여건·상황 단서로 풂 {sum(1 for x in r['shaky'] if x.get('kind') == 'condition')} · 그때그때 취향 {sum(1 for x in r['shaky'] if x.get('kind') == 'mood')}")
    for x in r['shaky'][:20]:
        print('  ' + x['note'])
    for h in (r.get('history') or [])[-5:]:
        print(f"바뀐 판단 {h['date']} (기록 {h['events']}건): " + ' / '.join(h['changes'][:6]))
    return 0


def cmd_suggest(argv):
    src = write = None
    signals = []
    i = 0
    while i < len(argv):
        if argv[i] == '--from' and i + 1 < len(argv):
            src = argv[i + 1]; i += 2
        elif argv[i] == '--signals' and i + 1 < len(argv):
            signals = [s.strip() for s in argv[i + 1].split(',') if s.strip()]; i += 2
        elif argv[i] == '--write':
            write = True; i += 1
        else:
            print(f'모르는 인자 {argv[i]}'); return 2
    rules = (load_json(rules_path()) if rules_path().exists() else learn(read_log()['events']))['rules']
    B = bank()
    if src:
        reco, notes = clean_reco(load_json(src), B)
        for n in notes:
            print('알림: ' + n)
        sig = reco_signals(reco) | set(signals)
    else:
        reco, sig = None, set(signals)
    picked = suggest(sig, rules)
    picked = {k: r for k, r in picked.items() if item_of(k, B) and (r['no_preselect'] or not check_value(k, r['value'], B)[1])}
    if reco is None:
        print(json.dumps({k: {'value': r['value'], 'no_preselect': r['no_preselect'], 'reason': r['reason'], 'rule': r['id']} for k, r in sorted(picked.items())}, ensure_ascii=False, indent=1))
        return 0
    merged, lines = merge(reco, picked)
    for ln in lines:
        print(ln)
    if not lines:
        print('규칙으로 더하거나 바꾼 칸 없음(기록이 쌓이면 늘어납니다).')
    if write:
        pathlib.Path(src).write_bytes((json.dumps(merged, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
        n = sum(len(merged.get(sec) or {}) for sec, _ in SECTIONS)
        print(f'썼습니다: {src} (추천 {n}칸)')
    return 0


def cmd_check(argv):
    if not argv:
        print(__doc__); return 2
    reco, notes = clean_reco(load_json(argv[0]))
    for n in notes:
        print('알림: ' + n)
    n = {sec: len(reco.get(sec) or {}) for sec, _ in SECTIONS}
    print(f"추천: 1부 {n['dimensions']} · 취향 {n['aspects']} · 3부 {n['project']} · 신호 {len(reco['signals'])}")
    return 1 if notes else 0


def validate(know=None):
    """check_store.py 용: (오류 목록, 알림 목록)"""
    errs, info = [], []
    p = log_path(know)
    if not p.exists():
        info.append('recommend_log.json 없음 — 첫 기록 때 만든다')
        return errs, info
    try:
        d = load_json(p)
    except ValueError as e:
        return [f'recommend_log.json: JSON 오류 {e}'], info
    seen = set()
    for i, e in enumerate(d.get('events') or []):
        w = f'recommend_log.json events[{i}]'
        if not KEY_RE.match(str(e.get('key') or '')):
            errs.append(f'{w}: 키 형식 {e.get("key")!r}')
        if e.get('kind') not in ('interview', 'correction'):
            errs.append(f'{w}: kind {e.get("kind")!r}')
        if e.get('outcome') not in OUTCOMES:
            errs.append(f'{w}: outcome {e.get("outcome")!r}')
        if not isinstance(e.get('weight'), (int, float)) or e['weight'] <= 0:
            errs.append(f'{w}: weight')
        if e.get('kind') == 'correction' and not e.get('said'):
            errs.append(f'{w}: 수정 요청에 사용자 원문(said) 없음')
        bad = [s for s in e.get('signals') or [] if not SIG_RE.match(str(s))]
        if bad:
            errs.append(f'{w}: 신호 형식 {bad}')
        k = (e.get('run'), e.get('key'), e.get('kind'), e.get('said'))
        if e.get('kind') == 'interview' and k in seen:
            errs.append(f'{w}: 같은 제출·같은 칸이 두 번 기록됨 ({e.get("run")} {e.get("key")})')
        seen.add(k)
    n = len(d.get('events') or [])
    rp = rules_path(know)
    if n and not rp.exists():
        errs.append('recommend_rules.json 없음 — recommend.py learn')
    elif rp.exists():
        try:
            r = load_json(rp)
            if (r.get('stats') or {}).get('events') != n:
                errs.append(f'recommend_rules.json 이 기록({n}건)보다 옛것 — recommend.py learn')
            else:
                info.append(f"대화 추천: 기록 {n}건 · 규칙 {len(r.get('rules') or [])} · 갈린 칸 {len(r.get('shaky') or [])} · 적중률 {fmt_rate((r.get('stats') or {}).get('hit_rate'))}")
        except ValueError as e:
            errs.append(f'recommend_rules.json: JSON 오류 {e}')
    return errs, info


# ---------- 자체 시험 ----------
def cmd_selftest():
    fails = []

    def ok(c, m):
        print(('OK   ' if c else 'FAIL ') + m)
        if not c:
            fails.append(m)
    tmp = pathlib.Path(tempfile.mkdtemp())
    S = ['dim.material_type=slides', 'tag:강의']
    TH = 'asp.P2.4.theme'

    def mk(proj, day, sig, final, key=TH, outcome='answered', kind='interview', w=1.0, rec=None, said=None):
        e = {'run': f'{proj}@{day}', 'date': f'2026-01-{day:02d}', 'project': proj, 'kind': kind, 'signals': sig, 'weight': w,
             'key': key, 'recommended': rec, 'final': final, 'outcome': outcome}
        if said:
            e['said'] = said
        return e

    def rules_for(r, key=TH):
        return [x for x in r['rules'] if x['key'] == key]
    # 1) 두 번 같은 답 → 보통 규칙
    ev = [mk('A', 1, S, 'dark'), mk('B', 2, S, 'dark')]
    r = learn(ev)
    ok(any(x['kind'] == 'plain' and x['value'] == 'dark' and x['when'] == [] for x in rules_for(r)), '두 번 같은 답 → 규칙')
    # 2) 확실한 단서: 야외가 아닐 때 dark 3번, 야외일 때 light 3번 → 우연일 확률 5% → 단서 규칙 둘
    ev = [mk(c, i, S, 'dark') for i, c in enumerate('ABC', 1)] + [mk(c, i, S + ['tag:야외'], 'light', rec='dark', outcome='changed') for i, c in enumerate('DEF', 4)]
    r = learn(ev)
    sh = next((x for x in r['shaky'] if x['key'] == TH), {})
    ok(sh.get('kind') == 'condition' and sh.get('clue') == 'tag:야외' and abs(sh.get('p', 1) - 0.05) < 1e-9, f"같은 상황 다른 답 → 작업 여건 차이로 판단(단서 tag:야외, 우연 {sh.get('p')})")
    sp = {tuple(x['when']): x['value'] for x in rules_for(r) if x['kind'] == 'split'}
    ok(sp.get(('tag:야외',)) == 'light' and sp.get(('!tag:야외',)) == 'dark', '단서 규칙 둘: 야외 → light · 야외 아님 → dark')
    ok(suggest(set(S) | {'tag:야외'}, r['rules']).get(TH, {}).get('value') == 'light' and suggest(set(S), r['rules']).get(TH, {}).get('value') == 'dark', '추천: 야외면 light, 아니면 dark')
    # 3) 애매: 2번 대 2번 완전 갈림(우연 17%) → 단서로 보지 않고 그때그때 취향 — 아직 반반이라 미리 고르지 않음
    ev = [mk('A', 1, S, 'dark'), mk('B', 2, S, 'dark'), mk('C', 3, S + ['tag:야외'], 'light'), mk('D', 4, S + ['tag:야외'], 'light')]
    r = learn(ev)
    sh = next((x for x in r['shaky'] if x['key'] == TH), {})
    ok(sh.get('kind') == 'mood' and not rules_for(r) and not suggest(set(S) | {'tag:야외'}, r['rules']).get(TH), f"기록 4건은 우연일 수 있음 → 그때그때 취향, 미리 고르지 않음 (기울 확률 {sh.get('lean_prob')})")
    # 4) 그때그때 취향이 쌓이면 기우는 쪽을 고른다: 같은 여건에서 dark 6 · light 3 (단서 없음)
    ev = [mk('M', i, S, v) for i, v in enumerate(['dark', 'light', 'dark', 'dark', 'light', 'dark', 'dark', 'light', 'dark'], 1)]
    r = learn(ev)
    mo = [x for x in rules_for(r) if x['kind'] == 'mood']
    sh = next((x for x in r['shaky'] if x['key'] == TH), {})
    ok(bool(mo) and mo[0]['value'] == 'dark' and mo[0]['lean_prob'] >= LEAN_PROB and suggest(set(S), r['rules']).get(TH, {}).get('value') == 'dark',
       f"기록 9건(dark 6 · light 3) → dark 쪽으로 기울 확률 {sh.get('lean_prob')} → 미리 고름")
    r_half = learn(ev[:5])
    sh5 = next((x for x in r_half['shaky'] if x['key'] == TH), {})
    ok(sh5.get('kind') == 'mood' and sh5.get('lean_prob', 1) < LEAN_PROB and not rules_for(r_half), f"기록 5건(dark 3 · light 2) → 기울 확률 {sh5.get('lean_prob')} — 기준({LEAN_PROB}) 미만이라 미리 고르지 않고 쌓기만")
    ok(abs(_lean_prob(0, 0) - 0.5) < 1e-6 and abs(_lean_prob(1, 0) - 0.75) < 1e-6, '기울 확률 계산(반반 50% · 1번 대 0번 75%)')
    # 5) 늘 같이 움직이는 단서 둘 → 규칙은 만들되 「같이 움직이는 단서」로 적는다(어느 것이 까닭인지 모름)
    ev = [mk(c, i, S, 'dark') for i, c in enumerate('ABC', 1)] + [mk(c, i, S + ['tag:야외', 'tag:행사'], 'light') for i, c in enumerate('DEF', 4)]
    sh = next((x for x in learn(ev)['shaky'] if x['key'] == TH), {})
    ok(sh.get('clue') == 'tag:야외' and sh.get('together') == ['tag:행사'], '늘 같이 움직이는 단서(tag:행사)를 함께 적음')
    # 6) 작업 여건(ctx:): 휴대폰이면 light, 넓은 화면이면 dark → 여건 규칙은 페이지가 열릴 때 판정(ctx_rules)
    ev = [mk(c, i, S + ['ctx:기기=넓은화면'], 'dark') for i, c in enumerate('ABC', 1)] + [mk(c, i, S + ['ctx:기기=휴대폰'], 'light') for i, c in enumerate('DEF', 4)]
    r = learn(ev)
    cr = ctx_rules(S, r['rules'])
    ok(not suggest(set(S), r['rules']).get(TH) and {(tuple(x['when']), x['value']) for x in cr if x['key'] == TH} >= {(('ctx:기기=넓은화면',), 'dark'), (('!ctx:기기=넓은화면',), 'light')},
       '작업 여건 단서 → suggest 는 쓰지 않고 페이지로 보낼 여건 규칙(ctx_rules)으로')
    ok(context_signals({'device': '휴대폰', 'local_hour': 23, 'weekday': 6, 'client': 'artifact'}) == {'ctx:기기=휴대폰', 'ctx:시간대=저녁', 'ctx:요일=주말', 'ctx:열기=게시페이지'}
       and context_signals({'device': 'x', 'local_hour': 99}) == set(), '제출 때 작업 여건 → ctx 신호(틀린 값은 버림)')
    # 7) 수정 요청 한 번(가중치 5)이 보통 기록 두 번을 이긴다
    ev2 = [mk('A', 1, S, 'dark'), mk('B', 2, S, 'dark'), mk('E', 5, S, 'light', kind='correction', outcome='corrected', w=CORRECTION_WEIGHT, rec='dark', said='밝게 바꿔')]
    top = [x for x in rules_for(learn(ev2)) if x['when'] == []]
    ok(bool(top) and top[0]['value'] == 'light' and top[0]['corrections'] == 1, '수정 요청 한 번이 보통 기록 두 번을 이김')
    ev2b = [mk('A', 1, S, 'dark'), mk('E', 2, S, 'light', kind='correction', outcome='corrected', w=CORRECTION_WEIGHT, said='밝게')]
    ok(suggest(set(S), learn(ev2b)['rules']).get(TH, {}).get('value') == 'light', '기록 2건이라도 수정 요청이 든 쪽은 바로 보정')
    # 8) 지움 → 미리 고르지 않음
    ev3 = [mk(c, i, S, None, key='pq.delivery', outcome='cleared', rec='file') for i, c in enumerate('XY', 1)]
    ok(any(x['key'] == 'pq.delivery' and x['no_preselect'] for x in learn(ev3)['rules']), '두 번 지움 → 미리 고르지 않음 규칙')
    st = learn([mk('A', 1, S, 'dark', outcome='kept', rec='dark'), mk('A', 1, S, 'x', key='asp.P1.1.energy', outcome='changed', rec='calm')])['stats']
    ok(st['recommended'] == 2 and st['kept'] == 1 and st['hit_rate'] == 0.5, f"적중률 계산 {st['hit_rate']}")
    # 9) merge: said 는 지키고 inferred 는 강한 규칙이 이긴다
    rule = {'id': 'R-x', 'kind': 'plain', 'when': [], 'key': TH, 'value': 'light', 'no_preselect': False, 'confidence': 1, 'support': 5, 'corrections': 1, 'reason': 'r'}
    m, _ = merge({'aspects': {'P2.4.theme': {'value': 'dark', 'basis': 'said'}}}, {TH: rule})
    ok(m['aspects']['P2.4.theme']['value'] == 'dark', '사용자가 직접 말한 값은 규칙이 바꾸지 않음')
    m, _ = merge({'aspects': {'P2.4.theme': {'value': 'dark', 'basis': 'inferred'}}}, {TH: rule})
    ok(m['aspects']['P2.4.theme']['value'] == 'light', '짐작한 값은 강한 규칙이 이김')
    # 10) 쓰기·다시 배우기(바뀐 판단을 history 에) · 검사
    ev = [mk('A', 1, S, 'dark'), mk('B', 2, S, 'dark'), mk('C', 3, S + ['tag:야외'], 'light'), mk('D', 4, S + ['tag:야외'], 'light')]
    write_log({'version': 1, 'events': ev}, tmp)
    relearn(tmp)
    d = read_log(tmp); d['events'] += [mk('E', 5, S, 'dark'), mk('F', 6, S + ['tag:야외'], 'light')]; write_log(d, tmp)
    r = relearn(tmp)
    ch = ' | '.join(c for h in r['history'] for c in h['changes'])
    ok('그때그때 → 단서' in ch and '생김: 단서 규칙' in ch, '기록이 쌓여 그때그때 → 확실한 단서로 바뀐 것을 history 에 남김')
    e, _ = validate(tmp)
    ok(not e, '기록·규칙 검사 통과')
    d = read_log(tmp); d['events'].append(dict(ev[0])); write_log(d, tmp)
    e, _ = validate(tmp)
    ok(any('두 번' in x for x in e) and any('옛것' in x for x in e), '같은 제출 두 번 · 옛 규칙 파일을 잡음(반대 시험)')
    print('실패 ' + str(len(fails)) if fails else '자체 시험 통과')
    return 1 if fails else 0


def main(argv):
    if not argv:
        print(__doc__); return 2
    cmd, rest = argv[0], argv[1:]
    if cmd == 'record':
        return cmd_record(rest)
    if cmd == 'correct':
        return cmd_correct(rest)
    if cmd == 'suggest':
        return cmd_suggest(rest)
    if cmd == 'check':
        return cmd_check(rest)
    if cmd == 'learn':
        if not ST.STORE_WRITABLE:
            print('데이터 폴더가 없습니다(starter 를 쓰는 중).'); return 1
        r = relearn()
        print(f"규칙 {len(r['rules'])}개 · 갈린 칸 {len(r['shaky'])}개 · 적중률 {fmt_rate(r['stats']['hit_rate'])} → {rules_path()}")
        return 0
    if cmd == 'stats':
        return cmd_stats()
    if cmd == 'selftest':
        return cmd_selftest()
    print(__doc__); return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
