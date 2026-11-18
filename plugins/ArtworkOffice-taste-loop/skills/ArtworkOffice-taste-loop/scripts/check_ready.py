#!/usr/bin/env python3
"""준비 완료 점검표 검사 — 받은 자료를 다 읽고 정리 · 분석한 뒤에 만들기 시작한다 (엔진 1.7.0).

받은 자료(첨부 파일 · 레퍼런스 · 위 문서 · 양식)가 있는 일은 이 점검표가 통과하고 사용자가 확인한 뒤에 만든다.
「빠르게 · 간단하게 · 마감 임박」 이어도 건너뛰지 않는다 — 시간이 모자라면 준비를 줄이지 말고 결과물의 범위를 줄일지 묻는다
(scope_cut 에 사용자 답을 적는다). 빠른 초안 → 고치기 순서는 수정 · 토큰 · 시간을 더 쓴다.

점검표: <작업폴더>/materials/00_준비점검표.json (JSON 객체 하나)
  {"version": 1,
   "materials": [                                  받은 자료 전부 — 하나도 빼지 않는다
     {"path": "<파일 · 폴더 · 주소>",
      "kind": "reference|upstream|form|source|other",   reference = 같은 종류의 지난 결과물 · upstream = 소주제 · 단계 · 이름을 이미 정한 위 문서(계획서 등)
                                                        form = 채울 양식 · source = 원자료 · other = 그 밖
      "read_by": "leader",                         일을 이끄는 에이전트(리더)가 직접 읽음. 보조 에이전트 요약으로 대신하지 않는다
      "read": "all",                               끝까지 읽음(일부만 읽었으면 통과하지 않는다 — 다 읽거나, 범위를 줄일지 사용자에게 묻는다)
      "range": "<읽은 범위 — 1~14쪽 전부 · 시트 3개 전부 …>",
      "tool": "<그 자료 종류의 전문 도구 — 문서 변환기 · 웹사이트 분석 도구 · 영상 분석 도구 …>",
      "found": "<알게 된 것 한 줄>"}],              (found 는 선택)
   "keep":   [{"item": "<그대로 쓸 것 — 이름 · 직위 · 소속 · 제목 · 칸 이름 · 소주제 · 본문 부호 · 표 꼴 · 쪽 배치>", "value": "<레퍼런스의 값>", "from": "<파일:쪽>"}],
   "change": [{"item": "<바꿀 곳>", "to": "<새 값>", "why": "<근거 — 무엇이 달라져서>", "from": "<근거 파일:쪽>"}],
   "subtopics": [{"text": "<위 문서에 정해진 소주제 · 단계 · 이름 — 글자 그대로>", "from": "<파일:쪽>"}],
   "subtopics_none": "<위 문서에 정해진 소주제가 없을 때 그 까닭>",   (subtopics 를 비울 때만)
   "scope_cut": "<시간이 모자라 범위를 줄이기로 했으면 사용자 답 원문>",  (선택)
   "confirmed": {"by": "<확인한 사람>", "at": "<YYYY-MM-DD>", "said": "<확인한 말 원문>"}}
  「<…>」 꼴 그대로 둔 칸은 빈 칸으로 본다(양식을 채우지 않고 통과하지 못하게).

언제 필요한가(gate): 아래 가운데 하나라도 있으면 점검표가 있어야 하고, 점검표가 있으면(필요 없어도) 통과해야 한다.
  - 인터뷰 답의 references(「레퍼런스 먼저」) · 「레퍼런스대로」 답 · 기본 양식(base_project) · 서랍에서 넣은 지난 프로젝트 ·
    새 메모 · 레퍼런스 카드(refs 의 project · new_ref · design_ref · template, new_refs)
  - 질문 메모 · 기타 의견(dim: · pq:) · 3부 글 답 · 검토 메모에 적은 파일 경로(드라이브 · UNC · ~/ · / · 폴더가 있는 상대 경로) · 주소
    (폴더 없이 파일 이름만 쓴 글은 결과물 이름 · 예시일 수 있어 받은 자료로 보지 않는다 — 받은 자료면 레퍼런스 칸이나 경로로 준다)
  - 인터뷰 답의 recommend.items 가운데 근거가 첨부자료(basis attached)인 칸(그 from 의 파일)
  - <작업폴더>/materials/인터뷰/00_추천.json 의 attachments (읽지 못하면 있는 것으로 본다)
  인터뷰 답 · 추천 파일에 나온 자료는 모두 점검표 materials 에 있어야 한다. 경로가 있는 자료는 전체 경로로 맞추고(상대 경로는
  작업 폴더 · 프로젝트 루트 기준, 주소는 스킴 · 호스트만 대소문자 무시), 폴더 없이 파일 이름만 적힌 것(레퍼런스 칸의
  「보고서.pdf」, 추천 근거 「공문.pdf:2」)만 파일 이름으로 맞춘다.
  인터뷰 답 파일을 주지 않으면 <작업폴더>/materials/인터뷰/*답변*.json 을 모두 읽는다.
  「레퍼런스만 먼저 보내기」 답(stage references)도 같은 검사를 받는다. answers_to_plan.py 는 그 답으로 계획을 만들지 않는다
  (스킬 3.1-0 — 레퍼런스를 분석해 점검표 · 기준표 · 채움 답을 만들고, 다시 만든 인터뷰의 제출 답으로 계획을 만든다).

사용법
  python3 check_ready.py --lecture <작업폴더> [--answers <답변.json>]... [--file <점검표.json>]
                                   통과 · 필요 없음 → 종료 0, 통과하지 못함 → 1, 잘못된 인자 → 2
  python3 check_ready.py init --lecture <작업폴더>    빈 양식을 materials/00_준비점검표.json 에 만든다(있으면 덮어쓰지 않음)
  python3 check_ready.py template                    빈 양식을 화면에 보여 준다
  python3 check_ready.py selftest
answers_to_plan.py 가 계획 문서를 만들기 전에 같은 검사(gate)를 돌리고, 통과하지 못하면 아무것도 쓰지 않고 멈춘다.
"""
import json
import os
import pathlib
import posixpath
import re
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

READY_REL = ('materials', '00_준비점검표.json')
RECO_REL = ('materials', '인터뷰', '00_추천.json')
KINDS = ('reference', 'upstream', 'form', 'source', 'other')
EXT = r'(?:pdf|pptx?|hwpx?|hml|docx?|odt|ods|odp|key|xlsx?|csv|txt|png|jpe?g|gif|webp|svg|ai|psd|mp4|mov|webm|mkv|avi|mp3|wav|html?|md|zip|json)'
END = r'(?![A-Za-z0-9/\\]|\.[A-Za-z0-9])'  # \b 는 한글 조사(「.pdf를」)를 단어로 보아 놓친다. 「a.pdf/b.docx」 · 「a.pdf.bak」 는 중간에서 끊지 않는다
HANGUL = '\uac00-\ud7a3\u3131-\u318e'
# 앞 것이 먼저 잡고, 이미 잡힌 자리와 겹치는 뒤 것은 버린다(같은 경로의 조각 · 주소 속 「s://」를 따로 세지 않게)
SEP_OK = r'(?<![^\s"\'(「『:\[])'  # 경로가 시작할 수 있는 자리(글 처음 · 띄어쓰기 · 따옴표 · 여는 괄호 · 「참고:」 뒤)
P_QUOTED = re.compile(r'"([^"\n]+?)"')                                                      # 따옴표 안 — 경로 하나일 때만
P_URL = re.compile(r'https?://[^\s"<>]+', re.I)                                            # 주소(한글 주소 포함 — 끝의 조사만 뗌)
P_DRIVE_EXT = re.compile(r'(?<![A-Za-z])[A-Za-z]:[\\/][^"\n<>|?*,」』]*?\.' + EXT + END, re.I)  # 드라이브 + 확장자(띄어쓰기는 실제로 있을 때만)
P_UNC_EXT = re.compile(SEP_OK + r'(?:\\\\|~[\\/])[^"\n<>|?*,」』]*?\.' + EXT + END, re.I)      # UNC · ~/ + 확장자(띄어쓰기는 실제로 있을 때만)
P_DRIVE_DIR = re.compile(r'(?<![A-Za-z])[A-Za-z]:[\\/][^\s"<>|?*,」』]*')                  # 드라이브 경로 · 폴더(확장자 없음)
P_UNC_DIR = re.compile(SEP_OK + r'(?:\\\\|~[\\/])[^\s"\'<>|?*,」』]+')                       # UNC · ~/ 폴더
P_POSIX = re.compile(SEP_OK + r'/[^\s"\'<>|?*,」』]+')                                        # / 로 시작하는 절대 경로 · 폴더(실제로 있을 때만)
P_REL_EXT = re.compile(SEP_OK + r'[^\s"\'<>|?*「」『』():,]+?\.' + EXT + END, re.I)             # 상대 경로 · 파일 이름(실제로 있을 때만 · 이름만이면 뺌)
P_REL_DIR = re.compile(SEP_OK + r'[^\s"\'<>|?*「」『』():,\\/]+[\\/][^\s"\'<>|?*「」『』():,]*')  # 상대 폴더(실제로 있을 때만)
# 앞 것이 먼저 잡고, 이미 잡힌 자리와 겹치는 뒤 것은 버린다(같은 경로의 조각 · 주소 속 「s://」를 따로 세지 않게)
FIND = [P_QUOTED, P_URL, P_DRIVE_EXT, P_UNC_EXT, P_DRIVE_DIR, P_UNC_DIR, P_POSIX, P_REL_EXT, P_REL_DIR]
PARTICLE = re.compile(r'(?:에서|으로|을|를|이|가|은|는|에|의|로|와|과|도)$')

