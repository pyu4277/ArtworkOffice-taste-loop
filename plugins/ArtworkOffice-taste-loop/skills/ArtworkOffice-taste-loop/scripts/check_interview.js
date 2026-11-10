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
// 번호 칸 세 형식: 「E1」 · 합칠 때 번호를 바꾼 줄 「E2 (옛 E?-demo-1)」 · 작업 공간 임시 번호 「E?-demo-2」
fs.writeFileSync(k05, fs.readFileSync(k05, 'utf8').replace(/^(\|---.*)$/m, '$1\n| E1 | 2026-01-01 · demo | 누락 | 예시 증상 | 예시 원인 | 예시 방법 | 1회 |'
  + '\n| E2 (옛 E?-demo-1) | 2026-01-02 · demo | 절차 | 번호를 바꾼 예시 | 예시 원인 | 예시 방법 | 1회 |'
  + '\n| E?-demo-2 | 2026-01-03 · demo | 버그 | 임시 번호 예시 | 예시 원인 | 예시 방법 | 1회 |'));
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
      window.__y = 0; // 스크롤 흉내: scrollTo 가 정한 자리를 scrollY 로 돌려준다
      window.scrollTo = (x, y) => { window.__y = y || 0; };
      Object.defineProperty(window, 'scrollY', {configurable: true, get: () => window.__y});
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
// 선택지 예시: 데이터 폴더는 엔진 기본 예시를 복사하지 않는다(init_store 와 같게). 「내 예시」로 왼쪽 사이드바 v2 를 올려 본다
fs.rmSync(path.join(store, 'knowledge', 'demos'), {recursive: true, force: true});
const demoV2 = path.join(tmp, 'left_v2.html');
fs.writeFileSync(demoV2, '<style>.v2x{padding:8px}</style><div class="v2x">왼쪽 목차 v2 — 데모 프로젝트에서 만든 모습</div>');
{
  const r = spawnSync(PY, [...PYARGS, path.join(HERE, 'demos.py'), 'add', 'dim.frame|left', demoV2, '--from', 'demo_project', '--what', '접기 단추 추가'], {encoding: 'utf8', env: Object.assign({}, process.env, ENV)});
  ok(r.status === 0 && /v2/.test(r.stdout), '내 예시 올리기(demos.py add): 왼쪽 사이드바 → v2' + (r.status ? ': ' + r.stdout + r.stderr : ''));
}
const fileA = path.join(tmp, 'out', '01_제작인터뷰.html');
console.log(build(['--lecture', 'demo', '--mode', 'interview', '--out', fileA]));
const src = fs.readFileSync(fileA, 'utf8');
const scripts = src.match(/<script>[\s\S]*?<\/script>/g) || [];
ok(scripts.length === 1, `script 블록 ${scripts.length}개 (1이어야 함)`);
try { new Function(scripts[0].replace(/^<script>|<\/script>$/g, '')); ok(true, '스크립트 문법'); } catch (e) { ok(false, '스크립트 문법: ' + e.message); }
ok(src.startsWith('<!doctype html>') && !/__TITLE__|__SPEC__/.test(src), '파일용 doctype · 자리표시자 치환');

// 1-1) 실수 표: 괄호에 옛 표기가 붙은 줄 · 임시 번호 줄도 읽는다(1.4.1 — 전에는 괄호가 붙은 줄을 통째로 빠뜨렸다)
{
  const {w, d, errors} = open(fileA, false);
  const PE = w.PE;
  const ids = PE.store.mistakes.map(m => m.id).join(',');
  const e2 = PE.store.mistakes.find(m => m.id === 'E2');
  ok(ids === 'E1,E2,E?-demo-2' && !!e2 && e2.old === '옛 E?-demo-1' && e2.symptom === '번호를 바꾼 예시', `실수 표 번호 칸 세 형식: ${ids} · E2 옛 표기 ${e2 && e2.old}`);
  PE.view('store', 'mistakes');
  ok(d.querySelectorAll('#screen .rc[data-kind="mistake"]').length === 3, '저장소 → 실수 카드 3개');
  d.querySelector('#storeq').value = 'demo-1'; d.querySelector('#storeq').dispatchEvent(new w.Event('input', {bubbles: true}));
  const cards = d.querySelectorAll('#screen .rc[data-kind="mistake"]');
  ok(cards.length === 1 && /E2/.test(cards[0].textContent) && /옛 E\?-demo-1/.test(cards[0].textContent), '옛 표기로 검색 → 그 카드 하나, 카드에 옛 표기가 보임');
  ok(errors.length === 0, '실수 표 화면 오류 없음' + (errors.length ? ': ' + errors.join(' | ') : ''));
}

