#!/usr/bin/env python3
"""준비 완료 점검표 검사 — 받은 자료를 하나하나 다 열어 처음부터 끝까지 분석 · 정리한 뒤에 만들기 시작한다 (엔진 1.8.0).

받은 자료(첨부 파일 · 레퍼런스 · 위 문서 · 양식)가 있는 일은 이 점검표가 통과하고 사용자가 확인한 뒤에 만든다.
「빠르게 · 간단하게 · 마감 임박」 이어도 건너뛰지 않는다 — 시간이 모자라면 준비를 줄이지 말고 결과물의 범위를 줄일지 묻는다
(scope_cut 에 사용자 답을 적는다). 빠른 초안 → 고치기 순서는 수정 · 토큰 · 시간을 더 쓴다.

점검표 version 2 (1.8.0 — init 이 만든다. 사용자 원문 2026-11-18 「자유 인터뷰 진행하고 제공하는 모든 자료에대해 하나하나씩 다 열어서
처음부터 끝까지 제대로 완벽히 분석하고 정리하도록 지침과 셋팅 수정보완해줘.」)
  {"version": 2,
   "notes_dir": "materials/<YYMMDD>_받은자료분석",       자료마다 분석 노트를 두는 폴더
   "index": "materials/<YYMMDD>_받은자료분석/00_받은자료_목록.md",   모든 자료 → 노트 목록(add · index 가 만든다)
   "folders": [{"path": "<받은 폴더 · 압축 파일>", "extracted_to": "<푼 폴더 — zip 이 아닌 압축일 때>"}],
        폴더 · 압축 파일은 한 줄로 세지 않는다 — 안의 파일(하위 폴더까지)마다 materials 에 한 줄. zip 안의 파일은 「<zip 경로>!/<안 경로>」.
        건너뛰는 것은 잡음뿐(.git · node_modules · __pycache__ · __MACOSX · Thumbs.db · .DS_Store · desktop.ini · ~$ 잠금 파일 · ._ 파일)
   "materials": [{"path": "<파일 하나 · 주소>", "kind": …, "read_by": "leader", "read": "all", "range": …, "tool": …,
                  "unit": "<쪽 · 장 · 시트 · 줄 · 분 · 초 · 그림 …>", "total": <전체 분량>, "covered": <다 본 분량 = total>,
                  "note": "<분석 노트 .md — 무엇인가 · 처음부터 끝까지 정리 · 이 일에 그대로 쓸 것 · 바꿀 곳 · 근거 · 확인 필요>",
                  "size": <바이트>, "sha256": "<분석한 때의 파일>", "mtime_ns": <선택>}],
   "scope_cut": {"said": "<사용자 답 원문>", "skipped": ["<빼기로 한 파일 경로>", …]},   파일을 빼는 길은 이것 하나
   keep · change · subtopics · subtopics_none · confirmed 는 version 1 과 같다}
  - 분량: pptx 장 · xlsx 시트 · 글 파일 줄 · (압축 안 된) pdf 쪽 · mp4/mov 초 · 분은 파일에서 직접 세어 total 과 견준다. 셀 수 없거나
    단위가 다르면 견주지 않는다(불확실하면 막지 않음). 이 PC 에 없는 파일 · 폴더는 크기 · 분량 · 안의 파일을 확인하지 못했다고 알리고 막지 않는다.
  - 새로움: 분석한 뒤 파일이 바뀌면(크기 · sha256) 「다시 분석」으로 막는다. 한 번에 1 GiB 넘게는 해시하지 않고 크기만 견준다(알림).
  - version 1(1.7.0) 점검표는 2026-11-18 까지 확인받은 것만 알림과 함께 통과한다(그 뒤 확인이면 version 2 로 올린다).
  python3 check_ready.py add --lecture <작업폴더> [--kind <종류>] <파일 · 폴더 · 압축 · 주소>...
        자료를 materials 에 한 줄씩(폴더 · 압축은 안의 파일마다) 더하고 크기 · sha256 · 셀 수 있는 분량 · 분석 노트 틀 · 목록을 만든다
  python3 check_ready.py index --lecture <작업폴더>     목록(index)을 다시 만든다

점검표 version 1 (1.7.0 — 아래는 그때의 형식, version 2 도 이 칸을 그대로 쓴다): <작업폴더>/materials/00_준비점검표.json (JSON 객체 하나)
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
  python3 check_ready.py init --lecture <작업폴더>    빈 양식(version 2)을 materials/00_준비점검표.json 에 만든다(있으면 덮어쓰지 않음)
  python3 check_ready.py template                    빈 양식을 화면에 보여 준다
  python3 check_ready.py selftest
answers_to_plan.py 가 계획 문서를 만들기 전에 같은 검사(gate)를 돌리고, 통과하지 못하면 아무것도 쓰지 않고 멈춘다.
"""
import datetime
import hashlib
import io
import json
import os
import pathlib
import posixpath
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import unicodedata
import zipfile
import zlib

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
NOTES_DIR = 'materials/{d}_받은자료분석'
INDEX_NAME = '00_받은자료_목록.md'
TEMPLATE = {
    'version': 2,
    'notes_dir': NOTES_DIR.format(d='<YYMMDD>'),
    'index': NOTES_DIR.format(d='<YYMMDD>') + '/' + INDEX_NAME,
    'folders': [],
    'materials': [{'path': '<받은 파일 하나 · 주소>', 'kind': '<reference|upstream|form|source|other>', 'read_by': '<leader>',
                   'read': '<all>', 'range': '<읽은 범위>', 'tool': '<전문 도구>', 'unit': '<쪽 · 장 · 시트 · 줄 · 분 · 초 · 그림>',
                   'total': 0, 'covered': 0, 'note': '<분석 노트 경로>', 'size': 0, 'sha256': '', 'found': '<알게 된 것 한 줄>'}],
    'keep': [{'item': '<그대로 쓸 것>', 'value': '<레퍼런스의 값>', 'from': '<파일:쪽>'}],
    'change': [],
    'subtopics': [{'text': '<위 문서에 정해진 소주제 — 글자 그대로>', 'from': '<파일:쪽>'}],
    'subtopics_none': '',
    'scope_cut': {'said': '', 'skipped': []},
    'confirmed': {'by': '<확인한 사람>', 'at': '<YYYY-MM-DD>', 'said': '<확인한 말 원문>'},
}
# ---- version 2(1.8.0): 하나하나 · 처음부터 끝까지 ----
LEGACY_UNTIL = '2026-11-18'  # 이날까지 확인받은 version 1 점검표는 알림만(1.8.0 전에 만든 것 — 그 뒤 확인이면 version 2 로)
NOISE_DIRS = {'.git', 'node_modules', '__pycache__', '__macosx', '.svn', '.hg', '.ipynb_checkpoints'}
NOISE_FILES = {'thumbs.db', 'ehthumbs.db', '.ds_store', 'desktop.ini'}
ARCHIVE_EXT = ('.zip', '.7z', '.rar', '.alz', '.egg', '.tar', '.gz', '.tgz', '.bz2', '.xz')
MEMBER = '!/'  # zip 안의 파일: 「<zip 경로>!/<안 경로>」
NOTE_SECTIONS = (('무엇인가', False), ('처음부터 끝까지', False), ('그대로 쓸 것', False), ('바꿀 곳', True), ('확인 필요', True))  # True = 「없음」도 내용
NOTE_MIN_CHARS = 200  # 노트 본문(제목 줄 뺌) 글자 수 하한
HASH_BUDGET = 1 << 30  # 한 번 검사에 해시하는 바이트 상한(넘으면 크기만 견주고 알림 — 훅 시간 한도)
TEXT_EXT = ('.txt', '.md', '.csv', '.tsv', '.json', '.html', '.htm', '.xml', '.srt', '.vtt', '.yaml', '.yml', '.log', '.py', '.js', '.css')
UNIT_KIND = {'slides': {'장', '슬라이드', '쪽', 'slide', 'slides', 'page', 'pages'}, 'sheets': {'시트', 'sheet', 'sheets'},
             'lines': {'줄', 'line', 'lines'}, 'pages': {'쪽', '페이지', 'page', 'pages', 'p'},
             'seconds': {'초', 'sec', 'secs', 'second', 'seconds', 's'}, 'minutes': {'분', 'min', 'mins', 'minute', 'minutes'}}


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
    if doc.get('version', 1) not in (1, 2) or isinstance(doc.get('version'), bool):
        err.append(f'version: 2(또는 2026-11-18 까지 확인받은 1)여야 합니다({doc.get("version")!r})')
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


# ---------- version 2 (1.8.0): 하나하나 · 처음부터 끝까지 · 새로움 ----------
def isint(v):
    return isinstance(v, int) and not isinstance(v, bool)


def nfc(s):
    return unicodedata.normalize('NFC', str(s))


def is_noise(name):
    n = nfc(name).lower()
    return n in NOISE_FILES or n.startswith('~$') or n.startswith('._') or n.startswith('.~lock.')


def is_archive(name):
    return nfc(name).lower().endswith(ARCHIVE_EXT)


def split_member(s):
    """「a.zip!/b/c.pdf」 → ('a.zip', 'b/c.pdf'), 아니면 (s, None)"""
    s = str(s or '').strip()
    i = s.lower().find('.zip' + MEMBER)
    return (s[:i + 4], s[i + 4 + len(MEMBER):]) if i >= 0 else (s, None)


def local_of(p, lec):
    """로컬 파일 경로 — 주소 · 빈 값이면 None. 상대 경로는 작업 폴더 기준(없으면 프로젝트 루트 기준)."""
    s = str(p or '').strip().strip('"\'')
    if not s or re.match(r'(?i)https?://', s):
        return None
    s = os.path.expanduser(s)
    q = pathlib.Path(s)
    if q.is_absolute() or is_local_abs(s):
        return q
    if (pathlib.Path(lec) / q).exists():
        return pathlib.Path(lec) / q
    if (_project_root() / q).exists():
        return _project_root() / q
    return pathlib.Path(lec) / q


_ROOTS = {}


def _project_root():
    """프로젝트 루트(store.project_root 는 git 을 부른다 — 같은 환경 · 같은 cwd 면 한 번만)"""
    k = (os.environ.get('TASTE_LOOP_PROJECT'), os.environ.get('CLAUDE_PROJECT_DIR'), os.getcwd())
    if k not in _ROOTS:
        import store as ST
        _ROOTS[k] = ST.project_root()
    return _ROOTS[k]


def zip_members(zp):
    """zip 안의 파일(잡음 · 폴더 뺌) — 열지 못하면 None"""
    try:
        with zipfile.ZipFile(zp) as z:
            names = [i.filename for i in z.infolist() if not i.is_dir()]
    except (OSError, zipfile.BadZipFile, ValueError):
        return None
    return [n for n in names if not is_noise(n.rstrip('/').rsplit('/', 1)[-1]) and not any(nfc(x).lower() in NOISE_DIRS for x in n.split('/')[:-1])]