VALUE_FIELDS = ('value', 'to', 'text')  # 본문 부호 · 표 꼴 같은 값이 들어가는 칸 — 자리표시 판정을 하지 않는다
PLACEHOLDERS = {'todo', 'tbd', 'x', 'xx', 'n/a', 'na', 'none', '?', '없음', '미정', '추후', '나중에'}
TEMPLATE = {
    'version': 1,
    'materials': [{'path': '<받은 자료 경로 · 주소>', 'kind': '<reference|upstream|form|source|other>', 'read_by': '<leader>',
                   'read': '<all>', 'range': '<읽은 범위>', 'tool': '<전문 도구>', 'found': '<알게 된 것 한 줄>'}],
    'keep': [{'item': '<그대로 쓸 것>', 'value': '<레퍼런스의 값>', 'from': '<파일:쪽>'}],
    'change': [],
    'subtopics': [{'text': '<위 문서에 정해진 소주제 — 글자 그대로>', 'from': '<파일:쪽>'}],
    'subtopics_none': '',
    'scope_cut': '',
    'confirmed': {'by': '<확인한 사람>', 'at': '<YYYY-MM-DD>', 'said': '<확인한 말 원문>'},
}


def filled(v):
    """빈 칸이 아닌 글인가. 양식의 「<…>」 꼴을 그대로 둔 것도 빈 칸이다."""
    if not isinstance(v, str):
        return False
    s = v.strip()
    if not s or re.fullmatch(r'[\W_]+', s) or s.lower() in PLACEHOLDERS:
        return False
    return not (s[0] in '<([{' and (s[-1] in '>)]}' or s[0] == '<'))


def is_local_abs(p):
    s = str(p or '').strip()
    return bool(re.match(r'^(?:[A-Za-z]:[\\/]|\\\\|~[\\/]|/)', s))


TEMPLATE_TEXT = None


def given(v):
    """값 칸(그대로 쓸 값 · 새 값 · 소주제 글자) — 본문 부호(□ ○ ※ -) · 「(가)」 · 「<표 1>」 · 「없음」도 값이다. 양식 글 그대로만 빈 칸."""
    global TEMPLATE_TEXT
    if TEMPLATE_TEXT is None:
        TEMPLATE_TEXT = {x for row in TEMPLATE.values() if isinstance(row, list) for r in row for x in r.values()} | set(TEMPLATE['confirmed'].values())
    return isinstance(v, str) and bool(v.strip()) and v.strip() not in TEMPLATE_TEXT


def find_paths(text, bases=()):
    """글에 적힌 받은 자료(파일 · 폴더 경로 · 주소).
    - 폴더 없이 파일 이름만 쓴 것(「강의_01_주제.html 로 저장」 같은 결과물 이름 · 예시)은 받은 자료로 보지 않는다.
    - 상대 경로는 bases(작업 폴더 · 프로젝트 루트) 아래에 실제로 있을 때만 받은 자료다(「slides/…html 로 저장」 같은 만들 파일 · 잡음은 뺌).
    - 절대 경로 끝에 붙은 조사(「폴더를」)는, 붙은 채로는 없고 떼면 있을 때만 뗀다."""
    t, spans, out = str(text or ''), [], []
    for rx in FIND:
        for m in rx.finditer(t):
            g = 1 if rx.groups else 0
            a, b = m.span(g)
            if any(a < y and x < b for x, y in spans):
                continue
            w = m.group(g).strip().lstrip('([「『').rstrip('.,)」』')  # 여는 괄호 · 닫는 괄호(「[scripts/x]」 · 「(D:/자료)」)
            exists = lambda x: os.path.exists(os.path.expanduser(x)) or any((pathlib.Path(b) / x).exists() for b in bases)  # noqa: E731
            spaced = bool(re.search(r'\s', w))
            if rx is P_QUOTED and not (re.match(r'(?i)https?://\S+$', w) or bare(w) or exists(w)
                                      or (is_local_abs(w) and (not spaced or not re.search(r'\.' + EXT + r'\s', w, re.I)))):
                continue  # 따옴표 안이 경로 하나가 아니면(경로 뒤에 문장이 이어짐 등) 글이다 — 자리를 차지하지 않아 안의 경로를 뒤 패턴이 찾는다
            if rx is P_DRIVE_DIR and re.fullmatch(r'[A-Za-z]:[\\/][^\\/]?', w):
                continue  # 「비율 W:/H」 · 「Q:/A 형식」 — 한 글자뿐인 드라이브 글은 경로가 아님(R04 · R05)
            if rx in (P_DRIVE_EXT, P_UNC_EXT) and spaced and not exists(w):
                continue  # 따옴표 없는 띄어쓰기 드라이브 경로는 실제로 있을 때만 — 아니면 띄어쓰기에서 끊는 뒤 패턴이 찾는다
            if rx in (P_POSIX, P_REL_DIR, P_REL_EXT):
                hit = next((v for v in tails(w) if exists(v)), None)  # 「scripts/x를」 · 「[scripts/x]」 — 뗀 꼴이 있으면 그것
                if hit is None and rx is not P_REL_EXT:
                    continue  # / 로 시작하는 글(「/ 표시」 등) · 없는 상대 폴더는 받은 자료가 아님
                w = hit or w
            spans.append((a, b))
            if re.fullmatch(r'[/\\~.]+|[A-Za-z]:[/\\]?', w or ''):
                continue  # 「(/) 대신」 · 「"/" 로 통일」 같은 기호 이야기(R04)
            if not w or bare(w) or w in out:
                continue
            if re.match(r'(?i)https?://', w):
                out.append(w); continue  # 주소는 그대로(「…/고양이」 를 자르지 않는다) — 끝 조사는 맞출 때 견준다(loose)
            if is_local_abs(w):
                cut_w = PARTICLE.sub('', w)
                if cut_w != w and not os.path.exists(os.path.expanduser(w)) and os.path.exists(os.path.expanduser(cut_w)):
                    w = cut_w
                if (OUTPUT_EN.search(t[max(0, a - 120):a]) or OUTPUT_KO.search(t[b:b + 15].lstrip('"\'」』)'))):
                    continue  # 「결과는 D:/exports/x.html 에 저장」 — 출력 말 옆의 경로는 이미 있는 파일이어도 받은 자료가 아니라 내보낼 자리(R06 · R08)
                out.append(w); continue
            if any((pathlib.Path(b) / w).exists() for b in bases):
                out.append(w)
    return out


OUTPUT_EN = re.compile(r"(?i)\b(?:save|export|output|write)\b[^.;,]*\b(?:to|into|in|as|at)\s*[\x22\x27「『(]?\s*$")  # 영어는 경로 앞(앞 문장 전체 · 여는 따옴표 허용 — R07)(「save the result to D:/…」)
OUTPUT_KO = re.compile(r"^\S{0,3}\s*(?:에|로|으로)?\s*(?:저장|내보내|내보냄|출력)")  # 한국어는 경로 뒤(「D:/…/x.hwpx 로 저장」)


def tails(w):
    """글 속 경로 뒤에 붙은 조사 · 닫는 괄호를 하나씩 뗀 꼴들(원래 꼴 먼저). 「「D:/자료」를」 → D:/자료」 → D:/자료."""
    c = w.rstrip(')]」』')
    cands = [w, c, PARTICLE.sub('', w).rstrip(')]」』'), PARTICLE.sub('', c).rstrip(')]」』')]  # 조사는 한 번만(「도로」 → 「도」 → 뿌리까지 떼지 않게 — R04)
    # 원래 꼴(「scripts/」 · 「https://…/ref/」)은 늘 남기고, 떼어 낸 꼴만 「/ 로 끝남 · 뿌리」(「D:/자료/도」 → 「D:/자료/」)를 버린다(R05)
    return [w] + [x for x in dict.fromkeys(cands[1:]) if x and x != w and not re.search(r'(?:[\\/]|^[A-Za-z]:)$', x)]


def bare(p):
    """폴더 없이 파일 이름만 적혔나(주소 아님)."""
    s = str(p or '').strip().strip('"\'')
    return bool(s) and not re.match(r'(?i)https?://', s) and '/' not in s and '\\' not in s


def keys(p, bases=()):
    """자료를 맞출 열쇠들 — 전체 경로(상대 경로는 bases 마다) · 주소(스킴 · 호스트만 소문자)."""
    s = str(p or '').strip().strip('"\'')
    if not s:
        return set()
    if s.startswith('~'):
        s = os.path.expanduser(s)
    m = re.match(r'(?i)(https?)://([^/?#]*)(.*)$', s)
    if m:
        return {'url:' + m.group(1).lower() + '://' + m.group(2).lower() + m.group(3)}
    t = s.replace('\\', '/')
    winlike = os.name == 'nt' or re.match(r'^[A-Za-z]:/', t) or '\\' in s
    absolute = bool(re.match(r'^[A-Za-z]:/', t) or t.startswith('/'))
    cands = [t] if absolute else [str(b).replace('\\', '/').rstrip('/') + '/' + t for b in bases] + [t]
    out = set()
    for c in cands:
        n = posixpath.normpath(c)
        if c.startswith('//'):
            n = '/' + n if not n.startswith('//') else n  # UNC 앞의 // 를 지키기
        out.add('path:' + (n.lower() if winlike else n))
    return out


def same_material(given, listed, bases=(), loose=False):
    """받은 자료(given)가 점검표의 자료(listed)인가. 파일 이름만 적힌 받은 자료만 파일 이름으로 맞춘다."""
    if not str(listed or '').strip() or not str(given or '').strip():
        return False
    if bare(given):
        if re.match(r'(?i)https?://', str(listed).strip().strip('"\'')):
            return False  # 로컬 파일 이름과 주소는 같은 자료가 아니다
        name = str(listed).strip().strip('"\'').replace('\\', '/').rstrip('/').rsplit('/', 1)[-1]
        return name.lower() == str(given).strip().strip('"\'').lower()
    # 글에서 찾은 자료(loose)만 끝 조사 · 닫는 괄호를 뗀 꼴도 견준다 — 레퍼런스 칸 · 첨부 목록의 경로는 글자 그대로(「…/고양이」 ≠ 「…/고양」)
    variants = tails(str(given).strip()) if loose else [str(given).strip()]
    lk = keys(listed, bases)
    return any(keys(v, bases) & lk for v in variants)


