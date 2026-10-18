(async () => { const R=window.SP_REACT, sp=window.__claudeSpike, orig=sp.orig;
 const Icon = () => R.createElement('div', { className:'claude-spike-icon', style:{color:'#d97757',fontSize:'22px',fontWeight:700,padding:'0 8px',cursor:'pointer',display:'flex',alignItems:'center',height:'100%'},
   onClick:()=>{window.__claudeSpikeClicks=(window.__claudeSpikeClicks||0)+1;console.log('[claude-spike] click',window.__claudeSpikeClicks);} }, '✳');
 const patched=function(props){ const ret=orig.call(this,props);
   try { if(!props.quickAccessHeader){ const inner=ret?.props?.children; const arr=inner?.props?.children;
     if(Array.isArray(arr)){ const grp=[...arr].reverse().find(x=>x&&x.type===R.Fragment&&Array.isArray(x.props.children)); if(grp){ grp.props.children=[R.createElement(Icon,{key:'claude-spike'}),...grp.props.children]; window.__claudeSpikeRenders=(window.__claudeSpikeRenders||0)+1; } } } } catch(e){console.error('[claude-spike]',e);}
   return ret; };
 patched.__claudeOrig=orig; const old=sp.memo.type; sp.memo.type=patched;
 const bw=[...SteamUIStore.WindowStore.SteamUIWindows].map(x=>x.m_BrowserWindow||x.BrowserWindow).find(Boolean);
 const host=bw.document.querySelector('.FlexGrowUniversalSearch'); let f=host[Object.keys(host).find(x=>x.startsWith('__reactFiber'))];
 while(f&&f.type!==old&&f.type!==orig) f=f.return; if(!f) return 'fiber not found';
 f.type=patched; if(f.alternate) f.alternate.type=patched; f.memoizedState.queue.dispatch(n=>n+1);
 await new Promise(r=>setTimeout(r,600));
 const e=bw.document.querySelector('.claude-spike-icon'); if(!e) return 'not in DOM, renders='+window.__claudeSpikeRenders;
 const r=e.getBoundingClientRect(); return `icon x=${Math.round(r.left)} y=${Math.round(r.top)} ${Math.round(r.width)}x${Math.round(r.height)} next=${e.nextElementSibling?.className?.slice(0,30)}`; })()
