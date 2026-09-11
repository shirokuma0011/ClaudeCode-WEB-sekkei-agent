/**
 * verify-prototype.js
 * ────────────────────────────────────────────────────────────────
 * prototype/ の2ページを Chromium で実際に描画し、設計書 08章「受入基準」の
 * うち自動判定できる項目を検証します。実装後の本番サイトにも流用できます。
 *
 *   使い方:  node tools/verify-prototype.js
 *   必要:    npm i -D playwright  （本スクリプトは /opt/node22 の playwright を参照します。
 *            手元で動かす場合は require のパスを 'playwright' に変えてください）
 *
 * 検証項目:
 *   - 320 / 390 / 768 / 1024 / 1440px で横スクロールが発生しないこと
 *   - html lang / h1の数 / 見出し階層 / ID重複
 *   - 全画像の alt と width・height 属性（CLS対策）
 *   - viewport に user-scalable=no がないこと
 *   - title・description の文字数（07章2節のルール）
 *   - タップターゲット44px（WCAG 2.5.5/2.5.8 の例外を適用して判定）
 *       ・stretched link（::after{position:absolute}）はカード全体を実効領域とみなす
 *       ・文章中のインラインリンク／パンくずは inline 例外として除外
 * ────────────────────────────────────────────────────────────────
 */
const {chromium}=require('/opt/node22/lib/node_modules/playwright');
const path=require('path');
(async()=>{
  const b=await chromium.launch();
  let fail=0;
  for(const file of ['index.html','property.html']){
    const url='file://'+path.resolve(__dirname,'..','prototype',file);
    console.log('\n══ '+file+' ══');
    for(const w of [320,390,768,1024,1440]){
      const p=await b.newPage({viewport:{width:w,height:900}});
      await p.goto(url,{waitUntil:'load'}); await p.waitForTimeout(200);
      const r=await p.evaluate(()=>{
        const de=document.documentElement;
        const over=[...document.querySelectorAll('*')].filter(el=>el.getBoundingClientRect().right>de.clientWidth+1)
          .map(el=>el.tagName+(el.className&&typeof el.className==='string'?'.'+el.className.split(' ')[0]:''));
        return {sw:de.scrollWidth, cw:de.clientWidth, over:[...new Set(over)].slice(0,5)};
      });
      const ok = r.sw<=r.cw+1;
      if(!ok) fail++;
      console.log(`  ${String(w).padStart(4)}px  横スクロール: ${ok?'なし ✅':'あり ❌ '+JSON.stringify(r.over)}  (scrollW=${r.sw}/clientW=${r.cw})`);
      await p.close();
    }
    const p=await b.newPage({viewport:{width:1440,height:900}});
    await p.goto(url,{waitUntil:'load'});
    const a=await p.evaluate(()=>{
      const imgs=[...document.querySelectorAll('img')];
      const ids=[...document.querySelectorAll('[id]')].map(e=>e.id);
      const dup=ids.filter((v,i)=>ids.indexOf(v)!==i);
      // heading order
      const hs=[...document.querySelectorAll('h1,h2,h3,h4')].map(h=>+h.tagName[1]);
      let skip=[]; for(let i=1;i<hs.length;i++) if(hs[i]-hs[i-1]>1) skip.push(hs[i-1]+'→'+hs[i]);
      // tap targets
      // WCAG 2.5.5/2.5.8 に沿って例外を適用して判定
      //  - stretched link（::after{position:absolute;inset:0}）はカード全体が実効領域
      //  - 文章中のインラインリンクは「inline」例外に該当
      const effRect=e=>{
        const af=getComputedStyle(e,'::after');
        if(af.position==='absolute' && af.content!=='none'){
          const host=e.closest('.pcard,.wcard,.purpose,article');
          if(host) return host.getBoundingClientRect();
        }
        return e.getBoundingClientRect();
      };
      const isInline=e=>{
        const pa=e.parentElement; if(!pa) return false;
        if(!/^(P|LI|SPAN|TD|DD|EM|STRONG|SMALL)$/.test(pa.tagName)) return false;
        const own=(e.textContent||'').trim();
        const all=(pa.textContent||'').trim();
        if(all.length>own.length+2) return true;          // 周囲に地の文がある
        if(pa.closest('nav[aria-label="パンくず"]')) return true;  // パンくずは一行の文中リンク
        return false;
      };
      const small=[...document.querySelectorAll('a,button')].filter(e=>{
        const r0=e.getBoundingClientRect();
        if(r0.width===0||r0.right<=0||r0.bottom<=0) return false;   // 画面外（スキップリンク等）
        if(isInline(e)) return false;
        const r=effRect(e);
        return r.width<44||r.height<44;
      }).map(e=>(e.textContent||'').trim().slice(0,18)||e.className);
      return {
        imgTotal:imgs.length,
        noAlt:imgs.filter(i=>!i.hasAttribute('alt')).length,
        noDim:imgs.filter(i=>!i.hasAttribute('width')||!i.hasAttribute('height')).map(i=>i.src.split('/').pop()),
        h1:document.querySelectorAll('h1').length,
        lang:document.documentElement.lang,
        dupIds:[...new Set(dup)], skip,
        labels:[...document.querySelectorAll('input,select,textarea')].length,
        smallTargets:[...new Set(small)].slice(0,6),
        viewportOk:!/user-scalable\s*=\s*no|maximum-scale\s*=\s*1/.test(document.querySelector('meta[name=viewport]').content),
        title:document.title, desc:(document.querySelector('meta[name=description]')||{}).content||''
      };
    });
    const chk=(cond,label,extra='')=>{ if(!cond) fail++; console.log(`  ${cond?'✅':'❌'} ${label}${extra?'  '+extra:''}`); };
    chk(a.lang==='ja','html lang="ja"');
    chk(a.h1===1,'h1 が1つ',`(${a.h1})`);
    chk(a.noAlt===0,'全画像に alt',`(欠落 ${a.noAlt}/${a.imgTotal})`);
    chk(a.noDim.length===0,'全画像に width/height',a.noDim.length?JSON.stringify(a.noDim):'');
    chk(a.dupIds.length===0,'ID重複なし',a.dupIds.join(','));
    chk(a.skip.length===0,'見出し階層を飛ばさない',a.skip.join(','));
    chk(a.viewportOk,'viewport に user-scalable=no がない');
    chk(a.title.length<=40,`title ${a.title.length}文字`,`"${a.title}"`);
    chk(a.desc.length>=60&&a.desc.length<=130,`description ${a.desc.length}文字`);
    chk(a.smallTargets.length===0,'タップターゲット 44px以上（WCAG例外適用後）',a.smallTargets.length?JSON.stringify(a.smallTargets):'');
    await p.close();
  }
  await b.close();
  console.log('\n'+(fail?`❌ ${fail} 件の不合格`:'✅ すべて合格'));
  process.exit(fail?1:0);
})();
