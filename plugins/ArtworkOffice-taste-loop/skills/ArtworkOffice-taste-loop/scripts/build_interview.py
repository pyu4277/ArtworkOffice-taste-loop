#!/usr/bin/env python3
"""인터뷰·구성 확인·검토·승인 페이지를 만든다 (GUI-Interview.html 엔진 + 사양 JSON).

사용법:
  python3 build_interview.py --lecture <강의폴더> --mode interview --out <출력.html> [--artifact]
      [--like <강의폴더>] [--answers <이전 답변.json>] [--topic <낱말>]... [--title <제목>] [--intro <안내문>]
  python3 build_interview.py --lecture <강의폴더> --mode structure --spec <구성안.json> --out <출력.html>
  python3 build_interview.py --lecture <강의폴더> --mode review --spec <항목.json> --out <출력.html>
  python3 build_interview.py --lecture <강의폴더> --mode approve --spec <제안.json> --out <출력.html>
  python3 build_interview.py --lecture <강의폴더> --mode edit --out <출력.html> [--artifact]
      구조 편집기(GUI-Structure.html): 목차 → 질문 → 선택지(1부), 취향 묶음 → 하위 → 질문 → 선택지(2부), 3부 질문을
      고치고 「보이는 조건」을 단다. 고친 것은 편집 기록 JSON(05_구조편집.json)으로 내보내고
      structure_edits.py add <JSON> 으로 「반영 대기」에 쌓았다가 마무리 때 structure_edits.py apply --yes 로 반영한다.
--no-pending: 기록 모음(knowledge/structure_edits.json)의 반영 대기 구조 편집을 적용하지 않고 파일 그대로 보여 준다.
              (기본: 인터뷰·구성 확인·검토·승인 페이지는 반영 대기 편집을 메모리에서 적용해 보여 준다. 파일은 마무리 때 바뀐다)

--artifact: claude.ai 게시용(문서 머리 없음). 없으면 브라우저로 여는 파일용(doctype·head 포함).
--like: 그 프로젝트 기록(knowledge/projects/<강의폴더>.json)의 차원 값을 기본값으로 미리 선택한다.
        생략하면 같은 강의의 기록이 있을 때 그것을 쓴다.
--spec(structure/review/approve): {"items":[{"id","title","desc","url","chapters":[...]}], "items_title", "items_question"}

페이지는 사이트형 앱이다: 메뉴 줄(대시보드·인터뷰·저장소·도움말) · 리본 · 왼쪽 「참고 서랍」 · 본문.
안에 품는 것: 차원·질문 은행·취향 항목 전부(status 무관, 판정은 활성 항목만) + 저장소(store):
  knowledge/projects/*.json(프로젝트 기록), <강의폴더>/materials/인터뷰/*답변*.json(지난 답변),
  knowledge/01(교훈)·05(실수+점검표)·03(디자인 레퍼런스 서비스)·04(템플릿)·02(변경이력)·choices.json(선택별 진화 기록).
서랍의 카드를 질문 카드에 끌어다 놓거나 「넣기」로 붙이면 답변 JSON의 refs / base_project / new_refs 로 돌아온다
(판정 규칙은 scripts/match.py 와 같다). 답은 db(게시 페이지) 또는 JSON 내려받기·복사로 돌아온다.
"""
import datetime
import json
import pathlib
import re
import sys

sys.dont_write_bytecode = True  # 설치 폴더(플러그인 캐시)에 __pycache__ 를 만들지 않는다
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import store as ST  # noqa: E402  엔진과 데이터 분리
import demos as DM  # noqa: E402
SKILL = ST.ENGINE
REPO = ST.project_root()
TEMPLATE = SKILL / 'GUI-Interview.html'
EDIT_TEMPLATE = SKILL / 'GUI-Structure.html'
KNOW = ST.KNOW if ST.KNOW.exists() else ST.STARTER / 'knowledge'
MODES = ('interview', 'structure', 'review', 'approve', 'edit')
FILE_HEAD = '<!doctype html>\n<html lang="ko">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n</head>\n<body>\n'
FILE_TAIL = '\n</body>\n</html>\n'
ANSWER_KEYS = ('spec_id', 'mode', 'lecture', 'submitted_at', 'client', 'dimensions', 'aspects', 'project', 'base_project', 'refs', 'new_refs', 'items', 'overall')