def walk(d, skip=()):
    """폴더 안의 파일(하위 폴더까지, 잡음 뺌) → (파일 경로 목록, 안에 든 zip 아닌 압축 파일 목록). zip 은 안의 파일로 편다."""
    files, archives = [], []
    skip = {os.path.normcase(os.path.abspath(s)) for s in skip}
    for top, dirs, names in os.walk(d):
        dirs[:] = sorted(x for x in dirs if nfc(x).lower() not in NOISE_DIRS and os.path.normcase(os.path.abspath(os.path.join(top, x))) not in skip)
        for n in sorted(names):
            f = os.path.join(top, n)
            if is_noise(n) or os.path.normcase(os.path.abspath(f)) in skip:
                continue
            if n.lower().endswith('.zip'):
                mem = zip_members(f)
                if mem is None:
                    files.append(f)  # 열지 못한 zip 은 파일 하나로(분석 노트에 「열지 못함」을 적는다)
                else:
                    files += [f + MEMBER + m for m in mem]
            elif is_archive(n):
                archives.append(f)
            else:
                files.append(f)
    return files, archives


def expand(folder, lec, skip=()):
    """folders 의 한 줄 → (안의 파일 목록 또는 None(이 PC 에서 볼 수 없음), 안의 압축 파일, 오류)"""
    path, ex = folder.get('path'), folder.get('extracted_to')
    if filled(ex):
        q = local_of(ex, lec)
        return walk(q, skip) + ([],) if q is not None and q.is_dir() else (None, [], [])
    p = local_of(path, lec)
    if p is None or not p.exists():
        return None, [], []
    if p.is_dir():
        return walk(p, skip) + ([],)
    if p.name.lower().endswith('.zip'):
        mem = zip_members(p)
        return (None, [], []) if mem is None else ([str(path).strip() + MEMBER + m for m in mem], [], [])
    if is_archive(p.name):
        return None, [], [f'{path}: zip 이 아닌 압축 파일은 풀어서 그 폴더를 extracted_to 에 적습니다(안의 파일을 하나하나 세려고)']
    return None, [], [f'{path}: folders 에는 받은 폴더 · 압축 파일만 적습니다(파일 하나는 materials 에)']


def measure(name, opener, size):
    """셀 수 있는 분량 → {종류: 값}. 셀 수 없거나 불확실하면 {}(막지 않음)."""
    n = nfc(name).lower()
    try:
        if n.endswith('.pptx'):
            with opener() as f, zipfile.ZipFile(f) as z:
                pres = no_comments(xml_text(z.read('ppt/presentation.xml')))  # 실제 장 목록(sldIdLst) — 파일 이름으로 세지 않는다(R01)
            return {'slides': len(re.findall(r'<(?:\w+:)?sldId\b', pres))} if pres is not None else {}
        if n.endswith('.xlsx'):
            with opener() as f, zipfile.ZipFile(f) as z:
                wb = no_comments(xml_text(z.read('xl/workbook.xml')))
            return {'sheets': len(re.findall(r'<(?:\w+:)?sheet\b', wb))} if wb is not None else {}
        if n.endswith(TEXT_EXT) and size <= 200 << 20:
            with opener() as f:
                data = f.read()
            s = xml_text(data)  # UTF-16 은 풀어서 · 인코딩을 모르면(NUL 바이트) 세지 않는다(R02)
            return {'lines': len(re.findall(r'\r\n|\r|\n', s)) + (1 if s and not s.endswith(('\n', '\r')) else 0)} if s is not None else {}  # CRLF · LF · CR 만(R01)
        if n.endswith('.pdf') and size <= 300 << 20:
            with opener() as f:
                c = pdf_pages(f.read())
            return {'pages': c} if c else {}
        if n.endswith(('.mp4', '.mov', '.m4v', '.m4a')):
            with opener() as f:
                s = mp4_seconds(f)
            return {'seconds': s} if s else {}
    except (OSError, KeyError, ValueError, zipfile.BadZipFile, struct.error, RuntimeError, IndexError, EOFError, NotImplementedError, zlib.error):  # 암호 zip · 깨진 영상 머리(R01)
        return {}
    return {}


def no_comments(s):
    """XML 주석 · CDATA 를 뺀다 — 주석 속 <sldId> · <sheet> 를 세지 않게(R03)"""
    return None if s is None else re.sub(r'<!--.*?-->|<!\[CDATA\[.*?\]\]>', '', s, flags=re.S)


def xml_text(b):
    """바이트 → 글. UTF-16(BOM)은 풀고, BOM 없이 NUL 바이트가 있으면 인코딩을 몰라 None(세지 않음 — R02)."""
    if b[:4] in (b'\xff\xfe\x00\x00', b'\x00\x00\xfe\xff'):
        return b.decode('utf-32', 'replace')  # UTF-32 BOM 이 UTF-16 BOM 으로 시작하므로 먼저(R03)
    if b[:2] in (b'\xff\xfe', b'\xfe\xff'):
        return b.decode('utf-16', 'replace')
    if b'\x00' in b[:4096]:
        return None
    return b.decode('utf-8', 'replace')


def pdf_pages(data):
    """압축 안 된 PDF 의 뿌리 쪽 목록(/Type /Pages, /Parent 없음)의 /Count — 하나로 정해질 때만, 아니면 None."""
    if re.search(rb'/Type\s*/ObjStm\b', data):
        return None  # 개체가 압축 묶음 안에 있으면 뿌리를 다 볼 수 없다
    counts = set()
    for m in re.finditer(rb'/Type\s*/Pages\b', data):
        a = data.rfind(b' obj', 0, m.start())
        b = data.find(b'endobj', m.end())
        if a < 0 or b < 0:
            return None
        body = data[a:b]
        if b'/Parent' in body:
            continue
        c = re.search(rb'/Count\s+(\d+)', body)
        if not c:
            return None
        counts.add(int(c.group(1)))
    return counts.pop() if len(counts) == 1 else None


def mp4_seconds(f):
    """mp4 · mov 의 길이(초) — moov/mvhd 에서. 못 찾으면 None."""
    f.seek(0, 2)
    end = f.tell()

    def find(pos, stop, want):
        while pos + 8 <= stop:
            f.seek(pos)
            size, typ = struct.unpack('>I4s', f.read(8))
            hl = 8
            if size == 1:
                size, hl = struct.unpack('>Q', f.read(8))[0], 16
            elif size == 0:
                size = stop - pos
            if size < hl:
                return None
            if typ == want:
                return pos + hl, pos + size
            pos += size
        return None
    moov = find(0, end, b'moov')
    mvhd = moov and find(moov[0], moov[1], b'mvhd')
    if not mvhd:
        return None
    f.seek(mvhd[0])
    head = f.read(min(32, mvhd[1] - mvhd[0]))
    if len(head) < 20 or (head[0] == 1 and len(head) < 32):
        return None  # 모자란 mvhd(R01)
    ts, dur = struct.unpack('>IQ', head[20:32]) if head[0] == 1 else struct.unpack('>II', head[12:20])
    return dur / ts if ts and dur not in (0, 0xFFFFFFFF, 0xFFFFFFFFFFFFFFFF) else None


def unit_kinds(unit):
    u = nfc(unit).strip().lower()
    return {k for k, v in UNIT_KIND.items() if u in v}


def total_mismatch(meas, unit, total):
    """잰 분량과 total 이 확실히 다르면 (잰 값, 종류), 아니면 None"""
    for k in unit_kinds(unit):
        if k == 'minutes' and 'seconds' in meas:
            if abs(meas['seconds'] / 60 - total) > 1:
                return round(meas['seconds'] / 60, 1), k
        elif k == 'seconds' and 'seconds' in meas:
            if abs(meas['seconds'] - total) > 1:
                return round(meas['seconds'], 1), k
        elif k == 'lines' and k in meas:
            if abs(meas[k] - total) > 1:  # 끝 줄바꿈 셈법 차이는 봐준다
                return meas[k], k
        elif k in meas and meas[k] != total:
            return meas[k], k
    return None


def note_line(b):
    """노트의 내용 줄인가 — 글자 · 숫자가 있고 자리표시(없음 · TODO …)가 아니면. 링크 · 대괄호 글도 내용이다(R01)."""
    s = b.strip()
    return bool(re.search(r'\w', s)) and s.lower() not in PLACEHOLDERS


def note_problems(text, m, total):
    """분석 노트 → 문제 목록(빈 목록 = 통과)"""
    lines = text.splitlines()
    code, fence = set(), None
    for i, ln in enumerate(lines):  # 코드 블록(``` · ~~~ · 네 칸 들여쓰기) — 그 속 <div> · # 줄은 양식 글 · 절 제목이 아니다(R03 · R04)
        f = re.match(r'^\s{0,3}(`{3,}|~{3,})(.*)$', ln)
        if fence is None and f:
            fence = (f.group(1)[0], len(f.group(1)))
            code.add(i)
        elif fence is not None:
            code.add(i)
            if f and f.group(1)[0] == fence[0] and len(f.group(1)) >= fence[1] and not f.group(2).strip():
                fence = None  # 같은 글자로 같거나 더 긴 닫는 울타리만(R04)
        elif re.match(r'^(?: {4}|\t)', ln):
            code.add(i)
    heads = [i for i, ln in enumerate(lines) if i not in code and re.match(r'^\s{0,3}#{1,6}\s', ln)]
    marker = re.compile(r'^(?:[-*+]|\d+[.)]|\|)?\s*')
    holder = re.compile(r'^<(?![a-zA-Z][\w+.-]*:|[^<>\s@]+@)[^<>]*>\s*\|?$')  # 양식 글 <…> — 자동 링크 <https://…> · <a@b> 는 내용(R02)
    probs, chars = [], 0
    for key, may_none in NOTE_SECTIONS:
        h = next((i for i in heads if key.replace(' ', '') in lines[i].replace(' ', '')), None)
        if h is None:
            probs.append(f'「{key}」 절(# 제목)이 없습니다'); continue
        lvl = len(lines[h].strip()) - len(lines[h].strip().lstrip('#'))
        # 절은 같은 · 더 높은 단계의 다음 제목까지 — 「### 1쪽」 같은 아래 제목은 그 절의 내용이다
        stop = next((i for i in heads if i > h and len(lines[i].strip()) - len(lines[i].strip().lstrip('#')) <= lvl), len(lines))
        body = [marker.sub('', ln.strip().lstrip('#').strip()) for ln in lines[h + 1:stop] if ln.strip()]
        body = [b for b in body if b and not holder.match(b) and not re.fullmatch(r'[|:\-\s]+', b)]
        chars += sum(len(b) for b in body)
        good = body if may_none else [b for b in body if note_line(b)]
        if not good:
            probs.append(f'「{key}」 절이 비었습니다' + (' — 없으면 「없음」' if may_none else ' — 없으면 그 까닭을 적습니다'))
        elif key == '처음부터 끝까지' and isint(total) and len(good) < min(total, 5):
            probs.append(f'「{key}」 절이 {len(good)}줄뿐입니다 — 단위({m.get("unit")}) 순서대로 마지막까지(전체 {total}, 적어도 {min(total, 5)}줄)')
    left = [ln.strip() for i, ln in enumerate(lines) if i not in code and holder.match(marker.sub('', ln.strip()))]
    if left:
        probs.append(f'양식 글(<…>)이 {len(left)}줄 남았습니다 — 예: {left[0]}')
    if chars < NOTE_MIN_CHARS:
        probs.append(f'내용이 너무 짧습니다({chars}자 < {NOTE_MIN_CHARS}자) — 처음부터 끝까지 정리합니다')
    s = str(m.get('path') or '').strip()
    if not re.match(r'(?i)https?://', s):
        base = re.split(r'[\\/]', split_member(s)[1] or split_member(s)[0])[-1]
        if base and nfc(base).lower() not in nfc(text).lower():
            probs.append(f'원본 이름({base})이 노트에 없습니다 — 어느 자료의 노트인지 머리에 적습니다')
    return probs


