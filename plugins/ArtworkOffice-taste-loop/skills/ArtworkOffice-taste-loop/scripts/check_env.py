#!/usr/bin/env python3
"""환경 점검 — 어떤 도구가 있고 없는지 표로 보여 준다. 막지 않는다.

사용법:
  python3 check_env.py              표 출력
  python3 check_env.py --brief      한두 줄 요약(세션 시작 훅용)
  python3 check_env.py --json       JSON 출력
  python3 check_env.py --strict pc  PC 모드 필수 도구가 없으면 종료 코드 1 (기본은 항상 0)

판정 낱말: 가능 / 설치 필요 / 원칙상 불가 (knowledge/06_환경_점검_기준.md)
커넥터·MCP(Higgsfield·Figma)는 스크립트가 볼 수 없다. Claude가 도구 목록에서 확인해 표에 보탠다.
"""
import json
import os
import pathlib
import platform
import shutil
import subprocess
import sys

# (명령, 용도, 어디서 쓰나, 중요도) — 어디서: all / pc ; 중요도: required / optional / agent
TOOLS = [
    ('python3', '스킬 스크립트', 'all', 'required'),
    ('git', '커밋·push', 'all', 'required'),
    ('node', 'jsdom 검증·kordoc·템플릿 빌드', 'all', 'required'),
    ('kordoc', '원자료 해독(HWP·PDF 등)', 'all', 'optional'),
    ('ieumoffice', '문서 편집·변환', 'all', 'optional'),
    ('ffmpeg', '영상 처리·단일 파일 압축', 'all', 'optional'),
    ('ffprobe', '영상 정보', 'all', 'optional'),
    ('exiftool', '사진 정보', 'all', 'optional'),
    ('tesseract', 'OCR', 'all', 'optional'),
    ('ego-browser', '브라우저 화면 검수·스크린샷 (규칙 3.1)', 'pc', 'required'),
    ('codex', 'Codex 에이전트(장면 코딩)', 'pc', 'agent'),
    ('agy', 'Antigravity CLI(가벼운 글 작업)', 'pc', 'agent'),
    ('gemini', 'Gemini CLI', 'pc', 'agent'),
    ('higgsfield', 'Higgsfield CLI', 'pc', 'optional'),
]


def version_of(cmd):
    try:
        out = subprocess.run([cmd, '--version'], capture_output=True, text=True, timeout=8)
        line = (out.stdout or out.stderr).strip().splitlines()
        return line[0][:40] if line else ''
    except Exception:  # noqa: BLE001
        return ''


def jsdom_path():
    for base in [os.environ.get('NODE_PATH', ''), '/tmp/slidecheck/node_modules']:
        if base and pathlib.Path(base, 'jsdom', 'package.json').exists():
            return base
    return ''


def collect():
    cloud = os.environ.get('CLAUDE_CODE_REMOTE') == 'true'
    rows = []
    for cmd, use, where, level in TOOLS:
        found = shutil.which(cmd)
        if found:
            status, hint = '가능', version_of(cmd)
        elif cloud and where == 'pc':
            status, hint = '원칙상 불가', '클라우드에서는 쓰지 않음 → 「PC에서 할 일」'
        else:
            status, hint = '설치 필요', ('docs/setup.md' if pathlib.Path('docs/setup.md').exists() else '스킬 README 「설치」')
        rows.append({'tool': cmd, 'use': use, 'where': where, 'level': level, 'status': status, 'hint': hint})
    jp = jsdom_path()
    rows.append({'tool': 'jsdom', 'use': 'HTML 검증', 'where': 'all', 'level': 'optional',
                 'status': '가능' if jp else '설치 필요', 'hint': jp or 'npm install --prefix /tmp/slidecheck jsdom@24.1.3'})
    env = {
        'session': '클라우드' if cloud else '로컬',
        'os': f'{platform.system()} {platform.release()}',
        'python': platform.python_version(),
        'cwd': os.getcwd(),
        'computer': platform.node(),
    }
    return env, rows


def main(argv):
    env, rows = collect()
    strict = argv[argv.index('--strict') + 1] if '--strict' in argv and argv.index('--strict') + 1 < len(argv) else None
    missing_required = [r['tool'] for r in rows if r['level'] == 'required' and r['status'] != '가능'
                        and (r['where'] == 'all' or strict in ('pc', 'hybrid'))]
    if '--json' in argv:
        print(json.dumps({'env': env, 'tools': rows, 'missing_required': missing_required}, ensure_ascii=False, indent=1))
    elif '--brief' in argv:
        ok = [r['tool'] for r in rows if r['status'] == '가능']
        need = [r['tool'] for r in rows if r['status'] == '설치 필요']
        no = [r['tool'] for r in rows if r['status'] == '원칙상 불가']
        print(f"환경: {env['session']} ({env['os']}). 가능: {', '.join(ok) or '없음'}. 설치 필요: {', '.join(need) or '없음'}. "
              f"이 환경에서 원칙상 불가: {', '.join(no) or '없음'}. 커넥터(Higgsfield·Figma)는 도구 목록에서 확인.")
    else:
        print(f"세션: {env['session']} · OS: {env['os']} · Python {env['python']} · PC 이름: {env['computer']}")
        print('| 도구 | 용도 | 어디서 | 중요도 | 판정 | 비고 |')
        print('|---|---|---|---|---|---|')
        for r in rows:
            print(f"| {r['tool']} | {r['use']} | {'PC' if r['where'] == 'pc' else '모두'} | {r['level']} | {r['status']} | {r['hint']} |")
        print('| Higgsfield 커넥터/MCP | 이미지·영상 생성 | 모두 | optional | (Claude가 도구 목록에서 확인) | 클라우드: mcp__Higgsfield__* · PC: .mcp.json |')
        print('| Figma 커넥터/MCP | 디자인 기준·레퍼런스 | 모두 | optional | (Claude가 도구 목록에서 확인) | 클라우드: mcp__Figma__* · PC: .mcp.json |')
        if missing_required:
            print('필수 도구 없음:', ', '.join(missing_required))
    return 1 if (strict and missing_required) else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
