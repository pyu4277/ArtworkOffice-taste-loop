#!/usr/bin/env python3
"""인터뷰 답변 JSON → 강의 폴더 materials/00_제작계획.md 뼈대.

사용법:
  python3 answers_to_plan.py --lecture <강의폴더> --answers <답변.json> [--out <계획.md>] [--topic <낱말>]...

- 처음이면 계획 문서를 새로 만든다. 이미 있으면 <!-- taste-loop:begin --> … <!-- taste-loop:end --> 사이만 바꾼다(예전 표식 preference-evolution:begin/end 도 알아본다)
  (그 밖의 절 — 배정표·구성·시간 배분·산출물 목록·PC에서 할 일·작업현황 — 은 손으로 채우는 곳이라 건드리지 않는다).
- 적용 취향 표는 scripts/match.py 와 같은 규칙으로 계산한다. 답하지 않은 항목은 「기본값 적용」으로 표시한다.
- 환경 점검 표는 check_env.py 를 실행해 넣는다(클라우드·Linux·macOS). PC 결과는 사용자가 붙여 넣는다.
- 인터뷰 페이지에서 끌어다 넣은 것도 옮긴다: base_project(기본 양식 — 그 프로젝트 기록을 출발점으로 삼는다),
  refs(질문별 참고 — 적용 취향 표의 「참고」 칸과 「참고로 넣은 것」 절), new_refs(새 레퍼런스 메모 — 6절에서 서랍에 등록).
"""
import datetime
import json
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.dont_write_bytecode = True  # 설치 폴더(플러그인 캐시)에 __pycache__ 를 만들지 않는다
sys.path.insert(0, str(HERE))
import store as ST  # noqa: E402  엔진과 데이터 분리
import match as M  # noqa: E402
SKILL = ST.ENGINE
REPO = ST.project_root()

BEGIN, END = '<!-- taste-loop:begin -->', '<!-- taste-loop:end -->'
OLD_MARKS = ('<!-- preference-evolution:begin -->', '<!-- preference-evolution:end -->')
EXT = {'html169': 'html', 'mp4_916': 'mp4', 'mp4_169': 'mp4', 'pdf': 'pdf', 'hwpx': 'hwpx', 'docx': 'docx', 'pptx': 'pptx', 'print_a4': 'pdf', 'audio_file': 'mp3'}
CHOICE = {'keep': '그대로', 'change': '이번엔 다르게', 'new': '처음 정함', 'skip': '나중에·해당 없음'}
KIND = {'project': '프로젝트', 'past_all': '지난 답변', 'past': '지난 답', 'entry': '취향', 'decision': '결정', 'lesson': '교훈', 'mistake': '실수', 'design_ref': '레퍼런스', 'template': '템플릿', 'new_ref': '새 메모'}

MANUAL_SECTIONS = """
## 배정표 (스킬 3.2절 — 단위마다 에이전트·모델·effort·예상 비용·실행 환경)

| 단위 | 에이전트 | 모델 / effort | 예상 비용 | 실행 환경 | 상태 |
|---|---|---|---|---|---|
| (예: 자료별 분석) | Claude 서브에이전트 | sonnet / medium | — | 클라우드 가능 | 대기 |

## 구성과 시간 배분 (스킬 3.3절 — 원자료 분석 뒤 확정)

| 챕터 | 섹션 | 하위 주제 | 배분 | 비고 |
|---|---|---|---|---|

## 생성 목록·크레딧 (스킬 3.4절·최상위 2.4)

| 장면 | 무엇을 | 모델 | 예상 크레딧 | 결과 |
|---|---|---|---|---|

## 산출물 목록 (보고 끝 「확인할 결과물」 표의 원본)

| 경로 | 게시 URL | 한 줄 설명 | 확인 포인트 | 단일 파일 |
|---|---|---|---|---|

## PC에서 할 일 (클라우드에서 못 한 것 — 스킬 2절)

- (없음)

## 작업현황

- (날짜) 시작
"""


def lecture_name(folder):
    m = re.match(r'^\d{4}(?:\d{2})?_[^_/]+_(.+)$', folder)
    return m.group(1) if m else folder


def label_dim(dims, did, v):
    d = next((x for x in dims['dimensions'] if x['id'] == did), None)
    if not d:
        return str(v)
    if d.get('type') == 'text':
        return str(v)
    lab = {x['id']: x['label'] for x in d.get('values', [])}
    return ', '.join(lab.get(x, x) for x in v) if isinstance(v, list) else lab.get(v, str(v))


