#!/usr/bin/env python3
"""ArtworkOffice-taste-loop — 엔진(스킬 폴더)과 데이터(사용자 저장소)의 위치를 찾는 공통 모듈.

엔진: 이 파일이 있는 스킬 폴더(SKILL.md, GUI-Interview.html, scripts/, starter/). 누구에게나 같다.
데이터: 사용자마다 다르다(취향·차원·질문·선택별 진화 기록·교훈·실수·프로젝트 기록).

데이터 폴더를 찾는 순서:
  1. 환경 변수 TASTE_LOOP_STORE
  2. <프로젝트 루트>/.claude/ArtworkOffice-taste-loop-data/   (있으면)
  3. ~/.claude/ArtworkOffice-taste-loop-data/                (있으면 — 여러 프로젝트에서 같은 취향을 쓸 때)
  4. 엔진의 starter/ (빈 저장소 — 읽기만. 쓰려면 init_store.py로 데이터 폴더를 만든다)

프로젝트 루트: 환경 변수 TASTE_LOOP_PROJECT → CLAUDE_PROJECT_DIR → 현재 폴더의 git 최상위 → 현재 폴더.
"""
import os
import pathlib
import subprocess

NAME = 'ArtworkOffice-taste-loop'
DATA_DIRNAME = NAME + '-data'
ENGINE = pathlib.Path(__file__).resolve().parent.parent
STARTER = ENGINE / 'starter'


def project_root():
    for var in ('TASTE_LOOP_PROJECT', 'CLAUDE_PROJECT_DIR'):
        v = os.environ.get(var)
        if v and pathlib.Path(v).is_dir():
            return pathlib.Path(v).resolve()
    try:
        # git 은 경로를 UTF-8 로 낸다. text=True 는 Windows 에서 CP949 로 읽어 한글 경로가 깨지므로 직접 푼다
        out = subprocess.run(['git', 'rev-parse', '--show-toplevel'], capture_output=True, timeout=5)
        top = (out.stdout or b'').decode('utf-8', 'replace').strip()
        if out.returncode == 0 and top:
            return pathlib.Path(top).resolve()
    except Exception:  # noqa: BLE001
        pass
    return pathlib.Path.cwd().resolve()


def candidates():
    v = os.environ.get('TASTE_LOOP_STORE')
    if v:
        yield pathlib.Path(v).expanduser().resolve(), 'TASTE_LOOP_STORE'
    yield project_root() / '.claude' / DATA_DIRNAME, '프로젝트'
    yield pathlib.Path.home() / '.claude' / DATA_DIRNAME, '개인(~/.claude)'


def store_dir():
    """(데이터 폴더, 출처 설명, 쓸 수 있는가). 데이터 폴더가 없으면 starter(읽기 전용)."""
    for p, how in candidates():
        if how == 'TASTE_LOOP_STORE' or (p / 'preferences.json').exists():
            return p, how, True
    return STARTER, 'starter(빈 저장소 — init_store.py로 데이터 폴더를 만드세요)', False


STORE, STORE_HOW, STORE_WRITABLE = store_dir()
KNOW = STORE / 'knowledge'


def path(name):
    """데이터 파일 경로. 데이터 폴더에 없으면 starter의 같은 파일(기본값)."""
    p = STORE / name
    if p.exists() or STORE == STARTER:
        return p
    s = STARTER / name
    return s if s.exists() else p


if __name__ == '__main__':
    print(f'엔진: {ENGINE}')
    print(f'프로젝트 루트: {project_root()}')
    print(f'데이터: {STORE} ({STORE_HOW}{"" if STORE_WRITABLE else ", 읽기 전용"})')
