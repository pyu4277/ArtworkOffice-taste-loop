#!/usr/bin/env python3
"""선택지 예시(움직이는 HTML) — 판(version) 관리.

예시는 선택지 하나에 HTML 조각 하나다. 인터뷰 페이지가 선택지 카드 안에 띄워 직접 눌러 보게 한다.
프로젝트에서 실제로 만든 것(예: 이번 프로젝트의 위쪽 메뉴 줄)을 줄여 새 판으로 올리면,
다음 인터뷰에서는 그 최신 모습이 예시로 나온다(같은 선택을 해도 진화한 방법이 보인다).

자리:
  엔진 기본 예시: <skill>/starter/knowledge/demos/        (index.json + <키 폴더>/<선택지>.v<판>.html)
  내 예시:        <데이터 폴더>/knowledge/demos/          (같은 구조. 같은 키가 있으면 이쪽이 이긴다)
  키: dim.<1부 질문 id>|<선택지 id>   또는   asp.<취향 질문 id>|<선택지 id>
  공통 바탕 CSS: <skill>/demo_base.css (페이지가 예시 앞에 붙인다)

사용법:
  python3 demos.py list                      키 · 판 · 출처 (내 예시 / 엔진 기본)
  python3 demos.py add <키> <조각.html> --from <프로젝트> --what "<무엇이 달라졌나>" [--now "<누른 순간>"] [--later "<나중에>"]
                                             새 판으로 올린다(옛 판 파일은 남겨 「지난 판 보기」에 쓴다)
  python3 demos.py show <키>                 판 기록
검사: node check_demos.js <demos 폴더> (조각 규칙·스크립트 문법·실행 오류)
"""
import copy
import datetime
import json
import pathlib
import re
import sys

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import store as ST  # noqa: E402

SKILL = HERE.parent
STARTER_DEMOS = SKILL / 'starter' / 'knowledge' / 'demos'
KEY_RE = re.compile(r'^(dim|asp)\.[^|/\\]+\|[^|/\\]+$')


def user_dir():
    return ST.STORE / 'knowledge' / 'demos'


def _load(d):
    p = pathlib.Path(d) / 'index.json'
    if p.exists():
        return json.loads(p.read_text(encoding='utf-8')).get('items', {})
    return {}


def merged():
    """{키: 항목(+ '_dir': 파일이 있는 폴더, '_origin': 'user'|'engine')} — 내 예시가 엔진 기본을 이긴다."""
    out = {}
    for k, it in _load(STARTER_DEMOS).items():
        out[k] = dict(it, _dir=str(STARTER_DEMOS), _origin='engine')
    ud = user_dir()
    if ud.resolve() != STARTER_DEMOS.resolve():
        for k, it in _load(ud).items():
            eng = out.get(k)
            if eng and it.get('source') == eng.get('source') and int(it.get('version', 0)) <= int(eng.get('version', 0)):
                continue  # 엔진 기본 예시를 그대로 복사해 둔 것이면 엔진 쪽(더 새것일 수 있음)을 쓴다
            out[k] = dict(it, _dir=str(ud), _origin='user')
    return out


def for_spec(max_old=3):
    """build_interview.py 용: 페이지에 넣을 예시(조각 HTML 포함)와 공통 CSS."""
    items = {}
    for k, it in merged().items():
        d = pathlib.Path(it['_dir'])
        fp = d / it['file']
        if not fp.exists():
            continue
        e = {x: it.get(x) for x in ('title', 'now', 'later', 'version', 'source', 'history')}
        e['origin'] = it['_origin']
        e['html'] = fp.read_text(encoding='utf-8')
        old = {}
        for h in sorted(it.get('history') or [], key=lambda h: -int(h.get('v', 0))):
            if len(old) >= max_old:
                break
            hf = h.get('file')
            if hf and hf != it['file']:
                # 옛 판은 내 폴더에 없으면 엔진 기본 폴더에서 찾는다
                for base in (d, STARTER_DEMOS):
                    if (base / hf).exists():
                        old[str(h.get('v'))] = (base / hf).read_text(encoding='utf-8')
                        break
        e['old'] = old
        items[k] = e
    base = (SKILL / 'demo_base.css').read_text(encoding='utf-8') if (SKILL / 'demo_base.css').exists() else ''
    return {'base_css': base, 'items': items}