def ref_text(refs):
    """refs 목록 → '종류: 이름 (URL)' 들을 ' / '로 이은 글. 표 칸에 넣으므로 | 는 뺀다."""
    out = []
    for r in refs or []:
        s = f'{KIND.get(r.get("kind"), r.get("kind"))}: {r.get("label", r.get("id", ""))}'
        if r.get('url'):
            s += f' ({r["url"]})'
        out.append(s.replace('|', '¦'))
    return ' / '.join(out)


def target_label(target, dims, aspects, pq):
    if target == 'base':
        return '기본 양식'
    kind, _, tid = target.partition(':')
    if kind == 'dim':
        d = next((x for x in dims['dimensions'] if x['id'] == tid), None)
        return f'차원 · {d["name"] if d else tid}'
    if kind == 'aspect':
        return f'취향 · {aspects.get(tid, {}).get("text", tid)}'
    if kind == 'pq':
        return f'이번 자료 · {pq.get(tid, {}).get("text", tid)}'
    if kind == 'item':
        return f'항목 · {tid}'
    return target


def main(argv):
    a, topics = {}, []
    i = 0
    while i < len(argv):
        if argv[i] == '--topic':
            topics.append(argv[i + 1]); i += 2
        elif argv[i] in ('--lecture', '--answers', '--out'):
            a[argv[i][2:]] = argv[i + 1]; i += 2
        else:
            print(__doc__, file=sys.stderr); return 2
    if not a.get('lecture') or not a.get('answers'):
        print(__doc__, file=sys.stderr); return 2
    dims = json.loads(ST.path('dimensions.json').read_text(encoding='utf-8'))
    qs = json.loads(ST.path('questions.json').read_text(encoding='utf-8'))
    prefs = json.loads(ST.path('preferences.json').read_text(encoding='utf-8'))
    ans = json.loads(pathlib.Path(a['answers']).read_text(encoding='utf-8'))
    aspects = {x['id']: x for x in qs['aspects']}
    pq = {x['id']: x for x in qs.get('project_questions', [])}
    name = lecture_name(a['lecture'])
    out = pathlib.Path(a.get('out') or REPO / a['lecture'] / 'materials' / '00_제작계획.md')
    today = datetime.date.today().isoformat()
    dv = ans.get('dimensions') or {}

    # 적용 취향 계산
    project = {k: (v if isinstance(v, list) else [v]) for k, v in dv.items() if not k.endswith('_other') and not k.endswith('_primary') and v not in (None, '', [])}
    project['lecture'] = [a['lecture']]
    if topics:
        project['topic'] = topics
    matches, _ = M.match(project, prefs)

    refs = ans.get('refs') or {}
    L = [BEGIN, f'_생성: {today} · 답변: `{pathlib.Path(a["answers"]).name}` · spec: `{ans.get("spec_id", "")}` · 경로: {ans.get("client", "")}_', '']
    bp = ans.get('base_project')
    if bp:
        src = f'knowledge/projects/{bp.get("id")}.json' if bp.get('kind') == 'project' else bp.get('id', '')
        L += ['## 기본 양식 (사용자가 인터뷰에서 끌어다 놓은 지난 프로젝트)', '',
              f'- **{bp.get("title", bp.get("id"))}** (`{src}`) — 차원 {bp.get("dims_set", "?")}개 · 취향 {bp.get("aspects_set", "?")}개를 이 기록대로 맞춤 ({str(bp.get("applied_at", ""))[:10]})',
              '- 뜻: 사용자는 이 프로젝트의 설정을 **기본 셋팅**으로 원한다. 그 기록의 차원 값·적용 항목·결정·결과를 출발점으로 삼고, 아래 표에서 달라진 답만 차이로 다룬다. 추측으로 바꾸지 않는다.', '']
    L += ['## 사양 (차원 값 — 인터뷰 1부)', '', '| 차원 | 값 | 참고 |', '|---|---|---|']
    for d in dims['dimensions']:
        v = dv.get(d['id'])
        if v in (None, '', []):
            continue
        txt = label_dim(dims, d['id'], v)
        if dv.get(d['id'] + '_other'):
            txt += f' (기타: {dv[d["id"] + "_other"]})'
        if dv.get(d['id'] + '_primary'):
            txt += f' — 주 대상: {label_dim(dims, d["id"], dv[d["id"] + "_primary"])}'
        L.append(f'| {d["name"]} | {txt} | {ref_text(refs.get("dim:" + d["id"]))} |')
    L += ['', '## 실행 모드 (스킬 2절)', '', f'- {label_dim(dims, "exec_mode", dv.get("exec_mode", "cloud"))}'
          + (f' · 함께 쓸 에이전트: {label_dim(dims, "other_agents", dv.get("other_agents"))}' if dv.get('other_agents') else '')]
    # 환경 점검
    L += ['', '## 환경 점검 (스킬 1절 ③ — 이 세션에서 실행)', '']
    try:
        r = subprocess.run([sys.executable, '-I', str(HERE / 'check_env.py')], capture_output=True, text=True, timeout=60)
        L += r.stdout.strip().splitlines()
    except Exception as e:  # noqa: BLE001
        L.append(f'(check_env.py 실행 실패: {e})')
    L.append('- PC 점검 결과(check_env.ps1)는 사용자가 붙여 넣으면 여기에 추가한다. 커넥터(Higgsfield·Figma) 확인 결과: (적을 것)')
    # 적용 취향
    L += ['', '## 적용 취향 (인터뷰 2부 — 「처음 시도」와 「갱신 후보」는 아래 표시)', '', '| 항목 | 이번 선택 | 값 | 근거 항목 | 비고 | 참고 |', '|---|---|---|---|---|---|']
    asp_ans = ans.get('aspects') or {}
    seen = set()
    for aid, r in sorted(matches.items()):
        a_ = aspects.get(aid, {})
        s = asp_ans.get(aid)
        seen.add(aid)
        rt = ref_text(refs.get('aspect:' + aid))
        if s and s.get('choice'):
            val = s.get('value') if s.get('choice') in ('change', 'new') else r['value']
            note = ('⭐항상 바꾸기 → 갱신 후보' if s.get('always') else '') + (f' 메모: {s["note"]}' if s.get('note') else '') + (f' (출처: {s["from"]})' if s.get('from') else '')
            L.append(f'| {a_.get("text", aid)} | {CHOICE.get(s["choice"], s["choice"])} | {M.json.dumps(val, ensure_ascii=False)} | {r["winner"]} | {note} | {rt} |')
        else:
            flag = '⚠충돌 — 사용자 선택 필요' if r['conflict'] else ('⚠추론 — 확인 전 적용 금지' if r['inferred'] else '기본값 적용')
            L.append(f'| {a_.get("text", aid)} | (답 없음) | {M.json.dumps(r["value"], ensure_ascii=False)} | {r["winner"]} | {flag} | {rt} |')
    for aid, s in asp_ans.items():
        if aid in seen or not s.get('choice'):
            continue
        a_ = aspects.get(aid, {})
        lab = '지난 양식 값 (지금 범위엔 학습 항목 없음)' if s['choice'] == 'keep' else CHOICE.get(s['choice'], s['choice']) + ' (처음 시도)'
        L.append(f'| {a_.get("text", aid)} | {lab} | {M.json.dumps(s.get("value"), ensure_ascii=False)} | — | {"⭐항상 → 갱신 후보" if s.get("always") else ""}{(" 메모: " + s["note"]) if s.get("note") else ""}{(" (출처: " + s["from"] + ")") if s.get("from") else ""} | {ref_text(refs.get("aspect:" + aid))} |')
    # 선택별 진화 기록 적용 — 답한 값마다 choices.json의 지금 버전 방법
    choices = {}
    cj = ST.path('knowledge/choices.json')
    if cj.exists():
        try:
            choices = json.loads(cj.read_text(encoding='utf-8')).get('choices', {})
        except ValueError:
            choices = {}
    L += ['', '## 선택별 진화 기록 적용 (knowledge/choices.json — 같은 선택이라도 지금 버전의 방법으로 만든다)', '']
    used = []
    for aid, s in asp_ans.items():
        if not s.get('choice') or s.get('choice') == 'skip':
            continue
        val = s.get('value') if s.get('value') is not None else (matches.get(aid) or {}).get('value')
        for oid in (val if isinstance(val, list) else [val]):
            c = choices.get(f'{aid}|{oid}')
            if not c:
                continue
            a_ = aspects.get(aid, {})
            lab = next((o['label'] for o in a_.get('options', []) if o['id'] == oid), oid)
            used.append(f'- **{a_.get("text", aid)} = {lab}** · v{c.get("version")} ({c.get("updated")}; 배운 곳 {", ".join(c.get("learned_from", []))})')
            used += [f'  - 방법: {h}' for h in c.get('how', [])]
            used += [f'  - 점검: {h}' for h in c.get('checks', [])]
            ex = c.get('examples') or {}
            if ex.get('liked'):
                used.append('  - 좋았던 예: ' + ' / '.join(ex['liked']))
    L += used or ['- (답한 선택지에 아직 진화 기록이 없음 — 마무리 때 이번 방법을 기록하면 다음부터 여기에 나온다)']
    # 참고로 넣은 것 전체 + 새 레퍼런스 메모
    L += ['', '## 참고로 넣은 것 (인터뷰에서 끌어다 넣은 지난 내역·레퍼런스 — 제작 때 그 예시를 본다)', '']
    L += [f'- {target_label(t, dims, aspects, pq)}: {ref_text(rs)}' for t, rs in refs.items() if rs] or ['- (없음)']
    L += ['', '## 새 레퍼런스 메모 (인터뷰 서랍 「새 메모」 — 마무리(6절) 때 서랍에 등록)', '']
    L += [f'- {n.get("text", "")}' + (f' — {n["url"]}' if n.get('url') else '') for n in (ans.get('new_refs') or [])] or ['- (없음)']
    cand = [(aid, s) for aid, s in asp_ans.items() if s.get('always') or s.get('choice') in ('change', 'new')]
    L += ['', '## 취향 갱신 후보 (스킬 6절에서 판정 — 지금은 반영하지 않음)', '']
    L += [f'- {aspects.get(aid, {}).get("text", aid)}: {CHOICE.get(s.get("choice"), s.get("choice"))} → {M.json.dumps(s.get("value"), ensure_ascii=False)}'
          + (' (항상)' if s.get('always') else '') + (f' — {s["note"]}' if s.get('note') else '') for aid, s in cand] or ['- (없음)']
    # 프로젝트 사항
    pr = ans.get('project') or {}
    L += ['', '## 이번 자료에 대해 (인터뷰 3부 — 프로젝트별 결정)', '']
    for qid, q in pq.items():
        v = pr.get(qid)
        if v in (None, '', []):
            continue
        if q.get('options'):
            lab = {o['id']: o['label'] for o in q['options']}
            v = ', '.join(lab.get(x, x) for x in v) if isinstance(v, list) else lab.get(v, v)
        L.append(f'- {q["text"]}: {v}')
    rp = pr.get('review_plan') or ['structure', 'first', 'mid', 'final']
    lab = {o['id']: o['label'] for o in pq.get('review_plan', {}).get('options', [])}
    L += ['', '## 검토 일정 (스킬 4절)', ''] + [f'- [ ] {lab.get(x, x)} — 검토 페이지: materials/인터뷰/03_검토_v?.html' for x in rp]
    ext = EXT.get(dv.get('format'), 'html')
    L += ['', '## 산출물 이름 후보 (최상위 6절 — 확정 뒤 `scripts/check-filenames.py`로 확인)', '', f'- `{name}_01_<주제>.{ext}` (공유본은 단일 파일 — 2.1절)', END]
    block = '\n'.join(L)
    if out.exists():
        s = out.read_text(encoding='utf-8')
        if OLD_MARKS[0] in s and OLD_MARKS[1] in s and BEGIN not in s:
            s = s.replace(OLD_MARKS[0], BEGIN).replace(OLD_MARKS[1], END)
        if BEGIN in s and END in s:
            s = s[:s.index(BEGIN)] + block + s[s.index(END) + len(END):]
        else:
            s = s.rstrip('\n') + '\n\n' + block + '\n'
        out.write_bytes(s.encode('utf-8'))  # 줄바꿈을 LF 로 고정: Windows 에서 만들어도 클라우드와 같은 파일이 된다
        print('갱신:', out)
    else:
        out.parent.mkdir(parents=True, exist_ok=True)
        s = (f'# 제작 계획 — {name}\n\n이 문서는 스킬 `ArtworkOffice-taste-loop`(SKILL.md)의 계획 문서다. 표시 블록 안은 `answers_to_plan.py`가 다시 만들고, 그 밖의 절은 손으로 채운다.\n\n'
             + block + '\n' + MANUAL_SECTIONS)
        out.write_bytes(s.encode('utf-8'))
        print('생성:', out)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
