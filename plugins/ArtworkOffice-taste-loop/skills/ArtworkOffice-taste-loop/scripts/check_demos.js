#!/usr/bin/env node
// 선택지 예시(knowledge/demos) 검사 + 한눈에 보기 페이지
// 사용법: node check_demos.js [<demos 폴더>] [--gallery <출력.html>]
//   <demos 폴더> 기본값: 엔진 starter/knowledge/demos
// 검사: index.json 의 항목마다 파일이 있는지, 크기(16KB 이하), 바깥 주소(http) 없음, <html>/<head>/<body> 태그 없음,
//       <script> 문법, 필수 칸(title·now·later·version·history). 옛 판 파일(history[].file)도 있는지.
// jsdom 이 있으면(NODE_PATH) 예시마다 실제로 열어 스크립트 오류가 없는지도 본다.
'use strict';
const fs = require('fs');
const path = require('path');
const HERE = __dirname;
const argv = process.argv.slice(2);
const gi = argv.indexOf('--gallery');
const gallery = gi >= 0 ? argv[gi + 1] : null;
// 폴더 인자: --gallery 의 값이 아닌 첫 인자. (1.2.0 에서는 --gallery 가 없을 때 gi + 1 = 0 이라 첫 인자를 늘 버려 엔진 기본 폴더만 검사했다 — 1.3.0 에서 고침)
const dir = path.resolve(argv.find((a, i) => !a.startsWith('--') && (gi < 0 || i !== gi + 1)) || path.join(HERE, '..', 'starter', 'knowledge', 'demos'));
const BASE = fs.readFileSync(path.join(HERE, '..', 'demo_base.css'), 'utf8');
let fails = 0;
const ok = (c, m) => { if (!c) fails++; console.log((c ? 'OK   ' : 'FAIL ') + m); };
const idxPath = path.join(dir, 'index.json');
if (!fs.existsSync(idxPath)) { console.log('index.json 없음: ' + idxPath); process.exit(1); }
const idx = JSON.parse(fs.readFileSync(idxPath, 'utf8'));
const items = idx.items || {};
let jsdom = null; try { jsdom = require('jsdom'); } catch (e) {}
// Windows 에서 core.autocrlf=true 로 받은 작업 사본은 파일이 CRLF 다. git 에 LF 로 들어 있으면(i/lf) 받을 때 바뀐 것이라 오류가 아니다(1.3.0).
// git 에 없는 새 파일(demos.py add 직후)이나 git 에도 CRLF 로 들어간 파일은 그대로 오류로 본다
const indexEol = (() => {
  try {
    const r = require('child_process').spawnSync('git', ['-C', dir, 'ls-files', '--eol', '-z', '.'], {encoding: 'utf8'});
    if (r.status !== 0) return {};
    const m = {};
    for (const rec of r.stdout.split('\0')) { const t = rec.indexOf('\t'); if (t > 0) m[rec.slice(t + 1)] = rec.slice(0, t).trim().split(/\s+/)[0]; }
    return m;
  } catch (e) { return {}; }
})();
const wrap = frag => '<!doctype html><html lang="ko"><head><meta charset="utf-8"><style>' + BASE + '</style></head><body>' + frag + '</body></html>';
const checkFile = (key, rel) => {
  const fp = path.join(dir, rel);
  if (!fs.existsSync(fp)) { ok(false, `${key}: 파일 없음 ${rel}`); return null; }
  const s = fs.readFileSync(fp, 'utf8');
  const errs = [];
  if (Buffer.byteLength(s) > 16 * 1024) errs.push(`크기 ${Buffer.byteLength(s)}B > 16KB`);
  if (/(src|href)\s*=\s*["']?\s*(https?:)?\/\//i.test(s) || /url\(\s*["']?(https?:)?\/\//i.test(s) || /@import/i.test(s)) errs.push('바깥 주소 참조');
  if (/<\/?(html|head|body)[\s>]/i.test(s)) errs.push('<html>/<head>/<body> 태그(조각만 쓴다)');
  if (/\r/.test(s) && indexEol[rel.replace(/\\/g, '/')] !== 'i/lf') errs.push('CRLF 줄바꿈(LF 로)');
  for (const m of s.matchAll(/<script>([\s\S]*?)<\/script>/g)) { try { new Function(m[1]); } catch (e) { errs.push('스크립트 문법: ' + e.message); } }
  ok(!errs.length, `${key} (${rel})` + (errs.length ? ': ' + errs.join(' · ') : ''));
  return s;
};
const shown = [];
for (const [key, it] of Object.entries(items)) {
  const miss = ['title', 'now', 'later', 'version', 'file', 'history'].filter(k => it[k] == null || it[k] === '');
  if (miss.length) ok(false, `${key}: 빈 칸 ${miss.join(',')}`);
  if (!/^(dim|asp)\.[^|]+\|[^|]+$/.test(key)) ok(false, `${key}: 키 형식은 dim.<질문>|<선택지> 또는 asp.<취향 질문>|<선택지>`);
  const s = checkFile(key, it.file);
  for (const h of it.history || []) if (h.file && h.file !== it.file) checkFile(key + ' v' + h.v, h.file);
  if (s != null) shown.push([key, it, s]);
}
(async () => {
  if (jsdom) {
    const {JSDOM, VirtualConsole} = jsdom;
    for (const [key, , s] of shown) {
      const errs = [];
      const vc = new VirtualConsole(); vc.on('jsdomError', e => { if (!/Not implemented/.test(e.message)) errs.push(e.message); });
      const dom = new JSDOM(wrap(s), {runScripts: 'dangerously', pretendToBeVisual: true, virtualConsole: vc,
        beforeParse(w) { w.addEventListener('error', e => errs.push(e.message)); w.matchMedia = w.matchMedia || (() => ({matches: false, addEventListener() {}, removeEventListener() {}})); w.requestAnimationFrame = f => setTimeout(() => f(Date.now()), 16); w.cancelAnimationFrame = id => clearTimeout(id); w.HTMLCanvasElement.prototype.getContext = () => null; }});
      await new Promise(r => setTimeout(r, 150));
      // 단추를 한 번씩 눌러 본다(오류만 본다)
      for (const b of Array.from(dom.window.document.querySelectorAll('button')).slice(0, 12)) { try { b.click(); } catch (e) { errs.push('클릭: ' + e.message); } }
      await new Promise(r => setTimeout(r, 50));
      ok(!errs.length, `${key}: 열기·단추 누르기 오류 없음` + (errs.length ? ': ' + errs.slice(0, 2).join(' | ') : ''));
      dom.window.close();
    }
  } else console.log('(jsdom 없음 — 실행 검사는 건너뜀. NODE_PATH 에 jsdom@24.1.3)');
  if (gallery) {
    const esc = t => String(t).replace(/[&<>"]/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]));
    const cards = shown.map(([key, it, s]) => `<div class="c"><b>${esc(key)}</b> · ${esc(it.title)} <small>v${it.version}</small><iframe sandbox="allow-scripts" srcdoc="${esc(wrap(s))}"></iframe><p><b>누른 순간</b> ${esc(it.now)}<br><b>나중에</b> ${esc(it.later)}</p></div>`).join('\n');
    fs.writeFileSync(gallery, `<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>선택지 예시 모음</title><style>body{font:14px/1.5 system-ui,sans-serif;margin:16px;background:#f4f6f8}.g{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:14px}.c{background:#fff;border:1px solid #d6dce4;border-radius:12px;padding:10px}iframe{width:100%;aspect-ratio:16/10;border:1px solid #d6dce4;border-radius:8px;margin:6px 0}p{margin:0;font-size:12px}</style></head><body><h1>선택지 예시 모음 (${shown.length})</h1><div class="g">${cards}</div></body></html>\n`);
    console.log('한눈에 보기: ' + gallery);
  }
  console.log(fails ? `실패 ${fails}개` : `오류 없음 (예시 ${shown.length}개)`);
  process.exit(fails ? 1 : 0);
})();
