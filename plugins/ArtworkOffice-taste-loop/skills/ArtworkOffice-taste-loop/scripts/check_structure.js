#!/usr/bin/env node
// GUI-Structure.html(구조 편집기) 범용 검사 — 누구의 데이터에도 기대지 않는다(starter + 임시 폴더).
// 편집기 빌드 → jsdom으로 열기 → 이름 바꾸기·질문/선택지 추가·조건 달기(화면 조작)·옮기기·빼기·되돌리기·미리보기·내보내기
// → 같은 편집 기록을 파이썬 structure.replay 로 적용한 결과와 JS 결과 대조(조건 판정도 대조)
// → structure_edits.py add / preview / apply --yes 로 임시 데이터 폴더에 반영 → 인터뷰 페이지에서 조건 동작 확인.
// 사용법: NODE_PATH=/tmp/slidecheck/node_modules node check_structure.js   (jsdom@24.1.3)
// 가정: starter 의 dimensions.json 에 질문 file_format(값 html 포함)이 있고, 첫 목차에 들어 있다.
'use strict';
const {JSDOM} = require('jsdom');
const {spawnSync} = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');

const HERE = __dirname;
const STARTER = path.join(HERE, '..', 'starter');
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'tl-struct-'));
let fails = 0;
const ok = (cond, msg) => { console.log((cond ? 'OK   ' : 'FAIL ') + msg); if (!cond) fails++; };
const proj = path.join(tmp, 'project'), store = path.join(tmp, 'store');
fs.mkdirSync(proj, {recursive: true});
fs.cpSync(STARTER, store, {recursive: true});
const ENV = Object.assign({}, process.env, {TASTE_LOOP_STORE: store, TASTE_LOOP_PROJECT: proj, CLAUDE_PROJECT_DIR: proj});
const PY = (process.platform === 'win32' ? ['python', 'py', 'python3'] : ['python3', 'python', 'py'])
  .find(c => spawnSync(c, ['-c', 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)']).status === 0) || 'python3';
const PYARGS = ['-X', 'utf8', '-I'];
const py = (args, input) => spawnSync(PY, [...PYARGS, ...args], {encoding: 'utf8', env: ENV, input});
const LECT = 'demo_lecture';

function build(mode, out, extra) {
  const r = py([path.join(HERE, 'build_interview.py'), '--lecture', LECT, '--mode', mode, '--out', out, ...(extra || [])]);
  if (r.status !== 0) { console.log(r.stdout, r.stderr); throw new Error('build 실패: ' + mode); }
  return r;
}
function open(file, withClaude) {
  const html = fs.readFileSync(file, 'utf8');
  const calls = {add: [], save: [], coll: []};
  const errors = [];
  const dom = new JSDOM(html, {runScripts: 'dangerously', pretendToBeVisual: true, url: 'http://localhost/',
    beforeParse(window) {
      window.scrollTo = () => {};
      window.addEventListener('error', e => errors.push(e.message));
      if (withClaude) window.claude = {use: async name => name === 'db' ? {collection: c => { calls.coll.push(c); return {add: async p => { calls.add.push(p); return {id: 'doc1'}; }}; }}
        : name === 'downloads' ? {save: async req => { calls.save.push(req); return {status: 'saved'}; }} : null};
    }});
  return {w: dom.window, d: dom.window.document, calls, errors};
}
const tick = () => new Promise(r => setTimeout(r, 0));
const btnByText = (root, txt) => Array.from(root.querySelectorAll('button')).find(b => b.textContent.trim() === txt);

(async () => {
  // 1) 편집기 빌드
  const fileE = path.join(tmp, 'out', '05_구조편집.html');
  const rb = build('edit', fileE);
  ok(/구조 편집기/.test(rb.stdout) && /반영 대기 편집 0건/.test(rb.stdout), '편집기 빌드: ' + rb.stdout.trim().slice(0, 80));
  const src = fs.readFileSync(fileE, 'utf8');
  ok(src.startsWith('<!doctype html>') && !/__TITLE__|__SPEC__/.test(src), '파일용 doctype · 자리표시자 치환');
  const scr = src.match(/<script>([\s\S]*)<\/script>/)[1];
  try { new Function(scr); ok(true, '스크립트 문법'); } catch (e) { ok(false, '스크립트 문법: ' + e.message); }
  const buildArt = build('edit', path.join(tmp, 'out', '05_구조편집_게시.html'), ['--artifact']);
  ok(fs.readFileSync(path.join(tmp, 'out', '05_구조편집_게시.html'), 'utf8').startsWith('<title>'), '게시용은 <title>로 시작');

  // 2) 편집 — 화면 조작 + 훅
  const {w, d, errors} = open(fileE, false);
  const E = w.PE_EDIT;
  ok(!!E && E.ops.length === 0 && E.pending.length === 0, '훅 PE_EDIT · 편집 0건');
  const M0 = E.model();
  const S1 = M0.dims.screens[0].id;
  const ff = M0.dims.dimensions.find(x => x.id === 'file_format');
  ok(!!ff && ff.values.some(v => v.id === 'html') && M0.dims.screens[0].dimensions.includes('file_format'), 'starter: 첫 목차에 file_format(html 포함)');
  const ffOther = ff.values.find(v => v.id !== 'html' && !v.free).id;
  ok(d.querySelectorAll('.part').length === 3 && d.querySelectorAll('#main > .tn').length === M0.dims.screens.length + M0.qs.categories.length + M0.qs.project_questions.length, '트리: 3부 머리 + 최상위 항목 전부');
  // 이름 바꾸기 (화면 조작)
  E.select({t: 'screen', id: S1});
  const panel = d.querySelector('.panel');
  panel.querySelector('input[data-f="name"]').value = '자료 종류(테스트)';
  btnByText(panel, '이름 바꾸기').click();
  ok(E.ops.length === 1 && E.ops[0].op === 'set' && E.ops[0].field === 'title' && E.model().dims.screens[0].title === '자료 종류(테스트)' && !!E.ops[0].at, '이름 바꾸기 → set 기록(시각 포함)');
  // 질문 추가 (화면 조작: 「+ 질문」 → 이름·유형 → 추가)
  E.select({t: 'screen', id: S1});
  btnByText(d.querySelector('.panel'), '+ 질문').click();
  const form = d.querySelector('[data-form="dim"]');
  form.querySelector('input[data-f="name"]').value = 'HTML 구성 방식';
  form.querySelector('input[data-f="id"]').value = 'd_test';
  btnByText(form, '추가').click();
  let M = E.model();
  ok(M.dims.dimensions.some(x => x.id === 'd_test' && x.type === 'single') && M.dims.screens[0].dimensions.slice(-1)[0] === 'd_test', '질문 추가 → 목차 끝에 들어감');
  E.add({t: 'value', dim: 'd_test', id: 'scroll'}, {label: '한 페이지 스크롤'});
  E.add({t: 'value', dim: 'd_test', id: 'app'}, {label: '메뉴가 있는 앱형'});
  E.add({t: 'value', dim: 'd_test', id: 'etc', }, {label: '기타', free: true});
  E.add({t: 'value', dim: 'd_test', id: 'mid'}, {label: '중간 넣기'}, null, 2);
  M = E.model();
  ok(M.dims.dimensions.find(x => x.id === 'd_test').values.map(v => v.id).join() === 'scroll,app,mid,etc', '선택지 추가·위치 지정');
  // 순서: d_test 를 목차 2번째로
  E.move({t: 'dim', id: 'd_test'}, null, 1);
  ok(E.model().dims.screens[0].dimensions[1] === 'd_test', '질문 옮기기(같은 목차 2번째)');
  // 조건 달기 (화면 조작)
  E.select({t: 'dim', id: 'd_test'});
  btnByText(d.querySelector('.panel'), '조건 바꾸기').click();
  btnByText(d.querySelector('[data-condeditor]'), '+ 조건 만들기').click();
  const sel = d.querySelector('[data-condeditor] select[data-f="cdim"]');
  ok(Array.from(sel.options).map(o => o.value).join() === ',file_format', '조건 후보: 앞에 있는 질문만(자기 자신 제외)');
  sel.value = 'file_format'; sel.dispatchEvent(new w.Event('change', {bubbles: true}));
  d.querySelector('[data-condeditor] .opt[data-id="html"]').click();
  ok(/「[^」]+」에서 HTML/.test(d.querySelector('[data-condeditor]').textContent), '미리 읽기 문장');
  btnByText(d.querySelector('[data-condeditor]'), '조건 저장').click();
  M = E.model();
  ok(JSON.stringify(M.dims.dimensions.find(x => x.id === 'd_test').when) === JSON.stringify({file_format: ['html']}), '조건 저장 → when {file_format:[html]}');
  // 선택지 묶음 제목 · 빼기 · 되살리기
  E.setField({t: 'value', dim: 'file_format', id: 'html'}, 'group', '웹');
  E.setField({t: 'value', dim: 'd_test', id: 'mid'}, 'retired', true);
  ok(E.model().dims.dimensions.find(x => x.id === 'd_test').values.find(v => v.id === 'mid').retired === true && E.model().dims.dimensions.find(x => x.id === 'file_format').values.find(v => v.id === 'html').group === '웹', '빼기 · 묶음 제목 기록');
  // 취향: 질문 추가(하위 묶음 id 로 시작) + 선택지 + 다른 하위 묶음으로 옮기기 + 하위 묶음 추가
  const cat0 = M.qs.categories[0]; const subs = Object.keys(cat0.subs);
  E.add({t: 'aspect', id: subs[0] + '.utest'}, {text: '테스트 취향 질문', type: 'single'}, subs[0]);
  E.add({t: 'option', aspect: subs[0] + '.utest', id: 'a'}, {label: '가'});
  E.add({t: 'aspect', id: subs[0] + '.utest2'}, {text: '테스트 취향 질문 2', type: 'text'}, subs[0]);
  const nOps = E.ops.length;
  ok(E.move({t: 'aspect', id: subs[0] + '.utest'}, subs[1], 0) === false && E.ops.length === nOps, '취향 질문을 다른 하위 묶음으로 옮기기 → 거절(id 규칙)');
  E.move({t: 'aspect', id: subs[0] + '.utest2'}, null, 0);
  M = E.model();
  const firstOfSub0 = M.qs.aspects.find(a => a.sub === subs[0]);
  ok(firstOfSub0 && firstOfSub0.id === subs[0] + '.utest2', '취향 질문 → 같은 하위 묶음 맨 앞으로');
  const crossMove = {op: 'move', node: {t: 'aspect', id: subs[0] + '.utest'}, parent: subs[1], index: 0};
  E.add({t: 'sub', cat: cat0.id, id: E.newId('sub', cat0.id)}, {name: '새 하위'});
  ok(Object.keys(E.model().qs.categories[0].subs).length === subs.length + 1, '하위 묶음 추가(dict 순서 끝)');
  // 3부 질문 + 또는 조건
  E.add({t: 'pq', id: 'q_test'}, {text: '테스트 3부 질문', type: 'text'});
  E.setWhen({t: 'pq', id: 'q_test'}, [{file_format: ['html']}, {file_format: [ffOther]}]);
  ok(Array.isArray(E.model().qs.project_questions.find(q => q.id === 'q_test').when), '또는 조건(목록)');
  // 목차 조건: 두 번째 목차는 html 일 때만 → 그 안 질문도 숨음
  const S2 = M.dims.screens[1].id, S2dim = M.dims.screens[1].dimensions[0];
  E.setWhen({t: 'screen', id: S2}, {file_format: ['html']});
  // 되돌리기: 선택지 추가 → 그 선택지 이름 바꾸기 → 추가를 되돌리면 이름 바꾸기도 같이 빠짐
  E.add({t: 'value', dim: 'd_test', id: 'tmp'}, {label: '임시'});
  E.setField({t: 'value', dim: 'd_test', id: 'tmp'}, 'label', '임시2');
  const n = E.ops.length;
  const gone = E.undo(n - 2);
  ok(E.ops.length === n - 2 && gone.length === 1 && !E.model().dims.dimensions.find(x => x.id === 'd_test').values.some(v => v.id === 'tmp'), '되돌리기: 뒤 편집 같이 빠짐 1건');
  // 실패하는 편집은 기록되지 않음
  const before = E.ops.length;
  ok(E.add({t: 'value', dim: 'd_test', id: 'scroll'}, {label: '중복'}) === false && E.ops.length === before, 'id 중복 → 기록 안 함');
  // 바뀐 것 화면
  E.view('changes');
  ok(d.querySelectorAll('[data-session] li').length === E.ops.length && /되돌리기/.test(d.querySelector('[data-session]').textContent), `바뀐 것: ${E.ops.length}건 · 되돌리기 버튼`);
  // 미리보기
  E.view('preview');
  ok(/숨음/.test(d.querySelector('[data-pdim="d_test"]').textContent), '미리보기: 답 전에는 조건 질문 숨음');
  d.querySelector('[data-pdim="file_format"] .opt[data-id="html"]').click();
  ok(!/숨음/.test(d.querySelector('[data-pdim="d_test"]').textContent) && !!d.querySelector('[data-pdim="d_test"] .opt[data-id="scroll"]') && !d.querySelector('[data-pdim="d_test"] .opt[data-id="mid"]'), '미리보기: HTML 고르면 보임 · 뺀 선택지는 안 보임');
  ok(E.shown.dim(S2dim) === true, '목차 조건 맞음 → 안 질문 보임');
  E.preview('file_format', [ffOther]);
  ok(E.shown.dim('d_test') === false && E.shown.dim(S2dim) === false, '다른 형식만 → 조건 질문·목차 안 질문 숨음');
  ok(Array.from(d.querySelectorAll('[data-pdim="file_format"] .cv p.small b')).some(x => x.textContent === '웹'), '미리보기: 선택지 묶음 제목 표시');
  // 내보내기
  E.view('export');
  const P = E.payload();
  ok(P.kind === 'structure_edits' && P.lecture === LECT && P.ops.length === E.ops.length && P.ops.every(o => o.at && o.node && o.op) && 'dims_version' in P.base, '내보내기 payload');
  ok(JSON.parse(d.querySelector('#json').textContent).ops.length === P.ops.length, '화면 JSON = payload');
  // 저장 → 다시 열면 복원
  const key = Object.keys(w.localStorage).find(k => k.startsWith('pe-edit:'));
  ok(!!key && JSON.parse(w.localStorage.getItem(key)).ops.length === E.ops.length, 'localStorage 저장');
  ok(errors.length === 0, '편집기 실행 중 오류 없음' + (errors.length ? ': ' + errors.join(' | ') : ''));

  // 3) 파이썬 structure.replay 와 대조
  const baseF = path.join(tmp, 'base.json'), opsF = path.join(tmp, 'ops.json');
  fs.writeFileSync(baseF, JSON.stringify(E.base()));
  fs.writeFileSync(opsF, JSON.stringify(E.ops));
  const pyCode = `import json,sys\nsys.path.insert(0, ${JSON.stringify(HERE)})\nimport structure as SX\nb=json.load(open(${JSON.stringify(baseF)},encoding='utf-8'))\nops=json.load(open(${JSON.stringify(opsF)},encoding='utf-8'))\nd,q,p=SX.replay(b['dims'],b['qs'],ops)\nans=[{},{'file_format':['html']},{'file_format':[${JSON.stringify(ffOther)}]}]\nvis=[[SX.dim_shown(x,a,d.get('screens',[])) for x in d['dimensions']] for a in ans]\nd2,q2,p2=SX.replay(b['dims'],b['qs'],ops+[json.loads(${JSON.stringify(JSON.stringify(crossMove))})])
print(json.dumps({'dims':d,'qs':q,'problems':p,'vis':vis,'qs2':q2,'p2':len(p2)},ensure_ascii=False))`;
  const r = py(['-c', pyCode]);
  if (r.status !== 0) console.log(r.stderr);
  const PYR = JSON.parse(r.stdout);
  const JSR = E.replay(E.ops);
  ok(PYR.problems.length === 0 && JSR.problems.length === 0, '두 쪽 모두 적용 문제 0');
  ok(JSON.stringify(PYR.dims) === JSON.stringify(JSR.m.dims), '파이썬 = JS: dimensions(순서·키 순서까지)');
  ok(JSON.stringify(PYR.qs) === JSON.stringify(JSR.m.qs), '파이썬 = JS: questions(하위 묶음 순서·취향 질문 위치까지)');
  const JX = E.replay(E.ops.concat([crossMove]));
  ok(PYR.p2 === 1 && JX.problems.length === 1 && JSON.stringify(PYR.qs2) === JSON.stringify(JX.m.qs), '파이썬 = JS: 다른 하위 묶음으로 옮기는 op 는 둘 다 거절(결과 변화 없음)');
  const ansSets = [{}, {file_format: ['html']}, {file_format: [ffOther]}];
  let same = true;
  ansSets.forEach((a, k) => { E.view('preview'); for (const key2 of Object.keys(E.previewAnswers())) E.preview(key2, null); for (const [kk, vv] of Object.entries(a)) E.preview(kk, vv);
    const js = E.model().dims.dimensions.map(x => E.shown.dim(x.id)); if (JSON.stringify(js) !== JSON.stringify(PYR.vis[k])) { same = false; console.log('  다름', k, JSON.stringify(js), JSON.stringify(PYR.vis[k])); } });
  ok(same, '조건 판정(질문 보임/숨음) 파이썬 = JS — 답 3가지');
  // 3-1) 손으로 쓴 「추가」 기록(1.3.0): 새 id 를 data.id 에만 두어도 받고, node.id 와 다르면 · 둘 다 없으면 거절하며 고칠 곳을 알린다
  const hand = {
    data_only: [{op: 'add', node: {t: 'value', dim: 'd_test'}, parent: 'd_test', data: {id: 'via_data', label: 'data에만 id'}}],
    mismatch: [{op: 'add', node: {t: 'value', dim: 'd_test', id: 'a1'}, parent: 'd_test', data: {id: 'b1', label: '다름'}}],
    no_id: [{op: 'add', node: {t: 'value', dim: 'd_test'}, parent: 'd_test', data: {label: 'id 없음'}}],
  };
  const handF = path.join(tmp, 'hand.json'); fs.writeFileSync(handF, JSON.stringify(hand));
  const pyHand = `import json,sys\nsys.path.insert(0, ${JSON.stringify(HERE)})\nimport structure as SX\nb=json.load(open(${JSON.stringify(baseF)},encoding='utf-8'))\nops=json.load(open(${JSON.stringify(opsF)},encoding='utf-8'))\nh=json.load(open(${JSON.stringify(handF)},encoding='utf-8'))\nout={}\nfor k,v in h.items():\n    d,q,p=SX.replay(b['dims'],b['qs'],ops+v)\n    out[k]={'dims':d,'problems':p}\nprint(json.dumps(out,ensure_ascii=False))`;
  const rh = py(['-c', pyHand]);
  if (rh.status !== 0) console.log(rh.stderr);
  const PH = JSON.parse(rh.stdout);
  const JH = Object.fromEntries(Object.entries(hand).map(([k, v]) => [k, E.replay(E.ops.concat(v))]));
  const vt = r0 => ((r0.dims || r0.m.dims).dimensions.find(x => x.id === 'd_test') || {values: []}).values.map(v => v.id).join(',');
  ok(PH.data_only.problems.length === 0 && JH.data_only.problems.length === 0 && /via_data/.test(vt(PH.data_only)) && vt(PH.data_only) === vt(JH.data_only), '손으로 쓴 추가: data.id 만 있어도 두 쪽 모두 받음 (' + vt(PH.data_only) + ')');
  ok(PH.mismatch.problems.length === 1 && JH.mismatch.problems.length === 1 && /두 곳에서 다름/.test(PH.mismatch.problems[0]) && /두 곳에서 다름/.test(JH.mismatch.problems[0].msg), 'node.id ≠ data.id → 두 쪽 모두 거절');
  ok(PH.no_id.problems.length === 1 && JH.no_id.problems.length === 1 && /node 안에/.test(PH.no_id.problems[0]) && /node 안에/.test(JH.no_id.problems[0].msg) && /"t": "value"/.test(PH.no_id.problems[0]), 'id 가 없으면 → 두 쪽 모두 거절, 새 id 자리를 예시로 알림');

  // 4) 기록 모음: add → 대기 편집이 인터뷰·편집기에 메모리로 보임 → preview → apply --yes
  const expF = path.join(tmp, 'out', '05_구조편집.json');
  fs.writeFileSync(expF, JSON.stringify(P, null, 1));
  let s = py([path.join(HERE, 'structure_edits.py'), 'add', expF]);
  ok(s.status === 0 && /쌓음: SE-/.test(s.stdout), 'structure_edits.py add → 반영 대기' + (s.status ? ': ' + s.stdout + s.stderr : ''));
  const fileI1 = path.join(tmp, 'out', '01_제작인터뷰_대기.html');
  const ri = build('interview', fileI1);
  ok(new RegExp(`반영 대기 구조 편집 ${P.ops.length}건`).test(ri.stderr) && /d_test/.test(fs.readFileSync(fileI1, 'utf8')), '인터뷰 빌드: 대기 편집을 메모리로 적용 + 알림');
  const riNo = build('interview', path.join(tmp, 'out', '01_제작인터뷰_원본.html'), ['--no-pending']);
  ok(!/반영 대기/.test(riNo.stderr) && !/d_test/.test(fs.readFileSync(path.join(tmp, 'out', '01_제작인터뷰_원본.html'), 'utf8')), '--no-pending: 파일 그대로');
  const fileE2 = path.join(tmp, 'out', '05_구조편집_2.html');
  build('edit', fileE2);
  {
    const o = open(fileE2, false);
    ok(o.w.PE_EDIT.pending.length === P.ops.length && o.w.PE_EDIT.ops.length === 0 && o.w.PE_EDIT.model().dims.dimensions.some(x => x.id === 'd_test'), '편집기: 대기 편집은 「반영 대기」로 따로, 이번 세션 0건');
    o.w.PE_EDIT.view('changes');
    ok(o.d.querySelectorAll('[data-pending] li').length === P.ops.length, '바뀐 것: 반영 대기(지난 편집) 목록');
    ok(o.errors.length === 0, '대기 편집 열기 오류 없음' + (o.errors.length ? ': ' + o.errors.join(' | ') : ''));
  }
  s = py([path.join(HERE, 'structure_edits.py'), 'preview']);
  ok(s.status === 0 && /검사: 문제 없음/.test(s.stdout), 'preview: 검사 문제 없음' + (s.status ? '\n' + s.stdout + s.stderr : ''));
  s = py([path.join(HERE, 'structure_edits.py'), 'apply']);
  ok(s.status === 0 && /--yes/.test(s.stdout) && !JSON.parse(fs.readFileSync(path.join(store, 'dimensions.json'), 'utf8')).dimensions.some(x => x.id === 'd_test'), 'apply(--yes 없음) → 파일 안 바뀜');
  s = py([path.join(HERE, 'structure_edits.py'), 'apply', '--yes']);
  const dimsAfter = JSON.parse(fs.readFileSync(path.join(store, 'dimensions.json'), 'utf8'));
  const led = JSON.parse(fs.readFileSync(path.join(store, 'knowledge', 'structure_edits.json'), 'utf8'));
  ok(s.status === 0 && JSON.stringify(dimsAfter.dimensions) === JSON.stringify(PYR.dims.dimensions) && led.batches.every(b => b.status === 'applied'), 'apply --yes → dimensions.json 반영 · 묶음 「반영됨」' + (s.status ? '\n' + s.stdout + s.stderr : ''));
  {  // 줄바꿈 LF 고정(실수 기록 E22): Windows 파이썬의 write_text 는 CRLF 로 써서 PC와 클라우드 결과가 달라진다
    const written = ['dimensions.json', 'questions.json', path.join('knowledge', 'structure_edits.json'), path.join('knowledge', '02_변경이력.md')]
      .filter(f => fs.existsSync(path.join(store, f)));
    const crlf = written.filter(f => fs.readFileSync(path.join(store, f)).includes('\r\n'));
    ok(written.length >= 3 && crlf.length === 0, `apply --yes 가 쓴 파일 ${written.length}개 줄바꿈 LF` + (crlf.length ? ' — CRLF: ' + crlf.join(', ') : ''));
  }
  s = py([path.join(HERE, 'check_store.py'), '--no-summary']);
  ok(s.status === 0, '반영 뒤 check_store 통과' + (s.status ? '\n' + s.stdout : ''));

  // 5) 반영 뒤 인터뷰: HTML 고르면 보이고, 아니면 숨음
  const fileI = path.join(tmp, 'out', '01_제작인터뷰.html');
  const r2 = build('interview', fileI);
  ok(!/반영 대기/.test(r2.stderr), '반영 뒤에는 대기 편집 없음');
  {
    const o = open(fileI, false);
    const PE = o.w.PE;
    const si = PE.screens.findIndex(x => x.id === S1);
    PE.setDim('file_format', [ffOther]); PE.go(si);
    ok(!o.d.querySelector('#screen .card[data-drop="dim:d_test"]'), `인터뷰: ${ffOther}만 → 「HTML 구성 방식」 숨음`);
    PE.setDim('file_format', ['html']); PE.go(si);
    const card = o.d.querySelector('#screen .card[data-drop="dim:d_test"]');
    ok(!!card && !!card.querySelector('.opt[data-id="scroll"]') && !card.querySelector('.opt[data-id="mid"]'), '인터뷰: HTML 고르면 보임 · 뺀 선택지 없음');
    const p = PE.payload ? PE.payload() : null;
    ok(o.errors.length === 0, '인터뷰 실행 중 오류 없음' + (o.errors.length ? ': ' + o.errors.join(' | ') : ''));
  }
  // 6) 게시 페이지 저장(가짜 db)
  {
    const o = open(fileE, true);
    o.w.PE_EDIT.view('export');
    btnByText(o.d, '저장 (게시 페이지)').click(); await tick(); await tick();
    ok(o.calls.coll[0] === 'structure_edits' && o.calls.add.length === 1 && o.calls.add[0].kind === 'structure_edits', 'db: structure_edits 에 add');
    btnByText(o.d, 'JSON 내려받기').click(); await tick(); await tick();
    ok(o.calls.save.length === 1 && o.calls.save[0].filename === '05_구조편집.json', 'downloads.save: 05_구조편집.json');
  }
  console.log(fails ? `실패 ${fails}개` : '오류 없음');
  try { fs.rmSync(tmp, {recursive: true, force: true}); } catch (e) {}
  process.exit(fails ? 1 : 0);
})().catch(e => { console.log('FAIL 예외: ' + (e && e.stack || e)); process.exit(1); });
