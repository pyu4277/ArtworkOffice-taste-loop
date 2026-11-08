#!/usr/bin/env python3
"""취향 저장소 검증 + 사람용 요약 생성.

사용법:
  python3 check_store.py              검증하고 knowledge/00_취향_요약.md 를 다시 만든다
  python3 check_store.py --no-summary 검증만 한다
  python3 check_store.py --json       결과를 JSON으로 출력한다(스크립트용)

검사하는 것:
  - dimensions.json / questions.json / preferences.json 이 읽히고 id가 유일한지
  - entry의 aspect·value가 질문 은행의 선택지와 맞는지, scope 키·값이 차원에 있는지
  - strength 1~5, status, 날짜 형식, conflicts 참조
  - 같은 aspect에서 범위가 겹치는데 값이 다른 항목(충돌): 구체성이 같으면 오류, 다르면 정보
  - knowledge/choices.json(선택별 진화 기록): 키 '<aspect>|<option>'이 질문 은행과 맞는지, version·how·history·source
종료 코드: 0 문제 없음(경고 가능) · 1 오류 있음
"""
import datetime
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.dont_write_bytecode = True  # 설치 폴더(플러그인 캐시)에 __pycache__ 를 만들지 않는다
sys.path.insert(0, str(HERE))
import store as ST  # noqa: E402  데이터 폴더 찾기(엔진과 데이터 분리)
FILES = {
    'dimensions': ST.path('dimensions.json'),
    'questions': ST.path('questions.json'),
    'preferences': ST.path('preferences.json'),
}
SUMMARY = ST.KNOW / '00_취향_요약.md'
CHOICES = ST.path('knowledge/choices.json')
STATUSES = ('proposed', 'confirmed', 'promoted_rule', 'retired')
ACTIVE = ('proposed', 'confirmed')
ID_RE = re.compile(r'^P\d\.\d+-\d{6}-\d{2}$')
STRENGTH_LABEL = {1: '직접 말함', 2: '여러 안 중 고름', 3: '고치라고 함', 4: '말없이 수용', 5: 'Claude 추론'}


def load_all():
    data, errors = {}, []
    for name, path in FILES.items():
        try:
            data[name] = json.loads(path.read_text(encoding='utf-8'))
        except Exception as e:  # noqa: BLE001
            errors.append(f'{path.name}: JSON을 읽을 수 없음 — {e}')
    if 'dimensions' in data:
        import upgrade_store as UP
        data['dimensions'], old = UP.migrate_dims(data['dimensions'])
        if old:
            UPGRADE_NOTE.append('dimensions.json 이 옛 구조(파일형식 차원 없음)입니다 — upgrade_store.py 로 올리세요(검증은 새 구조로 했습니다)')
    if 'questions' in data:
        import upgrade_store as UP
        data['questions'], oldq = UP.migrate_qs(data['questions'])
        if oldq:
            UPGRADE_NOTE.append('questions.json 이 옛 구조입니다 — upgrade_store.py 로 올리세요(검증은 새 구조로 했습니다)')
    return data, errors


UPGRADE_NOTE = []


def check_dimensions(dims, errors):
    ids = set()
    values = {}
    for d in dims.get('dimensions', []):
        did = d.get('id')
        if not did or did in ids:
            errors.append(f'dimensions: id 중복 또는 없음: {did!r}')
        ids.add(did)
        if d.get('type') not in ('single', 'multi', 'text'):
            errors.append(f'dimensions[{did}]: type은 single/multi/text')
        vids = set()
        for v in d.get('values', []):
            if v.get('id') in vids:
                errors.append(f'dimensions[{did}]: 값 id 중복 {v.get("id")!r}')
            vids.add(v.get('id'))
        values[did] = vids
    # 보이는 조건(when·ask_when·applies_when)은 structure.check_conditions 가 검사한다(main)
    for s in dims.get('screens', []):
        for did in s.get('dimensions', []):
            if did not in ids:
                errors.append(f'screens[{s.get("id")}]: 차원 {did!r} 없음')
    return values


