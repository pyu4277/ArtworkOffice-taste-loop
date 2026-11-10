#!/usr/bin/env python3
"""환경 점검 — 어떤 도구가 있고 없는지 표로 보여 준다. 막지 않는다.

사용법:
  python3 check_env.py              표 출력
  python3 check_env.py --brief      한두 줄 요약(세션 시작 훅용)
  python3 check_env.py --json       JSON 출력
  python3 check_env.py --strict pc  PC 모드 필수 도구가 없으면 종료 코드 1 (기본은 항상 0)

판정 낱말: 가능 / 설치 필요 / 원칙상 불가 (knowledge/06_환경_점검_기준.md)
커넥터·MCP(Higgsfield·Figma)는 스크립트가 볼 수 없다. Claude가 도구 목록에서 확인해 표에 보탠다.

프로젝트 필수 도구(1.3.1): 데이터 폴더의 env_tools.json 에 적은 도구를 엔진 기본 목록에 더해 판정한다.
  {"tools": [{"name", "use", "where": "all|pc", "level": "required|optional|agent", "install": "<설치 안내>",
              "check": {"command": "<명령>", "args": [...]}                       ← 실행해서 종료 코드 0 이면 가능
                    | {"path_record": "<PC별 설치 기록 json>", "key": "<도구>", "cloud_path": "<클라우드 경로>", "needs": ["<있어야 할 파일>"]}}]}
  --brief 는 이 세션에 해당하는 필수 도구 가운데 없는 것을 「필수 중 없음」으로 알린다(세션 시작 훅).
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


def decode(b):
    """하위 프로세스 출력(바이트) → 글. UTF-8 을 먼저, 안 되면 이 PC 의 기본 인코딩(Windows 는 CP949).
    text=True 로 받으면 Windows 에서 읽기 스레드가 UnicodeDecodeError 를 내고 stdout 이 None 이 된다."""
    if not b:
        return ''
    try:
        return b.decode('utf-8')
    except UnicodeDecodeError:
        pass
    # Windows 명령의 오류문은 OEM(콘솔) · ANSI 코드 페이지(한국어 CP949). -X utf8 에서는 locale 이 utf-8 이라 직접 고른다
    for enc in (('oem', 'mbcs') if os.name == 'nt' else ()):
        try:
            return b.decode(enc)
        except (UnicodeDecodeError, LookupError):
            continue
    import locale
    enc = locale.getencoding() if hasattr(locale, 'getencoding') else locale.getpreferredencoding(False)
    return b.decode(enc or 'utf-8', 'replace')


def version_of(cmd):
    try:
        out = subprocess.run([cmd, '--version'], capture_output=True, timeout=8)
        line = (decode(out.stdout) or decode(out.stderr)).strip().splitlines()
        return line[0][:40] if line else ''
    except Exception:  # noqa: BLE001
        return ''


def jsdom_path():
    for base in [os.environ.get('NODE_PATH', ''), '/tmp/slidecheck/node_modules']:
        if base and pathlib.Path(base, 'jsdom', 'package.json').exists():
            return base
    return ''


def python_cmd():
    """실제로 실행되는 파이썬 3.8 이상 명령을 고른다. 이름 찾기(which)만으로 판정하지 않는다:
    Windows 의 python3 는 마이크로소프트 스토어 바로가기(실행하면 오류만 내는 가짜)일 수 있다(실수 기록 E22)."""
    for c in (['python', 'py', 'python3'] if os.name == 'nt' else ['python3', 'python', 'py']):
        if not shutil.which(c):
            continue
        try:
            r = subprocess.run([c, '-c', 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)'],
                               capture_output=True, timeout=8)
        except Exception:  # noqa: BLE001
            continue
        if r.returncode == 0:
            return c
    return ''


def _store():
    """데이터 폴더 모듈(store.py) — check_env 는 -I 로 돌아 스크립트 폴더가 sys.path 에 없어 직접 넣는다."""
    try:
        sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
        import store as ST  # noqa: E402
        return ST
    except Exception:  # noqa: BLE001
        return None


def resolve_cmd(name):
    """`orca` 는 Linux 에서 GNOME 화면 낭독기와 이름이 같다 — Orca 가 알려 준 명령(ORCA_CLI_COMMAND)이나 orca-ide 를 쓴다."""
    if name == 'orca':
        return os.environ.get('ORCA_CLI_COMMAND') or ('orca-ide' if sys.platform.startswith('linux') else 'orca')
    return name


def check_project_tool(t, cloud, ST):
    """env_tools.json 의 도구 하나 → (판정, 비고). check 는 command(실행해서 종료 코드 0) 또는 path_record(PC별 설치 기록)."""
    c = t.get('check') or {}
    install = t.get('install') or 'docs/setup.md'
    if cloud and t.get('where', 'all') == 'pc':
        return '원칙상 불가', '클라우드에서는 쓰지 않음 → 「PC에서 할 일」'
    if c.get('command'):
        exe = shutil.which(resolve_cmd(c['command']))
        if not exe:
            return '설치 필요', install
        try:
            r = subprocess.run([exe, *c.get('args', ['--version'])], capture_output=True, timeout=float(c.get('timeout', 10)))
        except Exception as e:  # noqa: BLE001
            return '설치 필요', f'실행 실패({str(e)[:60]}) — {install}'
        lines = (decode(r.stdout) or decode(r.stderr)).strip().splitlines()
        if r.returncode == 0:
            return '가능', (lines[0][:60] if lines and not lines[0].startswith('{') else 'ok')
        return '설치 필요', f'종료 코드 {r.returncode}' + (f': {lines[-1][:60]}' if lines else '') + f' — {install}'
    path = None
    if cloud and c.get('cloud_path'):
        path = pathlib.Path(c['cloud_path'])
    elif c.get('path_record'):
        root = ST.project_root() if ST else pathlib.Path.cwd()
        try:
            rec = json.loads((root / c['path_record']).read_text(encoding='utf-8'))
            me = platform.node().upper()
            hit = next((e for e in (rec.get(c.get('key'), {}) or {}).get('installs', []) if str(e.get('computer') or '').upper() == me), None)
            path = pathlib.Path(hit['path']) if hit and hit.get('path') else None
        except (OSError, ValueError):
            return '설치 필요', f"기록 파일을 읽을 수 없음({c['path_record']}) — {install}"
        if path is None:
            return '설치 필요', f'이 PC({platform.node()}) 기록 없음 — {install}'
    if path is None:
        return '설치 필요', f'점검 방법(check)이 없음 — env_tools.json'
    missing = [n for n in c.get('needs', []) if not (path / n).exists()]
    if not path.exists() or missing:
        return '설치 필요', f"{path} 에 {', '.join(missing) or '폴더'} 없음 — {install}"
    return '가능', str(path)


def project_rows(cloud):
    """데이터 폴더의 env_tools.json — 이 프로젝트에서 꼭 있어야 하는 도구(엔진 기본 목록에 더한다)."""
    ST = _store()
    if not ST:
        return []
    p = ST.path('env_tools.json')
    if not p.exists():
        return []
    try:
        spec = json.loads(p.read_text(encoding='utf-8'))
    except ValueError as e:
        return [{'tool': 'env_tools.json', 'use': '프로젝트 필수 도구 목록', 'where': 'all', 'level': 'required', 'status': '설치 필요', 'hint': f'읽기 실패: {e}'[:80]}]
    rows = []
    for t in spec.get('tools', []):
        status, hint = check_project_tool(t, cloud, ST)
        rows.append({'tool': t.get('name', '?'), 'use': t.get('use', ''), 'where': t.get('where', 'all'), 'level': t.get('level', 'required'),
                     'status': status, 'hint': hint, 'project': True})
    return rows


def collect():
    cloud = os.environ.get('CLAUDE_CODE_REMOTE') == 'true'
    rows = []
    for cmd, use, where, level in TOOLS:
        if cmd == 'python3':  # 이름이 아니라 실제로 실행되는 명령으로 판정한다(E22)
            py = python_cmd()
            label = cmd if py in ('', 'python3') else f'{cmd}→{py}'
            if py:
                hint = version_of(py) + ('' if py == 'python3' else f' (python3 대신 {py} 를 쓴다)')
                rows.append({'tool': label, 'use': use, 'where': where, 'level': level, 'status': '가능', 'hint': hint})
            else:
                rows.append({'tool': label, 'use': use, 'where': where, 'level': level, 'status': '설치 필요',
                             'hint': 'python3 이름은 있어도 실행되지 않으면 설치 필요(스토어 바로가기 등)'})
            continue
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
    rows += project_rows(cloud)
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
        # 이 세션에 해당하는 필수 도구(클라우드면 「모두」만, PC면 PC 전용까지) 가운데 없는 것 — 시작 전에 설치한다
        must = [r['tool'] for r in rows if r['level'] == 'required' and r['status'] == '설치 필요' and (r['where'] == 'all' or env['session'] == '로컬')]
        print(f"환경: {env['session']} ({env['os']}). 가능: {', '.join(ok) or '없음'}. 설치 필요: {', '.join(need) or '없음'}. "
              f"이 환경에서 원칙상 불가: {', '.join(no) or '없음'}. 커넥터(Higgsfield·Figma)는 도구 목록에서 확인."
              + (f" 필수 중 없음: {', '.join(must)} — 작업 전에 설치(docs/setup.md · env_tools.json 의 install)." if must else ''))
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
