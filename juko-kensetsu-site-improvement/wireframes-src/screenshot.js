// screenshot.js — renders wireframe/diagram HTML sources to PNG with Playwright.
// Usage: NODE_PATH=/opt/node22/lib/node_modules node screenshot.js [name ...]
//   (no args = build everything). Names match the PNG basename without extension.
// Step 1: inline _kit.css into each HTML (between <style id="kit"> and </style>) so
//         every HTML file renders standalone from file://.
// Step 2: screenshot each page (fullPage PNG) into ../images/.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const SRC = __dirname;
const OUT = path.resolve(__dirname, '..', 'images');

// name, viewport width, deviceScaleFactor
const PAGES = [
  ['01_sitemap_current',   1400, 1],
  ['02_sitemap_proposed',  1600, 1],
  ['03_user_flow',         1600, 1],
  ['04_design_tokens',     1400, 1],
  ['05_priority_matrix',   1400, 1],
  ['06_layout_grid',       1400, 1],
  ['10_wf_top_pc',         1280, 1],
  ['11_wf_top_sp',          390, 2],
  ['12_wf_concept_pc',     1280, 1],
  ['13_wf_works_list_pc',  1280, 1],
  ['14_wf_works_detail_pc',1280, 1],
  ['15_wf_voice_pc',       1280, 1],
  ['16_wf_flow_pc',        1280, 1],
  ['17_wf_company_pc',     1280, 1],
  ['18_wf_contact_pc',     1280, 1],
  ['19_wf_contact_sp',      390, 2],
];

function inlineKit(file) {
  const kit = fs.readFileSync(path.join(SRC, '_kit.css'), 'utf8');
  let html = fs.readFileSync(file, 'utf8');
  const re = /<style id="kit">[\s\S]*?<\/style>/;
  if (!re.test(html)) throw new Error(`no <style id="kit"> in ${file}`);
  const next = html.replace(re, () => `<style id="kit">\n${kit}\n</style>`);
  if (next !== html) fs.writeFileSync(file, next);
}

(async () => {
  const only = process.argv.slice(2);
  const list = only.length ? PAGES.filter(p => only.includes(p[0])) : PAGES;
  if (!list.length) { console.error('nothing matched'); process.exit(1); }
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch();
  for (const [name, width, dsf] of list) {
    const file = path.join(SRC, `${name}.html`);
    inlineKit(file);
    const ctx = await browser.newContext({ viewport: { width, height: 400 }, deviceScaleFactor: dsf });
    const page = await ctx.newPage();
    const errors = [];
    page.on('pageerror', e => errors.push(String(e)));
    page.on('requestfailed', r => errors.push('request failed: ' + r.url()));
    await page.goto('file://' + file, { waitUntil: 'load' });
    await page.evaluate(() => document.fonts.ready);
    // guard: body must not scroll horizontally
    const sw = await page.evaluate(() => document.documentElement.scrollWidth);
    const out = path.join(OUT, `${name}.png`);
    await page.screenshot({ path: out, fullPage: true, type: 'png' });
    const st = fs.statSync(out);
    console.log(`${name}.png  ${width}x? @${dsf}x  ${(st.size/1024).toFixed(0)} KB${sw > width ? '  !! overflow scrollWidth=' + sw : ''}${errors.length ? '  !! ' + errors.join('; ') : ''}`);
    await ctx.close();
  }
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