def lecture_name(folder):
    m = re.match(r'^\d{4}(?:\d{2})?_[^_/]+_(.+)$', folder)
    return m.group(1) if m else folder


def load_json(p):
    return json.loads(pathlib.Path(p).read_text(encoding='utf-8'))


def read(p):
    p = pathlib.Path(p)
    return p.read_text(encoding='utf-8') if p.exists() else ''


def clean(cell):
    return cell.replace('`', '').replace('**', '').strip()


def md_tables(text):
    """Markdown 표 → [(머리 셀 목록, [행 셀 목록...]), ...]. 구분 행(---)의 바로 앞 행이 머리다."""
    tables, header, rows = [], None, []
    for line in text.splitlines() + ['']:
        s = line.strip()
        if s.startswith('|'):
            cells = [clean(c) for c in s.strip('|').split('|')]
            if cells and all(re.fullmatch(r':?-{2,}:?', c) for c in cells if c) and any(cells):
                continue  # 구분 행
            if header is None:
                header = cells
            else:
                rows.append(cells)
        else:
            if header is not None:
                tables.append((header, rows))
            header, rows = None, []
    return tables


def rows_as(text, keys, pick=None):
    out = []
    for header, rows in md_tables(text):
        for r in rows:
            if len(r) < len(keys):
                continue
            if pick and not pick(r):
                continue
            out.append(dict(zip(keys, r)))
    return out


def load_store():
    import upgrade_store as UP
    store = {'projects': [], 'past_answers': [], 'lessons': [], 'mistakes': [], 'checklist': [], 'design_refs': [], 'templates': [], 'changes': [], 'choices': {}}
    if (KNOW / 'choices.json').exists():
        try:
            store['choices'] = load_json(KNOW / 'choices.json').get('choices', {})
        except ValueError:
            pass
    for p in sorted((KNOW / 'projects').glob('*.json')) if (KNOW / 'projects').exists() else []:
        try:
            rec = load_json(p)
        except ValueError:
            continue
        rec.setdefault('lecture', p.stem)
        rec['dimensions'] = UP.migrate_answers_dims(rec.get('dimensions'))
        store['projects'].append(rec)
    for p in sorted(list(REPO.glob('*/materials/인터뷰/*답변*.json')) + list(REPO.glob('materials/인터뷰/*답변*.json'))):
        try:
            ans = load_json(p)
        except ValueError:
            continue
        if not isinstance(ans, dict) or not ans.get('dimensions') and not ans.get('items'):
            continue
        slim = {k: ans.get(k) for k in ANSWER_KEYS if ans.get(k) is not None}
        if 'dimensions' in slim:
            slim['dimensions'] = UP.migrate_answers_dims(slim['dimensions'])
        slim['file'] = str(p.relative_to(REPO))
        store['past_answers'].append(slim)
    # 01 교훈: 「---」 뒤의 「### 제목」 블록
    text = read(KNOW / '01_교훈_기록.md')
    body = text.split('\n---', 1)[1] if '\n---' in text else ''
    for block in re.split(r'\n(?=### )', body):
        block = block.strip()
        if not block.startswith('### '):
            continue
        title, _, rest = block[4:].partition('\n')
        store['lessons'].append({'title': title.strip(), 'date': title[:10] if re.match(r'\d{4}-\d{2}-\d{2}', title) else '', 'body': rest.strip()})
    # 05 실수 표 + 점검표
    text = read(KNOW / '05_실수_기록.md')
    store['mistakes'] = rows_as(text, ('id', 'when', 'kind', 'symptom', 'cause', 'fix', 'confirm'), lambda r: re.fullmatch(r'E\d+', r[0]))
    tail = text.split('## 시작 전 점검표', 1)[1] if '## 시작 전 점검표' in text else ''
    store['checklist'] = [m.group(1).strip() for m in re.finditer(r'^\d+\.\s+(.+)$', tail, re.M)]
    # 03 디자인 레퍼런스 서비스 표(주소 칸이 http로 시작하는 행)
    store['design_refs'] = rows_as(read(KNOW / '03_디자인_레퍼런스_서비스.md'), ('type', 'service', 'url', 'what', 'license', 'access'), lambda r: r[2].startswith('http'))
    # 04 템플릿 표
    store['templates'] = rows_as(read(KNOW / '04_템플릿_목록.md'), ('type', 'name', 'location', 'usage', 'single'), lambda r: r[0] != '자료 종류')
    # 02 변경이력 표
    store['changes'] = rows_as(read(KNOW / '02_변경이력.md'), ('date', 'project', 'target', 'action', 'basis', 'by'), lambda r: re.match(r'\d{4}-\d{2}-\d{2}', r[0]))
    return store


