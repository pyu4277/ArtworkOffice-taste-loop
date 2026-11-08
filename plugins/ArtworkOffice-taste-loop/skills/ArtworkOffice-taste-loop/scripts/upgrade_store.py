#!/usr/bin/env python3
"""데이터 폴더(취향 저장소)를 엔진의 새 구조로 올린다 — 사용자 기록은 지우지 않는다.

사용법:
  python3 upgrade_store.py            지금 쓰는 데이터 폴더(store.py가 찾는 곳)를 올린다
  python3 upgrade_store.py --check    올려야 하는지만 알려 준다(종료 코드 1 = 올려야 함)
  python3 upgrade_store.py --to <폴더>  그 폴더를 올린다

버전 기록(dimensions.json · questions.json 의 "version"):
  1 → 2 (2026-11-07, 사용자 요청)
    dimensions.json
      - 목차 S1 「자료 종류」 = 파일 형식 · PDF 변환본(HTML일 때) · 콘텐츠 형태 · 활용 목적. 모두 여러 개 선택
        · 파일 형식(새 질문 file_format): HTML · PPT(X) · DOC(X) · HWP(X) · Excel 기본 + MP4 · 음성 파일 · 기타
          여러 개 = 같은 내용을 확장자만 달리 동시에 만든다
        · PDF 변환본(새 질문 pdf_export): HTML을 골랐을 때만. HTML은 PDF 변환을 항상 지원, 다른 형식은 사용자가 직접
        · 콘텐츠 형태(옛 「자료 종류」 material_type), 활용 목적(옛 「목적·용도」 purpose): 선택지를 묶음 제목(group)으로 정리
      - 새 목차 SF 「화면·지면 규격」 = 방향(orientation) → 크기·비율(옛 format, 값을 새로 정리). 고른 파일 형식·방향에 맞는 크기만 보인다
      - 새 목차 SH 「HTML 화면 구성」(파일 형식에 HTML이 있을 때만) = 넘겨 보는 방식 → 화면 틀 → 목차(메뉴) 모양 → 넣을 기능
      - 목차 S4 「분야·언어·형식」 → 「분야·언어」(크기·비율은 SF로)
      - 전체 길이·분량: 고른 파일 형식·콘텐츠 형태에 맞는 단위만 보인다 / 생성 크레딧 한도: 생성을 허용했을 때만
    questions.json
      - P2.4.theme(바탕색): 콘텐츠 형태가 화면용이거나 파일 형식이 HTML이면 묻는다
      - P2.4.layout 질문 글 「화면 배치는?」 → 「장면 안 배치는?」(HTML 화면 틀 질문과 구분)
      - P4.1.method_slides·method_doc: 고른 파일 형식에 맞는 방법만 보인다
    knowledge/projects/*.json: 옛 format 값에서 file_format · orientation · format 을 채운다
  id 는 그대로 두므로(콘텐츠 형태 material_type 등) 취향 항목의 범위(scope)·질문 조건은 그대로 맞는다.
build_interview.py · check_store.py · structure_edits.py 는 옛 구조를 읽을 때 메모리에서 올려 쓴다(파일은 안 바꿈).
"""
import copy
import json
import pathlib
import sys

sys.dont_write_bytecode = True  # 설치 폴더(플러그인 캐시)에 __pycache__ 를 만들지 않는다
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

LATEST = 2
INF = '추론'
TODAY_SRC = '사용자 2026-11-07'
ALL_VISUAL = ['html', 'pptx', 'docx', 'hwpx', 'xlsx', 'mp4', 'other']
VIDEO = ['video_explainer', 'video_promo', 'video_tutorial', 'video_lecture']
DOCS = ['textbook', 'teacher_guide', 'workbook', 'worksheet', 'quiz', 'handout', 'report_summary', 'report_result', 'proposal', 'poster', 'script']

