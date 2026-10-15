import assert from 'node:assert/strict';
import { readFileSync, readdirSync, existsSync } from 'node:fs';
import { join } from 'node:path';
const root = new URL('../', import.meta.url);
const read=(p)=>readFileSync(new URL(p,root),'utf8');
const files=readdirSync(new URL('tools/',root)).filter(f=>f.endsWith('.html'));
assert.equal(files.length,26,'There must be exactly 26 real tool pages');
assert.ok(existsSync(new URL('assets/og-mohsin-tools.jpg',root)),'Social preview file must exist');
const entries=['index.html',...files.map(f=>'tools/'+f)];
const seenTitles=new Set(),seenDescriptions=new Set(),seenUrls=new Set();
for(const filename of entries){
 const content=read(filename);
 const tag=(name)=>content.match(new RegExp('<'+name+'\\b[^>]*>','i'))?.[0]??'';
 const title=content.match(/<title>([^<]+)<\/title>/i)?.[1]??'';
 const description=content.match(/<meta\s+name="description"\s+content="([^"]+)"/i)?.[1]??content.match(/<meta\s+content="([^"]+)"\s+name="description"/i)?.[1]??'';
 const canonical=content.match(/<link[^>]*rel="canonical"[^>]*>/i)?.[0]??'';
 const url=canonical.match(/href="([^"]+)"/)?.[1]??'';
 const expected='https://tools.mohsinlabs.com/'+(filename==='index.html'?'':filename);
 assert.equal(url,expected,filename+': canonical mismatch');
 assert.match(content,/<h1\b/i,filename+': h1 missing');
 assert.ok(title.length>22&&title.length<=95,filename+': title problem');
 assert.ok(description.length>=50&&description.length<=190,filename+': description problem');
 assert.ok(!seenTitles.has(title),filename+': duplicate title');
 assert.ok(!seenDescriptions.has(description),filename+': duplicate description');
 assert.ok(!seenUrls.has(url),filename+': duplicate canonical');
 seenTitles.add(title);seenDescriptions.add(description);seenUrls.add(url);
 for(const prop of ['og:title','og:description','og:url','og:image']) assert.ok(content.includes('property="'+prop+'"'),filename+': '+prop+' missing');
 const script=content.match(/<script\s+type="application\/ld\+json"[^>]*>([\s\S]*?)<\/script>/i);
 assert.ok(script,filename+': JSON-LD missing');
 const data=JSON.parse(script[1]);
 assert.equal(data['@context'],'https://schema.org');
 if(filename.startsWith('tools/')){
  assert.match(content,/class="container seo-related"/,filename+': related links missing');
  assert.ok(data['@graph'].some(o=>o['@type']==='WebApplication'),filename+': schema software app missing');
  assert.ok(data['@graph'].some(o=>o['@type']==='BreadcrumbList'),filename+': breadcrumbs missing');
 }
}
const sitemap=read('sitemap.xml');
for(const url of seenUrls) assert.ok(sitemap.includes('<loc>'+url+'</loc>'),'Sitemap missing '+url);
assert.equal((sitemap.match(/<loc>/g)||[]).length,28,'Expected homepage, privacy and 26 tools in sitemap');
assert.ok(read('robots.txt').includes('https://tools.mohsinlabs.com/sitemap.xml'));
console.log('PASS SEO: 27 distinct indexable core pages, titles/descriptions, OG/social, JSON-LD, related links and 28 sitemap URLs');