def file_sha(f, chunk=1 << 20):
    h = hashlib.sha256()
    for b in iter(lambda: f.read(chunk), b''):
        h.update(b)
    return h.hexdigest()


def freshness(m, name, lec, budget):
    """(오류, 경고, 잰 분량) — 분석한 때의 파일(크기 · sha256)과 지금 파일을 견준다."""
    arc, mem = split_member(str(m.get('path')))
    lp = local_of(arc, lec)
    if lp is None or not lp.is_file():
        return [], [f'{name}: 이 PC 에서 찾지 못해 크기 · sha256 · 분량을 확인하지 못했습니다'], {}
    size, sha = m.get('size'), m.get('sha256')
    if not isint(size) or not (isinstance(sha, str) and re.fullmatch(r'[0-9a-fA-F]{64}', sha.strip())):
        return [f'{name}: 분석한 때의 크기(size) · sha256 을 적지 않았습니다 — check_ready.py add 가 적습니다(파일이 바뀌면 다시 분석하려고)'], [], {}
    try:
        if mem:
            with zipfile.ZipFile(lp) as z:
                info = z.getinfo(mem)
                cur = info.file_size
                data = z.read(info) if cur <= budget[0] else None

            def opener():
                return io.BytesIO(data)
        else:
            st = lp.stat()
            cur, data = st.st_size, None

            def opener():
                return open(lp, 'rb')
    except KeyError:
        return [f'{name}: 압축 파일 안에 이 파일이 없습니다(압축이 바뀜) — 다시 분석합니다'], [], {}
    except (OSError, zipfile.BadZipFile, ValueError, RuntimeError, NotImplementedError, EOFError, zlib.error) as e:  # 암호 zip · 깨진 압축 데이터(R01 · R03)
        return [], [f'{name}: 열지 못해 새로움을 확인하지 못했습니다({type(e).__name__})'], {}
    if cur != size:
        return [f'{name}: 분석한 뒤 파일이 바뀌었습니다(크기 {size} → {cur}) — 다시 열어 처음부터 끝까지 분석합니다'], [], {}
    if not mem and m.get('mtime_ns') is not None and m.get('mtime_ns') == st.st_mtime_ns:
        pass  # 크기 · 수정 시각이 그대로면 해시를 건너뛴다(훅 시간 한도)
    elif cur > budget[0] or (mem and data is None):
        return [], [f'{name}: 커서 이번에는 sha256 을 견주지 않고 크기만 견줬습니다'], {}
    else:
        budget[0] -= cur
        try:
            with opener() as f:
                now = file_sha(f)
        except OSError as e:
            return [], [f'{name}: 읽지 못해 sha256 을 견주지 못했습니다({e})'], {}
        if now != sha.strip().lower():
            return [f'{name}: 분석한 뒤 파일 내용이 바뀌었습니다(sha256) — 다시 열어 처음부터 끝까지 분석합니다'], [], {}
    return [], [], measure(mem or lp.name, opener, cur)


def skipped_of(doc):
    sc = doc.get('scope_cut')
    return [str(x) for x in sc.get('skipped') or [] if isinstance(x, str) and x.strip()] if isinstance(sc, dict) and isinstance(sc.get('skipped'), list) else []


def validate_v2(doc, lec, bases):
    """version 2 점검표 → (오류, 알림, 받은 자료로 맞춰 줄 경로 — folders · 뺀 파일)"""
    err, warn = [], []
    lec = pathlib.Path(lec)
    mats = [m for m in doc.get('materials') if isinstance(m, dict)] if isinstance(doc.get('materials'), list) else []
    folders = doc.get('folders', [])
    if not isinstance(folders, list):
        err.append('folders: 목록이어야 합니다'); folders = []
    folders = [f for f in folders if isinstance(f, dict)]
    sc = doc.get('scope_cut')
    if sc not in (None, '') and not isinstance(sc, (str, dict)):
        err.append('scope_cut: {"said": "<사용자 답 원문>", "skipped": [<뺀 파일>]} 꼴이어야 합니다')
    if isinstance(sc, dict):
        if not isinstance(sc.get('skipped', []), list):
            err.append('scope_cut.skipped: 목록이어야 합니다')
        elif skipped_of(doc) and not given(sc.get('said')):
            err.append('scope_cut: 뺀 파일(skipped)이 있는데 사용자 답 원문(said)이 없습니다 — 파일을 빼는 것은 사용자에게 묻고 그 답을 적은 때만')
    skipped = skipped_of(doc)
    budget = [HASH_BUDGET]
    notes = {}
    for i, m in enumerate(mats):
        if not filled(m.get('path')):
            continue
        name = str(m['path']).strip()
        url = bool(re.match(r'(?i)https?://', name))
        arc, mem = split_member(name)
        lp = None if url else local_of(arc, lec)
        if not mem and lp is not None and lp.is_dir():
            err.append(f'{name}: 폴더를 한 줄로 셀 수 없습니다 — folders 에 적고 안의 파일마다 한 줄(check_ready.py add 가 폅니다)'); continue
        if not mem and not url and is_archive(name):
            err.append(f'{name}: 압축 파일을 한 줄로 셀 수 없습니다 — folders 에 적고 안의 파일마다 한 줄(zip 은 「<zip>!/<안 경로>」, 다른 압축은 풀어서 extracted_to)'); continue
        unit, total, covered = m.get('unit'), m.get('total'), m.get('covered')
        if not filled(unit):
            err.append(f'{name}: 분량 단위(unit — 쪽 · 장 · 시트 · 줄 · 분 · 초 · 그림)를 적지 않았습니다')
        if not (isint(total) and total >= 1):
            err.append(f'{name}: 전체 분량(total)을 1 이상 정수로 적지 않았습니다')
        elif covered != total or not isint(covered):
            err.append(f'{name}: 처음부터 끝까지 보지 않았습니다(covered {covered!r} / total {total}) — 끝까지 보고 covered = total, 아니면 범위를 줄일지 사용자에게 묻습니다')
        note = m.get('note')
        if not filled(note):
            err.append(f'{name}: 분석 노트(note)가 없습니다 — 자료마다 노트 하나(무엇인가 · 처음부터 끝까지 정리 · 그대로 쓸 것 · 바꿀 곳 · 근거 · 확인 필요)')
        else:
            npth = local_of(note, lec)
            key = os.path.normcase(os.path.abspath(npth)) if npth is not None else str(note)
            if key in notes:
                err.append(f'{name}: 분석 노트를 {notes[key]} 과 같이 씁니다 — 자료마다 노트 하나')
            notes[key] = name
            if npth is None or not npth.is_file():
                err.append(f'{name}: 분석 노트 파일이 없습니다 — {note}')
            else:
                try:
                    text = npth.read_bytes().decode('utf-8-sig')
                except (OSError, UnicodeDecodeError) as e:
                    err.append(f'{name}: 분석 노트를 UTF-8 로 읽지 못했습니다({e})')
                else:
                    err += [f'{name}: 분석 노트 {note} — {p}' for p in note_problems(text, m, total)]
        if not url:
            fe, fw, meas = freshness(m, name, lec, budget)
            err += fe
            warn += fw
            if isint(total) and filled(unit) and meas:
                bad = total_mismatch(meas, unit, total)
                if bad:
                    err.append(f'{name}: 전체 분량(total {total} {unit})이 파일과 다릅니다(파일에서 센 값 {bad[0]}) — 처음부터 끝까지 다 보고 total · covered 를 고칩니다')
    idx = doc.get('index')
    if mats and not filled(idx):
        err.append('index: 받은 자료 목록(자료 → 분석 노트) 파일 경로를 적지 않았습니다 — check_ready.py index 가 만듭니다')
    elif mats:
        ip = local_of(idx, lec)
        try:
            itext = nfc(ip.read_bytes().decode('utf-8-sig')) if ip is not None and ip.is_file() else None
        except (OSError, UnicodeDecodeError):
            itext = None
        if itext is None:
            err.append(f'index: 받은 자료 목록 파일이 없거나 읽지 못했습니다 — {idx}(check_ready.py index 가 만듭니다)')
        else:
            gone = [str(m.get('note')) for m in mats if filled(m.get('note')) and nfc(re.split(r'[\\/]', str(m['note']).strip())[-1]) not in itext]
            if gone:
                err.append(f'index: 목록에 없는 분석 노트 {len(gone)}개 — {gone[0]} …(check_ready.py index 로 다시 만듭니다)')
    listed = [str(m.get('path')) for m in mats if filled(m.get('path'))]
    have = set().union(*(keys(q, bases) for q in listed + skipped)) if listed or skipped else set()
    rp_skip = [lec.joinpath(*READY_REL)] + [q for q in (local_of(s, lec) for s in skipped) if q is not None]  # 뺀 하위 폴더 · 파일은 위 폴더에서도 넘김(R03)
    if filled(doc.get('notes_dir')):
        nd = local_of(doc['notes_dir'], lec)
        if nd is not None:
            rp_skip.append(nd)
    for f in folders:
        if not filled(f.get('path')):
            err.append('folders: 경로(path)가 빈 줄이 있습니다'); continue
        if keys(str(f['path']), bases) & set().union(*(keys(q, bases) for q in skipped)) if skipped else False:
            continue  # 사용자 답과 함께 통째로 뺀 폴더 · 압축(R02)
        files, archives, fe = expand(f, lec, rp_skip)
        err += fe
        if files is None and not fe:
            warn.append(f'{f["path"]}: 이 PC 에서 열지 못해 안의 파일을 하나하나 세지 못했습니다(다른 PC · 드라이브)')
            continue
        for a in archives:
            if keys(a, bases) & have:
                continue  # 사용자 답과 함께 뺀(skipped) 압축(R01)
            if not any(same_material(a, g.get('path'), bases) for g in folders):
                err.append(f'{a}: 폴더 안의 압축 파일 — 풀어서 folders 에 {{"path": 이 파일, "extracted_to": 푼 폴더}} 로 적고 안의 파일마다 한 줄')
        miss = [x for x in files or [] if not (keys(x, bases) & have)]
        if miss:
            err.append(f'{f["path"]}: 안의 파일 {len(files)}개 가운데 {len(miss)}개가 materials 에 없습니다 — 하나하나 열어 분석해 한 줄씩(check_ready.py add), '
                       f'빼려면 사용자에게 묻고 scope_cut 에 답 원문(said)과 뺀 파일(skipped) — 예: ' + ' · '.join(miss[:5]) + (' …' if len(miss) > 5 else ''))
    return err, warn, [str(f.get('path')) for f in folders if filled(f.get('path'))] + skipped