def check_questions(qs, dim_values, errors):
    subs = {}
    for c in qs.get('categories', []):
        for sid, sname in c.get('subs', {}).items():
            subs[sid] = (c['id'], sname)
    aspects = {}
    for a in qs.get('aspects', []):
        aid = a.get('id')
        if not aid or aid in aspects:
            errors.append(f'questions: aspect id 중복 또는 없음: {aid!r}')
            continue
        if a.get('sub') not in subs:
            errors.append(f'questions[{aid}]: sub {a.get("sub")!r} 가 categories에 없음')
        elif not aid.startswith(a['sub'] + '.'):
            errors.append(f'questions[{aid}]: id가 sub({a["sub"]})로 시작하지 않음')
        if a.get('type') not in ('single', 'multi', 'scale', 'text', 'rank', 'approve', 'compare'):
            errors.append(f'questions[{aid}]: type {a.get("type")!r} 지원 안 함')
        oids = set()
        for o in a.get('options', []):
            if o.get('id') in oids:
                errors.append(f'questions[{aid}]: 선택지 id 중복 {o.get("id")!r}')
            oids.add(o.get('id'))
        if a.get('type') in ('single', 'multi') and not oids:
            errors.append(f'questions[{aid}]: single/multi인데 선택지가 없음')
        aspects[aid] = a
    for r in qs.get('review_reasons', []):
        if r.get('aspect') and r['aspect'] not in aspects:
            errors.append(f'review_reasons[{r.get("id")}]: aspect {r["aspect"]!r} 없음')
    return subs, aspects


def scope_overlaps(a, b):
    """두 scope가 겹치는가. 한쪽에만 있는 키는 다른 쪽이 전체이므로 겹친다."""
    for k in set(a) & set(b):
        if not (set(a[k]) & set(b[k])):
            return False
    return True


def norm_value(v):
    return tuple(sorted(v)) if isinstance(v, list) else v