def from_file(src):
    """추천 근거 「파일:쪽」 · 「파일 2쪽」 · 「파일(2쪽)」 · 「파일, p.2」 → 파일 부분."""
    s = str(src or '').strip()
    if re.match(r'(?i)https?://', s):
        return s  # 주소의 포트 · 질의(「:8080」 · 「ids=1,2」)는 쪽 표기가 아니다
    page = r'\d+(?:\s*[-~]\s*\d+)?'
    return re.sub(r'(?:\s*:\s*(?:p\.?\s*)?' + page + r'\s*쪽?|(?:\s*,\s*|\s+|\s*(?=\())\(?\s*(?:p\.?\s*' + page + r'|' + page + r'\s*쪽)\s*\)?)\s*$', '', s, flags=re.I) or s  # 끝의 쪽 표기만(「회의 2026」 의 숫자 · 경로 · 주소 질의는 그대로)


def validate(doc):
    """점검표 → 오류 목록(빈 목록 = 통과)."""
    if not isinstance(doc, dict):
        return ['점검표는 JSON 객체여야 합니다']
    err = []
    if doc.get('version', 1) != 1:
        err.append(f'version: 1 이어야 합니다({doc.get("version")!r})')
    mats = doc.get('materials')
    if not isinstance(mats, list) or not mats:
        err.append('materials: 받은 자료가 하나도 없습니다 — 받은 자료(첨부 · 레퍼런스 · 위 문서 · 양식)를 모두 적습니다')
        mats = []
    kinds = set()
    for i, m in enumerate(mats):
        if not isinstance(m, dict):
            err.append(f'materials[{i}]: 객체여야 합니다'); continue
        name = m.get('path') if filled(m.get('path')) else f'materials[{i}]'
        if not filled(m.get('path')):
            err.append(f'materials[{i}]: 경로 · 주소(path)가 비었습니다')
        if m.get('kind') not in KINDS:
            err.append(f'{name}: 종류(kind)는 {" · ".join(KINDS)} 가운데 하나여야 합니다')
        else:
            kinds.add(m['kind'])
        if m.get('read_by') != 'leader':
            err.append(f'{name}: 리더가 직접 읽지 않았습니다(read_by = "leader") — 보조 에이전트의 요약 · 기준표로 대신하지 않습니다')
        if m.get('read') != 'all':
            err.append(f'{name}: 끝까지 읽지 않았습니다(read = "all") — 다 읽거나, 결과물의 범위를 줄일지 사용자에게 묻습니다')
        if not filled(m.get('range')):
            err.append(f'{name}: 읽은 범위(range)를 적지 않았습니다')
        if not filled(m.get('tool')):
            err.append(f'{name}: 이 자료 종류의 전문 도구(tool)를 적지 않았습니다 — 범용 방법으로 해 보다가 넘어가지 않습니다')

    def rows(key, fields):
        v = doc.get(key)
        if v is None:
            return []
        if not isinstance(v, list):
            err.append(f'{key}: 목록이어야 합니다'); return []
        for j, r in enumerate(v):
            miss = [f for f in fields if not (isinstance(r, dict) and (given if f in VALUE_FIELDS else filled)(r.get(f)))]
            if miss:
                err.append(f'{key}[{j}]: 빈 칸 {", ".join(miss)}')
        return v
    keep = rows('keep', ('item', 'value', 'from'))
    rows('change', ('item', 'to', 'why', 'from'))
    subs = rows('subtopics', ('text', 'from'))
    if 'reference' in kinds and not keep:
        err.append('keep: 레퍼런스(같은 종류의 지난 결과물)가 있는데 그대로 쓸 것 표가 비었습니다 — 이름 · 직위 · 소속 · 제목 · 칸 이름 · 소주제 · 본문 부호 · 표 꼴 · 쪽 배치를 먼저 뽑습니다')
    if 'upstream' in kinds and not subs and not filled(doc.get('subtopics_none')):
        err.append('subtopics: 위 문서(upstream)가 있는데 정해진 소주제 · 단계가 비었습니다 — 글자 그대로 옮기고 출처(from)를 답니다. 정해진 것이 없으면 subtopics_none 에 까닭')
    c = doc.get('confirmed')
    # 확인한 말(said)은 원문이라 기호 · 괄호만으로도 확인일 수 있다(「👍」 · 「(Approved, proceed)」) — 비었거나 양식 글 그대로만 빈 칸(R06)
    miss = [f for f in ('by', 'at', 'said') if not (isinstance(c, dict) and (given(c.get(f)) if f == 'said' else filled(c.get(f))))]
    if not miss and not re.fullmatch(r'\d{4}-\d{2}-\d{2}', c['at'].strip()):
        miss = ['at(YYYY-MM-DD)']
    if miss:
        err.append(f'confirmed: 사용자 확인이 없습니다(빈 칸 {", ".join(miss)}) — 점검표를 보여 주고 확인받은 뒤 그 말을 원문 그대로 적습니다')
    return err


def given_materials(lecture_dir, answers):
    """인터뷰 답(하나 또는 여럿) · 추천 파일로 받은 자료 → {why 까닭, paths 맞출 자료, ref 레퍼런스를 받았나}."""
    why, paths, loose, explicit = [], [], set(), set()
    D = lambda x: x if isinstance(x, dict) else {}  # noqa: E731  모양이 틀린 칸은 빈 것으로 읽는다(멈추지 않게)
    Ls = lambda x: x if isinstance(x, list) else []  # noqa: E731
    ref_given = False
    att_items = []
    import store as ST
    bases = (pathlib.Path(lecture_dir), ST.project_root())
    for ans in (answers if isinstance(answers, list) else [answers]):
        ans = D(ans)
        refs = [r for r in Ls(ans.get('references')) if isinstance(r, dict) and (r.get('where') or r.get('note'))]
        if refs:
            why.append(f'인터뷰 「레퍼런스 먼저」 {len(refs)}건')
            exp = [str(r['where']) for r in refs if str(r.get('where') or '').strip()]
            paths += exp
            explicit.update(x.strip() for x in exp)
            found = [w for r in refs for w in find_paths(r.get('note'), bases)]
            paths += found
            loose.update(found)
        texts = [s.get(k) for s in D(ans.get('aspects')).values() if isinstance(s, dict) for k in ('note', 'value', 'reason') if isinstance(s.get(k), str)]
        texts += [v for v in D(ans.get('opinions')).values()]
        texts += [ans.get('overall'), ans.get('notes')] + [s.get('note') for s in D(ans.get('items')).values() if isinstance(s, dict)]
        for v in list(D(ans.get('project')).values()) + list(D(ans.get('dimensions')).values()):
            texts += [x for x in (v if isinstance(v, list) else [v]) if isinstance(x, str)]
        memo = list(dict.fromkeys(w for t in texts for w in find_paths(t, bases)))
        if memo:
            why.append(f'질문 메모 · 기타 의견 · 3부 답 · 검토 메모에 적은 자료 {len(memo)}건')
            paths += memo
            loose.update(memo)
        ref_choice = any(isinstance(s, dict) and s.get('choice') == 'ref' for s in D(ans.get('aspects')).values())
        if ref_choice:
            why.append('「레퍼런스대로」 답')
        drawer = [r for rs in D(ans.get('refs')).values() for r in Ls(rs) if isinstance(r, dict) and r.get('kind') in ('project', 'new_ref', 'design_ref', 'template')]
        drawer += [dict(n, kind='new_ref') for n in Ls(ans.get('new_refs')) if isinstance(n, dict) and (n.get('url') or n.get('text'))]
        bp = D(ans.get('base_project'))
        if drawer or bp:
            why.append(f'서랍에서 넣은 지난 프로젝트 · 레퍼런스 {len(drawer) + bool(bp)}건')
            for r in drawer:
                exp = [str(r[k]) for k in ('url', 'location') if str(r.get(k) or '').strip()]
                paths += exp
                explicit.update(x.strip() for x in exp)
                found = [w for k in ('text', 'label', 'note') for w in find_paths(r.get(k), bases)]
                paths += found
                loose.update(found)
        ref_given = ref_given or bool(refs or ref_choice or drawer or bp)  # 메모의 경로는 원자료일 수 있어 대조표까지는 요구하지 않는다(자료 목록에는 있어야 함)
        att_items += [x for x in Ls(D(ans.get('recommend')).get('items')) if isinstance(x, dict) and x.get('basis') == 'attached']
    if att_items:
        why.append(f'첨부자료에서 채운 추천 {len(att_items)}칸')
        exp = [from_file(x['from']) for x in att_items if str(x.get('from') or '').strip()]
        paths += exp
        explicit.update(x.strip() for x in exp)
    unknown = []
    rf = pathlib.Path(lecture_dir).joinpath(*RECO_REL)
    att = []
    if rf.exists():
        parsed = False
        try:
            reco = json.loads(rf.read_text(encoding='utf-8-sig'))
            parsed = True
        except (ValueError, OSError):
            reco = None
            why.append(f'{RECO_REL[-1]} 을 읽지 못함 — 첨부자료가 있는지 알 수 없어 점검표를 요구합니다')
            unknown.append(f'{RECO_REL[-1]} 을 읽지 못했습니다 — 고친 뒤 다시 검사합니다(첨부자료가 있는지 알 수 없음)')
        bad_att = isinstance(reco, dict) and (not isinstance(reco.get('attachments', []), (list, type(None)))
                                               or any(not (isinstance(a, dict) and isinstance(a.get('path'), str) and a['path'].strip()) for a in Ls(reco.get('attachments'))))
        if parsed and (not isinstance(reco, dict) or bad_att or not isinstance(reco.get('listening', False), bool)):
            why.append(f'{RECO_REL[-1]} 모양이 틀림')
            unknown.append(f'{RECO_REL[-1]} 은 JSON 객체이고 attachments 는 path 가 있는 객체의 목록이어야 합니다 — 고친 뒤 다시 검사합니다')
        att = [a for a in Ls(D(reco).get('attachments')) if isinstance(a, dict) and str(a.get('path') or '').strip()]
        if D(reco).get('listening') is True:  # 사전 인터뷰 듣기 모드(1.7.0) — 사용자가 「됐어」라고 하기 전(받은 자료가 아니라 「아직 시작 전」)
            unknown.append('사전 인터뷰가 아직 듣는 중입니다(00_추천.json listening) — 사용자가 「됐어」라고 한 뒤 recommend.py listen … --done 으로 닫고 시작합니다')
        if att:
            why.append(f'00_추천.json 첨부자료 {len(att)}건')
            paths += [str(a['path']) for a in att]
            explicit.update(str(a['path']).strip() for a in att if not str(a.get('found') or '').startswith('듣기 모드 말씀'))
            loose.update(str(a['path']).strip() for a in att if str(a.get('found') or '').startswith('듣기 모드 말씀'))  # 말씀 속 「…폴더를」 (R05)
    if any(not str(x.get('from') or '').strip() for x in att_items) and not att:
        unknown.append('첨부자료에서 채운 추천 칸의 근거 파일(from)을 알 수 없습니다 — 00_추천.json 의 attachments 에 받은 자료를 적습니다')
    return {'why': why, 'paths': list(dict.fromkeys(p.strip() for p in paths if p.strip())), 'loose': {x.strip() for x in loose} - explicit, 'ref': ref_given, 'unknown': unknown}


