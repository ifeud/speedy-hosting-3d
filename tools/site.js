'use strict';
(() => {
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
  const money = value => new Intl.NumberFormat('en-US', {style:'currency', currency:'USD'}).format(value);
  const games = {
    minecraft: {name:'Minecraft', minimum:4, tip:'4 GB is a starting point for a small vanilla world. Mods may need more.'},
    rust: {name:'Rust', minimum:8, tip:'This example starts at 8 GB. Large maps, plugins and busy servers need extra headroom.'},
    palworld: {name:'Palworld', minimum:8, tip:'This example starts at 8 GB. Consider 16 GB as your world and community grow.'},
    valheim: {name:'Valheim', minimum:4, tip:'4 GB is an illustrative starting point. Large builds and mods may need more.'},
    terraria: {name:'Terraria', minimum:4, tip:'4 GB is an illustrative starting point. Heavy tModLoader packs may need more.'},
    ark: {name:'ARK: Survival Ascended', minimum:16, tip:'This demanding world starts at 16 GB in this demo. Verify real requirements before ordering.'}
  };
  const regions = {
    singapore:{name:'Singapore, Singapore',short:'Singapore',ping:24,desc:'A home base for your Asia-Pacific adventures.'},
    ashburn:{name:'Ashburn, United States',short:'Ashburn',ping:18,desc:'A home base for your North-American adventures.'},
    frankfurt:{name:'Frankfurt, Germany',short:'Frankfurt',ping:21,desc:'A home base for your European adventures.'}
  };
  let billing = 'monthly', selectedRegion = 'singapore', activeFilter = 'all', expandedGames = false;
  let appliedPromo = false, promoPrefill = '', quoteRecord = null, supportDraft = '', toastTimer;

  function toast(text) {
    $('#toast-text').textContent = text;
    $('#toast').classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => $('#toast').classList.remove('show'), 3800);
  }
  function download(content, name, type = 'text/plain;charset=utf-8') {
    const objectURL = URL.createObjectURL(new Blob([content], {type}));
    const a = document.createElement('a');
    a.href = objectURL; a.download = name; document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(objectURL), 1500);
  }
  function closeNavigation() {
    $('#main-nav').classList.remove('open');
    $('#mobile-toggle').setAttribute('aria-expanded','false');
    $('#mobile-toggle').setAttribute('aria-label','Open navigation');
    $('#mobile-toggle use').setAttribute('href','#i-list');
    $('#games-menu').hidden = true;
    $('#games-menu-button').setAttribute('aria-expanded','false');
  }
  $('#mobile-toggle').addEventListener('click', () => {
    const open = !$('#main-nav').classList.contains('open');
    $('#main-nav').classList.toggle('open',open);
    $('#mobile-toggle').setAttribute('aria-expanded',String(open));
    $('#mobile-toggle').setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
    $('#mobile-toggle use').setAttribute('href',open ? '#i-x' : '#i-list');
  });
  $('#games-menu-button').addEventListener('click', () => {
    const open = $('#games-menu').hidden;
    $('#games-menu').hidden = !open;
    $('#games-menu-button').setAttribute('aria-expanded',String(open));
  });
  document.addEventListener('click', event => {
    if (!event.target.closest('.nav-dropdown')) {
      $('#games-menu').hidden = true;
      $('#games-menu-button').setAttribute('aria-expanded','false');
    }
    if (!event.target.closest('.nav-wrap')) closeNavigation();
  });
  $$('.main-nav a').forEach(link => link.addEventListener('click',closeNavigation));
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') closeNavigation();
    if (event.key === '/' && !/INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName) && !document.querySelector('dialog[open]')) {
      event.preventDefault(); $('#game-search').focus();
    }
  });
  function filterGames() {
    const query = $('#game-search').value.trim().toLowerCase();
    let shown = 0, matching = 0;
    $$('.game-card').forEach((card,index) => {
      const match = (activeFilter === 'all' || card.dataset.categories.split(' ').includes(activeFilter)) && card.dataset.search.includes(query);
      if (match) matching++;
      const visible = match && (expandedGames || query || activeFilter !== 'all' || index < 4);
      card.hidden = !visible;
      if (visible) shown++;
    });
    $('#empty-games').hidden = shown > 0;
    $('#show-all-games').hidden = Boolean(query) || activeFilter !== 'all';
    $('#show-all-games').innerHTML = `${expandedGames ? 'Show fewer games' : 'View all 6 games'} <svg class="icon" aria-hidden="true"><use href="#i-arrow-right"/></svg>`;
    $('#game-results').textContent = `${shown} ${shown === 1 ? 'game' : 'games'} displayed. ${matching} matching games available.`;
  }
  $$('[data-filter]').forEach(button => button.addEventListener('click', () => {
    activeFilter = button.dataset.filter;
    $$('[data-filter]').forEach(tab => {tab.classList.toggle('active',tab===button);tab.setAttribute('aria-pressed',String(tab===button));});
    filterGames();
  }));
  $('#game-search').addEventListener('input',filterGames);
  $('#show-all-games').addEventListener('click', () => {expandedGames = !expandedGames;filterGames();});
  $('#reset-search').addEventListener('click', () => {$('#game-search').value=''; $('[data-filter="all"]').click(); $('#game-search').focus();});
  filterGames();

  function setBilling(period) {
    billing = period;
    $$('[data-billing]').forEach(button => {const active = button.dataset.billing===period;button.classList.toggle('active',active);button.setAttribute('aria-pressed',String(active));});
    $$('.plan-card').forEach(card => {
      const base = Number(card.dataset.price);
      $('.plan-price strong',card).textContent = money(period==='yearly' ? base * .8 : base);
      $('.plan-bill-note',card).textContent = period==='yearly' ? `${money(base*12*.8)} billed yearly` : 'Billed monthly. Example pricing.';
    });
  }
  $$('[data-billing]').forEach(button => button.addEventListener('click', () => setBilling(button.dataset.billing)));
  setBilling('monthly');

  function openDialog(dialog) {
    closeNavigation();
    if (!dialog.open) dialog.showModal();
    document.body.classList.add('modal-open');
  }
  $$('dialog').forEach(dialog => {
    $('[data-close]',dialog).addEventListener('click', () => dialog.close());
    dialog.addEventListener('click', event => {
      if (event.target!==dialog) return;
      const rect = dialog.getBoundingClientRect();
      if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) dialog.close();
    });
    dialog.addEventListener('close', () => {if (!document.querySelector('dialog[open]')) document.body.classList.remove('modal-open');});
  });

  function selectedRAM() {return Number($('input[name="ram"]:checked').value);}
  function enforceGameRAM() {
    const game = games[$('#config-game').value];
    $$('input[name="ram"]').forEach(input => input.disabled = Number(input.value) < game.minimum);
    const current = $('input[name="ram"]:checked');
    if (!current || current.disabled) $(`input[name="ram"][value="${game.minimum}"]`).checked = true;
    $('#game-recommendation').textContent = game.tip;
  }
  function currentQuote() {
    const game = games[$('#config-game').value];
    const ram = selectedRAM();
    const base = ram*1.5;
    const annual = $('#config-billing').value==='yearly';
    const discount = appliedPromo && !annual;
    return {brand:'Speedy Hosting',type:'Illustrative front-end quote   not an order',game:game.name,gameId:$('#config-game').value,ramGB:ram,region:regions[$('#config-region').value].name,billing:annual?'Yearly':'Monthly',baseMonthlyUSD:base,amountDueUSD:annual?base*12*.8:base*(discount?.8:1),renewalUSD:annual?base*12*.8:base,promo:discount?'FIRST20   20% off first month':annual?'20% annual-plan discount':'None',currency:'USD',created:new Date().toISOString()};
  }
  function updateQuote() {
    const q=currentQuote();
    $('#quote-summary').textContent=`${q.game} · ${q.ramGB} GB`;
    $('#quote-price').textContent=money(q.amountDueUSD);
    $('#quote-unit').textContent=q.billing==='Yearly'?'/ year':appliedPromo?'/ first month':'/ month';
    $('#quote-period').textContent=q.billing==='Yearly'?`${money(q.baseMonthlyUSD*.8)}/mo equivalent. One annual payment.`:appliedPromo?`${money(q.baseMonthlyUSD)}/mo after the first month.`:'Billed monthly. Example pricing.';
    if (appliedPromo) $('#promo-feedback').textContent=q.billing==='Yearly'?'Annual plans already save 20%. FIRST20 does not stack.':'FIRST20 applied. 20% off your first month.';
  }
  function openConfig(gameId='minecraft',ram) {
    if (!games[gameId]) gameId='minecraft';
    $('#config-form').hidden=false;$('#quote-result').hidden=true;
    $('#config-game').value=gameId;$('#config-region').value=selectedRegion;$('#config-billing').value=billing;
    appliedPromo=false;$('#promo-code').value=promoPrefill;$('#promo-feedback').textContent='';
    const desired=Math.max(games[gameId].minimum,Number(ram)||games[gameId].minimum);
    $(`input[name="ram"][value="${desired}"]`).checked=true;
    enforceGameRAM();updateQuote();openDialog($('#config-dialog'));
  }
  $$('[data-config]').forEach(button=>button.addEventListener('click',()=>openConfig(button.dataset.config,button.dataset.ram)));
  $('#config-game').addEventListener('change',()=>{enforceGameRAM();updateQuote();});
  $('#config-region').addEventListener('change',updateQuote);
  $('#config-billing').addEventListener('change',updateQuote);
  $$('input[name="ram"]').forEach(input=>input.addEventListener('change',updateQuote));
  $('#promo-code').addEventListener('input',()=>{appliedPromo=false;$('#promo-feedback').textContent='';updateQuote();});
  $('#apply-promo').addEventListener('click',()=>{
    const code=$('#promo-code').value.trim().toUpperCase();
    if (code==='FIRST20') {appliedPromo=true;$('#promo-code').value=code;updateQuote();}
    else {appliedPromo=false;updateQuote();$('#promo-feedback').textContent=code?'That code isn’t in this demo. Try FIRST20.':'Add a code first   try FIRST20.';}
  });
  $('#config-form').addEventListener('submit',event=>{
    event.preventDefault();quoteRecord=currentQuote();
    const rows=[['Game',quoteRecord.game],['Memory',`${quoteRecord.ramGB} GB`],['Location',quoteRecord.region],['Billing',quoteRecord.billing],['Discount',quoteRecord.promo],['Example total',`${money(quoteRecord.amountDueUSD)} ${quoteRecord.billing==='Yearly'?'per year':appliedPromo?'for the first month':'per month'}`],['Renewal',`${money(quoteRecord.renewalUSD)} ${quoteRecord.billing==='Yearly'?'per year':'per month'}`]];
    $('#quote-details').replaceChildren(...rows.map(([name,value])=>{const div=document.createElement('div');const dt=document.createElement('dt'),dd=document.createElement('dd');dt.textContent=name;dd.textContent=value;div.append(dt,dd);return div;}));
    $('#config-form').hidden=true;$('#quote-result').hidden=false;
    const heading=$('#quote-result h3');heading.tabIndex=-1;heading.focus();
  });
  $('#edit-quote').addEventListener('click',()=>{$('#quote-result').hidden=true;$('#config-form').hidden=false;$('#config-game').focus();});
  $('#download-quote').addEventListener('click',()=>{
    if (!quoteRecord) return;
    const text=`SPEEDY HOSTING   YOUR EXAMPLE ADVENTURE\n\nThis is an illustrative quote, not an order or invoice.\nNo payment was made and no real server was created.\n\nGame: ${quoteRecord.game}\nRAM: ${quoteRecord.ramGB} GB\nRegion: ${quoteRecord.region}\nBilling: ${quoteRecord.billing}\nDiscount: ${quoteRecord.promo}\nExample first payment: ${money(quoteRecord.amountDueUSD)}\nExample renewal: ${money(quoteRecord.renewalUSD)} / ${quoteRecord.billing==='Yearly'?'year':'month'}\nCurrency: USD\nCreated: ${quoteRecord.created}\n\nPrices, availability and features must be verified with the actual hosting provider.\n`;
    download(text,'speedy-example-quote.txt');
  });

  function selectRegion(id) {
    if (!regions[id]) return;selectedRegion=id;
    $$('[data-region]').forEach(button=>{const active=button.dataset.region===id;button.classList.toggle('active',active);button.setAttribute('aria-pressed',String(active));});
    $$('.map-pin').forEach(pin=>{const active=pin.dataset.mapRegion===id;pin.classList.toggle('active',active);pin.setAttribute('aria-pressed',String(active));});
    $('#location-name').textContent=regions[id].name;$('#location-desc').textContent=regions[id].desc;
    $('#location-ping').innerHTML=`${regions[id].ping}<small>ms</small>`;
    $('#location-deploy').setAttribute('aria-label',`Configure a server in ${regions[id].short}`);
  }
  $$('[data-region]').forEach(button=>button.addEventListener('click',()=>selectRegion(button.dataset.region)));
  $$('.map-pin').forEach(pin=>{
    pin.addEventListener('click',()=>selectRegion(pin.dataset.mapRegion));
    pin.addEventListener('keydown',event=>{if (event.key==='Enter'||event.key===' ') {event.preventDefault();selectRegion(pin.dataset.mapRegion);}});
  });
  $('#location-deploy').addEventListener('click',()=>openConfig('minecraft'));

  function selectPanel(name) {
    $$('[data-panel]').forEach(tab=>{const active=tab.dataset.panel===name;tab.classList.toggle('active',active);tab.setAttribute('aria-selected',String(active));tab.tabIndex=active?0:-1;});
    $$('.panel-tab-content').forEach(content=>content.hidden=content.id!==`panel-${name}`);
  }
  $$('[data-panel]').forEach(tab=>{
    tab.addEventListener('click',()=>selectPanel(tab.dataset.panel));
    tab.addEventListener('keydown',event=>{
      const tabs=$$('[data-panel]');let index=tabs.indexOf(tab);
      if (event.key==='ArrowDown'||event.key==='ArrowRight') index=(index+1)%tabs.length;
      else if (event.key==='ArrowUp'||event.key==='ArrowLeft') index=(index+tabs.length-1)%tabs.length;
      else if (event.key==='Home') index=0;
      else if (event.key==='End') index=tabs.length-1;
      else return;
      event.preventDefault();selectPanel(tabs[index].dataset.panel);tabs[index].focus();
    });
  });
  let serverRunning=true, restarting=false;
  function addConsole(message) {
    const line=document.createElement('p'),time=document.createElement('time'),span=document.createElement('span');
    time.textContent=new Date().toLocaleTimeString('en-GB',{hour12:false});span.textContent=' [Demo] ';
    line.append(time,span,document.createTextNode(message));
    $('#console-lines').insertBefore(line,$('.console-cursor'));
    while ($$('#console-lines p').length>8) $$('#console-lines p')[0].remove();
    $('#console-lines').scrollTop=$('#console-lines').scrollHeight;
  }
  function displayServer(running,label) {
    serverRunning=running;
    $('#panel-status').classList.toggle('offline',!running);
    $('#panel-status').textContent=label||(running?'Running':'Stopped');
    $('#server-toggle span').textContent=running?'Stop':'Start';
    $('#server-toggle use').setAttribute('href',running?'#i-stop':'#i-play');
    $('#server-toggle').setAttribute('aria-label',`${running?'Stop':'Start'} demo server`);
    $('#cpu-meter').innerHTML=running?'18.4<small>%</small>':'0<small>%</small>';
    $('#memory-meter').innerHTML=running?'2.1<small>/ 8 GB</small>':'0<small>/ 8 GB</small>';
    $('#players-meter').innerHTML=running?'8<small>/ 20</small>':'0<small>/ 20</small>';
    $$('.panel-meters .meter i').forEach((bar,index)=>bar.style.width=running?['18.4%','26%','40%'][index]:'0%');
  }
  $('#server-toggle').addEventListener('click',()=>{
    if(restarting)return;
    displayServer(!serverRunning);addConsole(serverRunning?'Server started. Ready for the next adventure.':'Server stopped. World saved in this demonstration.');
  });
  $('#server-restart').addEventListener('click',()=>{
    if(restarting)return;restarting=true;
    $('#server-toggle').disabled=true;$('#server-restart').disabled=true;
    displayServer(false,'Restarting');addConsole('Restart requested. Getting things ready…');
    setTimeout(()=>{displayServer(true);addConsole('Done! Your demo world is ready.');restarting=false;$('#server-toggle').disabled=false;$('#server-restart').disabled=false;},1300);
  });
  $('#download-properties').addEventListener('click',()=>download('# Speedy Hosting   example only\n# No live server is configured by this download.\nmotd=Our little world | Powered by Speedy\nmax-players=20\ndifficulty=normal\ngamemode=survival\nonline-mode=true\npvp=true\nview-distance=10\nserver-port=25565\n','server.properties'));
  $('#make-backup').addEventListener('click',()=>{
    const div=document.createElement('div');
    div.innerHTML='<span class="backup-icon"><svg class="icon" aria-hidden="true"><use href="#i-cloud-check"/></svg></span><span><strong>Manual adventure backup</strong><small>Just now · Demo only</small></span><span class="backup-tag">READY</span>';
    $('#backup-list').prepend(div);
    while($('#backup-list').children.length>2) $('#backup-list').lastElementChild.remove();
    toast('Demo backup added. No real server data was stored.');
  });
  const showClient=()=>openDialog($('#client-dialog'));
  $('#client-open').addEventListener('click',showClient);$('#footer-client').addEventListener('click',showClient);
  $('#try-panel').addEventListener('click',()=>{$('#client-dialog').close();requestAnimationFrame(()=>{$('#panel').scrollIntoView({behavior:'smooth',block:'center'});$('#tab-console').focus({preventScroll:true});});});
  function showSupport() {$('#support-form').hidden=false;$('#support-result').hidden=true;openDialog($('#support-dialog'));}
  $('#support-open').addEventListener('click',showSupport);$('#footer-support').addEventListener('click',showSupport);
  $('#support-form').addEventListener('submit',event=>{
    event.preventDefault();const data=new FormData(event.currentTarget);
    supportDraft=`SPEEDY HOSTING   LOCAL SUPPORT DRAFT\n\nThis request was not sent or uploaded.\n\nName: ${data.get('name')}\nEmail: ${data.get('email')}\n\nMessage:\n${data.get('message')}\n`;
    $('#support-form').hidden=true;$('#support-result').hidden=false;
    const heading=$('#support-result h3');heading.tabIndex=-1;heading.focus();
  });
  $('#download-support').addEventListener('click',()=>download(supportDraft,'speedy-support-draft.txt'));
  const policies={privacy:{title:'Privacy, simply put.',content:'<p>This standalone design concept does not use analytics, tracking cookies, remote forms or a hosting backend. Fonts, icons and visual assets are embedded in the HTML.</p><h3>Your inputs stay in this page.</h3><p>Support and configuration inputs are held in memory in your browser for this session. They are not uploaded. Downloaded drafts and quotes are saved through your browser, at your request.</p><h3>Before going live</h3><p>Replace this notice with a policy reflecting your actual services, payment processors, data retention, analytics and applicable law. A hosting platform or server can maintain its own access logs; that is outside this file.</p>'},terms:{title:'A concept. Not a contract.',content:'<p>Speedy Hosting is the fictional brand used for this front-end website concept. Prices, discounts, locations, features and performance figures are illustrative, not binding offers.</p><h3>No real transactions</h3><p>The configurator produces a local example quote. No payment is collected, no account is created and no server is provisioned. The control panel is a demonstration.</p><h3>Before going live</h3><p>Add your business details and verified service terms, including billing, cancellation, refunds, acceptable use, support, backups and any service-level commitments. Connect a secure hosting and payment backend.</p><p>Game titles and artwork are owned by their respective publishers. This concept is not affiliated with those publishers.</p>'}};
  $$('[data-policy]').forEach(button=>button.addEventListener('click',()=>{const policy=policies[button.dataset.policy];$('#policy-title').textContent=policy.title;$('#policy-content').innerHTML=policy.content;openDialog($('#policy-dialog'));}));
  const logoSVG=@@LOGO_JSON@@;
  $('#download-logo').addEventListener('click',()=>download(logoSVG,'speedy-logo.svg','image/svg+xml'));
  $('#copyright-year').textContent=String(new Date().getFullYear());
  // Fine-pointer depth interactions. Touch and reduced-motion users get a stable layout.
  if (matchMedia('(hover:hover) and (pointer:fine)').matches && !matchMedia('(prefers-reduced-motion:reduce)').matches) {
    $$('.game-card, [data-tilt]').forEach(card => {
      const strength=Number(card.dataset.tilt)||5;
      card.addEventListener('pointermove',event=>{
        const r=card.getBoundingClientRect();
        const x=(event.clientX-r.left)/r.width-.5;
        const y=(event.clientY-r.top)/r.height-.5;
        card.style.transform=`perspective(1000px) rotateX(${-y*strength}deg) rotateY(${x*strength}deg) translateY(-4px)`;
      });
      card.addEventListener('pointerleave',()=>{card.style.transform='';});
    });
  }
})();