def check_preferences(prefs, dim_values, extra_keys, subs, aspects, errors, warnings):
    ids = set()
    entries = prefs.get('entries', [])
    for e in entries:
        eid = e.get('id', '?')
        if eid in ids:
            errors.append(f'preferences: id 중복 {eid}')
        ids.add(eid)
        if not ID_RE.match(eid):
            errors.append(f'preferences[{eid}]: id 형식은 <sub>-<YYMMDD>-<nn>')
        if e.get('sub') not in subs:
            errors.append(f'preferences[{eid}]: sub {e.get("sub")!r} 없음')
        a = aspects.get(e.get('aspect'))
        if not a:
            errors.append(f'preferences[{eid}]: aspect {e.get("aspect")!r} 가 질문 은행에 없음')
        else:
            if a['sub'] != e.get('sub'):
                errors.append(f'preferences[{eid}]: aspect의 sub({a["sub"]})와 entry.sub({e.get("sub")})가 다름')
            oids = {o['id'] for o in a.get('options', [])}
            v = e.get('value')
            if a['type'] == 'single' and not (isinstance(v, str) and v in oids):
                errors.append(f'preferences[{eid}]: value {v!r} 는 {a["id"]} 선택지 {sorted(oids)} 중 하나여야 함')
            elif a['type'] == 'multi' and not (isinstance(v, list) and v and set(v) <= oids):
                errors.append(f'preferences[{eid}]: value {v!r} 는 {a["id"]} 선택지의 부분집합(목록)이어야 함')
            elif a['type'] == 'text' and not (isinstance(v, str) and v.strip()):
                errors.append(f'preferences[{eid}]: text aspect의 value는 비어 있지 않은 문자열')
        if not isinstance(e.get('statement'), str) or not e['statement'].strip():
            errors.append(f'preferences[{eid}]: statement 없음')
        scope = e.get('scope')
        if not isinstance(scope, dict):
            errors.append(f'preferences[{eid}]: scope는 객체({{}} 가능)')
        else:
            for k, vs in scope.items():
                if k in dim_values:
                    if not isinstance(vs, list) or not vs:
                        errors.append(f'preferences[{eid}].scope[{k}]: 값 목록이어야 함')
                    else:
                        for v in vs:
                            if v not in dim_values[k]:
                                errors.append(f'preferences[{eid}].scope[{k}]: 값 {v!r} 가 차원에 없음')
                elif k in extra_keys:
                    if not isinstance(vs, list) or not all(isinstance(x, str) and x for x in vs):
                        errors.append(f'preferences[{eid}].scope[{k}]: 문자열 목록이어야 함')
                else:
                    errors.append(f'preferences[{eid}].scope: 키 {k!r} 는 차원도 extra_scope_keys도 아님')
        s = e.get('strength')
        if s not in (1, 2, 3, 4, 5):
            errors.append(f'preferences[{eid}]: strength는 1~5')
        if e.get('status') not in STATUSES:
            errors.append(f'preferences[{eid}]: status는 {STATUSES}')
        if e.get('status') == 'confirmed' and s == 5:
            errors.append(f'preferences[{eid}]: 추론(strength 5) 항목은 사용자 확인 전에 confirmed가 될 수 없음')
        for key in ('first', 'last'):
            try:
                datetime.date.fromisoformat(e.get(key, ''))
            except ValueError:
                errors.append(f'preferences[{eid}]: {key} 는 YYYY-MM-DD')
        if not isinstance(e.get('count'), int):
            errors.append(f'preferences[{eid}]: count는 정수')
        if not isinstance(e.get('source'), list) or not e['source']:
            errors.append(f'preferences[{eid}]: source 목록이 비어 있음 (출처 필수)')
    for e in entries:
        for c in e.get('conflicts', []):
            if c not in ids:
                errors.append(f'preferences[{e["id"]}].conflicts: {c!r} 없음')
    # 충돌 검사: 같은 aspect, 둘 다 활성, 값이 다르고 범위가 겹침
    by_aspect = {}
    for e in entries:
        if e.get('status') in ACTIVE and isinstance(e.get('scope'), dict):
            by_aspect.setdefault(e.get('aspect'), []).append(e)
    info = []
    for aid, group in by_aspect.items():
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                a, b = group[i], group[j]
                if norm_value(a.get('value')) == norm_value(b.get('value')):
                    continue
                if not scope_overlaps(a['scope'], b['scope']):
                    continue
                sa, sb = len(a['scope']), len(b['scope'])
                listed = b['id'] in a.get('conflicts', []) and a['id'] in b.get('conflicts', [])
                if sa == sb:
                    msg = f'{aid}: {a["id"]} 와 {b["id"]} 는 범위가 겹치고 구체성이 같은데 값이 다름 — 사용자에게 물어 정해야 함'
                    (warnings if listed else errors).append(msg + ('' if listed else ' (conflicts에 서로 적으면 경고로 내려감)'))
                else:
                    narrow = a if sa > sb else b
                    info.append(f'{aid}: {narrow["id"]} 가 더 좁은 범위로 우선 (상대: {(b if narrow is a else a)["id"]})')
    return entries, info