// 2) 판정 규칙·질문 유형·제출
{
  const {w, d, errors} = open(fileA, false);
  const PE = w.PE;
  ok(PE.store.projects.length === 1 && PE.store.past_answers.length === 1 && PE.store.mistakes.length === 3 && PE.store.lessons.length === 1 && Object.keys(PE.store.choices).length === 1, '저장소 주입: 프로젝트·지난 답변·교훈·선택 기록 각 1 · 실수 3(번호 칸 세 형식)');
  PE.setDim('material_type', 'video_promo');
  let m = PE.matchAspect('P2.5.on_screen_text');
  ok(m && m.winner.id === 'P2.5-260101-01' && !m.conflict, '좁은 범위 항목이 이김 (전시 영상 → 자막 한 줄)');
  m = PE.matchAspect('P1.4.ai_phrasing');
  ok(m && m.inferred, '추론(세기 5) 항목은 확인 필요로 표시');
  PE.setDim('material_type', 'slides');
  ok(PE.matchAspect('P2.5.on_screen_text').winner.id === 'P2.5-260101-02', '범위가 안 맞으면 전체 범위 항목');
  ok(!PE.applicable('P4').includes('P4.1.method_slides'), '파일 형식을 안 고르면 발표자료 방법(선택지마다 파일 형식 조건)은 숨음');
  PE.setDim('file_format', ['html']);
  ok(PE.applicable('P4').includes('P4.1.method_slides') && !PE.applicable('P4').includes('P4.1.method_video'), 'applies_when: 발표자료면 발표자료 방법만');
  let cards = 0; for (let i = 0; i < PE.screens.length; i++) { PE.go(i); cards += d.querySelectorAll('#screen .card').length; }
  ok(cards > 20, `모든 화면 렌더 (카드 ${cards})`);
  PE.go(PE.screens.findIndex(s => s.id === 'P1'));
  Array.from(d.querySelectorAll('#midbtns .btn')).find(b => b.textContent === '이 묶음 모두 그대로').click();
  ok(PE.state.aspects['P1.2.form'] && PE.state.aspects['P1.2.form'].choice === 'keep', '「이 묶음 모두 그대로」');
  PE.setAspect('P1.1.formality', 'new', 'plain', true); PE.setProject('topic', '시험');
  const p = PE.payload();
  ok(p.client === 'file' && p.aspects['P1.1.formality'].always && p.project.topic === '시험' && 'refs' in p && 'base_project' in p && 'new_refs' in p, '제출 JSON 필드');
  // 파일형식(여러 개) → PDF 변환본은 HTML을 골랐을 때만 보임 → 콘텐츠 유형(여러 개) → 목적·용도
  const s1 = PE.screens.findIndex(s => s.id === 'S1');
  ok(PE.screens[s1].dimensions.slice(0, 4).join(',') === 'file_format,pdf_export,material_type,purpose', 'S1 순서: 파일형식 · PDF 변환본 · 콘텐츠 유형 · 목적·용도');
  delete PE.state.dimensions.file_format; PE.go(s1);
  const cardOf = id => d.querySelector(`#screen .card[data-drop="dim:${id}"]`);
  ok(!!cardOf('file_format') && !cardOf('pdf_export') && /여러 개/.test(cardOf('file_format').textContent) && /여러 개/.test(cardOf('material_type').textContent), '처음엔 PDF 변환본 숨김, 파일형식·콘텐츠 유형은 여러 개');
  ['HTML', 'PPT(X)', 'DOC(X)', 'HWP(X)', 'Excel'].forEach(lb => ok(Array.from(cardOf('file_format').querySelectorAll('.opt')).some(o => o.textContent.includes(lb)), `파일형식 기본 탑재: ${lb}`));
  cardOf('file_format').querySelector('.opt[data-id="pptx"]').click();
  ok(!cardOf('pdf_export'), 'PPT(X)만 고르면 PDF 변환본 질문 없음');
  cardOf('file_format').querySelector('.opt[data-id="html"]').click();
  ok(PE.state.dimensions.file_format.join(',') === 'pptx,html' && !!cardOf('pdf_export'), 'HTML도 고르면 → 두 형식 동시 + PDF 변환본 질문이 나타남');
  cardOf('material_type').querySelector('.opt[data-id="slides"]').click();
  ok(Array.isArray(PE.state.dimensions.material_type), '콘텐츠 유형 여러 개 선택(옛 한 값도 목록으로 받음)');
  ok(!!cardOf('material_type').querySelector('.ogrp') && /영상/.test(cardOf('material_type').textContent), '콘텐츠 형태 선택지에 묶음 제목');
  // 선택에 따라 다음 목록이 달라진다 — 목차·질문·선택지 모두
  const iSF = PE.screens.findIndex(s => s.id === 'SF'), iSH = PE.screens.findIndex(s => s.id === 'SH');
  const optIds = id => cardOf(id) ? Array.from(cardOf(id).querySelectorAll('.opt')).map(o => o.dataset.id) : null;
  PE.setDim('file_format', ['pptx']); PE.setDim('orientation', ['landscape']); PE.go(iSF);
  ok(!optIds('orientation').includes('responsive') && optIds('format').join() === 'w169,w43,a4l,a3,other', 'PPT(X)+가로 → 크기: 16:9 · 4:3 · A4 가로 · A3만 (반응형·9:16 없음) ' + optIds('format').join());
  PE.go(iSF - 1); d.querySelector('#next').click();
  ok(PE.index() === iSF, '다음 → 화면·지면 규격'); d.querySelector('#next').click();
  ok(PE.screens[PE.index()].id !== 'SH', 'HTML을 안 고르면 「HTML 화면 구성」 목차는 건너뜀');
  // 답을 골라 같은 화면을 다시 그려도 보던 자리를 지킨다(맨 위로 튀지 않음) — 화면을 옮길 때만 맨 위로
  PE.go(PE.screens.findIndex(s => s.id === 'S1')); w.__y = 640;
  cardOf('file_format').querySelector('.opt[data-id="html"]').click();
  ok(w.scrollY === 640 && !!cardOf('pdf_export'), '조건에 쓰이는 답(파일 형식)을 골라 화면을 다시 그려도 스크롤 자리 유지 (' + w.scrollY + ')');
  cardOf('material_type').querySelector('.opt[data-id="slides"]').click();
  ok(w.scrollY === 640, '콘텐츠 형태를 골라도 스크롤 자리 유지');
  d.querySelector('#next').click();
  ok(w.scrollY === 0, '「다음」으로 화면을 옮기면 맨 위로');
  PE.setDim('file_format', ['pptx', 'html']); PE.setDim('orientation', ['portrait']); PE.go(iSF);
  ok(optIds('orientation').includes('responsive') && optIds('format').join() === 'v916,a4p,a3,mobile,other', 'HTML 추가+세로 → 크기: 9:16 · A4 세로 · A3(PPT) · 휴대폰 폭 ' + optIds('format').join());
  PE.go(iSH);
  ok(!!cardOf('view_mode') && !cardOf('frame') && !cardOf('nav'), 'HTML 화면 구성: 처음엔 넘겨 보는 방식만');
  cardOf('view_mode').querySelector('.opt[data-id="scenes"]').click();
  ok(!cardOf('frame') && !cardOf('nav') && !optIds('html_features').includes('progress'), '장면 자동 재생 → 화면 틀·목차 모양 안 물음, 진행 막대는 기본이라 선택지에 없음');
  cardOf('view_mode').querySelector('.opt[data-id="scroll"]').click();
  ok(!!cardOf('frame') && !cardOf('nav') && cardOf('frame').classList.contains('sub') && /골라서 나온 질문/.test(cardOf('frame').textContent), '스크롤 → 화면 틀(하위 질문 표시), 목차 모양은 아직');
  cardOf('frame').querySelector('.opt[data-id="left"]').click();
  ok(!!cardOf('nav'), '왼쪽 사이드바 → 목차 모양 질문이 나타남');
  cardOf('nav').querySelector('.opt[data-id="tree"]').click();
  cardOf('view_mode').querySelector('.opt[data-id="scenes"]').click();
  const pl = PE.payload();
  ok(!('frame' in pl.dimensions) && !('nav' in pl.dimensions) && PE.state.dimensions.nav === 'tree', '숨은 질문의 답은 제출에서 빠짐(화면에는 남아 다시 고르면 살아남)');
  PE.setDim('file_format', ['pptx']);
  ok(!('view_mode' in PE.payload().dimensions), 'HTML을 빼면 그 목차 안의 답도 제출에서 빠짐');
  // 기타 의견: 선택지 바로 아래 칸, 참고 끌어다 넣기는 그 아래(카드 맨 끝). 카드와 트리가 같은 값
  PE.setDim('file_format', ['html']); PE.go(PE.screens.findIndex(s => s.id === 'S1'));
  const ffCard = cardOf('file_format'), kids = Array.from(ffCard.children);
  const iOp = kids.findIndex(e => e.matches('textarea.opinion')), iDrop = kids.findIndex(e => e.classList.contains('drop')), iOpts = kids.findIndex(e => e.classList.contains('opts'));
  ok(iOpts >= 0 && iOp > iOpts && iDrop > iOp && iDrop === kids.length - 1, `질문 카드 순서: 선택지 → 기타 의견 → 참고 칸(맨 끝) (${iOpts},${iOp},${iDrop}/${kids.length})`);
  const op = ffCard.querySelector('textarea.opinion'); op.value = 'HTML은 발표용, PPT는 배포용'; op.dispatchEvent(new w.Event('input', {bubbles: true}));
  ok(PE.state.opinions['dim:file_format'] === 'HTML은 발표용, PPT는 배포용' && PE.payload().opinions['dim:file_format'] === 'HTML은 발표용, PPT는 배포용', '기타 의견 → 답·제출 JSON(opinions)');
  PE.tree.open('part1'); PE.tree.open('scr:S1'); PE.tree.detail('dim:file_format');
  const tOp = d.querySelector('#tree [data-detail="file_format"] textarea.opinion');
  ok(tOp && tOp.value === 'HTML은 발표용, PPT는 배포용', '사이드 트리 질문에도 같은 기타 의견 칸·같은 값');
  tOp.value = '트리에서 고침'; tOp.dispatchEvent(new w.Event('input', {bubbles: true}));
  ok(PE.state.opinions['dim:file_format'] === '트리에서 고침' && ffCard.querySelector('textarea.opinion').value === '트리에서 고침', '트리에서 고치면 본문 카드 칸도 같이 바뀜');
  PE.setDim('view_mode', 'scroll'); PE.state.opinions['dim:frame'] = '왼쪽 목차가 좋음'; PE.setDim('file_format', ['pptx']);
  ok(!('dim:frame' in PE.payload().opinions) && PE.payload().opinions['dim:file_format'] === '트리에서 고침', '숨은 질문(HTML 화면 틀)의 의견은 제출에서 빠짐');
  // 선택지 예시(움직이는 카드): 예시가 있는 질문만 카드로, 없는 질문(파일 형식)은 글 단추
  PE.setDim('file_format', ['html']); PE.setDim('view_mode', 'scroll'); PE.go(iSH);
  const frameCard = cardOf('frame'), dcards = frameCard.querySelectorAll('.dcard');
  ok(dcards.length === 6 && frameCard.querySelectorAll('iframe.demo').length === 6 && !!frameCard.querySelector('.drest .opt[data-id="other"]'), `화면 틀: 예시 카드 ${dcards.length}개(움직이는 예시) + 기타는 글 단추`);
  const ifr0 = frameCard.querySelector('.dcard[data-id="top"] iframe');
  ok(/demo-fade/.test(ifr0.getAttribute('srcdoc') || '') && ifr0.getAttribute('sandbox') === 'allow-scripts', '예시는 공통 바탕 CSS를 붙여 따로 떨어진 작은 화면(sandbox)에서 돈다');
  const leftCard = frameCard.querySelector('.dcard[data-id="left"]');
  ok(/방법 v2/.test(leftCard.textContent) && /내 프로젝트에서/.test(leftCard.textContent) && /접기 단추 추가/.test(leftCard.textContent), '내 예시 v2 가 엔진 기본(v1)을 이기고, 판 기록에 무엇이 달라졌는지 보임');
  const oldBtn = leftCard.querySelector('[data-oldv="1"]');
  oldBtn.click();
  ok(/지난 판 v1/.test(leftCard.textContent) && !/왼쪽 목차 v2/.test(leftCard.querySelector('iframe').getAttribute('srcdoc')), '「이 판 보기」 → 지난 판(v1) 예시로 바뀜');
  PE.go(PE.screens.findIndex(s => s.id === 'S1'));
  ok(!cardOf('file_format').querySelector('iframe') && !!cardOf('file_format').querySelector('.opt[data-id="html"]'), '파일 형식처럼 그림이 필요 없는 질문은 글 단추 그대로');
  PE.setDim('html_features', []); PE.go(iSH);
  const featCard = cardOf('html_features'), fIfr = featCard.querySelector('.dcard[data-id="search"] iframe');
  featCard.querySelector('.dcard[data-id="search"] .dpick').click();
  ok(PE.state.dimensions.html_features.includes('search') && featCard.querySelector('.dcard[data-id="search"]').getAttribute('aria-pressed') === 'true' && featCard.querySelector('.dcard[data-id="search"] iframe') === fIfr, '「이걸로 고르기」 → 답·표시 갱신, 예시 화면은 다시 불러오지 않음');
  // 사이드 트리: 지금 보는 자리 강조 + 「다음」을 누르면 따라감
  PE.go(iSH);
  const hereRow = () => d.querySelector('#tree .tr.here');
  ok(hereRow() && hereRow().parentElement.dataset.id === 'scr:SH' && /지금/.test(hereRow().textContent), '사이드 트리: 지금 보는 목차(HTML 화면 구성)가 빛나고 「지금」 표시');
  d.querySelector('#next').click();
  ok(hereRow() && hereRow().parentElement.dataset.id === 'scr:' + PE.screens[PE.index()].id && PE.screens[PE.index()].id !== 'SH', '「다음」 → 트리의 강조가 다음 목차로 옮겨감 (' + PE.screens[PE.index()].id + ')');
  // 취향 질문에도 예시 카드: 바탕색(P2.4.theme)
  PE.setDim('material_type', ['slides']); PE.go(PE.screens.findIndex(s => s.id === 'P2'));
  const thCard = d.querySelector('#screen [data-drop="aspect:P2.4.theme"]');
  ok(thCard && thCard.querySelectorAll('.dsec .dcard').length === 3, '취향 질문(바탕색)도 선택지마다 움직이는 예시 3개');
  thCard.querySelector('.dcard[data-id="light"] .dpick').click();
  ok(PE.state.aspects['P2.4.theme'] && PE.state.aspects['P2.4.theme'].value === 'light' && thCard.querySelector('.dcard[data-id="light"]').getAttribute('aria-pressed') === 'true', '예시 카드에서 고르면 취향 답이 됨');
  // 기타(직접 입력)는 여러 줄 칸
  PE.go(PE.screens.findIndex(s => s.id === 'S1')); PE.setDim('file_format', ['html', 'other']); PE.go(PE.screens.findIndex(s => s.id === 'S1'));
  ok(cardOf('file_format').querySelector('textarea.free') && !cardOf('file_format').querySelector('input[type="text"]'), '기타(직접 입력)는 여러 줄 칸(긴 말이 잘리지 않음)');
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
  PE.view('dashboard'); ok(d.querySelectorAll('#screen .stat').length === 10 && d.querySelectorAll('#screen .sim').length === 1, '대시보드 타일 10(대화 추천 적중률 포함) · 비슷한 프로젝트 1');
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
  PE.go(PE.screens.findIndex(s => s.id === 'S1'));
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
  Array.from(d.querySelectorAll('#pklist .opt')).find(x => x.dataset.target === 'aspect:P2.4.density').click();
  ok(PE.state.new_refs.length === 1 && PE.state.refs['aspect:P2.4.density'][0].kind === 'new_ref', '새 메모 → 넣기(다른 화면)');
  PE.tree.open('refs.history');
  ok(d.querySelectorAll('#tree .rc[data-kind="past"]').length === 1, '지난 답 내역 카드');
  ok(errors.length === 0, '오류 없음' + (errors.length ? ': ' + errors.join(' | ') : ''));
}
// 4-1) 1.3.0: 「레퍼런스 먼저」(1부 앞) · 「레퍼런스대로」 · 「제외」 · P2.6 움직임은 HTML·MP4·기타일 때만 · P2.7 은 2부에서 빠짐 · --prefill
{
  ok(!/나중에·해당 없음/.test(src), '「나중에·해당 없음」 문구가 페이지에 없음(→ 「제외」)');
  const {w, d, errors} = open(fileA, false);
  const PE = w.PE;
  ok(PE.screens[1].id === 'R0' && PE.screens[1].kind === 'reffirst' && PE.screens[2].id === 'S1', '화면 순서: 첫 화면 → 레퍼런스 먼저 → 1부 자료 종류');
  PE.go(1);
  const links = d.querySelectorAll('#screen .reflink a[target="_blank"]');
  ok(links.length === PE.store.design_refs.length && links.length >= 20, `레퍼런스 사이트 목록 ${links.length}개(새 탭 링크)`);
  ok(d.querySelector('#refsend').disabled, '레퍼런스가 없으면 「레퍼런스만 먼저 보내기」는 꺼짐');
  d.querySelector('#addref').click();
  const inp = d.querySelector('#refs0 input.where');
  inp.value = 'https://example.org/deck'; inp.dispatchEvent(new w.Event('input', {bubbles: true}));
  ok(PE.state.references.length === 1 && PE.state.references[0].where === 'https://example.org/deck' && !d.querySelector('#refsend').disabled, '+ 레퍼런스 추가 → 주소 입력 → 보내기 단추 켜짐(다시 그리지 않음)');
  const chip = lab => Array.from(d.querySelectorAll('#refs0 .refitem .chip')).find(c => c.textContent.startsWith(lab));
  chip('디자인').click(); chip('글').click();
  ok(PE.state.references[0].follow.join() === 'design,text' && chip('전체').getAttribute('aria-pressed') === 'false', '따를 것: 디자인 + 글 (전체 양식은 꺼짐)');
  chip('전체').click();
  ok(PE.state.references[0].follow.join() === 'all', '「전체 양식」을 누르면 전체 하나만');
  PE.applyRef('ref0', PE.refObject('project', 'demo_expo'));
  const fromProj = PE.state.references.find(r => r.from === 'project:demo_expo');
  ok(!!fromProj && fromProj.where === 'https://example.org/demo', '서랍의 지난 프로젝트 카드 → 찾은 레퍼런스(결과물 주소)');
  const pr = PE.payload('references');
  ok(pr.stage === 'references' && pr.references.length === 2 && pr.references[0].follow.join() === 'all' && PE.payload().stage === 'full', '제출 JSON: stage(references/full) · references');
  // 2부: 레퍼런스가 있으면 「레퍼런스대로」, 건너뛰기는 「제외」
  PE.setDim('file_format', ['pptx']); PE.setDim('material_type', ['slides']);
  PE.go(PE.screens.findIndex(s => s.id === 'P1'));
  const card1 = d.querySelector('#screen [data-drop="aspect:P1.1.energy"]');
  const bt = (card, c) => card.querySelector(`.row .btn[data-c="${c}"]`);
  ok(bt(card1, 'ref') && bt(card1, 'skip').textContent === '제외', '취향 카드: 「레퍼런스대로」 · 「제외」 단추');
  bt(card1, 'ref').click();
  ok(PE.state.aspects['P1.1.energy'].choice === 'ref' && PE.state.aspects['P1.1.energy'].value == null && !!card1.querySelector('.refnote'), '「레퍼런스대로」 → choice ref, 값은 계획 단계에서(안내 표시)');
  PE.setAspect('P1.1.humor', 'keep', 'none');
  d.querySelector('#refall').click();
  ok(PE.state.aspects['P1.1.humor'].choice === 'keep' && PE.state.aspects['P1.1.formality'].choice === 'ref', '「답 안 한 것 모두 레퍼런스대로」: 이미 고른 답은 그대로');
  bt(d.querySelector('#screen [data-drop="aspect:P1.1.energy"]'), 'skip').click();
  ok(PE.state.aspects['P1.1.energy'].choice === 'skip' && !PE.state.aspects['P1.1.energy'].from, '「제외」로 바꾸면 레퍼런스 표시가 빠짐');
  // P2.6 · P2.7
  ok(!PE.applicable('P2').some(a => a.startsWith('P2.7.')), 'P2.7 레퍼런스 질문은 2부에 없음(맨 앞으로 옮김)');
  ok(PE.applicable('P2').includes('P2.6.motion_strength'), 'PPT(X)만이어도 P2.6 움직임 질문을 묻는다(질문 은행 v4 — 숨기지 않음)');
  PE.setDim('file_format', ['pptx', 'html']);
  ok(PE.applicable('P2').includes('P2.6.motion_strength'), 'HTML을 더해도 P2.6 움직임 질문 그대로');
  PE.setDim('file_format', ['mp4']); PE.setDim('material_type', ['video_promo']);
  ok(PE.applicable('P2').includes('P2.6.motion_still'), 'MP4 영상이면 P2.6 질문(정지 화면 검수 포함)');
  // 「이번엔 레퍼런스 없이」
  PE.go(1);
  d.querySelector('#refnone').click();
  ok(PE.state.references.length === 0 && PE.state.ref_none && PE.screens[PE.index()].id === 'S1' && !Object.values(PE.state.aspects).some(s => s.choice === 'ref' && s.value == null), '「이번엔 레퍼런스 없이」 → 비우고 다음 화면, 값 없는 「레퍼런스대로」 답도 뺌');
  PE.go(PE.screens.findIndex(s => s.id === 'P1'));
  ok(!d.querySelector('#screen .btn[data-c="ref"]') && !d.querySelector('#refall'), '레퍼런스가 없으면 「레퍼런스대로」 단추 없음');
  ok(PE.payload().ref_none === true, '제출 JSON: ref_none');
  ok(errors.length === 0, '오류 없음' + (errors.length ? ': ' + errors.join(' | ') : ''));
}
// 4-2) --prefill: 레퍼런스를 분석해 채운 답 → 빈 칸만 채우고 「레퍼런스에서」 표시
{
  const pfF = path.join(tmp, '00_레퍼런스_채움.json');
  writeJson(pfF, {id: 'pf1', source: 'materials/인터뷰/01_제작인터뷰_답변_레퍼런스.json', doc: 'materials/인터뷰/00_레퍼런스_기준표.md',
    references: [{where: 'https://example.org/ref', note: '표 꼴이 좋음', follow: ['text']}],
    dimensions: {file_format: ['pptx'], material_type: ['slides'], no_such_dim: 'x'},
    aspects: {'P1.2.form': {value: 'outline', reason: '레퍼런스는 개조식'}, 'P1.1.energy': {value: 'calm', reason: '차분한 톤'}, 'P9.9.none': {value: 'x'}, 'P2.4.density': {value: 'no_such', reason: '없는 값'}}});
  const fileP = path.join(tmp, 'out', '01_제작인터뷰_채움.html');
  const r = spawnSync(PY, [...PYARGS, path.join(HERE, 'build_interview.py'), '--lecture', 'demo', '--mode', 'interview', '--out', fileP, '--prefill', pfF], {encoding: 'utf8', env: Object.assign({}, process.env, ENV)});
  ok(r.status === 0 && /no_such_dim/.test(r.stderr) && /P9\.9\.none/.test(r.stderr) && /no_such/.test(r.stderr) && /취향 3개/.test(r.stderr), 'build --prefill: 없는 질문·값은 빼고 알림 (' + (r.stderr.match(/레퍼런스로 채운 답[^\n]*/) || [''])[0] + ')');
  const {w, d, errors} = open(fileP, false);
  const PE = w.PE;
  const s = PE.state;
  ok(s.aspects['P1.2.form'].choice === 'ref' && s.aspects['P1.2.form'].value === 'outline' && s.aspects['P1.2.form'].from === 'reference' && s.aspects['P2.4.density'].value == null, 'prefill: 취향 답 = 레퍼런스대로 + 분석 값(없는 값은 값 없이)');
  ok(s.dimensions.file_format.join() === 'pptx' && s.dim_from.file_format === 'reference' && s.references.length === 1 && s.references[0].follow.join() === 'text', 'prefill: 1부 값 · 레퍼런스 목록');
  PE.go(1);
  ok(/큰 구분 2개 · 취향 3개/.test(d.querySelector('#screen .cur').textContent), '레퍼런스 먼저 화면: 채운 답 요약');
  PE.go(PE.screens.findIndex(s2 => s2.id === 'S1'));
  ok(/레퍼런스에서/.test(d.querySelector('#screen [data-drop="dim:file_format"]').textContent), '1부 카드: 「레퍼런스에서」 표시');
  d.querySelector('#screen [data-drop="dim:file_format"] .opt[data-id="html"]').click();
  ok(!PE.state.dim_from.file_format, '직접 고르면 「레퍼런스에서」 표시가 빠짐');
  PE.go(PE.screens.findIndex(s2 => s2.id === 'P1'));
  const fc = d.querySelector('#screen [data-drop="aspect:P1.2.form"]');
  ok(/레퍼런스에서/.test(fc.textContent) && /개조식/.test(fc.querySelector('.refnote').textContent), '취향 카드: 「레퍼런스에서」 + 분석 근거');
  PE.setAspect('P1.1.energy', 'change', 'lively');
  const p = PE.payload();
  ok(p.prefill && p.prefill.id === 'pf1' && p.prefill.aspects_kept.includes('P1.2.form') && !p.prefill.aspects_kept.includes('P1.1.energy'), '제출 JSON: prefill(판 · 그대로 둔 답)');
  ok(errors.length === 0, '오류 없음' + (errors.length ? ': ' + errors.join(' | ') : ''));
  // 같은 기기에서 다시 열어도 사용자가 바꾼 답을 덮지 않는다(같은 판)
  const html = fs.readFileSync(fileP, 'utf8');
  const dom2 = new JSDOM(html, {runScripts: 'dangerously', pretendToBeVisual: true, url: 'http://localhost/', beforeParse(win) { win.scrollTo = () => {}; for (let i = 0; i < w.localStorage.length; i++) { const k = w.localStorage.key(i); win.localStorage.setItem(k, w.localStorage.getItem(k)); } }});
  ok(dom2.window.PE.state.aspects['P1.1.energy'].value === 'lively', '다시 열어도 바꾼 답 유지(prefill 은 한 번만)');
}
// 4-3) 1.4.0 대화 추천: --recommend → 추천 답이 골라진 채로 시작 · 「대화 추천」/「추천 → 바꿈」 · 요약판 · 제출 차이 → recommend.py record/correct/suggest
{
  const RC = (args, env) => spawnSync(PY, [...PYARGS, path.join(HERE, 'recommend.py'), ...args], {encoding: 'utf8', env: Object.assign({}, process.env, env || ENV)});
  const st = RC(['selftest']);
  ok(st.status === 0 && /자체 시험 통과/.test(st.stdout), 'recommend.py 자체 시험' + (st.status ? ': ' + st.stdout.split('\n').filter(l => l.startsWith('FAIL')).join(' | ') : ''));
  const rcF = path.join(proj, 'demo', 'materials', '인터뷰', '00_추천.json');
  writeJson(rcF, {id: 'rc1', summary: 'materials/인터뷰/00_대화요약.md', signals: ['tag:강의', 'bad signal'],
    dimensions: {material_type: {value: ['slides'], reason: '강의 발표자료라고 함', basis: 'said'}, file_format: {value: ['html'], reason: '발표는 HTML', basis: 'inferred'}, no_such: {value: 'x'}},
    aspects: {'P2.4.theme': {value: 'dark', reason: '어두운 강의실', basis: 'said'}, 'P1.2.form': {value: 'sentence', reason: '짧은 문장 선호', basis: 'inferred'}, 'P9.x': {value: 'a'}, 'P1.1.energy': {value: 'no_such'}},
    project: {delivery: {value: 'artifact', reason: '휴대폰으로 봄', basis: 'inferred'}}});
  const ck = RC(['check', rcF]);
  ok(ck.status === 1 && /no_such/.test(ck.stdout) && /P9\.x/.test(ck.stdout) && /bad signal/.test(ck.stdout) && /취향 2/.test(ck.stdout), 'recommend.py check: 없는 질문·값·틀린 신호를 알림 (반대 시험)');
  const fileRc = path.join(tmp, 'out', '01_제작인터뷰_추천.html');
  const r = spawnSync(PY, [...PYARGS, path.join(HERE, 'build_interview.py'), '--lecture', 'demo', '--mode', 'interview', '--out', fileRc, '--recommend', rcF, '--like', 'demo_expo'], {encoding: 'utf8', env: Object.assign({}, process.env, ENV)});
  ok(r.status === 0 && /대화 추천: 1부 2개 · 취향 2개 · 3부 1개/.test(r.stderr), 'build --recommend (' + ((r.stderr.match(/대화 추천[^\n]*/) || [''])[0]) + ')');
  const {w, d, errors} = open(fileRc, false);
  const PE = w.PE, s = PE.state;
  ok(s.dimensions.material_type.join() === 'slides' && s.dim_from.material_type === 'reco' && Array.isArray(s.dimensions.purpose) && s.dimensions.purpose.join() === 'exhibit', '순서: 대화 추천(콘텐츠 형태=발표자료)이 지난 프로젝트 기본값(홍보 영상)을 이기고, 추천이 없는 칸은 기본값');
  ok(s.aspects['P1.2.form'].choice === 'keep' && s.aspects['P1.2.form'].value === 'sentence' && s.aspects['P2.4.theme'].choice === 'new' && s.aspects['P2.4.theme'].value === 'dark' && s.project.delivery === 'artifact', '취향: 학습값과 같으면 「그대로」, 처음이면 「처음 정함」으로 골라 둠 · 3부도 골라 둠');
  PE.go(PE.screens.findIndex(x => x.id === 'S1'));
  const panel = d.querySelector('#screen #recopanel');
  ok(!!panel && d.querySelector('#screen').firstElementChild === panel && /대화 추천/.test(panel.textContent) && panel.querySelector('[data-n="kept"]').textContent === '5' && panel.querySelector('[data-n="changed"]').textContent === '0', '화면 위 요약판: 대화 추천 5 · 그대로 5 · 바꿈 0');
  const mt = d.querySelector('#screen [data-drop="dim:material_type"] .recoline');
  ok(mt && mt.dataset.st === 'kept' && /대화 추천/.test(mt.textContent) && /강의 발표자료라고 함/.test(mt.textContent) && /직접 말함/.test(mt.textContent), '1부 카드: 「대화 추천」 + 한 줄 이유 + 근거(직접 말함)');
  w.__y = 300;
  d.querySelector('#screen [data-drop="dim:file_format"] .opt[data-id="pptx"]').click();
  const ff = d.querySelector('#screen [data-drop="dim:file_format"] .recoline');
  ok(ff && ff.dataset.st === 'changed' && /추천 → 바꿈/.test(ff.textContent) && d.querySelector('#recopanel [data-n="changed"]').textContent === '1', '바꾸면 「추천 → 바꿈」(추천 → 지금) · 요약판 바꿈 1');
  ok(w.scrollY === 300, '추천 칸을 바꿔 다시 그려도 스크롤 자리 유지');
  PE.go(PE.screens.findIndex(x => x.id === 'P2'));
  PE.setAspect('P2.4.theme', 'skip', null); PE.go(PE.screens.findIndex(x => x.id === 'P2'));
  const th = d.querySelector('#screen [data-drop="aspect:P2.4.theme"] .recoline');
  ok(th && th.dataset.st === 'cleared' && /\(비움\)/.test(th.textContent) && /어두운 강의실/.test(th.textContent), '취향 카드: 「제외」하면 「추천 → 바꿈」(비움) + 추천 이유');
  PE.setAspect('P2.4.theme', 'change', 'light'); PE.go(PE.screens.findIndex(x => x.id === 'P2'));
  ok(/바꾼 것 2개/.test(d.querySelector('#recopanel details summary').textContent), '요약판: 바꾼 것 목록(펼침)');
  const p = PE.payload();
  const it = k => p.recommend.items.find(x => x.key === k);
  ok(p.recommend.id === 'rc1' && p.recommend.signals.join() === 'tag:강의' && it('asp.P2.4.theme').outcome === 'changed' && it('asp.P2.4.theme').final === 'light' && it('asp.P1.2.form').outcome === 'kept'
    && it('dim.file_format').outcome === 'changed' && it('dim.file_format').final.join() === 'html,pptx' && it('pq.delivery').outcome === 'kept' && p.recommend.stats.kept === 3 && p.recommend.stats.changed === 2, '제출 JSON recommend: 항목별 추천 · 최종 · 결과(그대로 3 · 바꿈 2) · 신호');
  PE.view('dashboard');
  ok(/이번 인터뷰/.test(d.querySelector('#recodash').textContent) && /그대로 3/.test(d.querySelector('#recodash').textContent), '대시보드: 대화 추천 카드(이번 인터뷰 그대로 3)');
  PE.view('flow');
  PE.go(PE.screens.length - 1);
  ok(/대화 추천: 5개 중 그대로 3 · 바꿈 2/.test(d.querySelector('#screen').textContent), '정리 화면: 대화 추천 결과 한 줄');
  ok(errors.length === 0, '오류 없음' + (errors.length ? ': ' + errors.join(' | ') : ''));
  // 다시 열어도 바꾼 답을 덮지 않는다(추천은 한 번만)
  const html = fs.readFileSync(fileRc, 'utf8');
  const dom2 = new JSDOM(html, {runScripts: 'dangerously', pretendToBeVisual: true, url: 'http://localhost/', beforeParse(win) { win.scrollTo = () => {}; for (let i = 0; i < w.localStorage.length; i++) { const k = w.localStorage.key(i); win.localStorage.setItem(k, w.localStorage.getItem(k)); } }});
  ok(dom2.window.PE.state.aspects['P2.4.theme'].value === 'light' && dom2.window.PE.state.dimensions.file_format.join() === 'html,pptx', '다시 열어도 바꾼 답 유지(추천은 한 번만)');
  // 기록 → 배우기
  const ansF = path.join(proj, 'demo', 'materials', '인터뷰', '01_제작인터뷰_답변.json');
  writeJson(ansF, p);
  const rec1 = RC(['record', ansF]);
  ok(rec1.status === 0 && /추천 그대로 3 · 바꿈 2 · 지움 0/.test(rec1.stdout) && /이번 적중률 60%/.test(rec1.stdout), 'record: 추천 결과 기록 · 적중률 60% (' + rec1.stdout.split('\n')[0] + ')');
  const planF = path.join(tmp, 'plan_rc.md');
  const ap = spawnSync(PY, [...PYARGS, path.join(HERE, 'answers_to_plan.py'), '--lecture', 'demo', '--answers', ansF, '--out', planF], {encoding: 'utf8', env: Object.assign({}, process.env, ENV)});
  const plan = ap.status === 0 ? fs.readFileSync(planF, 'utf8') : '';
  ok(/## 대화 추천/.test(plan) && /추천 5칸 중 그대로 3 · 바꿈 2 · 지움 0 → 적중률 60%/.test(plan) && /`asp\.P2\.4\.theme` \| "dark" \| "light"/.test(plan), '계획 문서: 「대화 추천」 절(적중률 · 바꾼 칸 표)' + (ap.status ? ': ' + ap.stderr : ''));
  const rec2 = RC(['record', ansF]);
  ok(rec2.status === 0 && /이미 기록한 제출/.test(rec2.stdout), 'record 두 번 → 이중 기록 막음');
  const bad = RC(['correct', '--project', 'demo', '--key', 'asp.P2.4.theme', '--value', '"purple"', '--said', '보라로']);
  ok(bad.status !== 0 && /선택지에 없는 값/.test(bad.stdout), 'correct: 없는 값은 거절(반대 시험)');
  const cor = RC(['correct', '--project', 'demo', '--key', 'pq.delivery', '--value', '"repo"', '--said', '결과물은 레포에 넣어 줘']);
  ok(cor.status === 0 && /가중치 5/.test(cor.stdout) && /규칙 R-/.test(cor.stdout), 'correct: 수정 요청 한 번(가중치 5)으로 바로 규칙');
  const sg = RC(['suggest', '--from', rcF]);
  ok(sg.status === 0 && /pq\.delivery: 짐작한 값 대신 'repo'/.test(sg.stdout), 'suggest: 짐작한 추천(artifact)을 수정 요청 규칙(repo)이 이김');
  const cs = spawnSync(PY, [...PYARGS, path.join(HERE, 'check_store.py'), '--no-summary'], {encoding: 'utf8', env: Object.assign({}, process.env, ENV)});
  ok(cs.status === 0 && /대화 추천: 기록 \d+건/.test(cs.stdout), 'check_store: 대화 추천 기록·규칙 검사 통과');
  const fileD = path.join(tmp, 'out', '01_제작인터뷰_추천2.html');
  build(['--lecture', 'demo2', '--mode', 'interview', '--out', fileD]);
  const o2 = open(fileD, false);
  o2.w.PE.view('dashboard');
  ok(/60%/.test(o2.d.querySelector('#recodash').textContent) && !o2.d.querySelector('#recopanel') && o2.errors.length === 0, '다음 인터뷰 대시보드: 지금까지 적중률 60% · 추천 없이 열면 요약판 없음');
  // 작업 여건: 넓은 화면에서는 차분하게(calm) 3번, 휴대폰에서는 경쾌하게(lively) 3번 → 확실한 단서(기기) → 페이지가 열린 자리의 기기로 고른다
  ok(p.context && p.context.device === '넓은화면' && Number.isInteger(p.context.local_hour) && p.context.client === 'file', '제출 JSON context: 작업 여건(기기 · 시간 · 요일 · 여는 방식)');
  const logF = path.join(store, 'knowledge', 'recommend_log.json');
  const lg = JSON.parse(fs.readFileSync(logF, 'utf8'));
  const ev = (proj, day, dev, v) => ({run: proj + '@x', date: '2026-01-0' + day, project: proj, kind: 'interview', signals: ['tag:강의', 'ctx:기기=' + dev], weight: 1, key: 'asp.P1.1.energy', recommended: null, final: v, outcome: 'answered'});
  lg.events.push(ev('w1', 1, '넓은화면', 'calm'), ev('w2', 2, '넓은화면', 'calm'), ev('w3', 3, '넓은화면', 'calm'), ev('m1', 4, '휴대폰', 'lively'), ev('m2', 5, '휴대폰', 'lively'), ev('m3', 6, '휴대폰', 'lively'));
  fs.writeFileSync(logF, JSON.stringify(lg, null, 1));
  const ln = RC(['learn']);
  const stt = RC(['stats']);
  ok(ln.status === 0 && /asp\.P1\.1\.energy: 같은 칸이 2가지로 끝남 → 작업 여건·상황 차이로 판단 — 단서 ctx:기기=/.test(stt.stdout), 'learn · stats: 같은 칸이 갈린 까닭을 작업 여건(기기)으로 판단');
  const fileX = path.join(tmp, 'out', '01_제작인터뷰_여건.html');
  const rx = spawnSync(PY, [...PYARGS, path.join(HERE, 'build_interview.py'), '--lecture', 'demo3', '--mode', 'interview', '--out', fileX, '--recommend', rcF], {encoding: 'utf8', env: Object.assign({}, process.env, ENV)});
  ok(rx.status === 0 && /작업 여건 규칙 [1-9]/.test(rx.stderr), 'build --recommend: 작업 여건 규칙을 페이지에 넣음 (' + ((rx.stderr.match(/작업 여건 규칙 \d+개/) || [''])[0]) + ')');
  const openAs = narrow => { const errs = []; const dm = new JSDOM(fs.readFileSync(fileX, 'utf8'), {runScripts: 'dangerously', pretendToBeVisual: true, url: 'http://localhost/',
    beforeParse(win) { win.scrollTo = () => {}; win.addEventListener('error', e => errs.push(e.message)); win.matchMedia = q => ({matches: narrow && /max-width/.test(q), addEventListener() {}, removeEventListener() {}}); }}); return {w: dm.window, errs}; };
  const wide = openAs(false), phone = openAs(true);
  const en = o => o.w.PE.state.aspects['P1.1.energy'] || {};
  ok(en(wide).value === 'calm' && en(phone).value === 'lively' && wide.errs.length + phone.errs.length === 0, `열린 자리의 작업 여건으로 고름: 넓은 화면 → ${en(wide).value} · 휴대폰 → ${en(phone).value}`);
  phone.w.PE.go(phone.w.PE.screens.findIndex(x => x.id === 'P1'));
  const ec = phone.w.document.querySelector('#screen [data-drop="aspect:P1.1.energy"] .recoline');
  ok(ec && /작업 여건/.test(ec.textContent) && /지금 작업 여건/.test(ec.textContent), '카드: 「대화 추천」 이유에 작업 여건 규칙과 근거 표시');
  // 질문 은행 v3 → v4: P2.6 의 파일 형식 조건(v3 가 더한 것)만 빠진다
  const mg = spawnSync(PY, [...PYARGS, '-c', 'import sys,json; sys.path.insert(0, sys.argv[1]); import upgrade_store as U; q={"version":3,"categories":[],"aspects":[{"id":"P2.6.a","sub":"P2.6","when":{"material_type":["slides"],"file_format":["html","mp4","other"]}},{"id":"P2.6.b","sub":"P2.6","when":{"file_format":["pptx"]}}]}; n,_=U.migrate_qs(q); print(json.dumps(n["aspects"]))', HERE], {encoding: 'utf8'});
  const ma = JSON.parse(mg.stdout || '[]');
  ok(ma.length === 2 && !ma[0].when && ma[0].applies_when.material_type.join() === 'slides' && !ma[0].applies_when.file_format && ma[1].when.file_format.join() === 'pptx', 'upgrade v4: v3 가 더한 파일 형식 조건만 빼고(콘텐츠 형태는 applies_when), 사용자가 단 다른 조건은 그대로');
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
  w.PE.go(1); // 「레퍼런스만 먼저 보내기」 → db 저장 · 내려받기(이름 _레퍼런스)
  d.querySelector('#addref').click();
  const ri = d.querySelector('#refs0 input.where'); ri.value = 'D:/자료/참고_발표자료.pdf'; ri.dispatchEvent(new w.Event('input', {bubbles: true}));
  d.querySelector('#refsend').click();
  ok(!d.querySelector('#refsendbox').hidden && /"stage": "references"/.test(d.querySelector('#rjson').textContent), '레퍼런스만 먼저 보내기 → 제출 상자(JSON 미리 보기)');
  d.querySelector('#rsubmit').click(); await wait(50);
  d.querySelector('#rdl').click(); await wait(50);
  ok(calls.add.length === 2 && calls.add[1].stage === 'references' && calls.add[1].references[0].where === 'D:/자료/참고_발표자료.pdf' && calls.save.length === 2 && /01_제작인터뷰_답변_레퍼런스\.json$/.test(calls.save[1].filename), 'db · downloads: stage references, 파일 이름 _레퍼런스');
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