def gate(lecture_dir, ans=None, ready=None):
    """(통과, 알림 목록, 점검표 또는 None). 받은 자료가 없고 점검표도 없으면 통과. ans 는 인터뷰 답 하나 또는 목록."""
    lecture_dir = pathlib.Path(lecture_dir)
    rp = pathlib.Path(ready) if ready else lecture_dir.joinpath(*READY_REL)
    g = given_materials(lecture_dir, ans)
    if not rp.exists():
        if g['unknown'] and not g['why']:
            return False, ['아직 시작할 수 없습니다:'] + ['  - ' + u for u in g['unknown']], None
        if g['why']:
            return False, [f'준비 완료 점검표가 없습니다: {rp}'] + ['  - ' + u for u in g['unknown']] + [
                           '받은 자료: ' + ' · '.join(g['why']),
                           '받은 자료를 리더가 직접 끝까지 읽고 → 레퍼런스 대조표(그대로 쓸 것 · 바꿀 곳과 근거) · 위 문서의 소주제를 정리해 점검표를 만들고 → 사용자 확인을 받은 뒤 다시 실행합니다.',
                           f'빈 양식: python3 {HERE / "check_ready.py"} init --lecture <작업폴더>  (형식은 이 스크립트 머리말 · 스킬 3.0의 0-1)',
                           '「빠르게 · 간단하게 · 마감 임박」도 이 준비를 줄이지 않습니다 — 시간이 모자라면 결과물의 범위를 줄일지 사용자에게 묻습니다.'], None
        return True, [], None
    try:
        doc = json.loads(rp.read_text(encoding='utf-8-sig'))
    except (ValueError, OSError) as e:
        return False, [f'준비 완료 점검표를 읽지 못했습니다: {rp} ({e})'], None
    err = validate(doc) + g['unknown']
    mats = doc.get('materials') if isinstance(doc, dict) else None
    listed = [m.get('path') for m in mats if isinstance(m, dict)] if isinstance(mats, list) else []
    import store as ST
    bases = (lecture_dir, ST.project_root())
    for p in g['paths']:
        if not any(same_material(p, q, bases, loose=p in g['loose']) for q in listed):
            err.append(f'materials: 받은 자료가 점검표에 없습니다 — {p}')
    if g['ref'] and isinstance(doc, dict) and not doc.get('keep') and not any(e.startswith('keep') for e in err):
        err.append('keep: 인터뷰에서 레퍼런스를 받았는데 그대로 쓸 것 표가 비었습니다 — 레퍼런스에서 그대로 쓸 것을 먼저 뽑습니다')
    if err:
        return False, [f'준비 완료 점검표가 통과하지 못했습니다: {rp}'] + ['  - ' + e for e in err], doc
    return True, [], doc


def summary_lines(doc, rp):
    """계획 문서에 넣을 「준비 완료 점검표」 절."""
    mats = doc.get('materials') or []
    c = doc.get('confirmed') or {}
    L = ['## 준비 완료 점검표 (스킬 3.0의 0-1 — 통과해야 만들기 시작)', '',
         f'- 점검표: `{rp}` — 받은 자료 {len(mats)}건 모두 리더가 끝까지 읽음 · 그대로 쓸 것 {len(doc.get("keep") or [])} · 바꿀 곳 {len(doc.get("change") or [])} · 위 문서 소주제 {len(doc.get("subtopics") or [])}',
         f'- 사용자 확인: {c.get("by")} · {c.get("at")} — 「{" ".join(str(c.get("said")).split())}」']
    if filled(doc.get('scope_cut')):
        L.append(f'- 범위를 줄임(사용자 답): {" ".join(str(doc["scope_cut"]).split())}')
    L += ['', '| 자료 | 종류 | 읽은 범위 | 전문 도구 |', '|---|---|---|---|']
    L += [f'| {str(m.get("path")).replace("|", "¦")} | {m.get("kind")} | {str(m.get("range")).replace("|", "¦")} | {str(m.get("tool")).replace("|", "¦")} |' for m in mats]
    L.append('')
    return L


def answer_files(lecture_dir):
    """인터뷰 폴더의 답 파일들(레퍼런스만 먼저 보낸 답 포함)."""
    return sorted(pathlib.Path(lecture_dir).joinpath('materials', '인터뷰').glob('*답변*.json'))


def load_answers(files):
    """(객체 답 목록, 읽지 못했거나 객체가 아닌 파일 목록). 읽지 못한 답에 받은 자료가 있는지 알 수 없으니 부르는 쪽이 막는다(R05)."""
    out, bad = [], []
    for f in files:
        try:
            x = json.loads(pathlib.Path(f).read_text(encoding='utf-8-sig'))
        except (ValueError, OSError):
            bad.append(f); continue
        if isinstance(x, dict):
            out.append(x)
        else:
            bad.append(f)
    return out, bad


def lecture_path(lecture):
    import store as ST
    return ST.project_root() / lecture


def cmd_check(argv):
    a, files, i = {}, [], 0
    while i < len(argv):
        if argv[i] in ('--lecture', '--answers', '--file') and i + 1 < len(argv) and argv[i + 1].strip() and not argv[i + 1].startswith('--'):
            if argv[i] == '--answers':
                files.append(pathlib.Path(argv[i + 1]))
            else:
                a[argv[i][2:]] = argv[i + 1]
            i += 2
        else:
            print(__doc__, file=sys.stderr); return 2
    if not a.get('lecture'):
        print(__doc__, file=sys.stderr); return 2
    lec = lecture_path(a['lecture'])
    if not files:  # 답 파일을 주지 않으면 인터뷰 폴더의 답 파일을 모두 읽는다(답을 안 보고 「받은 자료 없음」이라고 하지 않게)
        files = answer_files(lec)
    ans = []
    for f in files:
        try:
            one = json.loads(f.read_text(encoding='utf-8-sig'))
        except (ValueError, OSError) as e:
            print(f'답변 JSON 을 읽지 못했습니다: {f} ({e})'); return 1
        if not isinstance(one, dict):
            print(f'답변 JSON 이 객체가 아닙니다: {f}'); return 1
        ans.append(one)
    print(f'읽은 인터뷰 답: {len(ans)}개' + (' — ' + ' · '.join(f.name for f in files) if files else '') + '(나중 제출에서 뺀 레퍼런스라도 옛 답 파일에 있으면 요구합니다 — 필요 없으면 --answers 로 고릅니다)')
    ok, notes, doc = gate(lec, ans, a.get('file'))
    for n in notes:
        print(n)
    if ok:
        print('준비 완료 점검표 통과' if doc else '받은 자료 없음 — 점검표가 필요 없습니다')
    return 0 if ok else 1