def check_choices(aspects, errors):
    """선택별 진화 기록. 파일이 없으면 빈 것으로 본다(선택 사항이 아니라 아직 안 쌓인 것)."""
    if not CHOICES.exists():
        return {}
    try:
        data = json.loads(CHOICES.read_text(encoding='utf-8'))
    except Exception as e:  # noqa: BLE001
        errors.append(f'choices.json: JSON을 읽을 수 없음 — {e}')
        return {}
    choices = data.get('choices', {})
    if not isinstance(choices, dict):
        errors.append('choices.json: choices는 객체')
        return {}
    for key, c in choices.items():
        aid, _, oid = key.partition('|')
        a = aspects.get(aid)
        if not a:
            errors.append(f'choices[{key}]: aspect {aid!r} 가 질문 은행에 없음')
            continue
        if a.get('type') in ('single', 'multi') and oid not in {o['id'] for o in a.get('options', [])}:
            errors.append(f'choices[{key}]: 선택지 {oid!r} 가 {aid} 에 없음')
        if c.get('aspect') != aid or c.get('option') != oid:
            errors.append(f'choices[{key}]: aspect/option 칸이 키와 다름')
        if not isinstance(c.get('version'), int) or c['version'] < 1:
            errors.append(f'choices[{key}]: version은 1 이상 정수')
        if not isinstance(c.get('how'), list) or not c['how']:
            errors.append(f'choices[{key}]: how(방법) 목록이 비어 있음')
        if not isinstance(c.get('source'), list) or not c['source']:
            errors.append(f'choices[{key}]: source 목록이 비어 있음 (출처 필수)')
        hist = c.get('history')
        if not isinstance(hist, list) or not hist:
            errors.append(f'choices[{key}]: history 목록이 비어 있음 (처음 정한 날과 프로젝트)')
        else:
            for h in hist:
                try:
                    datetime.date.fromisoformat(h.get('date', ''))
                except ValueError:
                    errors.append(f'choices[{key}].history: date는 YYYY-MM-DD')
            if len(hist) > c.get('version', 0):
                errors.append(f'choices[{key}]: history({len(hist)}건)가 version({c.get("version")})보다 많음 — 방법이 바뀌었으면 version을 올린다')
        try:
            datetime.date.fromisoformat(c.get('updated', ''))
        except ValueError:
            errors.append(f'choices[{key}]: updated는 YYYY-MM-DD')
    return choices


def human_scope(scope, dims):
    if not scope:
        return '전체'
    names = {d['id']: d for d in dims.get('dimensions', [])}
    parts = []
    for k, vs in scope.items():
        d = names.get(k)
        if d:
            labels = {v['id']: v['label'] for v in d.get('values', [])}
            parts.append(f'{d["name"]}={"·".join(labels.get(v, v) for v in vs)}')
        else:
            parts.append(f'{k}={"·".join(vs)}')
    return ', '.join(parts)


def write_summary(data, subs, entries, info, choices=None):
    dims, qs = data['dimensions'], data['questions']
    cats = qs.get('categories', [])
    by_sub = {}
    for e in entries:
        by_sub.setdefault(e.get('sub'), []).append(e)
    lines = ['# 취향 요약 (자동 생성 — 손으로 고치지 말고 preferences.json을 고친 뒤 check_store.py 실행)', '',
             f'- 생성: {datetime.date.today().isoformat()} · 항목 {len(entries)}개 '
             f'(활성 {sum(1 for e in entries if e.get("status") in ACTIVE)}, 추론 {sum(1 for e in entries if e.get("strength") == 5)}, 폐기 {sum(1 for e in entries if e.get("status") == "retired")})',
             '- 읽는 법: **굵은 글씨**가 이렇게 한다는 문장. 괄호 안은 적용 범위 / 근거 세기 / 상태 / 출처. 규칙(AGENTS.md)과 충돌하면 규칙이 우선한다.', '']
    for c in cats:
        lines.append(f'## {c["id"]} {c["name"]}')
        lines.append('')
        for sid, sname in c.get('subs', {}).items():
            group = [e for e in by_sub.get(sid, []) if e.get('status') != 'retired']
            lines.append(f'### {sid} {sname}' + ('' if group else ' — (아직 없음: 인터뷰에서 처음 정한다)'))
            for e in sorted(group, key=lambda x: (x.get('status') != 'confirmed', x.get('strength', 9), x.get('id'))):
                src = '; '.join(f'{s.get("file", "")}' + (f':{s["line"]}' if s.get('line') else '') for s in e.get('source', []))
                flag = ' ⚠추론·확인 전 적용 금지' if e.get('strength') == 5 else ''
                lines.append(f'- **{e["statement"]}** ({human_scope(e.get("scope"), dims)} / 세기 {e.get("strength")} {STRENGTH_LABEL.get(e.get("strength"), "")} / {e.get("status")}{flag} / {src}) `{e["id"]}`')
            lines.append('')
    retired = [e for e in entries if e.get('status') == 'retired']
    if retired:
        lines.append('## 폐기된 항목')
        for e in retired:
            lines.append(f'- ~~{e["statement"]}~~ `{e["id"]}` ({e.get("reason", "")})')
        lines.append('')
    if choices:
        aspects = {a['id']: a for a in qs.get('aspects', [])}
        lines.append(f'## 선택별 진화 기록 (knowledge/choices.json — {len(choices)}개, 같은 선택도 version이 오르면 새 방법으로)')
        for key, c in sorted(choices.items()):
            a = aspects.get(c.get('aspect'), {})
            lab = next((o['label'] for o in a.get('options', []) if o['id'] == c.get('option')), c.get('option'))
            lines.append(f'- **{a.get("text", c.get("aspect"))} = {lab}** v{c.get("version")} ({c.get("updated")}; 배운 곳 {", ".join(c.get("learned_from", []))}): {c["how"][0] if c.get("how") else ""}')
        lines.append('')
    if info:
        lines.append('## 범위가 겹치는 항목 (좁은 범위가 우선)')
        lines += [f'- {x}' for x in info]
        lines.append('')
    text = '\n'.join(lines)
    old = SUMMARY.read_text(encoding='utf-8') if SUMMARY.exists() else None
    if old is None or old.split('\n', 3)[3:] != text.split('\n', 3)[3:]:  # 생성 날짜 줄만 다르면 다시 쓰지 않음
        SUMMARY.parent.mkdir(parents=True, exist_ok=True)
        SUMMARY.write_bytes((text + '\n').encode('utf-8'))  # 줄바꿈 LF 고정(Windows 에서도 클라우드와 같은 파일)
        return True
    return False