FILE_FORMAT = {
    'id': 'file_format', 'name': '파일 형식', 'type': 'multi',
    'desc': '만들 파일의 형식. 여러 개를 고르면 같은 내용을 확장자만 달리 동시에 만든다. HTML은 언제든 PDF로도 바꿀 수 있다(아래 「PDF 변환본」).',
    'source': f'{TODAY_SRC}(HTML·PPT(X)·DOC(X)·HWP(X)·Excel 기본 탑재)',
    'values': [
        {'id': 'html', 'label': 'HTML (웹·단일 파일)'},
        {'id': 'pptx', 'label': 'PPT(X) (파워포인트)'},
        {'id': 'docx', 'label': 'DOC(X) (워드)'},
        {'id': 'hwpx', 'label': 'HWP(X) (한글)'},
        {'id': 'xlsx', 'label': 'Excel (XLSX)'},
        {'id': 'mp4', 'label': 'MP4 (영상)', 'source': '기존 프로젝트 산출물(전시 영상)'},
        {'id': 'audio', 'label': '음성 파일 (MP3·WAV)', 'source': '추론(콘텐츠 형태 「음성」에 맞춤)'},
        {'id': 'other', 'label': '기타 (직접 입력)', 'free': True},
    ],
}
PDF_EXPORT = {
    'id': 'pdf_export', 'name': 'PDF 변환본 (HTML)', 'type': 'single', 'when': {'file_format': ['html']},
    'desc': 'HTML 자료는 언제나 PDF로 바꿀 수 있다(장면마다 한 쪽, 다 그려진 모습 + 자막). 이번에 PDF도 함께 만들지 고른다. 다른 형식은 그 프로그램에서 직접 PDF로 저장한다.',
    'source': f'{TODAY_SRC}(HTML만 PDF 변환을 항상 지원, 나머지는 사용자가 프로그램에서 직접 변환)',
    'values': [
        {'id': 'with', 'label': '이번에 PDF 변환본도 함께 만든다'},
        {'id': 'later', 'label': '필요할 때 변환한다 (바꿀 수 있게만 만든다)'},
    ],
}
MATERIAL_GROUP = {'slides': '발표', **{k: '영상' for k in VIDEO},
                  **{k: '교재·학습지' for k in ('textbook', 'teacher_guide', 'workbook', 'worksheet', 'quiz', 'handout')},
                  **{k: '보고·기획 문서' for k in ('report_summary', 'report_result', 'proposal')},
                  **{k: '그 밖의 형태' for k in ('poster', 'script', 'audio', 'interactive', 'other')}}
PURPOSE_ORDER = [('concept', '수업·학습'), ('lab', '수업·학습'), ('review', '수업·학습'), ('exam', '수업·학습'), ('selfstudy', '수업·학습'), ('teacher', '수업·학습'),
                 ('judged', '평가·보고'), ('report', '평가·보고'), ('persuade', '평가·보고'),
                 ('exhibit', '홍보·안내'), ('notice', '홍보·안내'), ('other', '기타')]