def material_plan_lines(lec, paths):
    """듣기를 닫은 뒤(recommend.py listen --done) — 받은 자료를 하나하나 열어 분석하라는 안내 줄"""
    L = ['', '받은 자료 — 다른 일보다 먼저, 리더가 직접 하나하나 다 열어 처음부터 끝까지 분석 · 정리합니다(AGENTS.md 0절 8 · 스킬 3.0의 0):']
    for p in dict.fromkeys(paths):
        q = local_of(p, lec)
        if q is not None and q.is_dir():
            files, archives = walk(q)
            L.append(f'  - {p}  (폴더 — 안의 파일 {len(files)}개를 하나하나' + (f', 압축 {len(archives)}개는 풀어서' if archives else '') + ')')
        elif q is not None and q.is_file() and q.name.lower().endswith('.zip'):
            L.append(f'  - {p}  (zip — 안의 파일 {len(zip_members(q) or [])}개를 하나하나)')
        else:
            L.append(f'  - {p}' + ('' if q is None or q.exists() else '  (이 PC 에서 찾지 못함 — 경로를 확인합니다)'))
    if not paths:
        L.append('  - 말씀에서 찾은 경로 · 주소는 없습니다. 대화에 올린 첨부 파일 · 알려 준 폴더가 있으면 그것도 받은 자료입니다.')
    L += [f'  1) python3 -I {HERE / "check_ready.py"} init --lecture {lec}',
          f'  2) python3 -I {HERE / "check_ready.py"} add --lecture {lec} <받은 파일 · 폴더 · 압축 · 주소>...   (폴더 · 압축은 안의 파일마다 한 줄 · 분석 노트 틀)',
          '  3) 자료마다 전문 도구로 열어 노트(무엇인가 · 처음부터 끝까지 정리 · 그대로 쓸 것 · 바꿀 곳 · 근거 · 확인 필요)를 채우고 covered = total.',
          '     보조 에이전트 요약으로 대신하지 않습니다. 너무 많으면 줄이지 말고, 뺄 파일을 사용자에게 묻고 답 원문과 함께 scope_cut 에 적습니다.']
    return L


def legacy_v1(doc):
    """version 1(1.7.0) 점검표 → (오류, 알림). 2026-11-18 까지 확인받은 것만 받는다."""
    c = doc.get('confirmed') if isinstance(doc.get('confirmed'), dict) else {}
    at = str(c.get('at') or '').strip()
    if re.fullmatch(r'\d{4}-\d{2}-\d{2}', at) and at > LEGACY_UNTIL:
        return [f'version: 1.8.0 부터 새 점검표는 version 2 입니다(확인 {at}) — 자료마다 한 줄 · 분석 노트 · 분량(total = covered) · 크기 · sha256 (check_ready.py init · add)'], []
    return [], ['알림: 1.7.0 양식(version 1) 점검표라 하나하나(폴더 속 파일) · 분석 노트 · 분량 · 새로움은 검사하지 않았습니다 — 다음 일은 version 2(check_ready.py init · add)']


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
    warn = []
    if isinstance(doc, dict) and doc.get('version') == 2 and not isinstance(doc.get('version'), bool):
        e2, warn, extra = validate_v2(doc, lecture_dir, bases)  # 하나하나 · 처음부터 끝까지 · 새로움(1.8.0)
        err += e2
        listed = listed + extra  # 받은 폴더 · 압축(folders) · 사용자가 빼기로 한 파일(scope_cut.skipped)도 점검표에 있는 것
    elif isinstance(doc, dict) and doc.get('version', 1) == 1:
        e1, warn = legacy_v1(doc)
        err += e1
    for p in g['paths']:
        if not any(same_material(p, q, bases, loose=p in g['loose']) for q in listed):
            err.append(f'materials: 받은 자료가 점검표에 없습니다 — {p}')
    if g['ref'] and isinstance(doc, dict) and not doc.get('keep') and not any(e.startswith('keep') for e in err):
        err.append('keep: 인터뷰에서 레퍼런스를 받았는데 그대로 쓸 것 표가 비었습니다 — 레퍼런스에서 그대로 쓸 것을 먼저 뽑습니다')
    if err:
        return False, [f'준비 완료 점검표가 통과하지 못했습니다: {rp}'] + ['  - ' + e for e in err] + ['  ' + w for w in warn], doc
    return True, warn, doc


