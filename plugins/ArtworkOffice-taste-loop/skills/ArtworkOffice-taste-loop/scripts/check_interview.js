#!/usr/bin/env node
// GUI-Interview.html 범용 검사 — 누구의 데이터에도 기대지 않는다.
// 임시 폴더에 starter + 가짜 예시 데이터(이름은 모두 demo…)로 저장소·프로젝트를 만들고, 빌드 → jsdom으로 열어
// 판정 규칙 · 앱 셸 · 사이드 트리 · 예시 타일 · 선택별 진화 기록 · 크게 보기 · 기본 양식 · 끌어 놓기 · 넣기 · 새 메모 · 제출(파일/가짜 db) · 검토·구성 모드 · 빈 저장소를 검사한다.
// 사용법: NODE_PATH=/tmp/slidecheck/node_modules node check_interview.js   (jsdom@24.1.3: npm install --prefix /tmp/slidecheck jsdom@24.1.3)
// jsdom에는 PointerEvent·elementFromPoint가 없다 → MouseEvent로 pointer 이벤트를 흉내 내고 elementFromPoint를 끼워 넣는다.
'use strict';
const {JSDOM} = require('jsdom');
const {spawnSync} = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');

const HERE = __dirname;
const STARTER = path.join(HERE, '..', 'starter');
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'tl-check-'));
let fails = 0;
const ok = (cond, msg) => { console.log((cond ? 'OK   ' : 'FAIL ') + msg); if (!cond) fails++; };
const writeJson = (p, o) => { fs.mkdirSync(path.dirname(p), {recursive: true}); fs.writeFileSync(p, JSON.stringify(o, null, 1)); };

// ---------- 가짜 예시 데이터 ----------
const proj = path.join(tmp, 'project'), store = path.join(tmp, 'store');
fs.cpSync(STARTER, store, {recursive: true});
const ent = (id, aspect, value, scope, strength, status, statement) => ({id, sub: aspect.split('.').slice(0, 2).join('.'), aspect, value, statement, scope, strength, status,
  reason: '테스트', examples: {liked: [], disliked: []}, source: [{file: 'test', kind: 'test'}], first: '2026-01-01', last: '2026-01-01', count: 1, conflicts: []});
const prefs = JSON.parse(fs.readFileSync(path.join(STARTER, 'preferences.json'), 'utf8'));
prefs.entries = [
  ent('P2.5-260101-01', 'P2.5.on_screen_text', 'caption', {material_type: ['video_promo']}, 1, 'confirmed', '전시 영상은 자막 한 줄'),
  ent('P2.5-260101-02', 'P2.5.on_screen_text', 'paragraph', {}, 2, 'proposed', '기본은 설명 문단'),
  ent('P1.4-260101-01', 'P1.4.ai_phrasing', ['past_ending'], {}, 5, 'proposed', '(추론) 딱딱한 끝맺음을 피한다'),
  ent('P1.1-260101-01', 'P1.1.formality', 'slogan', {material_type: ['video_promo']}, 1, 'confirmed', '전시 영상 문구는 헤드카피'),
  ent('P1.2-260101-01', 'P1.2.form', 'sentence', {material_type: ['slides']}, 1, 'confirmed', '발표자료 자막은 짧은 문장'),
];
writeJson(path.join(store, 'preferences.json'), prefs);
writeJson(path.join(store, 'knowledge', 'projects', 'demo_expo.json'), {lecture: 'demo_expo', title: '예시 전시 영상 (테스트)', created: '2026-01-01',
  dimensions: {material_type: 'video_promo', purpose: ['exhibit'], audience_age: ['adult'], audience_age_primary: 'adult', venue: ['kiosk'], format: 'mp4_916'},
  applied_entries: ['P2.5-260101-01', 'P1.1-260101-01'], decisions: ['예시 결정: 3부 구성'], deliverables: ['https://example.org/demo'], outcome: '테스트 만족', feedback: {rounds: 2, summary: '예시'}});
const ch = JSON.parse(fs.readFileSync(path.join(STARTER, 'knowledge', 'choices.json'), 'utf8'));
ch.choices = {'P1.1.formality|slogan': {aspect: 'P1.1.formality', option: 'slogan', version: 1, updated: '2026-01-01', how: ['대구·반전 구조', '소리 내어 읽어 검수'], checks: ['3초 안에 읽히는가'],
  examples: {liked: [], disliked: []}, learned_from: ['demo_expo'], source: [{file: 'test'}], history: [{date: '2026-01-01', project: 'demo_expo', change: '처음 정함'}]}};