ORIENTATION = {
    'id': 'orientation', 'name': '방향', 'type': 'multi', 'when': {'file_format': ALL_VISUAL},
    'desc': '가로로 만들지 세로로 만들지. 파일 형식이 여러 개면 형식마다 다를 수 있어 여러 개 고를 수 있다(예: HTML 가로 + 한글 문서 세로).',
    'source': TODAY_SRC,
    'values': [
        {'id': 'landscape', 'label': '가로'},
        {'id': 'portrait', 'label': '세로'},
        {'id': 'responsive', 'label': '화면에 맞춤 (반응형 웹)', 'when': {'file_format': ['html']}, 'source': INF},
    ],
}
SIZE_VALUES = [
    {'id': 'w169', 'label': '16:9 와이드 (1920×1080)', 'when': {'orientation': ['landscape'], 'file_format': ['html', 'pptx', 'mp4']}, 'source': '기존 프로젝트(발표자료 HTML·영상)'},
    {'id': 'w43', 'label': '4:3 (표준 슬라이드)', 'when': {'orientation': ['landscape'], 'file_format': ['html', 'pptx']}, 'source': INF},
    {'id': 'v916', 'label': '9:16 세로 (1080×1920)', 'when': {'orientation': ['portrait'], 'file_format': ['html', 'mp4']}, 'source': '기존 프로젝트(전시 세로 영상)'},
    {'id': 'a4p', 'label': 'A4 세로 (210×297mm)', 'when': {'orientation': ['portrait'], 'file_format': ['docx', 'hwpx', 'xlsx', 'pptx']}, 'source': INF},
    {'id': 'a4l', 'label': 'A4 가로 (297×210mm)', 'when': {'orientation': ['landscape'], 'file_format': ['docx', 'hwpx', 'xlsx', 'pptx']}, 'source': INF},
    {'id': 'a3', 'label': 'A3 (포스터·판넬)', 'when': {'file_format': ['pptx', 'docx', 'hwpx']}, 'source': '추론(옛 「인쇄 (A4·A3)」에서 나눔)'},
    {'id': 'fluid', 'label': '창 크기에 맞춤 (반응형)', 'when': {'orientation': ['responsive'], 'file_format': ['html']}, 'source': INF},
    {'id': 'mobile', 'label': '휴대폰 폭 우선 (세로로 내려 읽기)', 'when': {'orientation': ['portrait', 'responsive'], 'file_format': ['html']}, 'source': INF},
    {'id': 'other', 'label': '기타 (직접 입력)', 'free': True},
]
SH_DIMS = [
    {'id': 'view_mode', 'name': '넘겨 보는 방식', 'type': 'single',
     'desc': '내용을 어떤 흐름으로 보게 할지. 화면 틀·목차 모양은 이 답에 따라 묻는다.',
     'source': f'{TODAY_SRC}(한 페이지 스크롤 / 메뉴·사이드바가 있는 구성), 나머지 추론',
     'values': [
         {'id': 'scenes', 'label': '장면 자동 재생 (영상처럼 흐름 · 재생/이전/다음)', 'source': '기존 발표 형식'},
         {'id': 'slide', 'label': '한 장씩 넘김 (클릭·화살표)', 'source': INF},
         {'id': 'scroll', 'label': '한 페이지 스크롤 (위에서 아래로 읽기)'},
         {'id': 'snap', 'label': '한 화면씩 끊어 내리기', 'source': INF},
         {'id': 'app', 'label': '메뉴로 여러 화면 오가기 (앱형)'},
         {'id': 'dashboard', 'label': '한 화면에 카드 모음 (대시보드)', 'source': INF},
         {'id': 'other', 'label': '기타 (직접 입력)', 'free': True},
     ]},
    {'id': 'frame', 'name': '화면 틀', 'type': 'multi', 'when': {'view_mode': ['slide', 'scroll', 'snap', 'app', 'dashboard', 'other']},
     'desc': '본문 둘레에 고정해 둘 요소. 여러 개 고를 수 있다. 장면 자동 재생은 틀(재생 막대·자막)이 정해져 있어 묻지 않는다.',
     'source': f'{TODAY_SRC}(메뉴바·사이드바 왼쪽/오른쪽·리본메뉴), 나머지 추론',
     'values': [
         {'id': 'none', 'label': '틀 없음 (본문만)', 'source': INF},
         {'id': 'top', 'label': '위쪽 메뉴 줄'},
         {'id': 'ribbon', 'label': '리본 (도구 단추 모음)'},
         {'id': 'left', 'label': '왼쪽 사이드바'},
         {'id': 'right', 'label': '오른쪽 사이드바'},
         {'id': 'bottom', 'label': '아래 조작 막대 (이전·다음)', 'source': INF},
         {'id': 'other', 'label': '기타 (직접 입력)', 'free': True},
     ]},
    {'id': 'nav', 'name': '목차(메뉴) 모양', 'type': 'single', 'when': [{'frame': ['top', 'ribbon', 'left', 'right']}, {'view_mode': ['app']}],
     'desc': '목차·메뉴를 어떤 모양으로 보여 줄지. 메뉴가 없는 구성이면 묻지 않는다.',
     'source': f'{TODAY_SRC}(트리·목록·나열), 나머지 추론',
     'values': [
         {'id': 'tree', 'label': '접고 펴는 트리 (큰 묶음 → 작은 항목)'},
         {'id': 'list', 'label': '목록 (차례대로 한 줄씩)'},
         {'id': 'tabs', 'label': '탭 (가로로 늘어놓은 단추)'},
         {'id': 'steps', 'label': '단계 표시 (1 → 2 → 3)', 'source': INF},
         {'id': 'floating', 'label': '필요할 때 여는 목차 (떠 있는 단추)', 'source': INF},
         {'id': 'other', 'label': '기타 (직접 입력)', 'free': True},
     ]},
    {'id': 'html_features', 'name': '넣을 기능', 'type': 'multi',
     'desc': '화면에 더 넣을 기능. 장면 자동 재생은 재생·이전/다음·진행 막대·자막·키보드 조작이 기본으로 들어간다. 퀴즈 같은 교육 장치는 2부 P4.4에서 고른다.',
     'source': f'{TODAY_SRC}(에셋 등등 — 「등등」 규칙으로 추론해 채움)',
     'values': [
         {'id': 'progress', 'label': '진행 막대', 'group': '위치 알기', 'when': {'view_mode': ['slide', 'scroll', 'snap', 'app', 'dashboard', 'other']}, 'source': '기존 발표·인터뷰 페이지'},
         {'id': 'pagenum', 'label': '쪽(장면) 번호', 'group': '위치 알기', 'source': INF},
         {'id': 'toc_jump', 'label': '목차로 바로 가기', 'group': '위치 알기', 'source': INF},
         {'id': 'search', 'label': '검색', 'group': '읽기 돕기', 'source': '기존 인터뷰 페이지'},
         {'id': 'fold', 'label': '접기·펼치기', 'group': '읽기 돕기', 'source': '기존 인터뷰 페이지'},
         {'id': 'tooltip', 'label': '용어 풀이 말풍선', 'group': '읽기 돕기', 'source': INF},
         {'id': 'fontsize', 'label': '글자 크기 조절', 'group': '읽기 돕기', 'source': INF},
         {'id': 'theme_toggle', 'label': '밝게·어둡게 바꾸기 단추', 'group': '읽기 돕기', 'source': INF},
         {'id': 'timer', 'label': '타이머', 'group': '발표 돕기', 'source': INF},
         {'id': 'pen', 'label': '판서 펜', 'group': '발표 돕기', 'source': INF},
         {'id': 'fullscreen', 'label': '전체 화면 단추', 'group': '발표 돕기', 'source': INF},
         {'id': 'print_btn', 'label': '인쇄·PDF 저장 단추', 'group': '저장·공유', 'source': INF},
         {'id': 'none', 'label': '더 넣지 않음', 'group': '저장·공유'},
         {'id': 'other', 'label': '기타 (직접 입력)', 'free': True, 'group': '저장·공유'},
     ]},
]
LENGTH_WHEN = {
    'v': [{'file_format': ['mp4', 'audio']}, {'material_type': VIDEO + ['audio']}],
    't': [{'material_type': ['slides']}, {'file_format': ['pptx']}, {'purpose': ['judged']}],
    'doc': [{'file_format': ['docx', 'hwpx', 'xlsx']}, {'material_type': DOCS}],
}
# 옛 format 값 → (file_format, orientation, format)
OLD_FORMAT = {'html169': ('html', 'landscape', 'w169'), 'mp4_169': ('mp4', 'landscape', 'w169'), 'mp4_916': ('mp4', 'portrait', 'v916'),
              'pdf': (None, None, None), 'hwpx': ('hwpx', None, None), 'docx': ('docx', None, None), 'pptx': ('pptx', None, None),
              'audio_file': ('audio', None, None), 'print_a4': (None, None, None)}