def summary_lines(doc, rp):
    """계획 문서에 넣을 「준비 완료 점검표」 절."""
    mats = doc.get('materials') or []
    c = doc.get('confirmed') or {}
    L = ['## 준비 완료 점검표 (스킬 3.0의 0-1 — 통과해야 만들기 시작)', '',
         f'- 점검표: `{rp}` — 받은 자료 {len(mats)}건 모두 리더가 끝까지 읽음 · 그대로 쓸 것 {len(doc.get("keep") or [])} · 바꿀 곳 {len(doc.get("change") or [])} · 위 문서 소주제 {len(doc.get("subtopics") or [])}',
         f'- 사용자 확인: {c.get("by")} · {c.get("at")} — 「{" ".join(str(c.get("said")).split())}」']
    sc = doc.get('scope_cut')
    if filled(sc):
        L.append(f'- 범위를 줄임(사용자 답): {" ".join(str(sc).split())}')
    elif isinstance(sc, dict) and given(sc.get('said')):
        L.append(f'- 범위를 줄임(사용자 답): {" ".join(str(sc["said"]).split())} — 뺀 파일 {len(skipped_of(doc))}개')
    if doc.get('version') == 2:
        L.insert(2, f'- 하나하나 · 처음부터 끝까지(1.8.0): 받은 폴더 · 압축 {len(doc.get("folders") or [])}개는 안의 파일마다 한 줄 · 자료마다 분석 노트 — 목록 `{doc.get("index")}`')
        L += ['', '| 자료 | 종류 | 분량(다 봄) | 전문 도구 | 분석 노트 |', '|---|---|---|---|---|']
        L += [f'| {str(m.get("path")).replace("|", "¦")} | {m.get("kind")} | {m.get("covered")}/{m.get("total")} {str(m.get("unit")).replace("|", "¦")} | {str(m.get("tool")).replace("|", "¦")} | {str(m.get("note")).replace("|", "¦")} |' for m in mats]
        L.append('')
        return L
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
    if not outside_ok(out, lecture_path(argv[1])):
        print(f'쓰지 않음: {out} 가 작업 폴더 밖(연결 폴더)으로 갑니다'); return 1
    out.parent.mkdir(parents=True, exist_ok=True)
    d = datetime.date.today().strftime('%y%m%d')
    doc = dict(json.loads(json.dumps(TEMPLATE)), notes_dir=NOTES_DIR.format(d=d), index=NOTES_DIR.format(d=d) + '/' + INDEX_NAME, materials=[])
    try:
        with open(out, 'xb') as fh:  # 그 사이 생긴 점검표를 덮지 않는다(R02)
            fh.write((json.dumps(doc, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
    except OSError as e:
        print(f'만들지 못했습니다: {out} ({e})'); return 1
    print(f'만듦: {out} — 받은 자료를 하나하나 더합니다: python3 {HERE / "check_ready.py"} add --lecture {argv[1]} <파일 · 폴더 · 압축 · 주소>...\n'
          '  (폴더 · 압축은 안의 파일마다 한 줄 · 자료마다 분석 노트 틀). 리더가 하나하나 열어 처음부터 끝까지 분석해 노트를 채우고 covered = total,\n'
          '  대조표(keep · change) · 소주제를 채운 뒤 사용자 확인을 받고 check_ready.py 로 검사합니다')
    return 0


def write_json(p, doc):
    """같은 폴더의 임시 파일에 다 쓴 뒤 바꿔 넣는다 — 쓰다 실패해도 옛 점검표가 남는다(R04)"""
    p = pathlib.Path(p)
    tmp = p.with_name(p.name + '.tmp-' + str(os.getpid()))
    try:
        tmp.write_bytes((json.dumps(doc, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
        os.replace(tmp, p)
    finally:
        if tmp.exists():
            tmp.unlink()


def safe_name(s):
    s = nfc(s).replace('.', '_')
    s = re.sub(r'[\s<>:"/\\|?*\x00-\x1f]+', '_', s).strip('_ ')
    return s[:60] or '자료'


NOTE_SKELETON = '''# {nn} {base} — 받은 자료 분석

- 원본: `{path}`
- 분량: {total} {unit} · 크기 {size} 바이트 · sha256 {sha}

## 무엇인가
<이 자료가 무엇이고 이 일에서 어떤 자리인지(레퍼런스 · 위 문서 · 양식 · 원자료) · 열어 본 도구>

## 처음부터 끝까지 정리
<쪽 · 절 · 시트 · 장면 순서대로 한 단위에 한 줄 이상 — 마지막 단위까지>

## 이 일에 그대로 쓸 것
<이름 · 직위 · 소속 · 제목 · 칸 이름 · 소주제 · 본문 부호 · 표 꼴 · 쪽 배치 — 값과 쪽. 없으면 그 까닭>

## 바꿀 곳 · 근거
<바꿀 곳 · 새 값 · 근거(무엇이 달라져서) · 쪽. 없으면 「없음」>

## 확인 필요
<확인하지 못한 것 · 자료끼리 어긋난 곳. 없으면 「없음」>
'''


def outside_ok(p, lec):
    """p 가(연결 폴더를 풀어도) 작업 폴더 안인가(R02)"""
    lec_r, q = pathlib.Path(lec).resolve(), pathlib.Path(p).resolve()
    return q == lec_r or lec_r in q.parents


def own_spot(p, lec, ext):
    """add · index 가 쓸 자리 검사 — 문제가 있으면 까닭(빈 글 = 괜찮음). 작업 폴더 안 · 점검표가 아님 · 남의 파일을 덮지 않음(R01)."""
    if p is None:
        return '경로가 없습니다'
    lec_r, q = pathlib.Path(lec).resolve(), pathlib.Path(p).resolve()
    if q != lec_r and lec_r not in q.parents:
        return f'{p} 는 작업 폴더 밖입니다'
    if q == lec_r.joinpath(*READY_REL).resolve():
        return f'{p} 는 점검표 자리입니다'
    if not ext and q.exists() and not q.is_dir():
        return f'{p} 는 폴더가 아닙니다'
    if ext and q.is_dir():
        return f'{p} 는 폴더입니다'
    if ext and q.suffix.lower() != ext:
        return f'{p} 는 {ext} 파일이어야 합니다'
    if ext and q.is_file():
        try:
            first = q.read_bytes()[:200].decode('utf-8', 'replace')
        except OSError:
            return f'{p} 를 읽지 못했습니다'
        if not first.lstrip('\ufeff').startswith(INDEX_HEAD) and q.name != INDEX_NAME:  # \uc774 \ub3c4\uad6c\uc758 \ubaa9\ub85d \uc774\ub984\uc774\uba74 \ub2e4\uc2dc \ub9cc\ub4e0\ub2e4
            return f'{p} 는 이 도구가 만든 목록이 아니라 덮어쓰지 않습니다'
    return ''


INDEX_HEAD = '# 받은 자료 목록'


def write_index(lec, doc):
    """받은 자료 → 분석 노트 목록(index)을 점검표에서 다시 만든다"""
    ip = local_of(doc.get('index'), lec)
    if ip is None or not filled(doc.get('index')) or own_spot(ip, lec, '.md'):
        return None
    L = ['# 받은 자료 목록 — 하나하나 · 처음부터 끝까지', '',
         '이 목록은 `check_ready.py index` · `add` 가 준비 완료 점검표(materials/00_준비점검표.json)에서 다시 만든다. 손으로 고치지 않는다.', '']
    for f in doc.get('folders') or []:
        if isinstance(f, dict):
            L.append(f'- 받은 폴더 · 압축: `{f.get("path")}`' + (f' → 푼 곳 `{f.get("extracted_to")}`' if filled(f.get('extracted_to')) else ''))
    L += ['', '| 번호 | 자료 | 종류 | 분량(다 봄) | 분석 노트 |', '|---|---|---|---|---|']
    for i, m in enumerate(doc.get('materials') or [], 1):
        if isinstance(m, dict):
            nt = str(m.get('note') or '')
            L.append(f'| {i} | `{str(m.get("path")).replace("|", "¦")}` | {m.get("kind")} | {m.get("covered")}/{m.get("total")} {str(m.get("unit")).replace("|", "¦")} | '
                     f'[{nt.replace(chr(92), "/").rsplit("/", 1)[-1]}]({nt.replace(chr(92), "/").rsplit("/", 1)[-1].replace(" ", "%20")}) |')
    sk = skipped_of(doc)
    if sk:
        L += ['', f'뺀 파일 {len(sk)}개(사용자 답: {(doc.get("scope_cut") or {}).get("said")}):'] + [f'- `{x}`' for x in sk]
    try:
        ip.parent.mkdir(parents=True, exist_ok=True)
        ip.write_bytes(('\n'.join(L) + '\n').encode('utf-8'))
    except OSError:
        return None  # 위 경로가 파일인 자리 등(R03)
    return ip


def load_ready(lec):
    rp = lec.joinpath(*READY_REL)
    try:
        doc = json.loads(rp.read_text(encoding='utf-8-sig'))
    except (OSError, ValueError) as e:
        print(f'준비 완료 점검표를 읽지 못했습니다: {rp} ({e}) — 먼저 check_ready.py init'); return None, rp
    if not isinstance(doc, dict) or doc.get('version') != 2:
        print(f'version 2 점검표가 아닙니다: {rp} — add · index 는 version 2(1.8.0) 점검표에만 씁니다'); return None, rp
    return doc, rp


def cmd_index(argv):
    if len(argv) != 2 or argv[0] != '--lecture' or not argv[1].strip():
        print(__doc__, file=sys.stderr); return 2
    lec = lecture_path(argv[1])
    doc, _ = load_ready(lec)
    if doc is None:
        return 1
    ip = write_index(lec, doc)
    print(f'목록을 다시 만듦: {ip}' if ip else f'목록을 쓰지 않았습니다: {doc.get("index")!r}(빈 칸 · 작업 폴더 밖 · 이 도구가 만들지 않은 파일 · 폴더 · 쓸 수 없는 자리)'); return 0 if ip else 1


def cmd_add(argv):
    lecture, kind, items, i = None, None, [], 0
    while i < len(argv):
        if argv[i] in ('--lecture', '--kind') and i + 1 < len(argv) and argv[i + 1].strip():
            if argv[i] == '--lecture':
                lecture = argv[i + 1]
            else:
                kind = argv[i + 1]
            i += 2
        elif argv[i].startswith('--'):
            print(__doc__, file=sys.stderr); return 2
        else:
            items.append(argv[i]); i += 1
    if not lecture or not items or (kind is not None and kind not in KINDS):
        print(__doc__, file=sys.stderr); return 2
    lec = lecture_path(lecture)
    doc, rp = load_ready(lec)
    if doc is None:
        return 1
    import store as ST
    bases = (lec, ST.project_root())
    mats = doc.setdefault('materials', [])
    folders = doc.setdefault('folders', [])
    if not isinstance(mats, list) or not isinstance(folders, list):
        print('materials · folders 가 목록이 아닙니다 — 고친 뒤 다시'); return 1
    have = set().union(*(keys(m.get('path'), bases) for m in mats if isinstance(m, dict))) if mats else set()
    nd = doc.get('notes_dir') if filled(doc.get('notes_dir')) else NOTES_DIR.format(d=datetime.date.today().strftime('%y%m%d'))
    bad = ('' if outside_ok(rp, lec) else f'{rp} 가 작업 폴더 밖(연결 폴더)입니다') or own_spot(local_of(nd, lec), lec, '') or (filled(doc.get('index')) and own_spot(local_of(doc['index'], lec), lec, '.md'))
    if bad:
        print(f'쓰지 않음: {bad}'); return 1
    skip = [rp] + ([local_of(nd, lec)] if local_of(nd, lec) is not None else [])
    new, warn = [], []
    for it in items:
        s = it.strip()
        p = local_of(s, lec)
        if p is not None and (p.is_dir() or (p.is_file() and is_archive(p.name))):
            if not any(same_material(s, f.get('path'), bases) for f in folders if isinstance(f, dict)):
                folders.append({'path': str(p) if os.path.isabs(s) or s.startswith('~') else s})
            if p.is_file() and not p.name.lower().endswith('.zip'):
                warn.append(f'{s}: zip 이 아닌 압축 — 풀어서 folders 의 이 줄에 "extracted_to" 를 적고 그 폴더를 add 합니다'); continue
            files, archives, _ = expand({'path': str(p)}, lec, skip)
            new += files or []
            warn += [f'{a}: 폴더 안의 압축 — 풀어서 add 합니다(folders 에 extracted_to)' for a in archives]
        elif p is not None and not p.exists() and MEMBER not in s:
            warn.append(f'{s}: 이 PC 에서 찾지 못했습니다 — 경로를 확인합니다(그래도 줄은 더함)'); new.append(s)
        else:
            new.append(str(p) if p is not None and (os.path.isabs(s) or s.startswith('~')) else s)
    added = 0
    width = 3 if len(mats) + len(new) > 99 else 2
    for s in new:
        k = keys(s, bases)
        if k & have:
            continue
        have |= k
        n = len(mats) + 1
        arc, mem = split_member(s)
        base = re.split(r'[\\/]', mem or arc.rstrip('/\\'))[-1] if not re.match(r'(?i)https?://', s) else re.sub(r'(?i)^https?://', '', s).rstrip('/')
        stem = safe_name(base)
        note = f'{nd}/{n:0{width}d}_{stem}' + ('' if '_' in stem or '.' in base else '_분석') + '.md'
        row = {'path': s, 'kind': kind or '<reference|upstream|form|source|other>', 'read_by': '<leader>', 'read': '<all>',
               'range': '<읽은 범위>', 'tool': '<전문 도구>', 'unit': '<쪽 · 장 · 시트 · 줄 · 분 · 초 · 그림>', 'total': 0, 'covered': 0, 'note': note}
        lp = local_of(arc, lec)
        if lp is not None and lp.is_file():
            try:
                if mem:
                    with zipfile.ZipFile(lp) as z:
                        data = z.read(mem)
                    row.update(size=len(data), sha256=hashlib.sha256(data).hexdigest())
                    meas = measure(mem, lambda d=data: io.BytesIO(d), len(data))
                else:
                    st = lp.stat()
                    with open(lp, 'rb') as f:
                        row.update(size=st.st_size, sha256=file_sha(f), mtime_ns=st.st_mtime_ns)
                    meas = measure(lp.name, lambda: open(lp, 'rb'), st.st_size)
            except (OSError, KeyError, zipfile.BadZipFile, RuntimeError, NotImplementedError, EOFError, zlib.error) as e:
                warn.append(f'{s}: 읽지 못했습니다({e})'); meas = {}
            for k_, u in (('slides', '장'), ('sheets', '시트'), ('pages', '쪽'), ('lines', '줄'), ('seconds', '초')):
                if k_ in meas:
                    row.update(unit=u, total=int(-(-meas[k_] // 1)))
                    break
        np_ = local_of(note, lec)
        if not outside_ok(np_, lec):
            print(f'쓰지 않음: 노트 {np_} 가 작업 폴더 밖(연결)으로 갑니다'); return 1
        try:
            np_.parent.mkdir(parents=True, exist_ok=True)
        except OSError as e:  # 위 경로가 파일인 자리 등(R03) — FileExistsError 도 여기서는 실패
            print(f'노트 폴더를 만들지 못했습니다(점검표는 그대로): {np_.parent} ({e})'); return 1
        try:
            with open(np_, 'xb') as fh:  # 있는 노트는 덮지 않는다
                fh.write(NOTE_SKELETON.format(nn=f'{n:0{width}d}', base=base, path=s, total=row['total'] or '<전체>', unit=row['unit'],
                                                 size=row.get('size', '<이 PC 에 없음>'), sha=str(row.get('sha256', '-'))[:12]).encode('utf-8'))
        except FileExistsError:
            pass
        except OSError as e:
            print(f'노트를 만들지 못했습니다(점검표는 그대로): {np_} ({e})'); return 1
        mats.append(row)
        added += 1
    doc['notes_dir'] = nd
    if not filled(doc.get('index')):
        doc['index'] = nd + '/' + INDEX_NAME
    try:
        write_json(rp, doc)
    except OSError as e:
        print(f'점검표를 저장하지 못했습니다(옛 점검표는 그대로): {rp} ({e})'); return 1
    ip = write_index(lec, doc)
    if ip is None:
        warn.append(f'목록(index {doc.get("index")!r})을 쓰지 못했습니다 — 자리를 고친 뒤 check_ready.py index')
    for w in warn:
        print('알림: ' + w)
    print(f'더함: {added}줄(이미 있던 {len(new) - added}줄은 그대로) · 분석 노트 틀 · 목록 {ip}\n'
          '  다음: 리더가 자료를 하나하나 직접 열어 처음부터 끝까지 분석해 노트를 채우고, 줄마다 kind · read_by · read · range · tool 과 covered(= total)를 적습니다.')
    return 0 if ip else 1


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
    bad(lambda d: d.update(version=3), 'version', '모르는 version → 실패')
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
    selftest_v2(ok)
    print('실패 ' + str(len(fails)) if fails else '자체 시험 통과')
    return 1 if fails else 0


def _fixture(root):
    """받은 폴더 하나(글 · 슬라이드 · 표 · PDF · 영상 · zip · 잡음)를 만든다"""
    src = root / '받은폴더'
    (src / 'sub').mkdir(parents=True)
    (src / 'a.txt').write_bytes('첫 줄\n둘째 줄\n셋째 줄\n'.encode('utf-8'))
    (src / 'sub' / 'b.md').write_bytes('# 제목\n\n본문 한 줄\n'.encode('utf-8'))
    for junk in ('Thumbs.db', '.DS_Store', '~$잠금.docx', '._a.txt'):
        (src / junk).write_bytes(b'x')
    (src / '.git').mkdir()
    (src / '.git' / 'config').write_bytes(b'x')
    with zipfile.ZipFile(src / 'deck.pptx', 'w') as z:
        z.writestr('[Content_Types].xml', '<x/>')
        z.writestr('ppt/presentation.xml', '<p:presentation><p:sldIdLst><p:sldId id="256"/><p:sldId id="257"/><p:sldId id="258"/></p:sldIdLst></p:presentation>')
        for k in (1, 2, 3):
            z.writestr(f'ppt/slides/slide{k}.xml', '<p:sld/>')
        z.writestr('ppt/slides/_rels/slide1.xml.rels', '<x/>')
    with zipfile.ZipFile(src / 'book.xlsx', 'w') as z:
        z.writestr('xl/workbook.xml', '<workbook><sheets><sheet name="가" sheetId="1"/><sheet name="나" sheetId="2"/></sheets></workbook>')
    (src / 'doc.pdf').write_bytes(b'%PDF-1.4\n1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n2 0 obj << /Type /Pages /Kids [3 0 R 4 0 R] /Count 2 >> endobj\n'
                                  b'3 0 obj << /Type /Page /Parent 2 0 R >> endobj\n4 0 obj << /Type /Page /Parent 2 0 R >> endobj\ntrailer << /Root 1 0 R >>\n%%EOF\n')
    mvhd = struct.pack('>I4sB3sIIII', 108, b'mvhd', 0, b'\0\0\0', 0, 0, 1000, 10000) + bytes(80)
    (src / 'clip.mp4').write_bytes(struct.pack('>I4s4sI', 16, b'ftyp', b'isom', 0) + struct.pack('>I4s', 8 + len(mvhd), b'moov') + mvhd)
    with zipfile.ZipFile(src / 'inner.zip', 'w') as z:
        z.writestr('c.txt', '한 줄\n')
        z.writestr('__MACOSX/._c.txt', 'x')
        z.writestr('d/', '')
    return src


def _good_note(m):
    s = str(m['path'])
    base = re.split(r'[\\/]', split_member(s)[1] or s)[-1]
    rows = '\n'.join(f'- {k}번째 단위: {base} 의 이 부분을 직접 열어 처음부터 끝까지 읽고 정리한 줄이다' for k in range(1, max(2, min(m['total'], 5)) + 1))
    return (f'# {base} 분석\n\n## 무엇인가\n{base} 는 받은 폴더에 든 시험용 원자료다. 이 일에서 바탕 자료 자리이고, 전문 도구로 열어 처음부터 끝까지 보았다. '
            f'어긋난 곳이 있으면 확인 필요 절에 적는다.\n\n## 처음부터 끝까지 정리\n{rows}\n\n## 이 일에 그대로 쓸 것\n- 제목 꼴과 표 꼴을 그대로 쓴다(1쪽)\n\n'
            '## 바꿀 곳 · 근거\n없음\n\n## 확인 필요\n없음\n')


def selftest_v2(ok):
    """version 2(1.8.0) — 하나하나 · 처음부터 끝까지 · 새로움 · 옛 양식"""
    global HASH_BUDGET
    import contextlib
    tmp = pathlib.Path(tempfile.mkdtemp(prefix='tl-ready2-'))
    old_env = os.environ.get('TASTE_LOOP_PROJECT')
    os.environ['TASTE_LOOP_PROJECT'] = str(tmp)  # 프로젝트 루트를 git 으로 찾지 않게(빠르기) · 시험 폴더 밖을 보지 않게
    try:
        lec = tmp / 'work'
        (lec / 'materials' / '인터뷰').mkdir(parents=True)
        src = _fixture(tmp)
        q = io.StringIO()
        with contextlib.redirect_stdout(q):
            c_init = cmd_init(['--lecture', str(lec)])
            c_add = cmd_add(['--lecture', str(lec), '--kind', 'source', str(src)])
        rp = lec.joinpath(*READY_REL)
        doc = json.loads(rp.read_text(encoding='utf-8'))
        paths = [m['path'] for m in doc['materials']]
        names = sorted(re.split(r'[\\/]', split_member(p)[1] or p)[-1] for p in paths)
        ok(c_init == 0 and c_add == 0 and doc['version'] == 2 and re.fullmatch(r'materials/\d{6}_받은자료분석', doc['notes_dir']),
           f'init 은 version 2 · 날짜 붙은 노트 폴더, add 는 받은 폴더를 폄({c_init} · {c_add})')
        ok(names == ['a.txt', 'b.md', 'book.xlsx', 'c.txt', 'clip.mp4', 'deck.pptx', 'doc.pdf'],
           f'add: 폴더 안의 파일마다 한 줄(하위 폴더 · zip 안까지, 잡음 · 폴더 줄 뺌) — {names}')
        meas = {re.split(r'[\\/]', split_member(m['path'])[1] or m['path'])[-1]: (m['total'], m['unit']) for m in doc['materials']}
        ok(meas.get('deck.pptx') == (3, '장') and meas.get('book.xlsx') == (2, '시트') and meas.get('doc.pdf') == (2, '쪽')
           and meas.get('clip.mp4') == (10, '초') and meas.get('a.txt') == (3, '줄') and meas.get('c.txt') == (1, '줄'),
           f'add: 셀 수 있는 분량을 파일에서 셈(pptx 장 · xlsx 시트 · pdf 쪽 · mp4 초 · 글 줄) — {meas}')
        ok(all(isinstance(m.get('sha256'), str) and len(m['sha256']) == 64 and isint(m.get('size')) for m in doc['materials']), 'add: 자료마다 크기 · sha256')
        ok(all(local_of(m['note'], lec).is_file() for m in doc['materials']) and local_of(doc['index'], lec).is_file(), 'add: 자료마다 분석 노트 틀 · 목록 파일')
        doc['confirmed'] = {'by': '사용자', 'at': '2026-11-19', 'said': '좋아 이대로'}
        doc.update(keep=[], subtopics=[])  # 원자료(source)뿐 — 대조표 · 소주제는 이 시험의 대상이 아님
        for m in doc['materials']:
            m.update(read_by='leader', read='all', range='처음부터 끝까지', tool='전문 도구', covered=m['total'])
        write_json(rp, doc)
        g, n, _ = gate(lec, {})
        ok(not g and any('양식 글' in x for x in n), '노트 틀(<…>)만 두고 채우지 않으면 막음')
        for m in doc['materials']:
            local_of(m['note'], lec).write_bytes(_good_note(m).encode('utf-8'))
        good = json.loads(json.dumps(doc))
        notes0 = {m['note']: local_of(m['note'], lec).read_bytes() for m in doc['materials']}

        def check(change=None, note=None, msg='', want=None, passes=False, ans=None):
            d = json.loads(json.dumps(good))
            if change:
                change(d)
            write_json(rp, d)
            if note:
                note(d)
            g, n, _ = gate(lec, ans if ans is not None else {})
            hit = passes and g or (not passes and not g and (want is None or any(want in x for x in n)))
            ok(hit, msg + ('' if hit else f' — {n[:4]}'))
            for k, v in notes0.items():
                local_of(k, lec).write_bytes(v)
            write_json(rp, good)
            write_index(lec, good)
        check(msg='version 2: 하나하나 · 처음부터 끝까지 · 노트 · 목록이 다 맞으면 통과', passes=True)
        first = good['materials'][0]['path']
        check(lambda d: d['materials'].pop(0), msg='폴더 안의 파일이 한 줄이라도 빠지면 막음', want='materials 에 없습니다')
        check(lambda d: (d['materials'].pop(0), d.update(scope_cut={'said': '그 파일은 빼', 'skipped': [first]})), msg='사용자 답과 함께 뺀 파일(skipped)은 통과', passes=True)
        zm = next(m['path'] for m in good['materials'] if MEMBER in m['path'])
        check(lambda d: (d['materials'].__setitem__(slice(None), [m for m in d['materials'] if m['path'] != zm]), d.update(scope_cut={'said': 'zip 안 c.txt 는 빼', 'skipped': [zm]})),
              msg='사용자 답과 함께 뺀 zip 안의 파일도 통과', passes=True)
        check(lambda d: (d['materials'].pop(0), d.update(scope_cut={'said': '', 'skipped': [first]})), msg='뺀 파일이 있는데 사용자 답(said)이 없으면 막음', want='said')
        check(lambda d: d['materials'][0].update(covered=d['materials'][0]['total'] - 1 if d['materials'][0]['total'] > 1 else 0), msg='covered < total → 막음', want='처음부터 끝까지 보지 않았습니다')
        check(lambda d: d['materials'][0].update(total=0, covered=0), msg='total 없음 → 막음', want='1 이상 정수')
        check(lambda d: d['materials'][0].update(unit=''), msg='단위 없음 → 막음', want='단위')
        check(lambda d: d['materials'][0].pop('note'), msg='분석 노트 칸 없음 → 막음', want='분석 노트(note)가 없습니다')
        check(note=lambda d: local_of(d['materials'][0]['note'], lec).unlink(), msg='분석 노트 파일 없음 → 막음', want='분석 노트 파일이 없습니다')
        dk = next(m for m in good['materials'] if m['path'].endswith('deck.pptx'))
        dk_i = good['materials'].index(dk)

        def edit_note(fn, i=dk_i):
            return lambda d: local_of(d['materials'][i]['note'], lec).write_bytes(fn(local_of(d['materials'][i]['note'], lec).read_text(encoding='utf-8')).encode('utf-8'))
        check(note=edit_note(lambda t: t.replace('## 확인 필요', '## 기타')), msg='노트에 필요한 절(확인 필요)이 없으면 막음', want='「확인 필요」 절')
        check(note=edit_note(lambda t: t.replace('## 무엇인가\n', '## 무엇인가\n<무엇인지>\n')), msg='노트에 양식 글(<…>)이 남으면 막음', want='양식 글')
        check(note=edit_note(lambda t: re.sub(r'(## 처음부터 끝까지 정리\n)(?:- .*\n)+', r'\1- 한 줄만 정리\n', t)), msg='처음부터 끝까지 절이 단위 수보다 적으면 막음(3장인데 1줄)', want='줄뿐입니다')
        check(note=edit_note(lambda t: '# deck.pptx\n## 무엇인가\n슬라이드\n## 처음부터 끝까지\n- 1장 표지\n- 2장 목차\n- 3장 끝\n## 그대로 쓸 것\n- 제목\n## 바꿀 곳\n없음\n## 확인 필요\n없음\n'),
              msg='노트가 너무 짧으면 막음', want='너무 짧습니다')
        check(note=edit_note(lambda t: re.sub(r'(## 처음부터 끝까지 정리\n)((?:- .*\n)+)', lambda mm: mm.group(1) + ''.join(
                  f'### {k}장\n{ln[2:]}\n' for k, ln in enumerate(mm.group(2).splitlines(), 1)), t)),
              msg='「처음부터 끝까지」 아래를 ### 소제목(1장 · 2장 …)으로 나눠 써도 통과', passes=True)
        check(note=edit_note(lambda t: t.replace('deck.pptx', '다른자료.pptx')), msg='노트에 원본 이름이 없으면 막음(다른 자료의 노트)', want='원본 이름')
        check(note=edit_note(lambda t: t.replace('## 이 일에 그대로 쓸 것\n- 제목 꼴과 표 꼴을 그대로 쓴다(1쪽)\n', '## 이 일에 그대로 쓸 것\n없음\n')),
              msg='「그대로 쓸 것」 은 「없음」만으로는 막음(까닭을 적음)', want='「그대로 쓸 것」 절이 비었습니다')
        check(lambda d: d['materials'][1].update(note=d['materials'][0]['note']), msg='두 자료가 노트 하나를 같이 쓰면 막음', want='같이 씁니다')
        check(note=lambda d: local_of(d['index'], lec).write_bytes('# 목록\n'.encode('utf-8')), msg='목록(index)에 노트가 빠지면 막음', want='목록에 없는 분석 노트')
        check(lambda d: d.update(index=''), msg='목록(index) 칸이 비면 막음', want='파일 경로를 적지 않았습니다')
        check(lambda d: d['materials'][dk_i].pop('sha256'), msg='크기 · sha256 을 적지 않으면 막음', want='sha256 을 적지 않았습니다')
        a_i = next(i for i, m in enumerate(good['materials']) if m['path'].endswith('a.txt'))
        a_path = pathlib.Path(good['materials'][a_i]['path'])
        a0 = a_path.read_bytes()
        try:
            a_path.write_bytes(a0.replace('첫'.encode('utf-8'), '새'.encode('utf-8')))  # 크기는 같고 내용만 바뀜
            check(msg='분석한 뒤 내용이 바뀌면(sha256) 막음 — 다시 분석', want='내용이 바뀌었습니다')
            HASH_BUDGET, keep_budget = 1, HASH_BUDGET
            try:
                check(msg='해시 상한을 넘으면 크기만 견주고 막지 않음(알림)', passes=True)
            finally:
                HASH_BUDGET = keep_budget
            a_path.write_bytes(a0 + '넷째 줄\n'.encode('utf-8'))
            check(msg='분석한 뒤 크기가 바뀌면 막음 — 다시 분석', want='크기')
        finally:
            a_path.write_bytes(a0)
        os.utime(a_path, ns=(a_path.stat().st_atime_ns, a_path.stat().st_mtime_ns + 10 ** 9))
        check(msg='수정 시각만 바뀌고 내용이 같으면 통과(해시로 견줌)', passes=True)
        for nm, wrong in (('deck.pptx', 4), ('book.xlsx', 3), ('doc.pdf', 3), ('clip.mp4', 20), ('a.txt', 9)):
            i_ = next(i for i, m in enumerate(good['materials']) if m['path'].endswith(nm))
            check(lambda d, i_=i_, w=wrong: d['materials'][i_].update(total=w, covered=w), msg=f'{nm}: 전체 분량이 파일과 다르면 막음', want='파일과 다릅니다')
        check(lambda d: d['materials'][dk_i].update(unit='그림', total=1, covered=1), note=edit_note(lambda t: t),
              msg='단위가 셀 수 있는 종류가 아니면 분량을 견주지 않음(불확실하면 막지 않음)', passes=True)
        i_ = next(i for i, m in enumerate(good['materials']) if m['path'].endswith('clip.mp4'))
        check(lambda d: d['materials'][i_].update(unit='분', total=1, covered=1), msg='영상 10초를 1분으로 적어도 단위를 바꿔 견줌(1 이내 통과)', passes=True)
        check(lambda d: d['materials'].append(dict(d['materials'][0], path=str(src), note='materials/x.md')), msg='폴더를 materials 한 줄로 적으면 막음', want='폴더를 한 줄로')
        check(lambda d: d['materials'].append(dict(d['materials'][0], path=str(src / 'inner.zip'), note='materials/x.md')), msg='압축 파일을 materials 한 줄로 적으면 막음', want='압축 파일을 한 줄로')
        check(lambda d: d['folders'].append({'path': str(tmp / '이PC에없는폴더')}), msg='이 PC 에 없는 받은 폴더는 알리고 막지 않음', passes=True)
        check(lambda d: d['materials'].append(dict(d['materials'][0], path=str(tmp / '없는자료.pdf'), note=d['materials'][0]['note'].replace('.md', '_없음.md'))),
              note=lambda d: (local_of(d['materials'][-1]['note'], lec).write_bytes(_good_note(d['materials'][-1]).encode('utf-8')), write_index(lec, d)),
              msg='이 PC 에 없는 자료는 크기 · 분량을 확인하지 못했다고 알리고 막지 않음', passes=True)
        reco = lec / 'materials' / '인터뷰' / '00_추천.json'
        reco.write_text(json.dumps({'attachments': [{'path': str(src), 'read': 'all'}]}, ensure_ascii=False), encoding='utf-8')
        check(msg='인터뷰 · 추천의 받은 폴더는 folders 에 있으면 점검표에 있는 것', passes=True)
        reco.unlink()
        sev = src / '묶음.7z'
        sev.write_bytes(b'7z')
        check(msg='폴더 안의 zip 아닌 압축은 풀어 적기 전에는 막음', want='폴더 안의 압축 파일')
        ex = tmp / '묶음_풀림'
        ex.mkdir()
        (ex / 'e.txt').write_bytes('e\n'.encode('utf-8'))
        check(lambda d: d['folders'].append({'path': str(sev), 'extracted_to': str(ex)}), msg='푼 폴더(extracted_to)의 파일도 하나하나 요구', want=str(ex / 'e.txt'))
        sev.unlink()
        shutil.rmtree(ex)
        pdf2 = src / 'doc.pdf'
        p0 = pdf2.read_bytes()
        try:
            pdf2.write_bytes(p0.replace(b'trailer', b'5 0 obj << /Type /ObjStm /N 1 >> endobj\ntrailer'))
            i_ = next(i for i, m in enumerate(good['materials']) if m['path'].endswith('doc.pdf'))
            check(lambda d: d['materials'][i_].update(total=7, covered=7, size=len(pdf2.read_bytes()), sha256=hashlib.sha256(pdf2.read_bytes()).hexdigest()),
                  note=lambda d: local_of(d['materials'][i_]['note'], lec).write_bytes(_good_note(d['materials'][i_]).encode('utf-8')), msg='압축 개체(ObjStm)가 든 PDF 는 쪽 수를 견주지 않음(불확실하면 막지 않음)', passes=True)
        finally:
            pdf2.write_bytes(p0)
        check(lambda d: d.update(version=1, confirmed=dict(d['confirmed'], at='2026-11-18')), msg='옛 양식(version 1) · 2026-11-18 까지 확인 → 알림만, 통과', passes=True)
        check(lambda d: d.update(version=1), msg='옛 양식(version 1)인데 2026-11-19 확인 → 막음(version 2 로)', want='version 2')
        # R01 코덱스 보고(거짓 막힘 · 고장 · 자료 손상)
        bz = io.BytesIO()
        with zipfile.ZipFile(bz, 'w') as z:
            z.writestr('ppt/presentation.xml', '<p:presentation><p:sldIdLst><p:sldId id="256"/></p:sldIdLst></p:presentation>')
            z.writestr('ppt/slides/custom.xml', '<p:sld/>')
            z.writestr('ppt/slides/slide9.xml', '<p:sld/>')
            z.writestr('ppt/slides/slide10.xml', '<p:sld/>')
        ok(measure('a.pptx', lambda: io.BytesIO(bz.getvalue()), 1) == {'slides': 1}, 'R01: pptx 장 수는 presentation.xml 의 장 목록으로 셈(파일 이름 아님)')
        ok(measure('a.txt', lambda: io.BytesIO(b'a\rb\rc\rd\re'), 9) == {'lines': 5} and measure('b.txt', lambda: io.BytesIO(b'a\r\nb\r\n'), 6) == {'lines': 2},
           'R01: CR · CRLF 줄끝도 줄로 셈')
        ok(measure('a.mp4', lambda: io.BytesIO(bytes.fromhex('000000106d6f6f76000000086d766864')), 16) == {}, 'R01: 모자란 mvhd 는 모름으로(추적 출력 없이)')
        ezip = tmp / '암호.zip'
        with zipfile.ZipFile(ezip, 'w') as z:
            z.writestr('secret.txt', b'plain')
        eb = bytearray(ezip.read_bytes())
        for sig, off in ((b'PK\x03\x04', 6), (b'PK\x01\x02', 8)):  # 암호 표시(flag 0x1)만 켬
            i0 = eb.find(sig)
            eb[i0 + off] |= 0x1
        ezip.write_bytes(bytes(eb))
        try:
            fe, fw, _ = freshness({'path': str(ezip) + MEMBER + 'secret.txt', 'size': 5, 'sha256': hashlib.sha256(b'plain').hexdigest()}, 'x', lec, [HASH_BUDGET])
            ok(not fe and fw, f'R01: 암호 걸린 zip 안의 파일은 알림만(추적 출력 없이) {fe} {fw}')
        except Exception as e:  # noqa: BLE001
            ok(False, f'R01: 암호 걸린 zip → {type(e).__name__}')
        sev = src / '묶음.7z'
        sev.write_bytes(b'7z')
        check(lambda d: d.update(scope_cut={'said': '묶음.7z 는 빼', 'skipped': [str(sev)]}), msg='R01: 사용자 답과 함께 뺀 압축은 풀라고 하지 않음', passes=True)
        sev.unlink()
        check(note=edit_note(lambda t: re.sub(r'(## 처음부터 끝까지 정리\n)((?:- .*\n)+)', lambda mm: mm.group(1) + ''.join(
                  f'{k}. [{ln[2:]}](https://example.org/{k})\n' for k, ln in enumerate(mm.group(2).splitlines(), 1)), t)),
              msg='R01: 링크로 된 정리 줄(「[문장](주소)」)도 내용으로 셈', passes=True)
        ck0 = rp.read_bytes()
        with contextlib.redirect_stdout(io.StringIO()):
            for bad_idx in ('materials/00_준비점검표.json', '../밖/목록.md', 'materials/남의파일.md'):
                if bad_idx.endswith('남의파일.md'):
                    (lec / 'materials' / '남의파일.md').write_bytes('# 내 메모\n'.encode('utf-8'))
                write_json(rp, dict(good, index=bad_idx))
                ci = cmd_index(['--lecture', str(lec)])
                ca = cmd_add(['--lecture', str(lec), str(src / 'a.txt')])
                ok(ci == 1 and ca == 1 and json.loads(rp.read_text(encoding='utf-8'))['index'] == bad_idx and not (tmp / '밖').exists()
                   and (not bad_idx.endswith('남의파일.md') or (lec / 'materials' / '남의파일.md').read_bytes() == '# 내 메모\n'.encode('utf-8')),
                   f'R01: index 가 점검표 · 작업 폴더 밖 · 남의 파일이면 index · add 가 쓰지 않음({bad_idx} → {ci} · {ca})')
            write_json(rp, dict(good, notes_dir='../밖'))
            ok(cmd_add(['--lecture', str(lec), str(src / 'a.txt')]) == 1 and not (tmp / '밖').exists(), 'R01: notes_dir 가 작업 폴더 밖이면 add 가 쓰지 않음')
            nd_bad = dict(good, notes_dir='materials/00_준비점검표.json')
            write_json(rp, nd_bad)
            ok(cmd_add(['--lecture', str(lec), str(src / 'a.txt')]) == 1 and json.loads(rp.read_text(encoding='utf-8')) == nd_bad, 'R01: notes_dir 가 파일(점검표) 자리면 add 가 쓰지 않음(추적 출력 없이)')
        rp.write_bytes(ck0)
        # R02 코덱스 보고
        ok(measure('u.txt', lambda: io.BytesIO(('a' + chr(13) + chr(10)).encode('utf-16') * 1 + ('a' + chr(13) + chr(10)).encode('utf-16-le') * 4), 9) == {'lines': 5},
           'R02: UTF-16 글은 풀어서 줄을 셈')
        ok(measure('u.txt', lambda: io.BytesIO('a\nb\n'.encode('utf-16-le')), 8) == {}, 'R02: BOM 없는 UTF-16(NUL 바이트)은 세지 않음')
        for nm_, part, tag in (('u.pptx', 'ppt/presentation.xml', '<p:presentation><p:sldIdLst><p:sldId id="1"/><p:sldId id="2"/></p:sldIdLst></p:presentation>'),
                               ('u.xlsx', 'xl/workbook.xml', '<workbook><sheets><sheet name="a"/><sheet name="b"/></sheets></workbook>')):
            bz = io.BytesIO()
            with zipfile.ZipFile(bz, 'w') as z:
                z.writestr(part, ('<?xml version="1.0" encoding="UTF-16"?>' + tag).encode('utf-16'))
            got = measure(nm_, lambda bz=bz: io.BytesIO(bz.getvalue()), 1)
            ok(list(got.values()) == [2], f'R02: UTF-16 XML 의 {nm_} 도 셈({got})')
        check(note=edit_note(lambda t: t.replace('## 확인 필요\n', '## 확인 필요\n<https://example.org/source>\n')), msg='R02: 노트의 자동 링크 <https://…> 는 양식 글이 아님', passes=True)
        sev = tmp / '통째.7z'
        sev.write_bytes(b'7z')
        check(lambda d: (d['folders'].append({'path': str(sev)}), d.update(scope_cut={'said': '통째로 빼', 'skipped': [str(sev)]})),
              msg='R02: folders 의 압축을 사용자 답과 함께 통째로 빼면 풀라고 하지 않음', passes=True)
        sev.unlink()
        ck0 = rp.read_bytes()
        idx_dir = lec / 'materials' / '목록폴더.md'
        idx_dir.mkdir()
        with contextlib.redirect_stdout(io.StringIO()):
            write_json(rp, dict(good, index='materials/목록폴더.md'))
            (tmp / '추가3.txt').write_bytes(b'x')
            ok(cmd_index(['--lecture', str(lec)]) == 1 and cmd_add(['--lecture', str(lec), str(tmp / '추가3.txt')]) == 1
               and json.loads(rp.read_text(encoding='utf-8')) == dict(good, index='materials/목록폴더.md'), 'R02: index 자리가 폴더면 index · add 가 점검표도 바꾸지 않음(추적 출력 없이)')
        idx_dir.rmdir()
        rp.write_bytes(ck0)
        ok(not outside_ok(lec / 'materials' / '..' / '..' / '밖' / 'x.json', lec) and outside_ok(rp, lec), 'R02: 작업 폴더 밖으로 풀리는 자리를 가림')
        # R03 코덱스 보고
        bz = io.BytesIO()
        with zipfile.ZipFile(bz, 'w', zipfile.ZIP_DEFLATED) as z:
            z.writestr('ppt/presentation.xml', '<p:presentation><p:sldIdLst>' + '<p:sldId id="1"/>' * 50 + '</p:sldIdLst></p:presentation>')
        zb = bytearray(bz.getvalue())
        zb[zb.find(b'ppt/presentation.xml') + len('ppt/presentation.xml')] = 0x07  # 압축 데이터 첫 바이트를 깨뜨림
        try:
            ok(measure('z.pptx', lambda: io.BytesIO(bytes(zb)), 1) == {}, 'R03: 깨진 압축 데이터(zlib)는 모름으로')
        except Exception as e:  # noqa: BLE001
            ok(False, f'R03: 깨진 압축 데이터 → {type(e).__name__}')
        ok(measure('w.txt', lambda: io.BytesIO(('a' + chr(13) + chr(10)).encode('utf-32') + ('a' + chr(13) + chr(10)).encode('utf-32-le') * 4), 9) == {'lines': 5}, 'R03: UTF-32 글은 UTF-32 로 풀어 셈')
        bz = io.BytesIO()
        with zipfile.ZipFile(bz, 'w') as z:
            z.writestr('ppt/presentation.xml', '<p:presentation><p:sldIdLst><p:sldId id="1"/><!-- removed: <p:sldId id="2"/> --></p:sldIdLst></p:presentation>')
        ok(measure('c.pptx', lambda: io.BytesIO(bz.getvalue()), 1) == {'slides': 1}, 'R03: XML 주석 속 장은 세지 않음')
        check(note=edit_note(lambda t: t.replace('## 확인 필요\n', '## 확인 필요\n```html\n<div>\n</div>\n```\n    <span>\n')), msg='R03: 코드 블록 속 <div> 줄은 양식 글이 아님', passes=True)
        exd = src / 'sub'
        check(lambda d: (d['folders'].append({'path': str(exd)}), d['materials'].__setitem__(slice(None), [m for m in d['materials'] if not m['path'].endswith('b.md')]),
                         d.update(scope_cut={'said': 'sub 폴더는 빼', 'skipped': [str(exd)]})),
              msg='R03: 사용자 답과 함께 뺀 하위 폴더의 파일을 위 폴더에서 다시 요구하지 않음', passes=True)
        ck0 = rp.read_bytes()
        (lec / 'materials' / 'blocked.txt').write_bytes(b'x')
        with contextlib.redirect_stdout(io.StringIO()):
            write_json(rp, dict(good, index='materials/blocked.txt/list.md'))
            try:
                ci = cmd_index(['--lecture', str(lec)])
            except Exception as e:  # noqa: BLE001
                ci = type(e).__name__
            write_json(rp, dict(good, notes_dir='materials/blocked.txt/notes'))
            try:
                (tmp / '추가.txt').write_bytes(b'x')
                ca = cmd_add(['--lecture', str(lec), str(tmp / '추가.txt')])
            except Exception as e:  # noqa: BLE001
                ca = type(e).__name__
        ok(ci == 1 and ca == 1 and json.loads(rp.read_text(encoding='utf-8'))['notes_dir'] == 'materials/blocked.txt/notes', f'R03: 위 경로가 파일인 목록 · 노트 자리 → 종료 1(추적 출력 없이, {ci} · {ca})')
        (lec / 'materials' / 'blocked.txt').unlink()
        rp.write_bytes(ck0)
        # R04 코덱스 보고(마지막 회차 — 모두 REALISTIC)
        check(note=edit_note(lambda t: t.replace('## 처음부터 끝까지 정리\n', '## 처음부터 끝까지 정리\n```markdown\n# Original title\n```\n')),
              msg='R04: 코드 블록 속 # 줄은 절 제목이 아님', passes=True)
        check(note=edit_note(lambda t: t.replace('## 확인 필요\n', '## 확인 필요\n````markdown\n```html\n<div>\n```\n<span>\n````\n')),
              msg='R04: 바깥 울타리(````) 안의 ``` 는 닫는 울타리가 아님', passes=True)
        import stat
        ck0 = rp.read_bytes()
        (tmp / '추가2.txt').write_bytes(b'x')
        os.chmod(rp, stat.S_IREAD)
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                try:
                    cw = cmd_add(['--lecture', str(lec), str(tmp / '추가2.txt')])
                except Exception as e:  # noqa: BLE001
                    cw = type(e).__name__
        finally:
            os.chmod(rp, stat.S_IREAD | stat.S_IWRITE)
        if os.name == 'nt' or rp.read_bytes() != ck0:  # 리눅스 root 는 읽기 전용도 바꿀 수 있어 Windows 에서만 따짐
            ok(cw == 1 and rp.read_bytes() == ck0 and not list(rp.parent.glob('*.tmp-*')), f'R04: 점검표를 저장하지 못하면 종료 1 · 옛 점검표 그대로 · 임시 파일 없음({cw})')
        rp.write_bytes(ck0)
        link_dir = lec / 'materials' / '링크노트'
        link_dir.mkdir()
        try:
            os.symlink(tmp / '밖노트.md', link_dir / '01_a_txt.md')
            linked = True
        except (OSError, NotImplementedError):
            linked = False  # Windows 는 권한이 없으면 링크를 못 만든다 — 그때는 이 시험을 건너뜀
        if linked:
            write_json(rp, dict(good, notes_dir='materials/링크노트', materials=[], index='materials/링크노트/00_받은자료_목록.md'))
            with contextlib.redirect_stdout(io.StringIO()):
                cl = cmd_add(['--lecture', str(lec), str(src / 'a.txt')])
            ok(cl == 1 and not (tmp / '밖노트.md').exists(), f'R03: 노트 자리가 밖을 가리키는 링크면 쓰지 않음({cl})')
        shutil.rmtree(link_dir, ignore_errors=True)
        rp.write_bytes(ck0)
        ok(pdf_pages(b'2 0 obj << /Type /Pages /Count 3 >> endobj 9 0 obj << /Type /Pages /Count 5 >> endobj') is None, 'PDF 뿌리 쪽 목록이 둘이고 수가 다르면 세지 않음(덧붙여 저장한 PDF)')
        ok(total_mismatch({'lines': 3}, '줄', 4) is None and total_mismatch({'lines': 3}, '줄', 5) is not None, '글 줄 수는 끝 줄바꿈 차이(1)를 봐줌')
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            ok(cmd_add(['--lecture', str(lec)]) == 2 and cmd_add(['--lecture', str(lec), '--kind', 'etc', str(src)]) == 2, 'add: 자료 없음 · 모르는 종류 → 종료 2')
        rp.write_text(json.dumps(dict(good, version=1)), encoding='utf-8')
        with contextlib.redirect_stdout(io.StringIO()):
            ok(cmd_add(['--lecture', str(lec), str(src)]) == 1, 'add: version 1 점검표에는 쓰지 않음(종료 1)')
    finally:
        if old_env is None:
            os.environ.pop('TASTE_LOOP_PROJECT', None)
        else:
            os.environ['TASTE_LOOP_PROJECT'] = old_env
        shutil.rmtree(tmp, ignore_errors=True)


def main(argv):
    if argv[:1] == ['selftest'] and len(argv) == 1:
        return cmd_selftest()
    if argv[:1] == ['template'] and len(argv) == 1:
        print(json.dumps(TEMPLATE, ensure_ascii=False, indent=1)); return 0
    if argv[:1] == ['init']:
        return cmd_init(argv[1:])
    if argv[:1] == ['add']:
        return cmd_add(argv[1:])
    if argv[:1] == ['index']:
        return cmd_index(argv[1:])
    if argv in ([], ['-h'], ['--help']):
        print(__doc__); return 0 if argv else 2
    return cmd_check(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
