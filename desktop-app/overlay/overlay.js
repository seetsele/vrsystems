(function(){
  const input = document.getElementById('overlay-input');
  const verifyBtn = document.getElementById('verify-btn');
  const closeBtn = document.getElementById('close-btn');
  const clipBtn = document.getElementById('clip-btn');
  const fullBtn = document.getElementById('full-btn');
  const logo = document.getElementById('logo');
  const card = document.querySelector('.card');

  // Try to paste clipboard on open
  try { window.verity.clipboard.read().then(text => { if (text) input.value = text; }).catch(()=>{}); } catch(e){}

  verifyBtn.addEventListener('click', () => {
    const text = input.value && input.value.trim();
    if (!text) return;
    try {
      window.verity.overlay.verify(text);
    } catch (e) {
      try { window.postMessage({ type: 'overlay:verify', text }); } catch(e){}
    }
  });

  // Attach file placeholder (no-op fallback)
  const attachBtn = document.getElementById('attach-btn');
  if (attachBtn) {
    attachBtn.addEventListener('click', () => {
      try {
        // If preload supports a file picker, call it; otherwise, briefly pulse the button
        if (window.verity && window.verity.file && window.verity.file.open) {
          window.verity.file.open().then(file => { if (file && file.text) input.value = file.text; });
        } else {
          attachBtn.animate([{transform:'scale(1)'},{transform:'scale(0.96)'},{transform:'scale(1)'}],{duration:220});
        }
      } catch(e) { attachBtn.classList.add('pulse'); setTimeout(()=>attachBtn.classList.remove('pulse'),300); }
    });
  }

  closeBtn.addEventListener('click', () => {
    try { window.verity.overlay.toggle(); } catch(e) { window.close(); }
  });

  // Enter to verify
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault(); verifyBtn.click();
    }
  });

  // Escape to close
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      try { window.verity.overlay.toggle(); } catch(e) { window.close(); }
    }
  });

  // Focus input on open
  setTimeout(() => { try { input.focus(); } catch(e){} }, 80);

  // Clipboard verify
  if (clipBtn) {
    clipBtn.addEventListener('click', async () => {
      try {
        const text = await window.verity.clipboard.read();
        if (text && text.trim()) { input.value = text.trim(); verifyBtn.click(); }
      } catch(e) {
        try { const text = await navigator.clipboard.readText(); if (text) { input.value = text; verifyBtn.click(); } } catch(_){}
      }
    });
  }

  // Open full report in external browser
  if (fullBtn) {
    fullBtn.addEventListener('click', async () => {
      const t = input.value && input.value.trim();
      const text = t || await window.verity.clipboard.read().catch(()=>'');
      try {
        const endpoint = await window.verity.api.getEndpoint().catch(()=>null) || 'http://127.0.0.1:3001';
        const url = `${endpoint.replace(/\/$/, '')}/verify.html?text=${encodeURIComponent(text || '')}`;
        window.verity.shell.openExternal(url);
      } catch(e) { console.warn('open full report failed', e); }
    });
  }

  // Toggle compact (popout) when clicking logo
  if (logo && card) {
    logo.addEventListener('click', () => {
      card.classList.toggle('compact');
      if (!card.classList.contains('compact')) setTimeout(()=>{ try{ input.focus(); }catch(e){} }, 80);
    });
  }

})();