NEW_SIZE_IDS = {v['id'] for v in SIZE_VALUES}


def _by(lst):
    return {x['id']: x for x in lst}


def migrate_dims(dims):
    """dimensions.json 내용을 최신 구조로. 바뀌었으면 (새 내용, True)."""
    d = copy.deepcopy(dims)
    if int(d.get('version', 1)) >= LATEST:
        return d, False
    D = d.setdefault('dimensions', [])
    by = _by(D)
    out = []
    for x in D:
        i = x['id']
        if i == 'material_type':
            if 'file_format' not in by:
                out.append(copy.deepcopy(FILE_FORMAT))
            if 'pdf_export' not in by:
                out.append(copy.deepcopy(PDF_EXPORT))
            x['name'] = '콘텐츠 형태'
            x['type'] = 'multi'
            x['desc'] = '무엇을 담은 결과물인가. 여러 개를 고를 수 있다(예: 발표자료 + 요약 카드).'
            for v in x.get('values', []):
                if v['id'] == 'slides' and '모션그래픽 HTML' in v.get('label', ''):
                    v['label'] = '발표자료 (강의·발표용)'
                if v['id'] in MATERIAL_GROUP:
                    v['group'] = MATERIAL_GROUP[v['id']]
            order = {k: n for n, k in enumerate(MATERIAL_GROUP)}
            x['values'].sort(key=lambda v: order.get(v['id'], len(order)))
        elif i == 'purpose':
            x['name'] = '활용 목적'
            vb = _by(x.get('values', []))
            vals = []
            for vid, g in PURPOSE_ORDER:
                if vid in vb:
                    vb[vid]['group'] = g
                    vals.append(vb.pop(vid))
            x['values'] = vals + list(vb.values())
        elif i == 'format':
            if 'orientation' not in by:
                out.append(copy.deepcopy(ORIENTATION))
            x['name'] = '크기·비율'
            x['type'] = 'multi'
            x['when'] = {'file_format': ALL_VISUAL}
            x['desc'] = '고른 파일 형식과 방향에 맞는 크기만 보인다. 형식이 여러 개면 형식마다 하나씩 고른다.'
            x['source'] = f'{TODAY_SRC}(가로·세로·크기), 값은 기존 프로젝트 + 추론'
            x['values'] = copy.deepcopy(SIZE_VALUES)
        elif i == 'length':
            for v in x.get('values', []):
                k = v['id'].split('_')[0]
                if k in LENGTH_WHEN:
                    v['when'] = copy.deepcopy(LENGTH_WHEN[k])
                if k == 'v' and v.get('label', '').startswith('영상 '):
                    v['label'] = '영상·음성 ' + v['label'][3:]
                    v['group'] = '영상·음성'
        elif i == 'credits':
            x['when'] = {'sources': ['gen_full', 'gen_staging']}
        elif i == 'pdf_export' and x.get('ask_when'):
            x.pop('ask_when', None); x.pop('ask_strict', None); x['when'] = {'file_format': ['html']}
        out.append(x)
    for sd in SH_DIMS:
        if sd['id'] not in by:
            out.append(copy.deepcopy(sd))
    d['dimensions'] = out
    scr = d.setdefault('screens', [])
    for s in scr:
        dd = [k for k in s.get('dimensions', []) if k not in ('file_format', 'pdf_export', 'orientation', 'format') and k not in [x['id'] for x in SH_DIMS]]
        if s.get('id') == 'S1':
            s['title'] = '자료 종류'
            rest = [k for k in dd if k not in ('material_type', 'purpose')]
            s['dimensions'] = ['file_format', 'pdf_export', 'material_type', 'purpose'] + rest
        else:
            s['dimensions'] = dd
        if s.get('id') == 'S4' and s.get('title') == '분야·언어·형식':
            s['title'] = '분야·언어'
    ids = [s['id'] for s in scr]
    pos = ids.index('S1') + 1 if 'S1' in ids else 0
    if 'SF' not in ids:
        scr.insert(pos, {'id': 'SF', 'title': '화면·지면 규격', 'dimensions': ['orientation', 'format']})
    if 'SH' not in ids:
        scr.insert(pos + 1, {'id': 'SH', 'title': 'HTML 화면 구성', 'when': {'file_format': ['html']}, 'dimensions': [x['id'] for x in SH_DIMS]})
    d['version'] = LATEST
    return d, True