def cmd_init(argv):
    if len(argv) != 2 or argv[0] != '--lecture' or not argv[1].strip():
        print(__doc__, file=sys.stderr); return 2
    out = lecture_path(argv[1]).joinpath(*READY_REL)
    if out.exists():
        print(f'이미 있습니다(덮어쓰지 않음): {out}'); return 1
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes((json.dumps(TEMPLATE, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
    print(f'만듦: {out} — 칸을 모두 채우고 사용자 확인을 받은 뒤 check_ready.py 로 검사합니다')
    return 0


def cmd_selftest():
    fails = []

    def ok(c, m):
        print(('OK   ' if c else 'FAIL ') + m)
        if not c:
            fails.append(m)
    good = {'version': 1,
            'materials': [{'path': 'materials/참고/지난_보고서.hwpx', 'kind': 'reference', 'read_by': 'leader', 'read': 'all', 'range': '1~14쪽 전부', 'tool': '문서 변환기'},
                          {'path': 'materials/위문서/계획서.pdf', 'kind': 'upstream', 'read_by': 'leader', 'read': 'all', 'range': '1~9쪽 전부', 'tool': '문서 변환기'}],
            'keep': [{'item': '책임자 소속 · 직위', 'value': '○○과 · 교수', 'from': '지난_보고서.hwpx:1쪽'}],
            'change': [{'item': '진행 기간', 'to': '올해 기간', 'why': '연도가 바뀜', 'from': '계획서.pdf:2쪽'}],
            'subtopics': [{'text': '1단계 현황 조사', 'from': '계획서.pdf:3쪽'}],
            'confirmed': {'by': '사용자', 'at': '2026-01-01', 'said': '좋아 이대로 시작해'}}
    ok(validate(good) == [], '바른 점검표 → 통과')

    def bad(change, want, msg):
        d = json.loads(json.dumps(good))
        change(d)
        e = validate(d)
        ok(any(want in x for x in e), msg + (f' — {e}' if not any(want in x for x in e) else ''))
    bad(lambda d: d.update(materials=[]), '하나도 없습니다', '받은 자료 없음 → 실패')
    bad(lambda d: d['materials'][0].update(read_by='helper'), '리더가 직접 읽지 않았습니다', '보조가 읽음 → 실패')
    bad(lambda d: d['materials'][0].pop('read_by'), '리더가 직접 읽지 않았습니다', '읽은 사람 없음 → 실패')
    bad(lambda d: d['materials'][0].update(read='part'), '끝까지 읽지 않았습니다', '일부만 읽음 → 실패')
    bad(lambda d: d['materials'][0].update(range=''), '읽은 범위', '읽은 범위 없음 → 실패')
    bad(lambda d: d['materials'][0].update(tool='<전문 도구>'), '전문 도구', '전문 도구 칸을 양식 그대로 둠 → 실패')
    bad(lambda d: d['materials'][0].update(kind='etc'), '종류(kind)', '모르는 종류 → 실패')
    bad(lambda d: d.update(keep=[]), '그대로 쓸 것 표가 비었습니다', '레퍼런스가 있는데 대조표 없음 → 실패')
    bad(lambda d: d['keep'][0].update({'from': ''}), 'keep[0]: 빈 칸 from', '대조표 줄에 출처 없음 → 실패')
    bad(lambda d: d['change'][0].pop('why'), 'change[0]: 빈 칸 why', '바꿀 곳에 근거 없음 → 실패')
    bad(lambda d: d['subtopics'][0].update({'from': ' '}), 'subtopics[0]: 빈 칸 from', '소주제에 출처 없음 → 실패')
    bad(lambda d: d.update(subtopics=[]), '정해진 소주제', '위 문서가 있는데 소주제 없음 → 실패')
    bad(lambda d: d.pop('confirmed'), '사용자 확인이 없습니다', '사용자 확인 없음 → 실패')
    bad(lambda d: d['confirmed'].update(said='<확인한 말 원문>'), '사용자 확인이 없습니다', '확인 말을 양식 그대로 둠 → 실패')
    d2 = json.loads(json.dumps(good)); d2.update(subtopics=[], subtopics_none='위 문서에 소주제가 정해져 있지 않음(목차만 있음)')
    ok(validate(d2) == [], '소주제가 없으면 까닭(subtopics_none)으로 통과')
    for said in ('👍', '(Approved, proceed)', '※ 좋아요'):
        d3 = json.loads(json.dumps(good)); d3['confirmed']['said'] = said
        ok(validate(d3) == [], f'확인한 말이 기호 · 괄호뿐이어도 원문이면 통과(R06, {said!r})')
    outp = find_paths('Create a new lesson; save the result to D:/exports/zz_none_r06/lesson.html')
    ok(outp == [], f'디스크에 없고 출력 말(save · 저장 · 내보내기) 옆의 경로는 받은 자료가 아님(R06, {outp})')
    outk = find_paths('결과는 D:/exports/zz_none_r06/보고서.hwpx 로 저장해 줘')
    ok(outk == [], f'「…에 저장」 출력 자리도 받은 자료가 아님(R06, {outk})')
    for txt in ('save the result to "D:/exports/zz_none_r06/lesson.html"',
                'save the complete final lesson result to D:/exports/zz_none_r06/lesson.html'):
        ok(find_paths(txt) == [], f'따옴표 안 · 긴 앞 문장의 출력 자리도 받은 자료가 아님(R07, {find_paths(txt)})')
    with tempfile.TemporaryDirectory() as td8:
        ex8 = (pathlib.Path(td8) / 'lesson.html'); ex8.write_text('x', encoding='utf-8')
        p8 = str(ex8).replace(chr(92), '/')
        ok(find_paths('save the result to "' + p8 + '"') == [], '이미 있는 파일이어도 출력 자리면 받은 자료가 아님(R08)')
    ink = find_paths('D:/자료/zz_none_r06/작년_보고서.pdf 이거 그대로 따라 해줘')
    ok(ink == ['D:/자료/zz_none_r06/작년_보고서.pdf'], f'출력 말이 없으면 없는 경로도 받은 자료로 봄(R06, {ink})')
    ok(validate(TEMPLATE) != [], '빈 양식 그대로 → 실패')
    for v in ('-', '(YYYY-MM-DD)', '[확인한 말 원문]', '<확인한 사람', 'TODO', '…', '미정'):
        bad(lambda d, v=v: d['confirmed'].update(by=v), '사용자 확인이 없습니다', f'자리표시 {v!r} → 빈 칸')
    bad(lambda d: d['confirmed'].update(at='어제'), 'at(YYYY-MM-DD)', '확인 날짜 꼴이 아님 → 실패')
    bad(lambda d: d.update(version=2), 'version', '모르는 version → 실패')
    ok(filled('(주)○○ 보고서 양식') and filled('[1] 개요'), '괄호로 시작해도 닫는 괄호로 끝나지 않으면 글로 봄')
    d3 = json.loads(json.dumps(good))
    d3['keep'] = [{'item': '본문 부호', 'value': v, 'from': '지난_보고서.hwpx:2쪽'} for v in ('□', '○', '※', '-', '(가)', '[참고]', '<표 1>', '없음', 'x')]
    d3['change'] = [{'item': '표 번호', 'to': '<표 2>', 'why': '표가 하나 늘어남', 'from': '계획서.pdf:4쪽'}]
    d3['subtopics'] = [{'text': '(1)', 'from': '계획서.pdf:3쪽'}]
    ok(validate(d3) == [], f'값 칸(그대로 쓸 값 · 새 값 · 소주제 글자)은 본문 부호 · 괄호 꼴 · 「없음」도 값(R02) {validate(d3)}')
    bad(lambda d: d['keep'][0].update(value='<레퍼런스의 값>'), 'keep[0]: 빈 칸 value', '값 칸을 양식 글 그대로 둠 → 실패')
    ok(validate([]) != [], 'JSON 객체가 아님 → 실패')

    tmp = pathlib.Path(tempfile.mkdtemp(prefix='tl-ready-'))  # 파일을 쓰는 시험은 임시 폴더에서만
    try:
        lec = tmp / 'work'
        (lec / 'materials' / '인터뷰').mkdir(parents=True)
        for f in ('materials/ref.pdf', 'materials/source.pdf', 'materials/archive.pdf/report.docx', 'materials/참고 자료/a.pdf', 'x.md'):
            (lec / f).parent.mkdir(parents=True, exist_ok=True)
            (lec / f).write_text('x', encoding='utf-8')  # 상대 경로는 실제로 있을 때만 받은 자료다
        (tmp / '참고폴더').mkdir()
        g, n, _ = gate(lec, {})
        ok(g and not n, '받은 자료 없음 · 점검표 없음 → 통과(옛 프로젝트 그대로)')
        ans_ref = {'references': [{'where': 'materials/참고/지난_보고서.hwpx', 'follow': ['all']}]}
        g, n, _ = gate(lec, ans_ref)
        ok(not g and any('점검표가 없습니다' in x for x in n), '레퍼런스를 받았는데 점검표 없음 → 막음')
        g, _, _ = gate(lec, {'stage': 'references', 'references': ans_ref['references']})
        ok(not g, '「레퍼런스만 먼저 보내기」 답도 같은 검사(점검표 없음 → 막음)')
        need = {
            '질문 메모(따옴표 경로)': {'aspects': {'P1.x': {'choice': 'keep', 'note': '"E:/모음/참고 자료집.pdf" 해당 자료 참고'}}},
            '「레퍼런스대로」 답': {'aspects': {'P1.x': {'choice': 'ref'}}},
            '첨부자료 근거 추천 칸': {'recommend': {'items': [{'key': 'dim.purpose', 'basis': 'attached', 'from': '공문.pdf:2'}]}},
            '3부 질문 의견(pq:)': {'opinions': {'pq:goal': 'D:/자료/계획서.pdf 참고'}},
            '조사가 붙은 경로(.pdf를)': {'aspects': {'P1.x': {'note': 'D:/자료/계획서.pdf를 참고해'}}},
            '상대 경로': {'aspects': {'P1.x': {'note': 'materials/ref.pdf 대로'}}},
            'UNC 경로': {'aspects': {'P1.x': {'note': '\\\\server\\share\\계획서.pdf'}}},
            '홈 경로': {'aspects': {'P1.x': {'note': '~/Documents/계획서.csv'}}},
            '주소': {'opinions': {'dim:x': 'https://example.org/ref 참고'}},
            '3부 글 답': {'project': {'topic': 'D:/자료/계획서.pdf 의 소주제대로'}},
            '검토 메모(overall)': {'overall': 'D:/자료/지난결과.pdf 그대로 따라'},
            '새 메모(new_refs)': {'new_refs': [{'text': '이 사이트처럼', 'url': 'https://example.com/ref'}]},
            '서랍 레퍼런스 카드(refs)': {'refs': {'aspect:P2.4.theme': [{'kind': 'new_ref', 'url': 'https://example.org/ref'}]}},
            '기본 양식(base_project)': {'base_project': {'id': 'p1', 'kind': 'project'}},
        }
        for name, a_ in need.items():
            g, n, _ = gate(lec, a_)
            ok(not g, f'{name} → 점검표 필요')
        free = {'project': {'topic': '파일 이름은 강의_01_주제.html 로, 예시는 x.md 처럼', 'goals': '버전 1.2 · 메일 a@b.com · 3.5배'},
                'overall': '좋아요.', 'aspects': {'P1.x': {'choice': 'keep', 'note': '지난번처럼'}}}
        g, n, _ = gate(lec, free)
        ok(g and not n, f'경로 · 주소가 없는 보통 글(결과물 이름 · 숫자 · 메일) → 점검표 필요 없음 {n}')
        ok(not gate(lec, {'dimensions': {'sources_other': 'materials/source.pdf'}})[0], '1부 기타(_other) 글 답의 경로 → 점검표 필요(R02)')
        gm = given_materials(lec, {'aspects': {'a': {'note': 'materials/archive.pdf/report.docx 와 materials/report.pdf.bak'}}})
        ok(gm['paths'] == ['materials/archive.pdf/report.docx'], f'확장자 뒤에 / · 다른 확장자가 이어지면 끊지 않음(R02, {gm["paths"]})')
        ok(not same_material('report.pdf', 'https://host/report.pdf', (lec,)), '파일 이름만 적힌 받은 자료도 주소와는 맞추지 않음(R02)')
        ok(not same_material('https://host/?id=a/', 'https://host/?id=a', (lec,)), '주소의 질의 · 끝 글자는 그대로 비교(R02)')
        gm = given_materials(lec, {'opinions': {'dim:x': 'https://example.com/files/sample.pdf 참고'}})
        ok(gm['paths'] == ['https://example.com/files/sample.pdf'], f'주소 속 「s://」를 드라이브 경로로 따로 세지 않음 ({gm["paths"]})')
        gm = given_materials(lec, {'aspects': {'a': {'note': '"E:/모음/참고 자료/계획서.pdf" 해당 자료 참고'}}})
        ok(gm['paths'] == ["E:/모음/참고 자료/계획서.pdf"], f'띄어쓰기 있는 경로를 조각내지 않음 ({gm["paths"]})')
        gm = given_materials(lec, [{'aspects': {'a': {'note': 'D:/a/x.pdf'}}}, {'references': [{'where': 'D:/b/y.pdf'}]}])
        ok(gm['paths'] == ['D:/a/x.pdf', 'D:/b/y.pdf'], f'답 여러 개를 함께 읽음 ({gm["paths"]})')
        ok(not given_materials(lec, {'aspects': {'a': {'note': 'D:/a/x.pdf'}}})['ref'], '메모의 경로만으로는 대조표(keep)까지 요구하지 않음(원자료일 수 있음)')
        bases = (lec, tmp)
        ok(not same_material('D:/b/report.pdf', 'D:/a/report.pdf', bases), '폴더가 다른 같은 이름 파일은 다른 자료')
        ok(not same_material('D:/a/index.html', 'E:/b/index.html', bases), '드라이브가 다른 같은 이름 파일은 다른 자료')
        ok(not same_material('https://x.com/A.pdf', 'https://x.com/a.pdf', bases), '주소의 경로 부분은 대소문자를 가림')
        ok(same_material('HTTPS://X.com/a.pdf', 'https://x.com/a.pdf', bases), '주소의 스킴 · 호스트는 대소문자를 가리지 않음')
        ok(not same_material('https://x.com/a.pdf', 'a.pdf', bases) and not same_material('D:/a/a.pdf', 'https://x.com/a.pdf', bases), '주소와 로컬 경로는 맞추지 않음')
        ok(same_material(str(lec / 'materials' / 'x.pdf'), 'materials/x.pdf', bases), '작업 폴더 기준 상대 경로 = 절대 경로')
        ok(same_material('D:\\자료\\x.pdf', 'd:/자료/x.pdf', bases), '역슬래시 · 드라이브 대소문자')
        ok(same_material('공문.pdf', 'materials/공문.pdf', bases) and not same_material('공문.pdf', 'materials/다른.pdf', bases), '폴더 없이 파일 이름만 적힌 받은 자료만 파일 이름으로 맞춤')
        ok(from_file('D:/x/공문.pdf:3') == 'D:/x/공문.pdf' and from_file('공문.pdf:2쪽') == '공문.pdf' and from_file('공문.pdf') == '공문.pdf', '추천 근거 「파일:쪽」 → 파일')
        ok(all(from_file(x) == '공문.pdf' for x in ('공문.pdf 2쪽', '공문.pdf, 2쪽', '공문.pdf(2쪽)', '공문.pdf p.2')), '추천 근거의 여러 쪽 표기(R02)')
        fp = lambda t: given_materials(lec, {'aspects': {'a': {'note': t}}})['paths']  # noqa: E731
        ok(fp('"materials/참고 자료/a.pdf" 그대로') == ['materials/참고 자료/a.pdf'], f'따옴표 안 띄어쓰기 상대 경로(R02, {fp(chr(34) + "materials/참고 자료/a.pdf" + chr(34))})')
        ok(fp('D:/자료/참고폴더 전부 봐') == ['D:/자료/참고폴더'] and fp('~/Desktop 폴더') == ['~/Desktop'], f'확장자 없는 폴더 경로(R02, {fp("D:/자료/참고폴더 전부 봐")})')
        ok(fp('결과물은 slides/강의_01_주제.html 로 저장, materials/01_대본.md 에 정리, Node.js/Express.md · 1/2.md') == [], '없는 상대 경로(만들 파일 · 잡음)는 받은 자료가 아님(R02)')
        ok(len(fp('https://x.com/a.pdf를 참고')) == 1 and same_material(fp('https://x.com/a.pdf를 참고')[0], 'https://x.com/a.pdf', (lec,), loose=True), '주소 끝 한글 조사는 맞출 때 견줌(R02 · R04)')
        ok(fp('D:/자료 폴더를 보고, 결과는 강의_01.html 로') == ['D:/자료'], f'따옴표 없는 드라이브 경로는 띄어쓰기 · 쉼표에서 끊음(R02, {fp("D:/자료 폴더를 보고, 결과는 강의_01.html 로")})')
        ok(fp('참고:materials/ref.pdf') == ['materials/ref.pdf'], f'「참고:」 앞붙이를 뗌(R02, {fp("참고:materials/ref.pdf")})')
        ok(fp('"이 자료 D:/자료/a.pdf 보고 정리" 라고 함') == ['D:/자료/a.pdf'], '경로가 든 따옴표 문장은 자리를 차지하지 않음(안의 경로를 찾음, R02)')
        folder = str(tmp / '참고폴더').replace(chr(92), '/')
        ok(fp(folder + '를 보고') == [folder], f'절대 경로 끝 조사는 떼면 있을 때만 뗌(R02, {fp(folder + "를 보고")})')
        ok(fp('https://자료.example.org/ref 참고') == ['https://자료.example.org/ref'] and fp('https://example.org/자료/report.pdf를 봐') == ['https://example.org/자료/report.pdf를'],
           f'한글 주소는 그대로 찾음(R03 · R04, {fp("https://example.org/자료/report.pdf를 봐")})')
        ok(fp('"D:/data/a.pdf please review"') == ['D:/data/a.pdf'] and fp('D:/data folder and save report.pdf') == ['D:/data'], f'경로 뒤 문장을 삼키지 않음(R03, {fp(chr(34) + "D:/data/a.pdf please review" + chr(34))} · {fp("D:/data folder and save report.pdf")})')
        posix = (tmp / '참고폴더').as_posix()
        if posix.startswith('/'):
            ok(fp(posix + ' 를 봐') == [posix], 'POSIX 절대 폴더(있을 때)(R03)')
        ok(fp('그 / 표시와 /없는/경로') == [], '/ 로 시작해도 없는 경로는 받은 자료가 아님(R03)')
        ok(from_file('materials/archive.pdf/report.docx:2') == 'materials/archive.pdf/report.docx' and from_file('https://x.org/a.pdf?version=2') == 'https://x.org/a.pdf?version=2',
           f"추천 근거는 끝의 쪽 표기만 뗌(R03, {from_file('materials/archive.pdf/report.docx:2')})")
        (lec / 'materials' / '참고자료').mkdir()
        ok(fp('materials/참고자료 폴더 전부 그대로 따라') == ['materials/참고자료'], f'있는 상대 폴더(R03, {fp("materials/참고자료 폴더 전부 그대로 따라")})')
        ok(fp('~/문서/계획서.pdf를 참고') == ['~/문서/계획서.pdf'] and fp('\\\\server\\share\\a.pdf를') == ['\\\\server\\share\\a.pdf'], f'~/ · UNC 파일 끝 조사(R03, {fp("~/문서/계획서.pdf를 참고")})')
        ok(fp('D:/자료 폴더를 보고 강의_01.html 로 저장해') == ['D:/자료'], f'띄어쓰기 뒤 결과물 이름을 삼키지 않음(R03, {fp("D:/자료 폴더를 보고 강의_01.html 로 저장해")})')
        for t_, want in (('D:/자료를 보고', 'D:/자료'), ('「D:/자료」를 참고', 'D:/자료'), ('(D:/자료)를', 'D:/자료'), ('[D:/자료/참고] 폴더', 'D:/자료/참고')):
            got = fp(t_)
            ok(len(got) == 1 and same_material(got[0], want, (lec,), loose=True), f'끝 조사 · 닫는 괄호가 붙어도 점검표의 경로와 맞음(R03, {t_} → {got})')
        ok(same_material('D:/자료/고양이', 'D:/자료/고양이', (lec,)), '조사처럼 끝나는 실제 이름도 그대로 맞음(R03)')
        ok(not same_material('D:/data/고양이', 'D:/data/고양', (lec,)), '레퍼런스 칸 · 첨부 목록의 경로는 글자 그대로 — 끝 글자를 떼어 맞추지 않음(R04)')
        ok(fp('https://example.org/고양이') == ['https://example.org/고양이'], '한글 주소 끝 글자를 자르지 않음(R04)')
        ok(same_material('https://example.org/자료/report.pdf를', 'https://example.org/자료/report.pdf', (lec,), loose=True), '글 속 주소 끝 조사는 맞출 때 견줌(R04)')
        ok(from_file('https://example.org:8080') == 'https://example.org:8080' and from_file('https://example.org/report?ids=1,2') == 'https://example.org/report?ids=1,2',
           '추천 근거 주소의 포트 · 질의는 그대로(R04)')
        for t_ in ('날짜 구분은 (/) 대신 점(.)으로', '구분 기호는 "/" 로 통일', '기호 /. 끝', '~/ 표시', '비율 W:/H', 'Q:/A 형식'):
            ok(fp(t_) == [], f'기호 · 비율 글은 받은 자료가 아님(R04, {t_} → {fp(t_)})')
        ok(not same_material('D:/자료/도로', 'D:/자료', (lec,), loose=True) and not same_material('C:/가가', 'C:/', (lec,), loose=True)
           and not same_material('D:/자료/도', 'D:/자료', (lec,), loose=True),
           '끝 조사는 한 번만 떼고 뿌리까지 떼지 않음(R04)')
        ok(from_file('D:/자료/회의 2026') == 'D:/자료/회의 2026', '띄어쓰기 + 숫자만은 쪽 표기가 아님(R04)')
        (lec / 'scripts' / 'project-board').mkdir(parents=True)
        ok(fp('scripts/ 참고') == ['scripts/'], f'끝 / 가 붙은 있는 폴더(R05, {fp("scripts/ 참고")})')
        ok(same_material('https://example.org/ref/', 'https://example.org/ref/', (lec,), loose=True), '끝 / 가 붙은 주소도 그대로 맞음(R05)')
        ok(fp('D:/x/source 와 D:/a/bundle') == ['D:/x/source', 'D:/a/bundle'], f'첫 폴더 이름이 한 글자인 경로(R05, {fp("D:/x/source 와 D:/a/bundle")})')
        gx = given_materials(lec, {'references': [{'where': 'https://example.org/고양이'}], 'overall': 'https://example.org/고양이'})
        ok('https://example.org/고양이' not in gx['loose'], '명시 칸(레퍼런스)에도 있는 경로는 글에 나와도 글자 그대로 맞춤(R05)')
        ok(fp('"D:/자료/참고 폴더" 를 봐') == ['D:/자료/참고 폴더'], f'따옴표 안 띄어쓰기 폴더 경로(R05, {fp(chr(34) + "D:/자료/참고 폴더" + chr(34) + " 를 봐")})')
        (lec / 'materials' / '인터뷰' / '00_추천.json').write_text(json.dumps({'attachments': [{'path': 'D:/자료/참고폴더를', 'read': 'unknown', 'found': '듣기 모드 말씀 1에서'}]}, ensure_ascii=False), encoding='utf-8')
        gl = given_materials(lec, {})
        ok('D:/자료/참고폴더를' in gl['loose'], '듣기 모드가 적은 첨부자료는 느슨하게 맞춤(끝 조사 — R05)')
        (lec / 'materials' / '인터뷰' / '00_추천.json').unlink()

        ok(fp('scripts/project-board를 참고') == ['scripts/project-board'] and fp('[scripts/project-board] 참고') == ['scripts/project-board'],
           f'있는 상대 폴더에 조사 · 괄호가 붙어도 찾음(R04, {fp("scripts/project-board를 참고")} · {fp("[scripts/project-board] 참고")})')
        g2 = given_materials(lec, {'aspects': {'P2.4.quality_bar': {'choice': 'new', 'value': 'D:/지난결과/보고서.pdf 수준 그대로'}}})
        ok(g2['paths'] == ['D:/지난결과/보고서.pdf'], f'2부 글 답(value)의 경로(R03, {g2["paths"]})')
        ok(fp('"https://x.com/a 참고"') == ['https://x.com/a'], f'따옴표 문장 속 주소(R03, {fp(chr(34) + "https://x.com/a 참고" + chr(34))})')
        ok(fp('"https://x.com/a"') == ['https://x.com/a'], '따옴표 안 주소 하나(R03)')
        dr = given_materials(lec, {'refs': {'x': [{'kind': 'template', 'location': 'templates/보고서양식.hwpx'}, {'kind': 'new_ref', 'label': 'D:/참고/지난보고서.pdf'}]}})
        ok('templates/보고서양식.hwpx' in dr['paths'] and 'D:/참고/지난보고서.pdf' in dr['paths'], f'서랍 카드의 location · label(R02, {dr["paths"]})')
        (lec / 'materials' / '인터뷰' / '00_추천.json').write_text('{', encoding='utf-8')
        g, n, _ = gate(lec, {})
        ok(not g and any('읽지 못함' in x for x in n), '읽지 못한 00_추천.json → 첨부자료가 있는 것으로 보고 점검표 요구')
        (lec / 'materials' / '인터뷰' / '00_추천.json').write_text(json.dumps({'listening': True}), encoding='utf-8')
        g, n, _ = gate(lec, {})
        ok(not g and any('듣는 중' in x for x in n) and not any('점검표가 없습니다' in x for x in n), '듣기 모드가 열려 있으면 막음 — 점검표를 만들라가 아니라 듣기를 닫으라고(R02)')
        (lec / 'materials' / '인터뷰' / '00_추천.json').write_bytes(b'\xef\xbb\xbf' + json.dumps({'attachments': [{'path': 'materials/공문.pdf', 'found': 'x'}]}, ensure_ascii=False).encode('utf-8'))
        g, n, _ = gate(lec, {})
        ok(not g and any('00_추천.json 첨부자료' in x for x in n), '00_추천.json 첨부자료 → 점검표 필요 (BOM 이 있어도 읽음)')
        g, n, _ = gate(lec, {'recommend': {'items': [{'key': 'dim.purpose', 'basis': 'attached'}]}})
        ok(not g, '근거 파일 없는 첨부자료 추천 칸')
        rp = lec.joinpath(*READY_REL)
        rp.write_text(json.dumps(good, ensure_ascii=False), encoding='utf-8')
        g, n, _ = gate(lec, ans_ref)
        ok(not g and any('점검표에 없습니다' in x and '공문.pdf' in x for x in n), '받은 자료(공문.pdf)가 점검표에 빠짐 → 막음')
        doc = json.loads(json.dumps(good)); doc['materials'].append(dict(good['materials'][1], path='materials/공문.pdf', kind='form'))
        rp.write_text(json.dumps(doc, ensure_ascii=False), encoding='utf-8')
        g, n, d = gate(lec, ans_ref)
        ok(g and d is not None, '받은 자료가 모두 있고 바른 점검표 → 통과' + ('' if g else f' — {n}'))
        g, n, _ = gate(lec, {'recommend': {'items': [{'key': 'dim.purpose', 'basis': 'attached'}]}})
        ok(g, '근거 파일 없는 첨부자료 칸도 00_추천.json attachments 로 맞추면 통과' + ('' if g else f' — {n}'))
        g, n, _ = gate(lec, {'recommend': {'items': [{'key': 'dim.purpose', 'basis': 'attached', 'from': '다른공문.pdf:1'}]}})
        ok(not g and any('다른공문.pdf' in x for x in n), '첨부자료 추천 칸의 근거 파일이 점검표에 없음 → 막음')
        rp.write_bytes(b'\xef\xbb\xbf' + json.dumps(doc, ensure_ascii=False).encode('utf-8'))
        g, n, _ = gate(lec, ans_ref)
        ok(g, 'BOM 이 있는 점검표도 읽음' + ('' if g else f' — {n}'))
        d5 = json.loads(json.dumps(doc))
        d5['materials'].append(dict(doc['materials'][0], path='https://x.com/a.pdf'))
        rp.write_text(json.dumps(d5, ensure_ascii=False), encoding='utf-8')
        g, n, _ = gate(lec, dict(ans_ref, aspects={'a': {'note': 'https://x.com/a.pdf를 참고'}}))
        ok(g, '글 속 주소 끝 조사는 점검표의 주소와 맞음(게이트, R04)' + ('' if g else f' — {n}'))
        g, n, _ = gate(lec, dict(ans_ref, references=ans_ref['references'] + [{'where': 'https://x.com/a.pdf를'}]))
        ok(not g, '레퍼런스 칸의 주소는 글자 그대로 — 끝 글자를 떼어 맞추지 않음(게이트, R04)')
        for bad_m in (5, True, 'x', {'a': 1}):
            rp.write_text(json.dumps(dict(doc, materials=bad_m), ensure_ascii=False), encoding='utf-8')
            try:
                g, n, _ = gate(lec, ans_ref)
                ok(not g, f'materials={bad_m!r} → 추적 출력 없이 막음')
            except Exception as e:  # noqa: BLE001
                ok(False, f'materials={bad_m!r} → {type(e).__name__}')
        rp.write_text(json.dumps(doc, ensure_ascii=False), encoding='utf-8')
        rf0 = lec / 'materials' / '인터뷰' / '00_추천.json'
        saved = rf0.read_bytes()
        rf0.unlink()
        g, n, _ = gate(lec, {'recommend': {'items': [{'key': 'dim.purpose', 'basis': 'attached'}]}})
        ok(not g and any('근거 파일(from)' in x for x in n), '바른 점검표가 있어도 근거 파일을 모르는 첨부자료 칸(00_추천.json 없음) → 막음')
        rf0.write_text(json.dumps({'listening': True}), encoding='utf-8')
        g, n, _ = gate(lec, ans_ref)
        ok(not g and any('듣는 중' in x for x in n), '바른 점검표가 있어도 듣는 중이면 막음(R02)')
        for bad_r in ('{', '[]', '{"attachments": 5}', 'null', '{"attachments": ["materials/a.pdf"]}', '{"attachments": [{}]}', '{"listening": "true"}'):
            rf0.write_text(bad_r, encoding='utf-8')
            g, n, _ = gate(lec, ans_ref)
            ok(not g, f'바른 점검표가 있어도 00_추천.json 이 {bad_r!r} 이면 막음(R02)')
        rf0.write_bytes(saved)
        doc2 =json.loads(json.dumps(doc)); doc2['materials'][0]['read_by'] = 'helper'
        rp.write_text(json.dumps(doc2, ensure_ascii=False), encoding='utf-8')
        (lec / 'materials' / '인터뷰' / '00_추천.json').unlink(missing_ok=True)
        g, n, _ = gate(lec, {})
        ok(not g, '받은 자료 표시가 없어도 점검표가 있으면 통과해야 함 → 막음')
        doc3 = json.loads(json.dumps(doc)); doc3['materials'] = [m for m in doc3['materials'] if m['kind'] != 'reference']; doc3['keep'] = []
        rp.write_text(json.dumps(doc3, ensure_ascii=False), encoding='utf-8')
        g, n, _ = gate(lec, {'references': [{'where': 'materials/위문서/계획서.pdf'}]})
        ok(not g and any('keep' in x for x in n), '인터뷰에서 레퍼런스를 받았는데 대조표 비었음 → 막음(종류를 reference 가 아니라고 적어도)')
        rp.write_text('{', encoding='utf-8')
        g, n, _ = gate(lec, {})
        ok(not g and any('읽지 못했습니다' in x for x in n), '깨진 점검표 → 막음')
        # answers_to_plan.py 가 이 검사로 멈추는지 — 아무것도 쓰지 않아야 한다
        env = dict(os.environ, TASTE_LOOP_STORE=str(HERE.parent / 'starter'), TASTE_LOOP_PROJECT=str(tmp))
        env.pop('CLAUDE_PROJECT_DIR', None)
        af = tmp / 'ans.json'
        af.write_text(json.dumps(dict(ans_ref, dimensions={}, aspects={}), ensure_ascii=False), encoding='utf-8')
        plan = tmp / 'plan.md'
        rp.unlink()

        def ap():
            r = subprocess.run([sys.executable, '-X', 'utf8', '-I', str(HERE / 'answers_to_plan.py'), '--lecture', 'work', '--answers', str(af), '--out', str(plan)],
                               capture_output=True, env=env, timeout=180)
            return r.returncode, (r.stderr or b'').decode('utf-8', 'replace')
        code, se = ap()
        ok(code == 1 and not plan.exists() and '점검표가 없습니다' in se, f'answers_to_plan: 레퍼런스를 받았는데 점검표 없음 → 멈추고 계획 문서를 쓰지 않음(종료 {code})')
        rp.write_text(json.dumps(doc2, ensure_ascii=False), encoding='utf-8')
        code, se = ap()
        ok(code == 1 and not plan.exists() and '리더가 직접 읽지 않았습니다' in se, f'answers_to_plan: 점검표가 통과하지 못함 → 멈춤(종료 {code})')
        rp.write_text(json.dumps(doc, ensure_ascii=False), encoding='utf-8')
        code, se = ap()
        txt = plan.read_text(encoding='utf-8') if plan.exists() else ''
        ok(code == 0 and '## 준비 완료 점검표' in txt and '좋아 이대로 시작해' in txt, f'answers_to_plan: 통과하면 계획 문서에 「준비 완료 점검표」 절(종료 {code}) {se[-200:]}')
        plan.unlink()
        af.write_text(json.dumps(dict(ans_ref, stage='references'), ensure_ascii=False), encoding='utf-8')
        (lec / 'materials' / '인터뷰' / '01_제작인터뷰_답변_레퍼런스.json').write_text(json.dumps(dict(ans_ref, stage='references')), encoding='utf-8')
        af_final = tmp / 'final.json'
        af_final.write_text(json.dumps({'ref_none': True, 'dimensions': {}, 'aspects': {}}), encoding='utf-8')
        rp_keep = rp.read_bytes()
        rp.unlink()
        r_ = subprocess.run([sys.executable, '-X', 'utf8', '-I', str(HERE / 'answers_to_plan.py'), '--lecture', 'work', '--answers', str(af_final), '--out', str(plan)],
                            capture_output=True, env=env, timeout=180)
        ok(r_.returncode == 1 and not plan.exists(), f'answers_to_plan: 인터뷰 폴더의 앞 답(레퍼런스)도 함께 봄 — 마지막 답에 레퍼런스가 없어도 막음(R04, 종료 {r_.returncode})')
        (lec / 'materials' / '인터뷰' / '01_제작인터뷰_답변_레퍼런스.json').write_text('{"stage": "references", "references": [{"where": "D:/자료/a.pdf"}', encoding='utf-8')
        rp.write_bytes(rp_keep)
        r_ = subprocess.run([sys.executable, '-X', 'utf8', '-I', str(HERE / 'answers_to_plan.py'), '--lecture', 'work', '--answers', str(af_final), '--out', str(plan)],
                            capture_output=True, env=env, timeout=180)
        ok(r_.returncode == 1 and not plan.exists(), f'answers_to_plan: 인터뷰 폴더의 다른 답 파일이 깨졌으면 막음(R05, 종료 {r_.returncode})')
        (lec / 'materials' / '인터뷰' / '01_제작인터뷰_답변_레퍼런스.json').unlink()
        code, se = ap()
        ok(code == 1 and not plan.exists() and '레퍼런스만 먼저 보내기' in se, f'answers_to_plan: 「레퍼런스만 먼저 보내기」 답으로는 계획을 만들지 않음(점검표가 통과해도, 종료 {code})')
        rp.unlink()
        af.write_text(json.dumps({'dimensions': {}, 'aspects': {}}, ensure_ascii=False), encoding='utf-8')
        code, se = ap()
        ok(code == 0 and plan.exists(), f'answers_to_plan: 받은 자료 없음 · 점검표 없음 → 그대로 만듦(종료 {code}) {se[-200:]}')
        plan.unlink()
        af.write_bytes(b'\xef\xbb\xbf' + json.dumps({'dimensions': {}, 'aspects': {}}).encode('utf-8'))
        code, se = ap()
        ok(code == 0 and plan.exists(), f'answers_to_plan: BOM 있는 답 파일도 읽음(R02, 종료 {code}) {se[-160:]}')
        plan.unlink()
        af.write_text('[]', encoding='utf-8')
        code, se = ap()
        ok(code == 1 and not plan.exists() and '객체' in se and 'Traceback' not in se, f'answers_to_plan: 객체가 아닌 답 파일 → 추적 출력 없이 멈춤(R02, 종료 {code})')
        # 명령으로(브리프 앞 검사): 답 파일을 주지 않아도 인터뷰 폴더의 답 파일을 읽는다
        (lec / 'materials' / '인터뷰' / '00_추천.json').unlink(missing_ok=True)
        (lec / 'materials' / '인터뷰' / '01_제작인터뷰_답변.json').write_text(json.dumps(ans_ref, ensure_ascii=False), encoding='utf-8')

        def cli(*args):
            r = subprocess.run([sys.executable, '-X', 'utf8', '-I', str(HERE / 'check_ready.py'), *args], capture_output=True, env=env, timeout=60)
            return r.returncode, (r.stdout or b'').decode('utf-8', 'replace')
        code, so = cli('--lecture', 'work')
        ok(code == 1 and '점검표가 없습니다' in so and '읽은 인터뷰 답: 1개' in so, f'check_ready 명령: 답 파일을 주지 않아도 인터뷰 폴더의 답을 읽고 막음(종료 {code})')
        (lec / 'materials' / '인터뷰' / '01_제작인터뷰_답변.json').write_text('[1]', encoding='utf-8')
        code, so = cli('--lecture', 'work')
        ok(code == 1 and '객체가 아닙니다' in so, f'check_ready 명령: 객체가 아닌 답 파일 → 종료 1(종료 {code})')
        af2 = lec / 'materials' / '인터뷰' / '01_제작인터뷰_답변.json'
        af2.write_bytes(b'\xef\xbb\xbf' + json.dumps({'dimensions': {}}).encode('utf-8'))
        code, so = cli('--lecture', 'work')
        ok(code == 0 and '읽은 인터뷰 답: 1개' in so, f'check_ready 명령: BOM 있는 답 파일도 읽음(R02, 종료 {code})')
        a1, a2 = tmp / 'a1.json', tmp / 'a2.json'
        a1.write_text('{}', encoding='utf-8')
        a2.write_text(json.dumps(ans_ref, ensure_ascii=False), encoding='utf-8')
        code, so = cli('--lecture', 'work', '--answers', str(a1), '--answers', str(a2))
        ok(code == 1 and '읽은 인터뷰 답: 2개' in so, f'check_ready 명령: --answers 여러 번(R02, 종료 {code})')
        code, _ = cli('--lecture')
        ok(code == 2, f'check_ready 명령: 값 없는 인자 → 종료 2(종료 {code})')
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print('실패 ' + str(len(fails)) if fails else '자체 시험 통과')
    return 1 if fails else 0


def main(argv):
    if argv[:1] == ['selftest'] and len(argv) == 1:
        return cmd_selftest()
    if argv[:1] == ['template'] and len(argv) == 1:
        print(json.dumps(TEMPLATE, ensure_ascii=False, indent=1)); return 0
    if argv[:1] == ['init']:
        return cmd_init(argv[1:])
    if argv in ([], ['-h'], ['--help']):
        print(__doc__); return 0 if argv else 2
    return cmd_check(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
