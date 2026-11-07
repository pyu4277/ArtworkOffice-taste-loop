#!/bin/bash
# SessionStart 훅: 취향 저장소 요약과 환경 점검 요약을 Claude 문맥에 넣는다.
# 레포 .claude/settings.json 또는 플러그인 hooks/hooks.json 이 부른다. 아무것도 막지 않고 항상 종료 코드 0.
# 표준 출력에는 훅 JSON만 낸다.
scripts="$(cd "$(dirname "$0")" && pwd)"
# 파이썬은 이름만 보지 않고 실제로 실행해 본 뒤 고른다: Windows 의 python3·python 은 스토어 바로가기(가짜)일 수 있다.
case "${OSTYPE:-}" in
  msys*|cygwin*) candidates="python py python3" ;;
  *) candidates="python3 python py" ;;
esac
py=""
for c in $candidates; do
  command -v "$c" >/dev/null 2>&1 \
    && "$c" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)' </dev/null >/dev/null 2>&1 \
    && { py="$c"; break; }
done
[ -n "$py" ] || exit 0
# -X utf8: Windows 파이썬은 출력을 CP949 로 내보내 한글이 깨진다(Claude Code 는 UTF-8 로 읽는다).
"$py" -X utf8 - "$scripts" <<'PY' 2>/dev/null || true
import json, pathlib, subprocess, sys
scripts = pathlib.Path(sys.argv[1])
sys.dont_write_bytecode = True
sys.path.insert(0, str(scripts))
parts = []
try:
    import store as ST
    prefs = json.loads(ST.path('preferences.json').read_text(encoding='utf-8'))
    n = len(prefs.get('entries', []))
    active = sum(1 for e in prefs.get('entries', []) if e.get('status') in ('proposed', 'confirmed'))
    msg = (f'[ArtworkOffice-taste-loop] 취향 저장소: 항목 {n}개(활성 {active}) · 데이터 {ST.STORE} ({ST.STORE_HOW}). '
           '자료(발표자료·교재·보조자료·영상·보고서)를 만들기 전에 스킬 ArtworkOffice-taste-loop의 SKILL.md 1절(시작할 때 반드시)과 '
           '데이터 폴더의 knowledge/00_취향_요약.md·PROJECT.md를 읽는다. 보고는 끝에 「확인할 결과물」 표를 둔다.')
    if not ST.STORE_WRITABLE:
        msg += ' 데이터 폴더가 아직 없다: 처음 쓸 때 scripts/init_store.py 로 만든다.'
    parts.append(msg)
except Exception as e:  # noqa: BLE001
    parts.append(f'[ArtworkOffice-taste-loop] 취향 저장소 읽기 실패: {e}')
try:
    out = subprocess.run([sys.executable, '-X', 'utf8', '-I', str(scripts / 'check_env.py'), '--brief'],
                         capture_output=True, encoding='utf-8', errors='replace', timeout=20)
    if out.stdout.strip():
        parts.append('[환경 점검] ' + out.stdout.strip())
except Exception as e:  # noqa: BLE001
    parts.append(f'[환경 점검] 실행 실패: {e}')
print(json.dumps({'hookSpecificOutput': {'hookEventName': 'SessionStart', 'additionalContext': '\n'.join(parts)}}, ensure_ascii=False))
PY
exit 0