def migrate_qs(qs):
    """questions.json 내용을 최신 구조로. 바뀌었으면 (새 내용, True)."""
    q = copy.deepcopy(qs)
    if int(q.get('version', 1)) >= LATEST:
        return q, False
    A = _by(q.get('aspects', []))
    a = A.get('P2.4.theme')
    if a and isinstance(a.get('applies_when'), dict) and 'file_format' not in a['applies_when']:
        a['applies_when'] = [a['applies_when'], {'file_format': ['html']}]
    a = A.get('P2.4.layout')
    if a and a.get('text') == '화면 배치는?':
        a['text'] = '장면 안 배치는?'
    METHOD = {'P4.1.method_slides': {'engine': ['html'], 'pptx': ['pptx'], 'pdf': ['html']},
              'P4.1.method_doc': {'md_office': ['docx'], 'hwpx': ['hwpx'], 'pptx': ['pptx'], 'html': ['html']}}
    for aid, m in METHOD.items():
        a = A.get(aid)
        if not a:
            continue
        for o in a.get('options', []):
            if o['id'] in m and not o.get('when'):
                o['when'] = {'file_format': m[o['id']]}
    q['version'] = LATEST
    return q, True


def _old_format(dv):
    """옛 format 한 값 → 새 답 조각."""
    f = dv.get('format')
    if isinstance(f, list) or f is None or f in NEW_SIZE_IDS:
        return dv, False
    if f not in OLD_FORMAT:
        return dv, False
    ff, ori, size = OLD_FORMAT[f]
    dv = dict(dv)
    if ff and 'file_format' not in dv:
        dv['file_format'] = [ff]
    if ori and 'orientation' not in dv:
        dv['orientation'] = [ori]
    if f == 'html169' and 'view_mode' not in dv:
        dv['view_mode'] = 'scenes'  # 옛 「가로 16:9 단일 HTML (모션그래픽)」 = 장면 자동 재생 발표 형식
    if size:
        dv['format'] = [size]
    else:
        dv.pop('format', None)
    return dv, True