def parse(argv):
    a = {'topics': [], 'artifact': False, 'no_pending': False}
    i = 0
    while i < len(argv):
        k = argv[i]
        if k == '--artifact':
            a['artifact'] = True; i += 1; continue
        if k == '--no-pending':
            a['no_pending'] = True; i += 1; continue
        if k == '--topic':
            a['topics'].append(argv[i + 1]); i += 2; continue
        if k in ('--lecture', '--mode', '--out', '--like', '--answers', '--spec', '--title', '--intro', '--pc'):
            a[k[2:]] = argv[i + 1]; i += 2; continue
        print(__doc__, file=sys.stderr); sys.exit(2)
    if not a.get('lecture') or not a.get('out'):
        print(__doc__, file=sys.stderr); sys.exit(2)
    a.setdefault('mode', 'interview')
    if a['mode'] not in MODES:
        print('mode는', MODES, file=sys.stderr); sys.exit(2)
    return a


def write_page(a, template, spec):
    html = template.read_text(encoding='utf-8')
    body = html.replace('__TITLE__', spec['title'].replace('<', '&lt;')).replace('__SPEC__', json.dumps(spec, ensure_ascii=False).replace('</', '<\\/'))
    out = pathlib.Path(a['out'])
    out.parent.mkdir(parents=True, exist_ok=True)
    text = body if a['artifact'] else FILE_HEAD + body + FILE_TAIL
    out.write_bytes(text.encode('utf-8'))  # 줄바꿈을 LF 로 고정
    return out, text


def build_edit(a, dims, qs, pending, name, today):
    """구조 편집기 페이지. 원본(데이터 폴더 파일, 메모리 이관) + 반영 대기 편집(pending_ops)을 품는다."""
    spec = {
        'spec_id': f"{a['lecture']}/edit/{today}",
        'mode': 'edit', 'lecture': a['lecture'],
        'title': a.get('title') or f'{name} 구조 편집',
        'answers_filename': '05_구조편집',
        'dimensions': dims, 'questions': qs, 'pending_ops': pending,
    }
    out, text = write_page(a, EDIT_TEMPLATE, spec)
    print(f"wrote {out} ({len(text.encode('utf-8'))} B, {'게시용' if a['artifact'] else '파일용'}, 구조 편집기: 목차 {len(dims.get('screens', []))} · 질문 {len(dims.get('dimensions', []))} · "
          f"취향 질문 {len(qs.get('aspects', []))} · 3부 질문 {len(qs.get('project_questions', []))} · 반영 대기 편집 {len(pending)}건)")
    return 0


