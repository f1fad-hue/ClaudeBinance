// Renders allocation.html as an Android phone would and fails on layout defects that a
// string check cannot see. Rev. 26 found five this way (see VERIFICATION.md).
//
//   NODE_PATH=$(npm root -g) node phone.mjs [width]        412 = Pixel 7, 360 = narrowest common
//
// The artifact host supplies the document shell, so the page is wrapped in one with the
// same device-width viewport and light colour scheme. CHROMIUM_PATH overrides the browser.
import { createRequire } from 'module';
import fs from 'fs';
const require = createRequire(import.meta.url);
const { chromium, devices } = require('playwright');
const width = +(process.argv[2] || 412);
const frag = fs.readFileSync(new URL('./allocation.html', import.meta.url), 'utf8');
const doc = `<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>:root{color-scheme:light}</style></head><body>${frag}</body></html>`;
const browser = await chromium.launch(process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {});
const page = await (await browser.newContext({ ...devices['Pixel 7'], viewport: { width, height: 839 } })).newPage();
const errs = [];
page.on('pageerror', e => errs.push(String(e)));
// web fonts may be unreachable from a sandbox; the page falls back to system fonts
await page.route(/fonts\.(googleapis|gstatic)\.com/, r => r.abort());
await page.setContent(doc, { waitUntil: 'load' });
const tabs = await page.$$eval('.tabs [data-p]', bs => bs.map(b => b.id));
const fails = [];
for (const t of tabs) {
  await page.tap('#' + t);
  await page.waitForTimeout(100);
  const r = await page.evaluate((t) => {
    const b = document.getElementById(t), p = document.getElementById(b.dataset.p);
    const vis = [...document.querySelectorAll('section.pane')].filter(s => getComputedStyle(s).display !== 'none').map(s => s.id);
    const bar = document.querySelector('.tabs').getBoundingClientRect();
    const scrolled = e => { for (let a = e.parentElement; a; a = a.parentElement) { const o = getComputedStyle(a).overflowX; if (o === 'auto' || o === 'scroll') return true; } return false; };
    const wide = [...p.querySelectorAll('*')].filter(e => { const q = e.getBoundingClientRect(); return q.width && q.right > innerWidth + 1 && !scrolled(e); })
      .map(e => e.tagName + '.' + e.className).slice(0, 3);
    // a table that scrolls sideways hides columns; the swipe deck is meant to scroll
    const hidden = [...p.querySelectorAll('.tw')].filter(w => w.scrollWidth > w.clientWidth + 1).map(w => w.querySelector('th').textContent);
    const pills = [...p.querySelectorAll('.sig')].filter(e => getComputedStyle(e).borderTopWidth !== '0px' || parseFloat(getComputedStyle(e).paddingTop) > 3).map(e => e.textContent);
    // SVG text sizes are in viewBox units: scale them to what the screen shows
    const sizes = [...p.querySelectorAll('*')].filter(e => [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim())).map(e => {
      const fs = parseFloat(getComputedStyle(e).fontSize), svg = e.closest('svg');
      return svg && svg.viewBox.baseVal && svg.viewBox.baseVal.width ? fs * svg.getBoundingClientRect().width / svg.viewBox.baseVal.width : fs; });
    return { vis, sel: b.getAttribute('aria-selected'), barBottom: Math.round(bar.bottom), vh: innerHeight,
             scrollW: document.documentElement.scrollWidth, wide, hidden, pills, minFont: Math.round(10 * Math.min(...sizes)) / 10 };
  }, t);
  const ok = r.vis.length === 1 && r.sel === 'true' && Math.abs(r.barBottom - r.vh) <= 1 && r.scrollW <= width &&
             !r.wide.length && !r.hidden.length && !r.pills.length && r.minFont >= 9;
  if (!ok) fails.push(t);
  console.log(`${ok ? 'ok  ' : 'FAIL'} ${t.padEnd(10)} pane=${r.vis.join(',')} bar@${r.barBottom}/${r.vh} width=${r.scrollW}/${width} min-font=${r.minFont}px` +
              (r.wide.length ? ` off-screen=${r.wide}` : '') + (r.hidden.length ? ` tables-overflow=${r.hidden}` : '') + (r.pills.length ? ` bad-pill=${r.pills}` : ''));
}
await browser.close();
if (errs.length) console.log('JS errors: ' + errs.join(' | '));
const bad = fails.length || errs.length;
console.log(bad ? `PHONE FAIL at ${width}px` : `phone: ${tabs.length} tabs at ${width}px, one pane each, bar pinned, nothing off-screen, text ≥ 9px`);
process.exit(bad ? 1 : 0);
