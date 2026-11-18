#!/usr/bin/env python3
"""대화 추천 — 기록하고 스스로 진화한다 (엔진 1.4.0, 사용자 결정 2026-11-09 · 1.6.0 첨부자료 먼저 · 더 물을 것 되돌기 2026-11-16).

흐름
  0. 미리 받은 첨부자료(파일 · 폴더 · 주소)를 먼저 끝까지 읽고, 거기서 알 수 있는 칸은 basis "attached"(+ 근거 from)로 채운다(1.6.0).
  1. Claude가 인터뷰 페이지를 만들기 전에 대화로 「무엇을 · 누구에게 · 왜 · 어떻게」를 알아본다.
     대화 요약은 <작업폴더>/materials/인터뷰/00_대화요약.md, 추천은 00_추천.json 에 쓴다(형식은 아래).
     `recommend.py gaps 00_추천.json` 이 아직 빈 칸 · 짐작만 한 칸을 보여 준다 — 물을 것이 없을 때까지 묻고 다시 본다(1.6.0, 「rounds」 에 회차 기록).
  2. `recommend.py suggest --from 00_추천.json --write` — 지난 기록에서 배운 규칙으로 대화가 정하지 않은 칸을 채운다.
     (대화에서 사용자가 직접 말한 것 basis "said" 와 첨부자료에 적힌 것 "attached" 는 규칙이 바꾸지 않는다. Claude가 짐작한 것 "inferred" 는
     수정 요청이 섞인 강한 규칙이 다르면 규칙이 이긴다.)
  3. `build_interview.py … --recommend 00_추천.json` — 인터뷰가 추천 답이 골라진 채로 열린다(「대화 추천」 표시 · 이유 · 요약판).
  4. 사용자가 제출하면 `recommend.py record <답변.json>` — 추천과 최종 답의 차이(그대로 · 바꿈 · 지움)와
     추천 없이 답한 것까지 상황 신호와 함께 기록하고 규칙을 다시 배운다. 첨부자료에 적힌 칸(basis attached)은 그 프로젝트의 사실이라 배우지 않는다.
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
   "attachments": [{"path": "<파일 · 폴더 · 주소>", "read": "all|part", "found": "<알게 된 것 한 줄>"}],   (1.6.0, 없으면 [])
   "rounds": [{"n": 1, "asked": ["dim.length", "pq.topic"], "answered": ["dim.length"]}],                 (1.6.0 묻기 회차)
   "listening": true,                                                                                       (1.7.0 듣기 모드 — listen 이 열고 닫는다)
   "dimensions": {"<질문>": {"value": 값, "reason": "<한 줄 근거>", "basis": "said|attached|inferred|rule:<id>", "from": "<attached 일 때 근거 파일:쪽>"}},
   "aspects":    {"<취향 질문>": {…같은 꼴}},
   "project":    {"<3부 질문>": {…같은 꼴}}}

사용법
  python3 recommend.py listen <00_추천.json> [--said "<원문>" | --said=<원문> | --said-file <UTF-8 파일> | --said -] [--done]
                                                                사전 인터뷰 듣기 모드(1.7.0, 기본): 사용자가 「됐어」라고 할 때까지 답 · 질문 · 요약 없이 듣기만 한다.
                                                                --said 는 말씀을 같은 폴더 00_대화요약.md 끝에 글자 그대로 덧붙이고 listening 을 연다(파일이 없으면 만든다).
                                                                화면에는 한 줄만: 「(듣는 중 — 「됐어」라고 하시면 정리해 드립니다)」. --done 은 듣기를 닫는다.
                                                                듣는 동안 gaps · check · suggest 는 종료 3(gaps --json 은 {"listening": true, "gaps": []}), check_ready.py 는 제작을 막는다.
                                                                --said - 는 표준 입력을 UTF-8 로 읽는다(Windows PowerShell 5.1 의 파이프는 한글을 ? 로 바꾼다 — 거기서는 --said-file).
  python3 recommend.py check <00_추천.json>                     질문 은행과 맞는지 검사(없는 질문·선택지를 알린다)
  python3 recommend.py gaps <00_추천.json> [--all] [--json]     더 물을 것: 핵심 칸(CORE) 가운데 빈 칸 · 짐작만 한 칸(1.6.0, --all 은 보이는 모든 1부 · 3부 칸,
                                                                --json 도 같은 범위 · 알림은 stderr)
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
BASES = ('said', 'attached', 'inferred')   # attached: 첨부자료에 적혀 있음(1.6.0) — from 에 근거 파일 · 쪽
PROTECTED = ('said', 'attached')           # 규칙이 바꾸지 않는 근거
# 대화에서 먼저 물을 핵심 칸(스킬 3.0의 1 — 무엇을 · 누구에게 · 왜 · 어디서 보나 · 길이 · 마감 · 원자료 · 꼭 넣을 것 · 뺄 것 · 주제 · 얻어 갈 것).
# 나머지 칸은 지난 기록 · 기본값으로 미리 고르고 인터뷰 페이지에서 확인한다(다 물으면 30개가 넘는다)
CORE = ('dim.file_format', 'dim.material_type', 'dim.purpose', 'dim.audience_age', 'dim.venue', 'dim.length', 'dim.deadline',
        'dim.sources', 'dim.must_include', 'dim.must_not', 'pq.topic', 'pq.goals')
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


def bank_docs():
    """(dimensions 문서, questions 문서) — 이관·반영 대기 편집을 적용한 지금 모습. 목차(screens)도 같은 적용본이다(R02)."""
    import upgrade_store as UP
    import structure_edits as SE
    dims, _ = UP.migrate_dims(load_json(ST.path('dimensions.json')))
    qs, _ = UP.migrate_qs(load_json(ST.path('questions.json')))
    try:
        dims, qs, _n, _p = SE.with_pending(dims, qs)
    except Exception:  # noqa: BLE001  편집 기록이 없거나 깨져도 추천은 원본 은행으로
        pass
    return dims, qs


def bank():
    """(1부 질문 {id: d}, 취향 질문 {id: a}, 3부 질문 {id: q}) — 이관·반영 대기 편집을 적용한 지금 모습."""
    dims, qs = bank_docs()
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
    if isinstance(reco.get('listening'), bool):
        out['listening'] = reco['listening']
    elif 'listening' in reco and reco['listening'] is not None:
        out['listening'] = True  # bool 이 아니면(「"true"」 등) 듣는 중으로 본다 — 묻기 · 추천 덮어쓰기를 막는 쪽(R05)
        notes.append(f"listening {reco['listening']!r}: true/false 여야 함 — 듣는 중으로 봄")  # 듣기 모드(1.7.0) — 정리 · 저장해도 지우지 않는다(gaps 가 묻지 않게 · 다시 열 때 알림)
    if isinstance(reco.get('heard'), int) and not isinstance(reco.get('heard'), bool) and reco['heard'] >= 0:
        out['heard'] = reco['heard']  # 들은 말씀 개수(R03 — suggest --write 뒤에도 번호가 이어지게)
    sig = []
    for s in reco.get('signals') or []:
        if isinstance(s, str) and SIG_RE.match(s.strip()):
            sig.append(s.strip())
        else:
            notes.append(f'신호 {s!r}: 형식은 dim.<질문>=<값> 또는 tag:<낱말> — 뺌')
    out['signals'] = sig
    att = []
    atts = reco.get('attachments')
    if atts is not None and not isinstance(atts, list):
        notes.append(f'attachments {atts!r}: 목록이어야 함 — 뺌')
        atts = []
    for a in atts or []:
        if isinstance(a, dict) and str(a.get('path') or '').strip():
            att.append({'path': str(a['path']).strip(), 'read': a.get('read') if a.get('read') in ('all', 'part') else 'unknown',  # 모르면 「다 읽음」으로 적지 않는다(R02)
                        'found': str(a.get('found') or '')})
        else:
            notes.append(f'첨부자료 {a!r}: path 가 있는 객체여야 함 — 뺌')
    out['attachments'] = att
    rounds = []
    for i, r in enumerate(reco.get('rounds') or []):
        keys = {}
        for f in ('asked', 'answered'):
            raw = r.get(f) if isinstance(r, dict) else None
            if raw is None and f == 'answered':
                raw = []
            if not isinstance(raw, list) or not all(isinstance(x, str) and KEY_RE.match(x) for x in raw):
                keys = None; break
            keys[f] = list(dict.fromkeys(raw))  # 한 회차 안 같은 칸은 한 번
        if keys is None:
            notes.append(f'rounds[{i}] {r!r}: asked · answered 는 칸 키(dim.|asp.|pq.) 목록이어야 함 — 뺌'); continue
        rounds.append({'n': r.get('n', len(rounds) + 1), 'asked': keys['asked'], 'answered': keys['answered']})
    out['rounds'] = rounds

    def basis_of(where, s):
        """(근거, from) — attached 는 공백 아닌 문자열 from 이 있어야 한다(없거나 문자열이 아니면 짐작으로 내림)."""
        basis = str(s.get('basis') or 'inferred')
        if basis not in BASES and not basis.startswith('rule:'):
            notes.append(f'{where}: basis {basis!r} → inferred'); basis = 'inferred'
        src = s.get('from')
        if basis == 'attached' and not (isinstance(src, str) and src.strip()):
            notes.append(f'{where}: basis attached 인데 근거(from: 파일 · 쪽 글)가 없거나 글이 아님 → inferred'); basis = 'inferred'
        return basis, (src.strip() if basis == 'attached' else None)
    for sec, kind in SECTIONS:
        out[sec] = {}
        if not isinstance(reco.get(sec) or {}, dict):
            notes.append(f'{sec}: 객체여야 함 — 뺌'); continue
        for qid, s in (reco.get(sec) or {}).items():
            if not isinstance(s, dict) or 'value' not in s:
                s = {'value': s}
            base = re.sub(r'_(other|primary)$', '', qid) if kind == 'dim' else qid
            if kind == 'dim' and base != qid:  # 기타 내용 · 주 대상은 값 검사 없이(주 대상은 고른 값 중 하나여야 한다)
                if not item_of('dim.' + base, B):
                    notes.append(f'dim.{qid}: 질문 은행에 없는 질문 — 뺌'); continue
                if norm(s.get('value')) == NONE:
                    notes.append(f'dim.{qid}: 값 없음 — 뺌'); continue
                basis, src = basis_of(f'dim.{qid}', s)
                out[sec][qid] = {'value': s.get('value'), 'reason': str(s.get('reason') or ''), 'basis': basis}
                if src:
                    out[sec][qid]['from'] = src
                continue
            v, prob = check_value(f'{kind}.{qid}', s.get('value'), B)
            if prob:
                notes.append(prob + ' — 뺌'); continue
            basis, src = basis_of(f'{kind}.{qid}', s)
            # 빈 목록 · 빈 글은 빈 칸(gaps 가 다시 묻게). 단 사용자가 직접 「없음」이라고 답한 것(said)은 답이다 — 남겨 규칙이 덮지 않게(R02)
            if v is None or ((norm(v) == NONE or (isinstance(v, str) and not v.strip())) and basis != 'said'):
                notes.append(f'{kind}.{qid}: 값 없음 — 뺌'); continue
            out[sec][qid] = {'value': v, 'reason': str(s.get('reason') or ''), 'basis': basis}
            if src:
                out[sec][qid]['from'] = src
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
    use = [e for e in events if e.get('outcome') in OUTCOMES and KEY_RE.match(e.get('key') or '')
           and e.get('basis') != 'attached']  # 첨부자료 칸은 프로젝트 사실 — 옛 기록에 있어도 배우지 않는다(R02)
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


def _adopted(r, cur):
    """merge() 가 이 규칙을 그 칸에 실제로 쓰는가(cur = 추천 파일의 지금 칸 또는 None). merge 와 같은 조건."""
    if not cur:
        return True
    if cur.get('basis') in PROTECTED:
        return False
    return r['corrections'] > 0 or r['support'] >= 3


def suggest(signals, rules, current=None):
    """신호 → {키: 규칙}. 확실한 단서 규칙 > 보통 규칙 > 그때그때 취향의 기울기, 같으면 구체적인(조건이 많은) 것 · 몫이 큰 것.
    작업 여건(ctx:) 조건이 든 규칙은 여기서 쓰지 않는다 — 인터뷰 페이지가 열릴 때 그 자리의 여건으로 판정한다(ctx_rules).
    추천한 1부 값은 신호에 더해 다시 본다. current(추천 파일의 지금 칸 {키: 칸})가 있으면 merge 가 실제로 쓸 규칙 값만 더하고,
    그 규칙이 바꿀 지금 값의 신호는 뺀다 — 보호된 답(said · attached)이나 약한 규칙이 못 바꾸는 짐작과 어긋난 값이
    다른 규칙을 부르지 않게(R03 · R04)."""
    current = current or {}
    base = set(signals)
    sig = set(base)
    picked = {}
    seen = set()
    # 수렴할 때까지 본다(R05: 3회로 끊으면 중간 추천이 철회된 것이 끝까지 전파되지 않아 전제 없는 파생 추천만 남았다).
    # 같은 신호가 다시 나오면(순환) 거기서 멈춘다 — 그때 picked 는 지금 sig 에서 조건이 맞는 규칙만이다.
    for _ in range(len(rules) + 3):
        seen.add(frozenset(sig))
        best = {}
        for r in rules:
            if any(w.lstrip('!').startswith('ctx:') for w in r['when']) or not _match(r['when'], sig):
                continue
            k = rule_key(r)
            if r['key'] not in best or k > best[r['key']][0]:
                best[r['key']] = (k, r)
        picked = {key: r for key, (_, r) in best.items()}
        new = set(base)
        for key, r in picked.items():
            cur = current.get(key)
            if not key.startswith('dim.') or not _adopted(r, cur):
                continue
            if cur:  # 규칙이 지금 값을 바꾸거나 뺀다 — 그 값의 신호는 더 이상 상황이 아니다
                cv = cur.get('value')
                for x in (cv if isinstance(cv, list) else [cv]):
                    new.discard(f'{key}={x}')
            if not r['no_preselect']:
                for x in (r['value'] if isinstance(r['value'], list) else [r['value']]):
                    new.add(f'{key}={x}')
        if new == sig or frozenset(new) in seen:
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
        if cur and cur.get('basis') in PROTECTED:
            if not r['no_preselect'] and norm(cur.get('value')) != norm(r['value']):
                what = '대화에서 직접 말한 값' if cur.get('basis') == 'said' else '첨부자료에 적힌 값'
                lines.append(f'{key}: {what} 유지 (규칙 {r["id"]} 은 {r["value"]!r})')
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
        if not learnable(item_of(key, B)) or it.get('basis') == 'attached':
            # 첨부자료에 적힌 값(attached)은 그 프로젝트의 사실이지 취향이 아니다 — 다른 프로젝트로 넘어갈 규칙에 넣지 않는다(1.6.0 교차 검토 R01, 「추론」)
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
        if reco is None:
            return 1
        raw = load_json(src)
        ra = raw.get('attachments') if isinstance(raw, dict) else None
        if write and ra is not None and (not isinstance(ra, list) or any(not (isinstance(a, dict) and str(a.get('path') or '').strip()) for a in ra)):
            print('멈춤: attachments 에 path 가 없는 항목이 있어 --write 로 덮어쓰지 않습니다(틀린 항목을 지우면 준비 점검표가 첨부자료를 못 봄 — R04). 고친 뒤 다시 실행합니다.')
            return 1
        if reco.get('listening'):  # 듣기 모드(1.7.0): 「됐어」 전에는 추천도 만들지 않는다
            print('듣는 중 — 사용자가 「됐어」라고 할 때까지 추천을 만들지 않습니다(recommend.py listen <00_추천.json> --done)')
            return 3
        sig = reco_signals(reco) | set(signals)
    else:
        reco, sig = None, set(signals)
    current = {f'{kind}.{qid}': s for sec, kind in SECTIONS for qid, s in ((reco or {}).get(sec) or {}).items() if isinstance(s, dict)}
    picked = suggest(sig, rules, current)
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


def gaps(reco, B=None, dims_doc=None):
    """더 물을 것(1.6.0): [(키, 이름, 상태, 핵심인가)] — 상태 empty 빈 칸 · inferred 짐작만 · asked2 두 번 물었는데 답 없음(짐작으로 두고 페이지에서 확인).
    1부 · 3부 모두 지금까지 고른 1부 값으로 보이는 질문만(숨은 하위 질문은 위 질문을 정해야 나온다), 1부는 화면 순서대로.
    물은 횟수는 rounds 의 asked 로 센다(answered 에 들었어도 근거가 짐작이면 아직 빈 것과 같다)."""
    import structure as SX
    import upgrade_store as UP
    B = B or bank()
    if dims_doc is None:
        dims_doc, _ = bank_docs()
    ans = {}
    for qid, s in (reco.get('dimensions') or {}).items():
        if not re.search(r'_(other|primary)$', qid):
            ans[qid] = s.get('value') if isinstance(s, dict) else s
    asked = collections.Counter()  # 물은 횟수 — 답이 애매해(짐작으로 남아) 「answered」 에 들었어도 센다(같은 칸은 두 번까지)
    for r in reco.get('rounds') or []:
        for k in dict.fromkeys(r.get('asked') or []):
            asked[k] += 1
    order = [d for s in dims_doc.get('screens', []) for d in s.get('dimensions', [])]
    order += [d for d in B[0] if d not in order]
    out = []

    def judge(key, cur):
        if cur and cur.get('basis') in PROTECTED:  # 확정은 사용자가 말함 · 첨부자료뿐 — 짐작 · 지난 기록 규칙은 아직 확인 전(R02)
            return None
        if asked[key] >= 2:
            return 'asked2'
        return 'inferred' if cur else 'empty'
    for did in order:
        d = B[0].get(did)
        if not d or d.get('retired') or not SX.dim_shown(d, ans, dims_doc.get('screens')):
            continue
        st = judge('dim.' + did, (reco.get('dimensions') or {}).get(did))
        if st:
            out.append(('dim.' + did, d.get('name') or did, st, 'dim.' + did in CORE))
    for qid, q in B[2].items():
        if q.get('retired') or not SX.when_ok(q, ans):  # 화면과 같이 보이는 조건(when)을 본다
            continue
        st = judge('pq.' + qid, (reco.get('project') or {}).get(qid))
        if st:
            out.append(('pq.' + qid, q.get('text') or q.get('title') or qid, st, 'pq.' + qid in CORE))
    return out


def cmd_gaps(argv):
    if not argv:
        print(__doc__); return 2
    reco, notes = clean_reco(load_json(argv[0]))
    for n in notes:  # 알림은 stderr — --json 의 stdout 은 JSON 만
        print('알림: ' + n, file=sys.stderr)
    if reco is None:
        return 1
    if reco.get('listening'):  # 사전 인터뷰 듣기 모드(1.7.0): 사용자가 「됐어」라고 하기 전에는 아무것도 묻지 않는다
        print('듣는 중 — 사용자가 「됐어」라고 할 때까지 묻지 않습니다. 끝나면 recommend.py listen <00_추천.json> --done', file=sys.stderr)
        if '--json' in argv:
            print(json.dumps({'listening': True, 'gaps': []}))  # 「물을 것 없음」([])과 구별되게
        return 3
    g = gaps(reco)
    show = g if '--all' in argv else [x for x in g if x[3]]
    if '--json' in argv:
        print(json.dumps([{'key': k, 'name': n, 'state': s, 'core': c} for k, n, s, c in show], ensure_ascii=False, indent=1))
        return 0
    label = {'empty': '빈 칸', 'inferred': '짐작 · 지난 기록만', 'asked2': '두 번 물었는데 답 없음 — 그만 묻고 페이지에서 확인'}
    for k, n, s, c in show:
        print(f"{'핵심' if c else '    '}  {label[s]:<6}  {k}  {n}")
    ask = [x for x in g if x[3] and x[2] != 'asked2']
    rest = [x for x in g if not x[3]]
    print(f"더 물을 것(핵심) {len(ask)}개"
          + (f' · 핵심 아닌 빈 칸 {len(rest)}개는 지난 기록 · 기본값으로 미리 고르고 페이지에서 확인' + ('' if '--all' in argv else '(--all 로 보기)') if rest else '')
          + (' — 핵심은 다 찼습니다. 인터뷰 페이지로 넘어갑니다.' if not ask else ''))
    return 0


LISTEN_ACK = '(듣는 중 — 「됐어」라고 하시면 정리해 드립니다)'
LISTEN_HEAD = '### 듣기 모드 말씀 '


def cmd_listen(argv):
    """사전 인터뷰 듣기 모드(1.7.0): 말씀을 글자 그대로 쌓고, 「됐어」 전에는 묻지 않게 listening 을 연다."""
    if not argv or argv[0].startswith('--'):
        print(__doc__); return 2
    path, said, done, i, anywhere = pathlib.Path(argv[0]), None, False, 1, False
    while i < len(argv):
        a = argv[i]
        if a == '--anywhere' and not anywhere:
            anywhere = True; i += 1
        elif a.startswith('--said=') and said is None:
            said = a[len('--said='):]; i += 1
        elif a == '--said' and i + 1 < len(argv) and said is None and argv[i + 1] not in ('--said', '--done', '--said-file'):
            # 「--said -」 는 표준 입력에서 읽는다(Windows PowerShell 5.1 은 인자 속 큰따옴표를 지운다)
            if argv[i + 1] == '-':
                try:
                    said = sys.stdin.buffer.read().decode('utf-8-sig')
                except (OSError, UnicodeDecodeError) as e:
                    print(f'표준 입력을 UTF-8 로 읽지 못했습니다: {e}'); return 1
            else:
                said = argv[i + 1]
            i += 2
        elif a == '--said-file' and i + 1 < len(argv) and said is None:
            try:
                said = pathlib.Path(argv[i + 1]).read_bytes().decode('utf-8-sig')
            except (OSError, UnicodeDecodeError) as e:
                print(f'말씀 파일을 읽지 못했습니다: {e}'); return 1
            i += 2
        elif a == '--done' and not done:
            done = True; i += 1
        else:
            print(__doc__); return 2
    if said is not None and not said.strip():
        print('빈 말씀은 적지 않습니다'); return 2
    if path.is_dir():
        print(f'추천 파일 자리에 폴더가 있습니다: {path}'); return 1
    if path.parts[-2:] != ('인터뷰', '00_추천.json') and not anywhere:
        # 잘못 넘긴 경로로 프로젝트 밖에 추천 파일 · 대화 요약을 만들지 않게 거절한다(R06 · R08). 정말 다른 자리면 --anywhere
        print(f'추천 파일은 <작업폴더>/materials/인터뷰/00_추천.json 자리여야 합니다(준비 점검표 검사도 그 자리만 봄) — 아무것도 쓰지 않음: {path}\n'
              '  다른 자리에 일부러 쓰려면 --anywhere 를 붙입니다'); return 2
    if path.exists():
        try:
            reco = load_json(path)
        except (ValueError, OSError) as e:
            print(f'추천 파일을 읽지 못했습니다: {path} ({e})'); return 1
        if not isinstance(reco, dict):
            print(f'추천 파일은 JSON 객체여야 합니다: {path}'); return 1
    elif said is None:
        print(f'아직 들은 말씀이 없습니다(추천 파일 없음): {path}'); return 1
    else:
        reco = {'id': path.stem, 'source': 'conversation', 'summary': 'materials/인터뷰/00_대화요약.md', 'signals': [], 'attachments': [],
                'rounds': [], 'dimensions': {}, 'aspects': {}, 'project': {}}
    if said is None and done and reco.get('pending_said'):
        print(f'적지 못한 말씀이 남아 있어 듣기를 닫지 않습니다 — 그 말씀(추천 파일의 pending_said)을 --said-file 로 다시 적으며 --done 을 붙입니다: {path}'); return 1
    if said is not None and reco.get('listening') is False:
        print('알림: 듣기를 닫은 뒤 새 말씀 — 다시 듣기 모드를 엽니다(「됐어」를 다시 받으면 --done)', file=sys.stderr)
    summ = path.parent / '00_대화요약.md'
    n = int(reco.get('heard') or 0) if isinstance(reco.get('heard'), int) else 0  # 개수는 추천 파일에 센다(말씀 속 같은 제목 글에 흔들리지 않게 — R02)
    entries = []
    if said is not None:
        # 앞서 적지 못한 말씀(pending_said)이 있으면 그것부터 원문 그대로 함께 적는다 — 새 말씀만 적고 앞 말씀을 지우지 않게(R07)
        pend = reco.get('pending_said')
        pend = [pend] if isinstance(pend, str) else [x for x in pend if isinstance(x, str)] if isinstance(pend, list) else []
        entries = [x for x in pend if x != said] + [said]
        first = n + 1
        n += len(entries)
        reco['heard'] = n
        # 말씀 속 파일 · 폴더 경로 · 주소는 받은 자료다 — 첨부자료로 적어 두어 준비 점검표가 요구하게 한다(읽기는 「됐어」 뒤 — R04)
        import check_ready as CR
        if reco.get('attachments') is None:
            reco['attachments'] = []
        if not isinstance(reco['attachments'], list):
            print(f'추천 파일의 attachments 가 목록이 아닙니다 — 고친 뒤 같은 말씀을 다시 적습니다(아무것도 쓰지 않음): {path}'); return 1
        lec = path.parent.parent.parent if path.parts[-2:] == ('인터뷰', '00_추천.json') else path.parent
        seen = {str(x.get('path')) for x in reco['attachments'] if isinstance(x, dict)}
        for p in CR.find_paths('\n'.join(entries), (lec, ST.project_root())):
            if p not in seen:
                reco['attachments'].append({'path': p, 'read': 'unknown', 'found': f'듣기 모드 말씀 {n}에서'})
                seen.add(p)
    reco['listening'] = True if said is not None else not done  # 말씀이 있으면 그것을 적은 뒤에야 닫는다(R04)
    try:
        # 추천 파일(듣는 중 표시)을 먼저 쓴다 — 말씀 붙이기가 실패해도 「듣는 중」이 남아 제작이 막힌다(R03). 이것이 실패하면 말씀도 붙이지 않는다(겹침 없음)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes((json.dumps(reco, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
    except OSError as e:
        print(f'추천 파일을 쓰지 못했습니다 — 말씀도 적지 않았습니다: {path} ({e})'); return 1
    if said is not None:
        try:
            old = summ.read_bytes() if summ.exists() else '# 대화 요약\n'.encode('utf-8')
            stamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
            # 앞 기록은 바이트 그대로 두고 새 기록만 붙인다(원문의 줄바꿈 · 끝 빈 줄을 바꾸지 않게 — R02). 원문 끝에 줄바꿈이 없을 때만 하나 붙인다
            sep = b'' if old.endswith(b'\n') else b'\n'
            add = ''.join(f'\n{LISTEN_HEAD}{first + k} · {stamp} (원문 그대로)\n\n{x}{"" if x.endswith(chr(10)) else chr(10)}' for k, x in enumerate(entries))
            summ.write_bytes(old + sep + add.encode('utf-8'))
        except OSError as e:
            # 적지 못한 말씀(앞서 못 적은 것 포함)을 추천 파일에 남기고 센 수를 되돌린다 — 그 말씀 없이 --done 으로 닫히지 않게(R06 · R07)
            reco['pending_said'] = entries
            reco['heard'] = first - 1
            try:
                path.write_bytes((json.dumps(reco, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
            except OSError:
                pass
            print(f'말씀을 대화 요약에 적지 못했습니다(듣는 중 표시는 남아 제작은 막힘 — 고친 뒤 같은 말씀을 다시 적습니다): {summ} ({e})'); return 1
        if done or 'pending_said' in reco:  # 마지막 말씀을 적은 뒤에 닫는다 · 남아 있던 적지 못한 말씀 표시는 지운다
            reco.pop('pending_said', None)
            reco['listening'] = not done
            try:
                path.write_bytes((json.dumps(reco, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
            except OSError as e:
                print(f'듣기를 닫지 못했습니다(아직 듣는 중 — 제작은 막힘): {path} ({e})'); return 1
    if done:
        print(f'듣기 끝 — 받은 말씀 {n}개({summ}). 다음(스킬 3.0): 0 받은 자료를 하나하나 다 열어 처음부터 끝까지 분석 · 정리 → 들은 말씀과 함께 한 번에 분석 → 1 · 1-1 gaps 의 빈 핵심 칸만 한 번에 묻기 '
              '→ 2~5 대화 요약 · 추천 · 인터뷰 페이지 → 6 답 기록 → 0-1 준비 완료 점검표 · 사용자 확인 → 3.1의 5 계획 → 제작')
        import check_ready as CR
        lec = path.parent.parent.parent if path.parts[-2:] == ('인터뷰', '00_추천.json') else path.parent
        for line in CR.material_plan_lines(lec, [str(a.get('path')) for a in reco.get('attachments') or [] if isinstance(a, dict) and str(a.get('path') or '').strip()]):
            print(line)
    else:
        print(LISTEN_ACK)
    return 0


def cmd_check(argv):
    if not argv:
        print(__doc__); return 2
    reco, notes = clean_reco(load_json(argv[0]))
    for n in notes:
        print('알림: ' + n)
    if reco is None:
        return 1
    n = {sec: len(reco.get(sec) or {}) for sec, _ in SECTIONS}
    print(f"추천: 1부 {n['dimensions']} · 취향 {n['aspects']} · 3부 {n['project']} · 신호 {len(reco['signals'])}")
    if reco.get('listening'):
        print('듣는 중 — 사용자가 「됐어」라고 할 때까지 이 추천으로 인터뷰를 열지 않습니다(recommend.py listen … --done)')
        return 3
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
    m, _ = merge({'aspects': {'P2.4.theme': {'value': 'dark', 'basis': 'attached', 'from': 'a.pdf:3'}}}, {TH: rule})
    ok(m['aspects']['P2.4.theme']['value'] == 'dark', '첨부자료에 적힌 값도 규칙이 바꾸지 않음(1.6.0)')
    # 9-1) 첨부자료 근거 · 더 물을 것(1.6.0) — 가짜 질문 은행으로
    FB = ({'file_format': {'id': 'file_format', 'name': '파일 형식', 'type': 'multi', 'values': [{'id': 'html'}, {'id': 'pdf'}]},
           'pdf_export': {'id': 'pdf_export', 'name': 'PDF 변환본', 'type': 'single', 'values': [{'id': 'y'}, {'id': 'n'}], 'when': {'file_format': ['html']}},
           'length': {'id': 'length', 'name': '길이', 'type': 'single', 'values': [{'id': 's'}, {'id': 'l'}]}},
          {}, {'topic': {'id': 'topic', 'text': '주제', 'type': 'text'}})
    FD = {'screens': [{'id': 'S1', 'dimensions': ['file_format', 'pdf_export', 'length']}], 'dimensions': list(FB[0].values())}
    cr, nt = clean_reco({'dimensions': {'length': {'value': 's', 'basis': 'attached'}}, 'attachments': [{'path': 'a.pdf', 'found': 'x'}]}, FB)
    ok(cr['dimensions']['length']['basis'] == 'inferred' and any('근거' in x for x in nt) and cr['attachments'][0]['read'] == 'unknown',
       'attached 인데 근거(from)가 없으면 짐작으로 내림 · 첨부자료 목록 정리')
    g = gaps({'dimensions': {'length': {'value': 's', 'basis': 'inferred'}}}, FB, FD)
    ok([k for k, _, s, _c in g] == ['dim.file_format', 'dim.length', 'pq.topic'] and dict((k, s) for k, _, s, _c in g)['dim.length'] == 'inferred'
       and [c for *_, c in g] == [True, True, True],
       f'더 물을 것: 빈 칸 · 짐작만 한 칸, 숨은 하위 질문(pdf_export)은 위 질문 전에는 안 나옴 — {g}')
    g = gaps({'dimensions': {'file_format': {'value': ['html'], 'basis': 'said'}, 'length': {'value': 's', 'basis': 'attached', 'from': 'a.pdf:1'}},
              'rounds': [{'n': 1, 'asked': ['pq.topic']}, {'n': 2, 'asked': ['pq.topic']}]}, FB, FD)
    ok([(k, s, c) for k, _, s, c in g] == [('dim.pdf_export', 'empty', False), ('pq.topic', 'asked2', True)],
       f'위 질문을 정하면 하위 질문이 나오고, 두 번 물었는데 답 없는 칸은 그만 묻는다 — {g}')
    # 9-2) 교차 검토 R01 고침: 빈 값 · 보조 칸 근거 · 글이 아닌 from · 3부 보이는 조건 · 애매한 답 횟수 · rounds 꼴 · 첨부 칸은 배우지 않음
    cr, nt = clean_reco({'dimensions': {'file_format': {'value': [], 'basis': 'attached', 'from': 'a.pdf:1'}, 'length': {'value': '', 'basis': 'inferred'}},
                         'project': {'topic': {'value': '  ', 'basis': 'inferred'}}}, FB)
    ok(not cr['dimensions'] and not cr['project'] and len(nt) == 3 and '값 없음' in nt[0] and '값 없음' in nt[2], f'빈 목록 · 빈 글 값은 빈 칸으로 뺌(다시 묻게) — {nt}')
    said_none, _ = clean_reco({'dimensions': {'file_format': {'value': [], 'basis': 'said'}}}, FB)
    rule_pdf = {'id': 'R-p', 'kind': 'plain', 'when': [], 'key': 'dim.file_format', 'value': ['pdf'], 'no_preselect': False, 'confidence': 1, 'support': 5, 'corrections': 1, 'reason': 'r'}
    ok(said_none['dimensions'].get('file_format', {}).get('value') == [] and merge(said_none, {'dim.file_format': rule_pdf})[0]['dimensions']['file_format']['value'] == []
       and 'dim.file_format' not in [k for k, *_ in gaps(said_none, FB, FD)],
       '사용자가 직접 「없음」이라고 한 빈 답(said)은 남고, 규칙이 덮지 않고, 다시 묻지 않음(R02)')
    ok([k for k, _, s, _c in gaps(cr, FB, FD)] == ['dim.file_format', 'dim.length', 'pq.topic'], '빈 값으로 뺀 칸은 gaps 에 다시 나옴')
    FB2 = ({**FB[0], 'audience_age': {'id': 'audience_age', 'name': '대상', 'type': 'multi', 'values': [{'id': 'adult'}, {'id': 'kid'}]}}, {}, FB[2])
    cr, nt = clean_reco({'dimensions': {'audience_age': {'value': ['adult'], 'basis': 'said'},
                                        'audience_age_primary': {'value': 'adult', 'basis': 'attached', 'from': ' 자료/공문 <1>.pdf:2 '},
                                        'audience_age_other': {'value': 'x', 'basis': 'attached'}}}, FB2)
    d = cr['dimensions']
    ok(d['audience_age_primary'].get('from') == '자료/공문 <1>.pdf:2' and d['audience_age_primary']['basis'] == 'attached'
       and d['audience_age_other']['basis'] == 'inferred' and 'from' not in d['audience_age_other'] and any('audience_age_other' in x for x in nt),
       '보조 칸(_primary · _other)도 근거 검사: from 보존(유니코드 · 특수문자), from 없으면 짐작으로')
    bad_from = [123, True, {'f': 'a'}, ['a.pdf'], '   ', None]
    res = [clean_reco({'dimensions': {'length': {'value': 's', 'basis': 'attached', 'from': f}}}, FB)[0]['dimensions']['length'] for f in bad_from]
    ok(all(x['basis'] == 'inferred' and 'from' not in x for x in res), 'from 이 글이 아니거나 비면(123 · true · 객체 · 목록 · 공백 · null) 짐작으로 내림')
    FB3 = (FB[0], {}, {**FB[2], 'html_only': {'id': 'html_only', 'text': 'HTML 전용', 'type': 'text', 'when': {'file_format': ['html']}}})
    gk = lambda fmt: [k for k, *_ in gaps({'dimensions': {'file_format': {'value': [fmt], 'basis': 'said'}}}, FB3, FD)]
    ok('pq.html_only' not in gk('pdf') and 'pq.html_only' in gk('html'), '3부 질문도 화면과 같은 보이는 조건(when)으로 — 숨은 질문은 묻지 않음')
    two = {'dimensions': {'length': {'value': 's', 'basis': 'inferred'}},
           'rounds': [{'n': 1, 'asked': ['dim.length'], 'answered': ['dim.length']}, {'n': 2, 'asked': ['dim.length'], 'answered': ['dim.length']}]}
    ruled = {'dimensions': {'length': {'value': 's', 'basis': 'rule:R-x'}}}
    r_src = {'id': 'R-s', 'kind': 'plain', 'when': [], 'key': 'dim.sources', 'value': ['user_video'], 'no_preselect': False, 'confidence': 1, 'support': 5, 'corrections': 1, 'reason': 's'}
    r_mp4 = {'id': 'R-m', 'kind': 'plain', 'when': ['dim.sources=user_video'], 'key': 'dim.file_format', 'value': ['mp4'], 'no_preselect': False, 'confidence': 1, 'support': 5, 'corrections': 1, 'reason': 'm'}
    ok('dim.file_format' not in suggest(set(), [r_src, r_mp4], {'dim.sources': {'value': [], 'basis': 'said'}}) and 'dim.file_format' in suggest(set(), [r_src, r_mp4]),
       '보호된 칸(said 「없음」)에 대한 규칙 값은 다음 규칙을 부르지 않음(R03)')
    weak = dict(r_src, support=2, corrections=0)
    cur_photo = {'dim.sources': {'value': ['user_photos'], 'basis': 'inferred'}}
    ok('dim.file_format' not in suggest({'dim.sources=user_photos'}, [weak, r_mp4], cur_photo)
       and 'dim.file_format' in suggest({'dim.sources=user_photos'}, [r_src, r_mp4], cur_photo),
       '약한 규칙이 못 바꾸는 짐작과 어긋난 값은 다음 규칙을 부르지 않고, 강한 규칙으로 바뀐 값은 부름(R04)')
    r_photo_pdf = dict(r_mp4, id='R-pp', when=['dim.sources=user_photos'], value=['docx'])
    ok('dim.file_format' not in suggest({'dim.sources=user_photos'}, [r_src, r_photo_pdf], cur_photo),
       '강한 규칙이 바꾼 지금 값(user_photos)의 신호는 빠져 옛 값의 규칙이 발동하지 않음(R04)')
    r_sl = dict(r_mp4, id='R-sl', when=['dim.sources=user_photos'], key='dim.material_type', value=['slides'])
    r_pdf = dict(r_mp4, id='R-pd', when=['dim.material_type=slides'], key='dim.file_format', value=['pdf'])
    r_dk = dict(r_mp4, id='R-dk', when=['dim.file_format=pdf'], key='dim.theme', value=['dark'])
    chain = suggest({'dim.sources=user_photos'}, [r_src, r_sl, r_pdf, r_dk], cur_photo)
    ok(set(chain) == {'dim.sources'}, f'중간 추천이 철회되면 그 뒤 파생 추천도 끝까지 철회됨(R05) — {sorted(chain)}')
    r_a = dict(r_mp4, id='R-a', when=['!dim.theme=x'], key='dim.theme', value=['x'])
    ok(isinstance(suggest(set(), [r_a]), dict), '규칙이 서로 켜고 끄는 순환에서도 끝남(R05)')
    ok(dict((k, s) for k, _, s, _c in gaps(ruled, FB, FD)).get('dim.length') == 'inferred', '지난 기록 규칙(rule:)으로만 채운 칸도 확인 전 — gaps 에 나옴(R02)')
    old_att = [dict(mk(p, i, S, ['pdf'], key='dim.file_format', outcome='kept', rec=['pdf']), basis='attached') for i, p in enumerate('PQ', 1)]
    ok(not [x for x in learn(old_att)['rules'] if x['key'] == 'dim.file_format'], '옛 기록에 남은 첨부자료 칸(attached)도 learn 이 배우지 않음(R02)')
    import structure_edits as SE_
    real_wp = SE_.with_pending

    def retire_first(dims, qs):
        d, q, n, p = real_wp(dims, qs)
        d = json.loads(json.dumps(d)); d['screens'][0]['retired'] = True
        return d, q, n, p
    first = [x for x in bank_docs()[0]['screens'][0].get('dimensions', [])]
    SE_.with_pending = retire_first
    try:
        hidden = [k for k, *_ in gaps({})]
    finally:
        SE_.with_pending = real_wp
    ok(bool(first) and not any(k == 'dim.' + d for d in first for k in hidden), f'gaps 의 목차도 반영 대기 편집을 적용한 것 — 뺀 목차의 질문은 묻지 않음(R02, {first[:3]})')
    ok(dict((k, s) for k, _, s, _c in gaps(clean_reco(two, FB)[0], FB, FD)).get('dim.length') == 'asked2',
       '애매한 답(answered 에 들었지만 근거가 짐작)도 물은 횟수로 셈 → 두 번이면 그만 묻기')
    cr, nt = clean_reco({'rounds': [{'n': 1, 'asked': ['dim.length', 'dim.length']}, {'n': 2, 'asked': 'dim.length'},
                                    {'n': 3, 'asked': ['dim.length'], 'answered': 'dim.length'}, 'x']}, FB)
    ok(cr['rounds'] == [{'n': 1, 'asked': ['dim.length'], 'answered': []}] and sum('rounds[' in x for x in nt) == 3
       and dict((k, s) for k, _, s, _c in gaps(cr, FB, FD)).get('dim.length') == 'empty',
       'rounds 꼴 검사: 글 하나인 asked · answered 와 객체 아닌 회차는 알리고 뺌, 한 회차 안 같은 칸은 한 번')
    ok(clean_reco([1, 2], FB)[0] is None and clean_reco({'dimensions': ['x']}, FB)[0]['dimensions'] == {}, 'JSON 객체가 아닌 추천 파일 · 객체가 아닌 칸 묶음은 오류 없이 알림')
    pay = {'recommend': {'items': [{'key': 'dim.length', 'outcome': 'kept', 'recommended': 's', 'final': 's', 'basis': 'attached'},
                                   {'key': 'dim.file_format', 'outcome': 'changed', 'recommended': ['html'], 'final': ['pdf'], 'basis': 'inferred'}]},
           'dimensions': {'length': 's', 'file_format': ['pdf']}, 'submitted_at': '2026-01-09T00:00:00'}
    ok([e['key'] for e in events_from_answers(pay, 'T', FB)] == ['dim.file_format'], '첨부자료 칸(attached)은 record 가 배우지 않음 — 프로젝트 사실이지 취향이 아님')
    import contextlib
    import io
    jf = tmp / 'reco_gaps.json'
    jf.write_text(json.dumps({'dimensions': {'length': {'value': 's', 'basis': 'attached'}}}), encoding='utf-8')
    so, se = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(so), contextlib.redirect_stderr(se):
        rc_ = cmd_gaps([str(jf), '--json'])
    try:
        js = json.loads(so.getvalue())
    except ValueError:
        js = None
    ok(rc_ == 0 and isinstance(js, list) and all(x['core'] for x in js) and '알림' in se.getvalue(),
       'gaps --json: stdout 은 JSON 만(알림은 stderr) · --all 없으면 핵심 칸만')
    jf.write_text('[1]', encoding='utf-8')
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        rc_ = cmd_gaps([str(jf)])
    ok(rc_ == 1, 'gaps: JSON 객체가 아닌 파일은 오류 없이 종료 코드 1')
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
    # 듣기 모드(1.7.0): 말씀은 글자 그대로 쌓이고, 「됐어」 전에는 gaps 가 묻지 않는다
    import contextlib
    import io
    lt = pathlib.Path(tempfile.mkdtemp(prefix='tl-listen-'))
    try:
        rf = lt / 'materials' / '인터뷰' / '00_추천.json'
        said1, said2 = '이번엔 작년 거랑 똑같이 | 그런데 <표>는 빼고\n둘째 줄도 그대로', '그리고 마감은 다음 주야'
        with contextlib.redirect_stdout(io.StringIO()) as o1:
            c1 = cmd_listen([str(rf), '--said', said1])
        with contextlib.redirect_stdout(io.StringIO()):
            c2 = cmd_listen([str(rf), '--said', said2])
        sm = (rf.parent / '00_대화요약.md').read_text(encoding='utf-8')
        ok(c1 == 0 and c2 == 0 and said1 in sm and said2 in sm and sm.count(LISTEN_HEAD) == 2 and o1.getvalue().strip() == LISTEN_ACK,
           '듣기 모드: 말씀 둘을 글자 그대로 쌓고 화면에는 한 줄만')
        ok(load_json(rf).get('listening') is True and clean_reco(load_json(rf))[0].get('listening') is True, '듣기 모드: listening 열림(정리해도 남음)')
        with contextlib.redirect_stdout(io.StringIO()) as og, contextlib.redirect_stderr(io.StringIO()):
            cg = cmd_gaps([str(rf), '--json'])
        ok(cg == 3 and json.loads(og.getvalue() or 'null') == {'listening': True, 'gaps': []}, f'듣는 중에는 gaps 가 물을 것을 내지 않음(종료 {cg}, 「물을 것 없음」과 구별)')
        with contextlib.redirect_stdout(io.StringIO()):
            cd = cmd_listen([str(rf), '--done'])
        with contextlib.redirect_stdout(io.StringIO()) as og2, contextlib.redirect_stderr(io.StringIO()):
            cg2 = cmd_gaps([str(rf), '--json'])
        ok(cd == 0 and load_json(rf).get('listening') is False and cg2 == 0 and json.loads(og2.getvalue() or 'null'), '「됐어」(--done) 뒤에는 gaps 가 빈 핵심 칸을 냄')
        with contextlib.redirect_stdout(io.StringIO()):
            ok(cmd_listen([str(rf), '--said', '  ']) == 2 and cmd_listen([str(rf), '--bogus']) == 2 and cmd_listen([str(rf), '--said', '--done']) == 2,
               '듣기 모드: 빈 말씀 · 모르는 인자 · 값 자리의 옵션(--said --done)은 거절(R02)')
            before = (rf.parent / '00_대화요약.md').read_bytes()
            raw = 'first\r\nsecond\n\n\n'
            cmd_listen([str(rf), '--said=' + raw])
            mid = (rf.parent / '00_대화요약.md').read_bytes()
            cmd_listen([str(rf), '--said', '--done 이라고 적어도 원문'])
            after = (rf.parent / '00_대화요약.md').read_bytes()
        ok(mid.startswith(before) and raw.encode('utf-8') in mid and after.startswith(mid) and '--done 이라고 적어도 원문'.encode('utf-8') in after,
           '듣기 모드: 앞 기록은 바이트 그대로 · 새 말씀만 붙음(CRLF · 끝 빈 줄 보존, --said=… 지원 — R02)')
        heading = LISTEN_HEAD + '9 이라는 글을 말씀에 넣어도'
        sf = lt / 'said.txt'
        sf.write_bytes('그가 "좋아" 했어\r\n'.encode('utf-8'))
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            cmd_listen([str(rf), '--said', heading])
            c_file = cmd_listen([str(rf), '--said-file', str(sf)])
            ck = cmd_check([str(rf)])
            lone = cmd_listen([str(lt / 'none' / '인터뷰' / '00_추천.json'), '--done'])
            (lt / 'arr' / '인터뷰').mkdir(parents=True)
            (lt / 'arr' / '인터뷰' / '00_추천.json').write_text('["x"]', encoding='utf-8')
            arr = cmd_listen([str(lt / 'arr' / '인터뷰' / '00_추천.json'), '--said', 'x'])
            dirarg = cmd_listen([str(lt), '--said', 'x'])
            (lt / 'bad' / '인터뷰').mkdir(parents=True)
            (lt / 'bad' / '인터뷰' / '00_추천.json').write_text('{', encoding='utf-8')
            broken = cmd_listen([str(lt / 'bad' / '인터뷰' / '00_추천.json'), '--said', 'x'])
        sm2 = (rf.parent / '00_대화요약.md').read_bytes()
        ok(c_file == 0 and '그가 "좋아" 했어\r\n'.encode('utf-8') in sm2, '듣기 모드: --said-file 은 큰따옴표 · 줄바꿈까지 원문 그대로(R02)')
        ok(load_json(rf).get('heard') == 6, f"듣기 모드: 말씀 개수는 추천 파일에 셈(말씀 속 제목 글에 흔들리지 않음 — {load_json(rf).get('heard')})")
        ok(ck == 3, f'듣는 중에는 check 도 종료 3(R02, {ck})')
        ok(lone == 1 and dirarg == 1 and broken == 1 and arr == 1, f'듣기 모드: 말씀 없는 --done · 폴더 · 깨진 파일은 추적 출력 없이 종료 1 ({lone} · {dirarg} · {broken})')
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            cmd_listen([str(rf), '--done'])
            cs0 = cmd_suggest(['--from', str(rf), '--write'])
            r0 = load_json(rf)
            cmd_listen([str(rf), '--said', '다시 한 말씀'])
            r1 = load_json(rf)
        ff = lt / 'fail' / '인터뷰' / '00_추천.json'
        (ff.parent / '00_대화요약.md').mkdir(parents=True)  # 대화 요약 자리에 폴더 → 말씀 붙이기가 실패
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            cf = cmd_listen([str(ff), '--said', '됐어', '--done'])
        ok(cf == 1 and load_json(ff).get('listening') is True, f'마지막 말씀을 못 적으면 듣기를 닫지 않음(제작은 막힘 — R04, 종료 {cf})')
        bad_att = lt / 'badatt' / '인터뷰' / '00_추천.json'
        bad_att.parent.mkdir(parents=True)
        bad_att.write_text(json.dumps({'attachments': ['materials/a.pdf']}), encoding='utf-8')
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            cba = cmd_suggest(['--from', str(bad_att), '--write'])
        ok(cba == 1 and load_json(bad_att) == {'attachments': ['materials/a.pdf']}, f'틀린 첨부 목록은 suggest --write 가 덮어쓰지 않음(R04, 종료 {cba})')
        pf = lt / 'pf' / 'materials' / '인터뷰' / '00_추천.json'
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            cmd_listen([str(pf), '--said', 'D:/자료/작년_보고서.pdf 이거 그대로 따라 해줘'])
        ok([a.get('path') for a in load_json(pf).get('attachments', [])] == ['D:/자료/작년_보고서.pdf'], '듣는 중 말씀 속 경로는 첨부자료로 적어 둠(준비 점검표가 요구 — R04)')
        given_dir = lt / '받은폴더'
        (given_dir / 'sub').mkdir(parents=True)
        for fn in ('a.pdf', 'sub/b.hwp', 'Thumbs.db'):
            (given_dir / fn).write_bytes(b'x')
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            cmd_listen([str(pf), '--said', given_dir.as_posix() + ' 폴더 자료 전부 봐'])
        with contextlib.redirect_stdout(io.StringIO()) as od, contextlib.redirect_stderr(io.StringIO()):
            cdn = cmd_listen([str(pf), '--done'])
        out_d = od.getvalue()
        ok(cdn == 0 and '하나하나' in out_d and '처음부터 끝까지' in out_d and 'D:/자료/작년_보고서.pdf' in out_d and '안의 파일 2개' in out_d and ' add --lecture ' in out_d,
           f'1.8.0: 듣기를 닫으면 받은 자료를 하나씩(폴더는 안의 파일 수) 보이고 하나하나 열어 분석하라고(init · add) 안내 — {out_d[-300:]}')
        pd = lt / 'pd' / 'materials' / '인터뷰' / '00_추천.json'
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            cmd_listen([str(pd), '--said', '첫 말씀'])
            sm = pd.parent / '00_대화요약.md'
            sm.unlink(); sm.mkdir()  # 요약 파일 자리를 폴더로 막아 쓰기 실패를 만든다
            q1 = cmd_listen([str(pd), '--said', '마지막 말씀', '--done'])
            q2 = cmd_listen([str(pd), '--done'])
            sm.rmdir()
            q3 = cmd_listen([str(pd), '--said', '마지막 말씀', '--done'])
        fin = load_json(pd)
        ok(q1 == 1 and q2 == 1 and q3 == 0 and fin.get('listening') is False and 'pending_said' not in fin and '마지막 말씀' in (pd.parent / '00_대화요약.md').read_text(encoding='utf-8'),
           f'적지 못한 마지막 말씀이 남으면 --done 만으로 닫히지 않고, 다시 적으면 닫힘(R06, {q1} {q2} {q3})')
        pe = lt / 'pe' / 'materials' / '인터뷰' / '00_추천.json'
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            cmd_listen([str(pe), '--said', '첫 말씀'])
            se = pe.parent / '00_대화요약.md'
            se.unlink(); se.mkdir()
            e1 = cmd_listen([str(pe), '--said', '마지막 요구사항'])
            se.rmdir()
            e2 = cmd_listen([str(pe), '--said', '됐어', '--done'])
        txt_e = (pe.parent / '00_대화요약.md').read_text(encoding='utf-8')
        fe = load_json(pe)
        ok(e1 == 1 and e2 == 0 and '마지막 요구사항' in txt_e and '됐어' in txt_e and txt_e.index('마지막 요구사항') < txt_e.index('됐어') and fe.get('heard') == 3 and 'pending_said' not in fe,
           f'적지 못한 말씀은 다음 말씀 앞에 원문 그대로 함께 적히고 지워지지 않음(R07, {e1} {e2} heard={fe.get("heard")})')
        out8 = lt / 'Documents' / '00_추천.json'
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            o1 = cmd_listen([str(out8), '--said', 'last message', '--done'])
            o2 = cmd_listen([str(out8), '--said', 'x', '--anywhere'])
        ok(o1 == 2 and o2 == 0, f'기본 자리(…/인터뷰/00_추천.json)가 아니면 아무것도 쓰지 않고 거절, --anywhere 면 씀(R08, {o1} {o2})')
        empty = lt / 'empty.json'
        empty.write_bytes(b'')
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            codes = [main(['check', str(empty)]), main(['gaps', str(empty)]), main(['suggest', '--from', str(empty)])]
        ok(codes == [1, 1, 1] and empty.read_bytes() == b'', f'빈 JSON 파일은 오류 없이 종료 1 · 파일 그대로(R07, {codes})')
        pn = lt / 'pn' / 'materials' / '인터뷰' / '00_추천.json'
        pn.parent.mkdir(parents=True)
        pn.write_text(json.dumps({'attachments': None}), encoding='utf-8')
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            cpn = cmd_listen([str(pn), '--said', 'https://example.org/ref', '--done'])
            p5 = lt / 'p5' / 'materials' / '인터뷰' / '00_추천.json'
            p5.parent.mkdir(parents=True)
            p5.write_text(json.dumps({'attachments': 5}), encoding='utf-8')
            cp5 = cmd_listen([str(p5), '--said', 'x'])
            ok_id = lt / 'okid.json'
            ok_id.write_text(json.dumps({'id': 'test'}), encoding='utf-8')
            cid = cmd_suggest(['--from', str(ok_id), '--write'])
            c5 = cmd_suggest(['--from', str(p5), '--write'])
        ok(cpn == 0 and [a.get('path') for a in load_json(pn)['attachments']] == ['https://example.org/ref'], f'attachments: null 이어도 말씀 속 주소를 적음(R05, 종료 {cpn})')
        ok(cp5 == 1 and load_json(p5) == {'attachments': 5}, f'attachments 가 목록이 아니면 아무것도 쓰지 않고 종료 1(R05, {cp5})')
        ok(cid == 0, f'첨부 칸이 없는 추천도 suggest --write 가 됨(R05, 종료 {cid})')
        ok(c5 == 1, f'attachments: 5 → 추적 출력 없이 --write 거절(R05, 종료 {c5})')
        ls = lt / 'ls.json'
        ls.write_text(json.dumps({'listening': 'true', 'attachments': []}), encoding='utf-8')
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            cls = cmd_suggest(['--from', str(ls), '--write'])
            cgs = cmd_gaps([str(ls)])
        ok(cls == 3 and cgs == 3 and load_json(ls).get('listening') == 'true', f'bool 아닌 listening 은 듣는 중으로 — suggest · gaps 종료 3, 파일 그대로(R05, {cls} · {cgs})')
        ok(cs0 == 0 and r0.get('listening') is False and r0.get('heard') == 6 and r1.get('heard') == 7 and r1.get('listening') is True,
           f"suggest --write 뒤에도 듣기 개수 · 닫힘 표시가 남음(R03, {r0.get('heard')} → {r1.get('heard')})")
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            cs = cmd_suggest(['--from', str(rf), '--write'])
        ok(cs == 3 and load_json(rf).get('listening') is True, f'듣는 중에는 suggest 가 추천을 고치지 않음(종료 {cs})')
    finally:
        import shutil
        shutil.rmtree(lt, ignore_errors=True)
    print('실패 ' + str(len(fails)) if fails else '자체 시험 통과')
    return 1 if fails else 0


def main(argv):
    if not argv:
        print(__doc__); return 2
    cmd, rest = argv[0], argv[1:]
    if cmd != 'selftest':
        try:
            return _dispatch(cmd, rest)
        except (ValueError, OSError) as e:  # 빈 파일 · 깨진 JSON · 못 읽는 파일 — 아무것도 쓰지 않고 종료 1(R07)
            print(f'파일을 읽지 못했습니다(아무것도 바꾸지 않음): {e}'); return 1
    return _dispatch(cmd, rest)


def _dispatch(cmd, rest):
    if cmd == 'record':
        return cmd_record(rest)
    if cmd == 'correct':
        return cmd_correct(rest)
    if cmd == 'suggest':
        return cmd_suggest(rest)
    if cmd == 'check':
        return cmd_check(rest)
    if cmd == 'gaps':
        return cmd_gaps(rest)
    if cmd == 'listen':
        return cmd_listen(rest)
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