def migrate_project(rec):
    """프로젝트 기록: 옛 format 값에서 file_format · orientation · format 을 채운다."""
    r = copy.deepcopy(rec)
    dv, ch = _old_format(r.get('dimensions') or {})
    if ch:
        r['dimensions'] = dv
    return r, ch


def migrate_answers_dims(dv):
    """답변·기본값의 차원 값(메모리에서만)."""
    return _old_format(dict(dv or {}))[0]


def upgrade(store, check_only=False):
    store = pathlib.Path(store)
    changed = []
    for name, fn in (('dimensions.json', migrate_dims), ('questions.json', migrate_qs)):
        p = store / name
        if p.exists():
            new, ch = fn(json.loads(p.read_text(encoding='utf-8')))
            if ch:
                changed.append(name)
                if not check_only:  # 줄바꿈 LF 고정: Windows 의 write_text 는 CRLF 로 쓴다(실수 기록 E22)
                    p.write_bytes((json.dumps(new, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
    pj = store / 'knowledge' / 'projects'
    for f in sorted(pj.glob('*.json')) if pj.exists() else []:
        new, ch = migrate_project(json.loads(f.read_text(encoding='utf-8')))
        if ch:
            changed.append(f'knowledge/projects/{f.name}')
            if not check_only:  # 줄바꿈 LF 고정(E22)
                f.write_bytes((json.dumps(new, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
    return changed


def main(argv):
    import store as S
    if '--to' in argv:
        target = pathlib.Path(argv[argv.index('--to') + 1]).expanduser().resolve()
    else:
        target = S.STORE
        if not S.STORE_WRITABLE:
            print(f'데이터 폴더가 없습니다(starter를 쓰는 중). 먼저 init_store.py 로 만드세요: {S.STORE}')
            return 0
    check = '--check' in argv
    ch = upgrade(target, check_only=check)
    if check:
        print(f'올려야 할 파일 {len(ch)}개' + (': ' + ', '.join(ch) if ch else ' — 최신입니다'))
        return 1 if ch else 0
    print(f'데이터 폴더: {target}')
    print(f'바꾼 파일 {len(ch)}개' + (': ' + ', '.join(ch) if ch else ' — 이미 최신입니다'))
    if ch:
        print('다음: python3 check_store.py  (검증과 요약 다시 만들기) → 인터뷰 페이지를 다시 만든다(build_interview.py)')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
