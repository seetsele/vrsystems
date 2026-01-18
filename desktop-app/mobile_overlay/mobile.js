(function(){
  const fab = document.getElementById('verify-fab');
  const overlay = document.getElementById('mobile-overlay');
  const close = document.getElementById('close-overlay');
  const verify = document.getElementById('overlay-verify');
  const ta = document.getElementById('overlay-input');

  fab.addEventListener('click', () => {
    overlay.setAttribute('aria-hidden','false');
    setTimeout(()=>{ ta.focus(); }, 160);
  });
  close.addEventListener('click', ()=> overlay.setAttribute('aria-hidden','true'));
  verify.addEventListener('click', async ()=>{
    const text = (ta.value||'').trim() || document.getElementById('p1').innerText;
    // fake verify result display
    const r = document.createElement('div'); r.style.padding='10px'; r.style.marginTop='8px'; r.style.background='rgba(0,0,0,0.35)'; r.style.borderRadius='8px'; r.innerText = 'VERDICT: TRUE — 92% confidence';
    overlay.querySelector('.overlay-card').appendChild(r);
  });

})();