def main(argv):
    a = parse(argv)
    import upgrade_store as UP
    dims, old = UP.migrate_dims(load_json(ST.path('dimensions.json')))
    if old:
        print('알림: 데이터 폴더의 dimensions.json 이 옛 구조라 새 구조(파일형식·PDF 변환본·콘텐츠 유형)로 읽었습니다. upgrade_store.py 로 파일도 올리세요.', file=sys.stderr)
    qs, _qold = UP.migrate_qs(load_json(ST.path('questions.json')))
    name = lecture_name(a['lecture'])
    today = datetime.date.today().isoformat()
    import structure_edits as SE
    if a['mode'] == 'edit':
        return build_edit(a, dims, qs, SE.pending_ops() if SE.ledger_path().exists() else [], name, today)
    if not a['no_pending']:
        dims, qs, n_pend, probs = SE.with_pending(dims, qs)
        if n_pend:
            print(f'알림: 반영 대기 구조 편집 {n_pend}건을 적용해 보여 줍니다(파일은 마무리 때 바뀜).', file=sys.stderr)
        for pr in probs:
            print(f'알림: 반영 대기 구조 편집 중 적용되지 않은 것 — {pr}', file=sys.stderr)
    prefs = load_json(ST.path('preferences.json'))
    store = load_store()
    spec = {
        'spec_id': f"{a['lecture']}/{a['mode']}/{today}",
        'mode': a['mode'], 'lecture': a['lecture'], 'topics': a['topics'], 'pc': a.get('pc'),
        'title': a.get('title') or f"{name} {'제작 인터뷰' if a['mode'] == 'interview' else {'structure': '구성 확인', 'review': '검토', 'approve': '취향 갱신 승인'}[a['mode']]}",
        'intro': a.get('intro') or '',
        'answers_filename': {'interview': '01_제작인터뷰_답변', 'structure': '02_구성확인_답변', 'review': '03_검토_답변', 'approve': '04_승인_답변'}[a['mode']],
        'questions': {'categories': qs['categories'], 'aspects': qs['aspects'], 'review_reasons': qs.get('review_reasons', []), 'project_questions': qs.get('project_questions', [])},
        'entries': prefs['entries'],  # 전부(은퇴 항목도 열람용). 판정은 엔진이 활성 항목만 쓴다
        'dimensions': {'screens': dims['screens'], 'dimensions': dims['dimensions']},
        'defaults': {'dimensions': {}},
        'store': store,
        'demos': DM.for_spec(),  # 선택지 예시(움직이는 HTML) — 내 예시가 엔진 기본을 이긴다
    }
    if a['mode'] == 'interview':
        like = a.get('like') or a['lecture']
        rec = KNOW / 'projects' / f'{like}.json'
        if rec.exists():
            spec['defaults']['dimensions'] = UP.migrate_answers_dims(load_json(rec).get('dimensions', {}))
            spec['defaults']['from'] = like
        if a.get('answers'):
            prev = load_json(a['answers'])
            spec['defaults']['dimensions'].update(UP.migrate_answers_dims(prev.get('dimensions', {})))
            spec['defaults']['from'] = a['answers']
    else:
        if not a.get('spec'):
            print('structure/review/approve 모드는 --spec <json> 이 필요합니다', file=sys.stderr); return 2
        extra = load_json(a['spec'])
        spec['items'] = extra.get('items', [])
        for k in ('items_title', 'items_question', 'title', 'intro'):
            if extra.get(k) and not a.get(k):
                spec[k] = extra[k]
    out, text = write_page(a, TEMPLATE, spec)
    active = sum(1 for e in prefs['entries'] if e.get('status') in ('proposed', 'confirmed'))
    print(f"wrote {out} ({len(text.encode('utf-8'))} B, {'게시용' if a['artifact'] else '파일용'}, 항목 {active}/{len(prefs['entries'])}개, 기본값 출처: {spec['defaults'].get('from', '없음')}, "
          f"저장소: 프로젝트 {len(store['projects'])} · 지난 답변 {len(store['past_answers'])} · 교훈 {len(store['lessons'])} · 실수 {len(store['mistakes'])} · 레퍼런스 {len(store['design_refs'])} · 템플릿 {len(store['templates'])} · 변경이력 {len(store['changes'])} · 선택 기록 {len(store['choices'])})")
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