def cmd_list():
    m = merged()
    if not m:
        print('예시가 없습니다.'); return 0
    for k in sorted(m):
        it = m[k]
        print(f"{k} · v{it.get('version')} · {'내 예시' if it['_origin'] == 'user' else '엔진 기본'} · {it.get('source', '')}")
    return 0


def cmd_show(key):
    it = merged().get(key)
    if not it:
        print(f'{key}: 예시 없음'); return 1
    print(f"{key} · {it.get('title')} · 지금 v{it.get('version')} ({'내 예시' if it['_origin'] == 'user' else '엔진 기본'})")
    for h in it.get('history') or []:
        print(f"  v{h.get('v')} {h.get('date')} · {h.get('from')} · {h.get('what')}")
    return 0


def cmd_add(argv):
    if len(argv) < 2:
        print(__doc__); return 2
    key, src = argv[0], pathlib.Path(argv[1])
    opt = {}
    i = 2
    while i < len(argv):
        if argv[i] in ('--from', '--what', '--now', '--later', '--title') and i + 1 < len(argv):
            opt[argv[i][2:]] = argv[i + 1]; i += 2
        else:
            print(f'모르는 옵션 {argv[i]}'); return 2
    if not KEY_RE.match(key):
        print('키 형식: dim.<질문 id>|<선택지 id> 또는 asp.<취향 질문 id>|<선택지 id>'); return 2
    if not opt.get('from') or not opt.get('what'):
        print('--from <프로젝트> 와 --what "<무엇이 달라졌나>" 는 꼭 적는다(판 기록).'); return 2
    if not ST.STORE_WRITABLE:
        print('데이터 폴더가 없습니다(starter 를 쓰는 중). 먼저 init_store.py 로 만드세요.'); return 1
    html = src.read_text(encoding='utf-8').replace('\r\n', '\n')
    if re.search(r'<\/?(html|head|body)[\s>]', html, re.I):
        print('조각에는 <html>/<head>/<body> 를 넣지 않습니다.'); return 1
    if len(html.encode('utf-8')) > 16 * 1024:
        print('16KB 를 넘습니다. 줄여서 다시 올려 주세요.'); return 1
    cur = merged().get(key)
    ud = user_dir()
    ud.mkdir(parents=True, exist_ok=True)
    idx_p = ud / 'index.json'
    idx = json.loads(idx_p.read_text(encoding='utf-8')) if idx_p.exists() else {'version': 1, 'note': '내 선택지 예시 — demos.py 로만 고친다', 'items': {}}
    v = int(cur.get('version', 0)) + 1 if cur else 1
    folder, oid = key.split('|')
    rel = f"{folder}/{folder.split('.', 1)[1]}-{oid}.v{v}.html"  # 이름만 보고 무엇인지 알게(질문-선택지.v판) — 파일 이름 검사 통과
    (ud / folder).mkdir(parents=True, exist_ok=True)
    (ud / rel).write_bytes(html.encode('utf-8'))  # LF 고정(Windows 에서도)
    hist = copy.deepcopy((cur or {}).get('history') or [])
    hist.append({'v': v, 'date': datetime.date.today().isoformat(), 'from': opt['from'], 'what': opt['what'], 'file': rel})
    it = {k2: (cur or {}).get(k2) for k2 in ('title', 'now', 'later')}
    it.update({k2: opt[k2] for k2 in ('title', 'now', 'later') if opt.get(k2)})
    if not it.get('title'):
        it['title'] = oid
    it['now'] = it.get('now') or ''
    it['later'] = it.get('later') or ''
    it.update({'file': rel, 'version': v, 'source': opt['from'], 'history': hist})
    idx['items'][key] = it
    idx_p.write_bytes((json.dumps(idx, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
    print(f'{key}: v{v} 로 올림 ({rel}). 옛 판은 「지난 판 보기」에 남습니다. 검사: node check_demos.js {ud}')
    return 0


def main(argv):
    if not argv:
        print(__doc__); return 2
    if argv[0] == 'list':
        return cmd_list()
    if argv[0] == 'show' and len(argv) > 1:
        return cmd_show(argv[1])
    if argv[0] == 'add':
        return cmd_add(argv[1:])
    print(__doc__); return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
