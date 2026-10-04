/* KALATRACE v8 — frontend/backend bindings.
 * One authenticated API client, live GET bindings for operational screens,
 * and a complete OpenAPI-backed route catalog for endpoints that require
 * contextual parameters or explicit user actions.
 */
(function(){
  const state={spec:null,routes:[],loaded:false};
  const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  async function api(path, options={}){ return window.ktApi(path, options); }
  function addStyle(){
    if(document.getElementById('kt-v8-style'))return;
    const s=document.createElement('style');s.id='kt-v8-style';s.textContent=`
      .kt-live-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:12px}
      .kt-live-card{background:#fff;border:1px solid var(--border);border-radius:10px;padding:12px;min-height:92px}
      .kt-live-card h4{margin:0 0 7px;color:var(--navy);font-size:12px}.kt-live-value{font-size:12px;color:var(--text-secondary);word-break:break-word}
      .kt-route-ok{color:var(--success)}.kt-route-err{color:var(--danger)}.kt-route-row{display:grid;grid-template-columns:70px 1fr 90px;gap:8px;align-items:center;padding:8px 0;border-bottom:1px solid var(--border);font-size:11px}
      .kt-route-row:last-child{border-bottom:0}.kt-route-row button{padding:4px 7px;font-size:10px}
      @media(max-width:900px){.kt-live-grid{grid-template-columns:1fr}.kt-route-row{grid-template-columns:60px 1fr 70px}}
    `;document.head.appendChild(s);
  }
  function ensureLivePanel(screenId,title='Dados em tempo real'){
    const screen=document.getElementById('screen-'+screenId); if(!screen)return null;
    let panel=screen.querySelector('.kt-live-panel');
    if(!panel){panel=document.createElement('div');panel.className='card kt-live-panel';panel.innerHTML=`<div class="card-head"><h2 class="card-title">${title}</h2><button type="button" class="kt-live-refresh">Atualizar</button></div><div class="kt-live-grid"></div><pre class="api-output kt-live-output"></pre>`;screen.appendChild(panel);panel.querySelector('button').onclick=()=>loadBindings(screenId);}
    return panel;
  }
  async function bind(screenId,label,path,format=x=>x){
    const panel=ensureLivePanel(screenId); if(!panel)return;
    const grid=panel.querySelector('.kt-live-grid');
    const card=document.createElement('div');card.className='kt-live-card';card.innerHTML=`<h4>${esc(label)}</h4><div class="kt-live-value">Carregando…</div>`;grid.appendChild(card);
    try{const d=await api(path);card.querySelector('.kt-live-value').innerHTML=esc(format(d));}
    catch(e){card.querySelector('.kt-live-value').innerHTML=`<span class="kt-route-err">${esc(e.message)}</span>`;}
  }
  async function loadBindings(screenId){
    const panel=ensureLivePanel(screenId); if(!panel)return; panel.querySelector('.kt-live-grid').innerHTML='';panel.querySelector('.kt-live-output').textContent='';
    const map={
      control:[['Persistência','/persistence/health',d=>d.healthy?'healthy':'degraded'],['Neo4j','/neo4j/health',d=>d.status||d.connected?'online':'offline'],['Ciclo cognitivo','/cognitive-cycle/health',d=>d.status||d.healthy?'online':'available'],['Aquisição','/acquisition/health',d=>d.status||'online'],['CMC','/cmc/health',d=>d.status||d.command_mission_center||'online'],['Agente','/agent/status',d=>d.status||'online']],
      workspace:[['Identidade','/workspace/me',d=>d.user?.email||'autenticado'],['Projetos','/projects',d=>(d.projects||[]).length+' projetos'],['Perfis','/workspace/profiles',d=>(d.profiles||[]).length+' perfis']],
      projects:[['Projetos','/projects',d=>(d.projects||[]).length+' projetos'],['Templates','/projects/templates',d=>(d.templates||[]).length+' templates']],
      cmc:[['Saúde','/cmc/health',d=>d.status||d.command_mission_center||'online'],['Estatísticas','/cmc/stats',d=>JSON.stringify(d)],['Missões runtime','/cmc/missions',d=>Array.isArray(d)?d.length+' missões':JSON.stringify(d)]],
      'agente-local':[['Agente','/agent/status',d=>JSON.stringify(d)],['Instâncias','/agent/instances',d=>(d.instances||[]).length+' instâncias'],['Tarefas','/agent/tasks',d=>(d.tasks||[]).length+' tarefas']],
      grafo:[['Neo4j','/neo4j/health',d=>d.status||d.connected?'online':'offline'],['Estatísticas','/neo4j/stats',d=>JSON.stringify(d)],['Grafo','/neo4j/graph',d=>(d.nodes||[]).length+' nós · '+(d.edges||[]).length+' relações']],
      governanca:[['Conflitos','/curation/conflicts',d=>JSON.stringify(d)],['Duplicidades','/curation/duplicates',d=>JSON.stringify(d)],['Lacunas','/curation/gaps',d=>JSON.stringify(d)]],
      metacognicao:[['Saúde do ciclo','/cognitive-cycle/health',d=>JSON.stringify(d)],['Ciclo ativo','/cognitive-cycle/active',d=>JSON.stringify(d)],['Estatísticas','/cognitive-cycle/stats',d=>JSON.stringify(d)]],
      evidencias:[['Histórico de validação','/validation/history',d=>JSON.stringify(d)],['Estatísticas de validação','/validation/stats',d=>JSON.stringify(d)]],
      modulos:[['API','/health',d=>d.status||'online'],['Persistência','/persistence/health',d=>JSON.stringify(d)],['Ciclo','/cognitive-cycle/health',d=>JSON.stringify(d)]]
    };
    for(const [label,path,format] of (map[screenId]||[])) await bind(screenId,label,path,format);
  }
  async function loadSpec(){
    try{state.spec=await api('/openapi.json');state.routes=Object.entries(state.spec.paths||{}).flatMap(([path,methods])=>Object.entries(methods).filter(([m])=>['get','post','put','patch','delete'].includes(m)).map(([m,op])=>({method:m.toUpperCase(),path,operation:op})));state.loaded=true;renderCatalog();return state.routes.length;}
    catch(e){const out=document.getElementById('api-explorer-output');if(out)out.textContent=e.message;return 0;}
  }
  function renderCatalog(){
    const el=document.getElementById('api-endpoint-list');if(!el)return;
    const q=(document.getElementById('kt-api-filter')?.value||'').toLowerCase();
    const routes=state.routes.filter(r=>(r.method+' '+r.path+' '+(r.operation.summary||'')).toLowerCase().includes(q));
    const count=document.getElementById('api-endpoint-count');if(count)count.textContent=state.routes.length+' rotas · '+routes.length+' exibidas';
    el.innerHTML=routes.map((r,i)=>`<div class="kt-route-row"><span class="method">${r.method}</span><code title="${esc(r.operation.summary||'')}">${esc(r.path)}</code><button type="button" data-route-index="${state.routes.indexOf(r)}">${r.method==='GET'&&!r.path.includes('{')?'Testar GET':'Abrir'}</button></div>`).join('')||'<span class="muted">Nenhum endpoint corresponde ao filtro.</span>';
    el.querySelectorAll('button[data-route-index]').forEach(b=>b.onclick=()=>{
      const r=state.routes[Number(b.dataset.routeIndex)]; if(!r)return;
      if(r.method==='GET'&&!r.path.includes('{')){runRoute(r)}else if(window.ktPickEndpoint){window.ktPickEndpoint(r.method,r.path);document.getElementById('api-body').value=JSON.stringify(exampleBody(r.operation),null,2);}
    });
  }
  function exampleBody(op){const props=op?.requestBody?.content?.['application/json']?.schema?.properties||{};const o={};Object.keys(props).forEach(k=>o[k]=props[k].example??props[k].default??(props[k].type==='string'?'':props[k].type==='integer'?0:false));return o;}
  async function runRoute(r){
    const out=document.getElementById('api-explorer-output');if(!out)return;out.textContent='Executando '+r.method+' '+r.path+'…';
    try{const d=await api(r.path,{method:'GET'});out.textContent=JSON.stringify(d,null,2);}catch(e){out.textContent='Erro: '+e.message;}
  }
  function wire(){
    addStyle();
    const backend=document.getElementById('screen-backend');if(backend){
      const head=backend.querySelector('.page-head');
      if(head&&!document.getElementById('kt-api-filter')){const input=document.createElement('input');input.id='kt-api-filter';input.placeholder='Filtrar endpoint…';input.style.cssText='max-width:280px;margin-left:auto';input.oninput=renderCatalog;head.appendChild(input);}
    }
    const original=window.ktLoadOpenApi;
    window.ktLoadOpenApi=async function(){if(original)await original();await loadSpec();};
    document.querySelectorAll('.nav-item').forEach(n=>n.addEventListener('click',()=>{const id=n.dataset.screen;if(['control','workspace','projects','cmc','agente-local','grafo','governanca','metacognicao','evidencias','modulos'].includes(id))setTimeout(()=>loadBindings(id),0);}));
    if(document.getElementById('screen-backend'))setTimeout(loadSpec,300);
    if(window.ktToken&&window.ktToken()) ['control','workspace','projects','cmc','agente-local','grafo','governanca','metacognicao','evidencias','modulos'].forEach(id=>setTimeout(()=>loadBindings(id),400));
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',wire);else wire();
  window.KTBackendBindings={loadSpec,loadBindings,runRoute};
})();
