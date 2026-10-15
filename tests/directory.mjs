import assert from 'node:assert/strict';
import {readFileSync,readdirSync} from 'node:fs';
const root=new URL('../',import.meta.url);
const html=readFileSync(new URL('index.html',root),'utf8');
const files=readdirSync(new URL('tools/',root)).filter(x=>x.endsWith('.html'));
const cards=[...html.matchAll(/data-tool-card[^>]*href="\/tools\/([^"]+)"/g)].map(x=>x[1]);
assert.equal(cards.length,26,'Exactly 26 unique working cards');
assert.equal(new Set(cards).size,26,'Duplicate tool cards');
assert.equal(files.length,26,'Exactly 26 tool pages');
assert.deepEqual(new Set(cards),new Set(files),'Every tool has a card');
const sitemap=readFileSync(new URL('sitemap.xml',root),'utf8');
for(const tool of files){
 const page=readFileSync(new URL(`tools/${tool}`,root),'utf8');
 assert(page.includes(`<title>`),`${tool}: missing title`);
 assert(page.includes(`rel="canonical"`),`${tool}: missing canonical`);
 assert(sitemap.includes(`https://tools.mohsinlabs.com/tools/${tool}`),`${tool}: not in sitemap`);
}
const sec=readFileSync(new URL('_headers',root),'utf8');
assert(sec.includes('https://static.cloudflareinsights.com'),'Cloudflare Analytics script blocked');
assert(sec.includes('connect-src \'self\''),'Cloudflare beacon POST blocked');
const code=readFileSync(new URL('assets/extra-tools.js',root),'utf8');
assert(!/fetch\s*\(|XMLHttpRequest|navigator\.sendBeacon/.test(code),'No tool input uploads');
console.log('PASS: 26 unique tools, linked/indexable pages, safe privacy-first processing and analytics CSP');