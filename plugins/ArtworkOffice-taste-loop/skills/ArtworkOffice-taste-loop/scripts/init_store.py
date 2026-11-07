#!/usr/bin/env python3
"""빈 데이터 폴더(취향 저장소)를 만든다 — 처음 설치한 뒤 한 번.

사용법:
  python3 init_store.py                프로젝트 안: <프로젝트 루트>/.claude/ArtworkOffice-taste-loop-data/
  python3 init_store.py --personal     개인용: ~/.claude/ArtworkOffice-taste-loop-data/ (여러 프로젝트에서 같은 취향)
  python3 init_store.py --to <폴더>    원하는 곳

starter/의 기본 차원·질문 은행·빈 취향·빈 기록을 복사한다. 이미 있는 파일은 덮어쓰지 않는다.
"""
import pathlib
import shutil
import sys

sys.dont_write_bytecode = True  # 설치 폴더(플러그인 캐시)에 __pycache__ 를 만들지 않는다
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import store as S  # noqa: E402


def main(argv):
    if '--to' in argv:
        dest = pathlib.Path(argv[argv.index('--to') + 1]).expanduser().resolve()
    elif '--personal' in argv:
        dest = pathlib.Path.home() / '.claude' / S.DATA_DIRNAME
    else:
        dest = S.project_root() / '.claude' / S.DATA_DIRNAME
    made, kept = [], []
    for src in sorted(S.STARTER.rglob('*')):
        if src.is_dir() or src.name == '.gitkeep':
            continue
        rel = src.relative_to(S.STARTER)
        out = dest / rel
        if out.exists():
            kept.append(str(rel)); continue
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, out)
        made.append(str(rel))
    (dest / 'knowledge' / 'projects').mkdir(parents=True, exist_ok=True)
    print(f'데이터 폴더: {dest}')
    print(f'새로 만든 파일 {len(made)}개' + (f', 그대로 둔 파일 {len(kept)}개' if kept else ''))
    print('다음: python3 check_store.py  (검증과 요약 생성)')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