writeJson(path.join(store, 'knowledge', 'choices.json'), ch);
const k05 = path.join(store, 'knowledge', '05_실수_기록.md');
fs.writeFileSync(k05, fs.readFileSync(k05, 'utf8').replace(/^(\|---.*)$/m, '$1\n| E1 | 2026-01-01 · demo | 누락 | 예시 증상 | 예시 원인 | 예시 방법 | 1회 |'));
fs.appendFileSync(path.join(store, 'knowledge', '01_교훈_기록.md'), '\n### 2026-01-01 — demo_expo / 예시\n- 예시 교훈\n');
writeJson(path.join(proj, 'demo_prev', 'materials', '인터뷰', '01_제작인터뷰_답변.json'), {mode: 'interview', lecture: 'demo_prev', submitted_at: '2026-01-02T00:00:00Z',
  dimensions: {material_type: 'slides'}, aspects: {'P1.1.energy': {choice: 'new', value: 'calm'}}, project: {topic: '예시'}});
const ENV = {TASTE_LOOP_STORE: store, TASTE_LOOP_PROJECT: proj, CLAUDE_PROJECT_DIR: proj};
// 파이썬은 이름만 보지 않고 실제로 실행해 본 뒤 고른다(Windows 의 python3 는 스토어 바로가기일 수 있다).
// -X utf8: Windows 파이썬은 파이프 입출력이 CP949 라 한글 출력 비교가 깨진다.
const PY = (process.platform === 'win32' ? ['python', 'py', 'python3'] : ['python3', 'python', 'py'])
  .find(c => spawnSync(c, ['-c', 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)']).status === 0) || 'python3';
const PYARGS = ['-X', 'utf8', '-I'];

function build(args, env) {
  const r = spawnSync(PY, [...PYARGS, path.join(HERE, 'build_interview.py'), ...args], {encoding: 'utf8', env: Object.assign({}, process.env, env || ENV)});
  if (r.status !== 0) { console.log(r.stdout, r.stderr); throw new Error('build 실패'); }
  return r.stdout.trim();
}
function open(file, withClaude) {
  const html = fs.readFileSync(file, 'utf8');
  const calls = {add: [], save: []};
  const errors = [];
  const dom = new JSDOM(html, {runScripts: 'dangerously', pretendToBeVisual: true, url: 'http://localhost/',
    beforeParse(window) {
      window.scrollTo = () => {};
      window.addEventListener('error', e => errors.push(e.message));
      if (withClaude) window.claude = {use: async name => name === 'db' ? {collection: () => ({add: async p => { calls.add.push(p); return {id: 'doc1'}; }})}
        : name === 'downloads' ? {save: async req => { calls.save.push(req); return {status: 'saved'}; }} : null};
    }});
  return {w: dom.window, d: dom.window.document, calls, errors};
}
const mouse = (w, type, x, y) => new w.MouseEvent(type, {bubbles: true, cancelable: true, clientX: x, clientY: y});

// 0) 저장소 검증
{
  const r = spawnSync(PY, [...PYARGS, path.join(HERE, 'check_store.py')], {encoding: 'utf8', env: Object.assign({}, process.env, ENV)});
  ok(r.status === 0 && /문제 없음 · 항목 5개 · 선택 기록 1개/.test(r.stdout), '가짜 저장소 검증 통과 (항목 5 · 선택 기록 1)');
}
// 1) 빌드·문법
const fileA = path.join(tmp, 'out', '01_제작인터뷰.html');
console.log(build(['--lecture', 'demo', '--mode', 'interview', '--out', fileA]));
const src = fs.readFileSync(fileA, 'utf8');
const scripts = src.match(/<script>[\s\S]*?<\/script>/g) || [];
ok(scripts.length === 1, `script 블록 ${scripts.length}개 (1이어야 함)`);
try { new Function(scripts[0].replace(/^<script>|<\/script>$/g, '')); ok(true, '스크립트 문법'); } catch (e) { ok(false, '스크립트 문법: ' + e.message); }
ok(src.startsWith('<!doctype html>') && !/__TITLE__|__SPEC__/.test(src), '파일용 doctype · 자리표시자 치환');

// 2) 판정 규칙·질문 유형·제출
{
  const {w, d, errors} = open(fileA, false);
  const PE = w.PE;
  ok(PE.store.projects.length === 1 && PE.store.past_answers.length === 1 && PE.store.mistakes.length === 1 && PE.store.lessons.length === 1 && Object.keys(PE.store.choices).length === 1, '저장소 주입: 프로젝트·지난 답변·실수·교훈·선택 기록 각 1');
  PE.setDim('material_type', 'video_promo');
  let m = PE.matchAspect('P2.5.on_screen_text');
  ok(m && m.winner.id === 'P2.5-260101-01' && !m.conflict, '좁은 범위 항목이 이김 (전시 영상 → 자막 한 줄)');
  m = PE.matchAspect('P1.4.ai_phrasing');
  ok(m && m.inferred, '추론(세기 5) 항목은 확인 필요로 표시');
  PE.setDim('material_type', 'slides');
  ok(PE.matchAspect('P2.5.on_screen_text').winner.id === 'P2.5-260101-02', '범위가 안 맞으면 전체 범위 항목');
  ok(PE.applicable('P4').includes('P4.1.method_slides') && !PE.applicable('P4').includes('P4.1.method_video'), 'applies_when: 발표자료면 발표자료 방법만');
  let cards = 0; for (let i = 0; i < PE.screens.length; i++) { PE.go(i); cards += d.querySelectorAll('#screen .card').length; }
  ok(cards > 20, `모든 화면 렌더 (카드 ${cards})`);
  PE.go(PE.screens.findIndex(s => s.id === 'P1'));
  Array.from(d.querySelectorAll('#midbtns .btn')).find(b => b.textContent === '이 묶음 모두 그대로').click();
  ok(PE.state.aspects['P1.2.form'] && PE.state.aspects['P1.2.form'].choice === 'keep', '「이 묶음 모두 그대로」');
  PE.setAspect('P1.1.formality', 'new', 'plain', true); PE.setProject('topic', '시험');
  const p = PE.payload();
  ok(p.client === 'file' && p.aspects['P1.1.formality'].always && p.project.topic === '시험' && 'refs' in p && 'base_project' in p && 'new_refs' in p, '제출 JSON 필드');
  ok(errors.length === 0, '오류 없음' + (errors.length ? ': ' + errors.join(' | ') : ''));
}
// 3) 앱 셸·트리·예시·진화 기록·크게 보기
{
  const {w, d, errors} = open(fileA, false);
  const PE = w.PE;
  ok(d.querySelectorAll('#menu .mbtn').length === 4 && d.querySelector('#ribbon') && d.querySelector('#sidetab'), '메뉴 4 · 리본 · 트리 손잡이');
  ok(PE.tree.nodes.map(n => n.id).join(',') === 'part1,part2,part3,refs', '트리 최상위 4묶음');
  PE.tree.expandAll(); const vAll = PE.tree.visible().length; PE.tree.collapseAll();
  ok(vAll > 100 && PE.tree.visible().length === 4, `모두 펼치기 ${vAll} · 모두 접기 4`);
  PE.tree.expandBy({cond: 'unanswered', groups: ['part2']});
  ok(PE.tree.visible().some(x => x.startsWith('asp:')) && !PE.tree.visible().some(x => x.startsWith('dim:')) && !!d.querySelector('#t-clear'), '선택 펼치기(2부·답 안 한 것) + 필터 칩');
  d.querySelector('#t-clear').click();
  ok(!PE.ui.filter, '필터 해제');
  PE.tree.open('part2'); PE.tree.open('cat:P1'); PE.tree.open('sub:P1.1');
  ok(!!d.querySelector('#tree .tn[data-id="part2"] > .tc > .tn[data-id="cat:P1"] > .tc > .tn[data-id="sub:P1.1"] > .tc > .tn[data-id="asp:P1.1.formality"]'), '선(.tc)으로 연결된 구조');
  PE.tree.detail('asp:P1.1.formality');
  const det = d.querySelector('#tree [data-detail="P1.1.formality"]');
  ok(det && det.querySelectorAll('.tile').length === 5 && det.querySelectorAll('.pv.txt').length === 5, '예시 타일 5 (글 샘플)');
  ok(/방법 v1/.test(det.querySelector('.tile[data-oid="slogan"] .ds').textContent) && !det.querySelector('.tile[data-oid="plain"] .ds'), '진화 기록 있는 선택에만 「방법 v1」');
  det.querySelector('.tile[data-oid="slogan"]').click();
  ok(PE.state.aspects['P1.1.formality'].value === 'slogan' && PE.state.aspects['P1.1.formality'].from === 'example', '예시 클릭 → 답');
  const gd = d.querySelector('#tree [data-detail="P1.1.formality"] [data-guide]');
  ok(gd && /소리 내어/.test(gd.textContent), '고른 선택의 현재 방법 상자');
  const aspectsAll = JSON.parse(src.match(/const SPEC = (.*?);\n/)[1]).questions.aspects;
  let perr = 0; for (const a of aspectsAll) for (const o of (a.options || [])) { try { PE.preview(a.id, o.id); } catch (e) { perr++; } }
  ok(perr === 0, '모든 선택지 예시 생성 오류 0');
  PE.tree.open('cat:P2'); PE.tree.open('sub:P2.4'); PE.tree.detail('asp:P2.4.theme');
  d.querySelector('#tree [data-detail="P2.4.theme"] [data-act="gallery"]').click();
  ok(PE.ui.view === 'gallery' && d.querySelectorAll('#screen .tile.big').length === 3 && d.querySelectorAll('#screen .pv svg').length === 3, '크게 보기: 화면 그림 3');
  PE.openGallery(['P2.4.theme', 'P1.2.form']);
  ok(d.querySelectorAll('#screen [data-gallery]').length === 2, '비교: 두 질문 동시');
  PE.view('flow'); PE.go(0); PE.tree.detail('asp:P2.4.theme', false);
  d.querySelector('#tree .tn[data-id="asp:P2.4.theme"] .tr').click();
  ok(PE.screens[PE.index()].id === 'P2' && !!d.querySelector('#screen .hl'), '트리 줄 클릭 → 화면 이동·강조');
  PE.tree.search('coolors');
  ok(d.querySelectorAll('#tree .rc').length === 1, '트리 검색');
  PE.tree.search('');
  PE.view('dashboard'); ok(d.querySelectorAll('#screen .stat').length === 9 && d.querySelectorAll('#screen .sim').length === 1, '대시보드 타일 9 · 비슷한 프로젝트 1');
  PE.view('store', 'choices'); ok(d.querySelectorAll('#screen table tr').length === 2, '저장소 → 선택 기록 표');
  PE.view('help'); ok(/선택 펼치기/.test(d.querySelector('#screen').textContent), '도움말');
  PE.side(false); ok(!d.querySelector('#sidetab').hidden, '트리 닫기 → 손잡이');
  d.querySelector('#sidetab').click(); ok(!d.querySelector('#side').classList.contains('closed'), '손잡이 → 다시 열림');
  ok(errors.length === 0, '오류 없음' + (errors.length ? ': ' + errors.join(' | ') : ''));
}
// 4) 기본 양식·끌어 놓기·넣기·새 메모
{
  const {w, d, errors} = open(fileA, false);
  const PE = w.PE;
  PE.go(1);
  d.querySelector('#rbase').click();
  const pc = d.querySelector('#tree .rc[data-kind="project"][data-id="demo_expo"]');
  ok(!!pc, '「기본 양식 고르기」 → 트리의 지난 프로젝트 카드');
  pc.querySelector('[data-act="base"]').click();
  const b = PE.state.base_project;
  ok(b && b.id === 'demo_expo' && b.aspects_set === 2 && PE.state.dimensions.material_type === 'video_promo' && PE.state.aspects['P2.5.on_screen_text'].choice === 'keep', '기본 양식 적용: 차원·취향 2개, 기본값과 같으면 그대로');
  PE.setDim('material_type', 'slides');
  PE.go(PE.screens.findIndex(s => s.id === 'P1'));
  PE.tree.open('refs'); PE.tree.open('refs.entries'); PE.tree.open('refs.entries.P1');
  const ec = d.querySelector('#tree .rc[data-id="P1.1-260101-01"]');
  const target = d.querySelector('#screen [data-drop="aspect:P1.1.formality"]');
  d.elementFromPoint = () => target;
  ec.querySelector('.grip').dispatchEvent(mouse(w, 'pointerdown', 10, 10));
  d.dispatchEvent(mouse(w, 'pointermove', 200, 200));
  ok(target.classList.contains('over'), '끌기: 놓을 카드 강조');
  d.dispatchEvent(mouse(w, 'pointerup', 200, 200));
  ok(PE.state.aspects['P1.1.formality'].value === 'slogan' && (PE.state.refs['aspect:P1.1.formality'] || []).length === 1 && d.querySelector('#ghost').hidden, '놓기: 답·참고 기록, 유령 숨김');
  d.querySelector('#screen [data-drop="aspect:P1.1.formality"] .rchip button').click();
  ok(!PE.state.refs['aspect:P1.1.formality'], '참고 빼기');
  PE.tree.open('refs.memo');
  d.querySelector('#nr-text').value = '예시 레퍼런스'; d.querySelector('#nr-add').click();
  d.querySelector('#tree .rc[data-kind="new_ref"] [data-act="insert"]').click();
  const sel = d.querySelector('#pksel'); sel.value = String(PE.screens.findIndex(s => s.id === 'P2')); sel.dispatchEvent(new w.Event('change', {bubbles: true}));
  Array.from(d.querySelectorAll('#pklist .opt')).find(x => x.dataset.target === 'aspect:P2.7.reference_use').click();
  ok(PE.state.new_refs.length === 1 && PE.state.refs['aspect:P2.7.reference_use'][0].kind === 'new_ref', '새 메모 → 넣기(다른 화면)');
  PE.tree.open('refs.history');
  ok(d.querySelectorAll('#tree .rc[data-kind="past"]').length === 1, '지난 답 내역 카드');
  ok(errors.length === 0, '오류 없음' + (errors.length ? ': ' + errors.join(' | ') : ''));
}
// 5) 빈 저장소(starter) — 처음 설치한 사람
{
  const fresh = path.join(tmp, 'fresh'); fs.mkdirSync(fresh);
  const fileF = path.join(tmp, 'out', '01_빈저장소.html');
  build(['--lecture', 'demo', '--out', fileF], {TASTE_LOOP_PROJECT: fresh, CLAUDE_PROJECT_DIR: fresh, TASTE_LOOP_STORE: ''});
  const {w, errors} = open(fileF, false);
  const PE = w.PE;
  ok(PE.store.projects.length === 0 && Object.keys(PE.store.choices).length === 0 && PE.store.design_refs.length >= 20, '빈 저장소: 개인 기록 0 · 레퍼런스 서비스만');
  for (let i = 0; i < PE.screens.length; i++) PE.go(i);
  PE.view('dashboard'); PE.view('store', 'entries'); PE.view('flow');
  ok(errors.length === 0, '빈 저장소: 모든 화면 오류 없음');
}
// 6) 가짜 db 제출·내려받기 + 검토·구성 모드
(async () => {
  const wait = ms => new Promise(r => setTimeout(r, ms));
  const {w, d, calls} = open(fileA, true);
  w.PE.go(w.PE.screens.length - 1);
  d.querySelector('#submit').click(); await wait(50);
  ok(calls.add.length === 1 && calls.add[0].client === 'artifact', 'db: answers.add (client=artifact)');
  d.querySelector('#dl').click(); await wait(50);
  ok(calls.save.length === 1 && /01_제작인터뷰_답변\.json$/.test(calls.save[0].filename), 'downloads.save');
  const specR = path.join(tmp, 'review.json');
  writeJson(specR, {items: [{id: 's1', title: '장면 1'}, {id: 's2', title: '장면 2'}]});
  const fileR = path.join(tmp, 'out', '03_검토.html');
  build(['--lecture', 'demo', '--mode', 'review', '--spec', specR, '--out', fileR, '--artifact']);
  ok(fs.readFileSync(fileR, 'utf8').startsWith('<title>'), '게시용은 <title>로 시작');
  const {w: wr, d: dr, errors: er} = open(fileR, false);
  wr.PE.go(1);
  Array.from(dr.querySelectorAll('#screen .btn')).find(x => x.textContent.includes('싫다')).click();
  Array.from(dr.querySelectorAll('#screen .chip')).find(x => x.textContent === '글이 AI스럽다').click();
  ok(wr.PE.payload().items.s1.reasons.includes('ai_text') && er.length === 0, '검토: 👎 + 이유 칩');
  const specS = path.join(tmp, 'structure.json');
  writeJson(specS, {items: [{id: 'A', title: '구성안 A', chapters: ['서론', '결과']}, {id: 'B', title: '구성안 B', chapters: ['문제', '해결', '결과']}]});
  const fileS = path.join(tmp, 'out', '02_구성.html');
  build(['--lecture', 'demo', '--mode', 'structure', '--spec', specS, '--out', fileS]);
  const {w: ws, d: ds} = open(fileS, false);
  ws.PE.go(1);
  Array.from(ds.querySelectorAll('#screen .opt')).find(x => x.textContent === '구성안 B').click();
  Array.from(ds.querySelectorAll('#screen .chip')).find(x => x.textContent === '▼').click();
  const ps = ws.PE.payload();
  ok(ps.items.chosen === 'B' && ps.items.order[0] === 1, '구성: 선택·순서 바꾸기');
  console.log(fails ? `실패 ${fails}개` : '오류 없음');
  fs.rmSync(tmp, {recursive: true, force: true});
  process.exit(fails ? 1 : 0);
})();