def main(argv):
    as_json = '--json' in argv
    data, errors = load_all()
    warnings, info, entries, choices = [], [], [], {}
    if not errors:
        dim_values = check_dimensions(data['dimensions'], errors)
        extra = set(data['dimensions'].get('extra_scope_keys', []))
        subs, aspects = check_questions(data['questions'], dim_values, errors)
        import structure as SX
        ce, cw = SX.check_conditions(data['dimensions'], data['questions'])
        errors += ce
        warnings += cw
        led = ST.path('knowledge') / 'structure_edits.json'
        if led.exists():
            try:
                bs = json.loads(led.read_text(encoding='utf-8')).get('batches', [])
                pend = [b for b in bs if b.get('status') == 'pending']
                if pend:
                    info.append(f"반영 대기 구조 편집 {len(pend)}묶음 · {sum(len(b.get('ops', [])) for b in pend)}건 (마무리 때 structure_edits.py apply)")
            except Exception as e:  # noqa: BLE001
                errors.append(f'knowledge/structure_edits.json 읽기 실패: {e}')
        entries, info = check_preferences(data['preferences'], dim_values, extra, subs, aspects, errors, warnings)
        choices = check_choices(aspects, errors)
        if not errors and '--no-summary' not in argv and ST.STORE_WRITABLE:
            changed = write_summary(data, subs, entries, info, choices)
            info.append(f'00_취향_요약.md {"갱신함" if changed else "변경 없음"}')
    info.insert(0, f'데이터: {ST.STORE} ({ST.STORE_HOW})')
    warnings.extend(UPGRADE_NOTE)
    if as_json:
        print(json.dumps({'errors': errors, 'warnings': warnings, 'info': info, 'entries': len(entries), 'choices': len(choices) if not errors else None}, ensure_ascii=False, indent=1))
    else:
        for e in errors:
            print('오류:', e)
        for w in warnings:
            print('경고:', w)
        for i in info:
            print('정보:', i)
        print(f'{"오류 " + str(len(errors)) + "개" if errors else "문제 없음"} · 항목 {len(entries)}개 · 선택 기록 {len(choices) if not errors else "?"}개 · 경고 {len(warnings)}개')
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
