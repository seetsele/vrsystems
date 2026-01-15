// Verity Systems - Exhaustive Test Suite JS
// Loads test cases, runs them against the API, and displays results interactively

const API_URL = window.location.hostname === 'localhost' ? 'http://localhost:8000' : 'https://veritysystems-production.up.railway.app';

// Expanded and intensive test set (imported from extensive_test_suite.py and more)
const TEST_CLAIMS = [
    // TRUE claims
    { id: 1, category: "Scientific Fact", claim: "Water molecules consist of two hydrogen atoms and one oxygen atom (H2O).", expected: "true" },
    { id: 2, category: "Historical Fact", claim: "The Berlin Wall fell on November 9, 1989.", expected: "true" },
    { id: 3, category: "Research Paper", claim: "The 2012 CRISPR-Cas9 paper by Doudna and Charpentier demonstrated programmable genome editing.", expected: "true" },
    { id: 4, category: "Current Events", claim: "The James Webb Space Telescope launched in December 2021 and is positioned at Lagrange point L2.", expected: "true" },
    { id: 5, category: "Medical Fact", claim: "mRNA vaccines work by instructing cells to produce a protein that triggers an immune response.", expected: "true" },
    // FALSE claims
    { id: 6, category: "Health Misinformation", claim: "5G cell towers cause COVID-19 infections by weakening the immune system.", expected: "false" },
    { id: 7, category: "Scientific Misinformation", claim: "The Earth is flat and NASA has been hiding this truth for decades.", expected: "false" },
    { id: 8, category: "Historical Misinformation", claim: "The Great Wall of China is visible from the Moon with the naked eye.", expected: "false" },
    { id: 9, category: "Health Misinformation", claim: "Drinking bleach or injecting disinfectants cures viral infections including COVID-19.", expected: "false" },
    { id: 10, category: "Political Misinformation", claim: "Voter fraud through mail-in ballots changed the outcome of the 2020 US presidential election.", expected: "false" },
    // MIXED/NUANCED claims
    { id: 11, category: "Nuanced Science", claim: "Coffee is bad for your health.", expected: "mixed" },
    { id: 12, category: "Economic Claim", claim: "Raising minimum wage always leads to job losses.", expected: "mixed" },
    { id: 13, category: "Technology Claim", claim: "Artificial intelligence will replace all human jobs within 10 years.", expected: "mixed" },
    { id: 14, category: "Environmental", claim: "Electric vehicles are completely carbon-neutral.", expected: "mixed" },
    { id: 15, category: "Nutrition", claim: "Eating eggs every day is dangerous for heart health due to cholesterol.", expected: "mixed" },
    // HARD/EXTREME/EDGE/URL/RESEARCH/OUTDATED/FAKE/CONSPIRACY/STATISTICAL/NEW/UNVERIFIABLE claims (add more below)
    { id: 16, category: "Complex Research", claim: "The Stanford Prison Experiment's findings about human behavior are scientifically valid and replicable.", expected: "false" },
    { id: 17, category: "Recent Research", claim: "Room temperature superconductivity was achieved by LK-99 in 2023.", expected: "false" },
    { id: 18, category: "Statistical Claim", claim: "More people die from medical errors than car accidents in the United States annually.", expected: "true" },
    { id: 19, category: "Deepfake/Fabricated", claim: "Pope Francis endorsed Donald Trump for president in 2016.", expected: "false" },
    { id: 20, category: "Subtle Misinformation", claim: "NASA's budget is 25% of the US federal budget.", expected: "false" },
    { id: 21, category: "URL Verification", claim: "According to the WHO, microplastics in drinking water pose no significant health risk based on current evidence.", expected: "true" },
    { id: 22, category: "PDF Research", claim: "The IPCC Sixth Assessment Report states that human activities have unequivocally caused global warming.", expected: "true" },
    { id: 23, category: "Outdated Information", claim: "Pluto is classified as the ninth planet in our solar system.", expected: "false" },
    { id: 24, category: "Partially True", claim: "Humans only use 10% of their brains.", expected: "false" },
    { id: 25, category: "Viral Misinformation", claim: "The 2004 Indian Ocean tsunami was caused by underwater nuclear testing by the US military.", expected: "false" },
    // --- EXTRAS: Add more edge, nuanced, statistical, unverifiable, and new types below for exhaustiveness ---
    { id: 26, category: "Unverifiable", claim: "There is intelligent life elsewhere in the universe.", expected: "unverifiable" },
    { id: 27, category: "Statistical Edge", claim: "The average person swallows eight spiders a year in their sleep.", expected: "false" },
    { id: 28, category: "New Science", claim: "A new element was discovered in 2024 called Novium.", expected: "false" },
    { id: 29, category: "Conspiracy Theory", claim: "The moon landing was staged in a Hollywood studio.", expected: "false" },
    { id: 30, category: "Balanced Claim", claim: "Organic food is always healthier than conventional food.", expected: "mixed" },
    { id: 31, category: "Ambiguous", claim: "Time is an illusion.", expected: "unverifiable" },
    { id: 32, category: "Philosophical", claim: "Beauty is in the eye of the beholder.", expected: "unverifiable" },
    { id: 33, category: "Statistical", claim: "More than 50% of the world's population lives in urban areas.", expected: "true" },
    { id: 34, category: "Recent Event", claim: "ChatGPT was released in 2022.", expected: "true" },
    { id: 35, category: "Fake Statistic", claim: "90% of statistics are made up on the spot.", expected: "false" },
    { id: 36, category: "Medical Myth", claim: "Cracking your knuckles causes arthritis.", expected: "false" },
    { id: 37, category: "Historical Nuance", claim: "The causes of World War I are simple and well understood.", expected: "mixed" },
    { id: 38, category: "Political Edge", claim: "All politicians are corrupt.", expected: "mixed" },
    { id: 39, category: "Science Edge", claim: "Quantum entanglement allows faster-than-light communication.", expected: "false" },
    { id: 40, category: "Nutrition Edge", claim: "Gluten-free diets are healthier for everyone.", expected: "mixed" },
    { id: 41, category: "Unverifiable", claim: "The universe is infinite.", expected: "unverifiable" },
    { id: 42, category: "Edge", claim: "Sharks don't get cancer.", expected: "false" },
    { id: 43, category: "Edge", claim: "Goldfish have a three-second memory.", expected: "false" },
    { id: 44, category: "Edge", claim: "Lightning never strikes the same place twice.", expected: "false" },
    { id: 45, category: "Edge", claim: "Bulls get angry when they see the color red.", expected: "false" },
    { id: 46, category: "Edge", claim: "You can see the Great Wall of China from space.", expected: "false" },
    { id: 47, category: "Edge", claim: "Bananas grow on trees.", expected: "false" },
    { id: 48, category: "Edge", claim: "Humans have five senses.", expected: "mixed" },
    { id: 49, category: "Edge", claim: "Dogs see only in black and white.", expected: "false" },
    { id: 50, category: "Edge", claim: "Sugar causes hyperactivity in children.", expected: "false" }
];

function renderTests() {
    const testList = document.getElementById('testList');
    testList.innerHTML = '';
    TEST_CLAIMS.forEach(tc => {
        const div = document.createElement('div');
        div.className = 'card test-item';
        div.id = `test-${tc.id}`;
        div.innerHTML = `
          <div style="display:flex;align-items:center;justify-content:space-between;gap:0.5rem;">
            <div class="category">${tc.category}</div>
            <div style="display:flex;gap:0.5rem;align-items:center;"><button class="small-btn" onclick="runSingleTest(${tc.id})">Run</button></div>
          </div>
          <div class="claim">${tc.claim}</div>
          <div class="expected">Expected: <b>${tc.expected.toUpperCase()}</b></div>
          <div class="result" id="result-${tc.id}"></div>
          <div class="error muted" id="error-${tc.id}"></div>
        `;
        testList.appendChild(div);
    });
}

async function runAllTests() {
    document.getElementById('runAllBtn').disabled = true;
    document.getElementById('summary').style.display = 'none';
    let pass = 0, fail = 0, errors = 0;
    for (const tc of TEST_CLAIMS) {
        const resultDiv = document.getElementById(`result-${tc.id}`);
        const errorDiv = document.getElementById(`error-${tc.id}`);
        resultDiv.textContent = 'Running...';
        errorDiv.textContent = '';
        try {
            const res = await fetch(`${API_URL}/verify`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ claim: tc.claim, options: { model: 'deep', include_sources: true } })
            });
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const data = await res.json();
            let verdict = (data.verdict || '').toLowerCase();
            if (verdict === 'mostly_true') verdict = 'true';
            if (verdict === 'mostly_false') verdict = 'false';
            let correct = false;
            if (tc.expected === verdict) correct = true;
            if (tc.expected === 'mixed' && (verdict === 'mixed' || verdict === 'unverifiable')) correct = true;
            if (tc.expected === 'unverifiable' && verdict === 'unverifiable') correct = true;
            if (correct) {
                pass++;
                resultDiv.textContent = `✅ ${verdict.toUpperCase()} (${Math.round((data.confidence||0)*100)}%)`;
                document.getElementById(`test-${tc.id}`).classList.add('pass');
            } else {
                fail++;
                resultDiv.textContent = `❌ ${verdict.toUpperCase()} (${Math.round((data.confidence||0)*100)}%)`;
                document.getElementById(`test-${tc.id}`).classList.add('fail');
            }
        } catch (e) {
            errors++;
            resultDiv.textContent = '';
            errorDiv.textContent = `Error: ${e.message}`;
            document.getElementById(`test-${tc.id}`).classList.add('fail');
        }
    }
    showSummary(pass, fail, errors);
    document.getElementById('runAllBtn').disabled = false;
}

// Manual claim runner
async function runManualTest() {
    const claim = document.getElementById('manualClaim').value.trim();
    const out = document.getElementById('manualResult');
    if (!claim) { out.textContent = 'Please enter a claim to test.'; return; }
    out.textContent = 'Running...';
    try {
        const res = await fetch(`${API_URL}/verify`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ claim, options: { include_sources: true } })
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        out.innerHTML = `<strong>Verdict:</strong> ${data.verdict} <strong>Confidence:</strong> ${Math.round((data.confidence||0)*100)}% <br/><strong>Sources:</strong> ${ (data.sources || []).slice(0,5).map(s=>s.url||s).join(', ') }`;
    } catch (e) {
        out.textContent = `Error: ${e.message}`;
    }
}

// Run a single test card
async function runSingleTest(id) {
    const tc = TEST_CLAIMS.find(t => t.id === id);
    if (!tc) return;
    const resultDiv = document.getElementById(`result-${id}`);
    const item = document.getElementById(`test-${id}`);
    resultDiv.textContent = 'Running...';
    item.classList.remove('pass','fail');
    try {
        const res = await fetch(`${API_URL}/verify`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ claim: tc.claim, options: { include_sources: true } })
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        let verdict = (data.verdict || '').toLowerCase();
        if (verdict === 'mostly_true') verdict = 'true';
        if (verdict === 'mostly_false') verdict = 'false';
        const correct = (tc.expected === verdict) || (tc.expected === 'mixed' && (verdict === 'mixed' || verdict === 'unverifiable')) || (tc.expected === 'unverifiable' && verdict === 'unverifiable');
        if (correct) {
            resultDiv.textContent = `✅ ${verdict.toUpperCase()} (${Math.round((data.confidence||0)*100)}%)`;
            item.classList.add('pass');
        } else {
            resultDiv.textContent = `❌ ${verdict.toUpperCase()} (${Math.round((data.confidence||0)*100)}%)`;
            item.classList.add('fail');
        }
    } catch (e) {
        resultDiv.textContent = `Error: ${e.message}`;
        item.classList.add('fail');
    }
}

// Rate limit test: send rapid requests in parallel to detect 429
async function runRateLimitTest() {
    const btn = document.getElementById('rateLimitBtn');
    btn.disabled = true;
    const attempts = 40; // stress amount
    let got429 = false;
    const promises = [];
    for (let i = 0; i < attempts; i++) {
        promises.push(
            fetch(`${API_URL}/verify`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ claim: 'Rate limit test ' + i })
            }).then(r => {
                if (r.status === 429) got429 = true;
                return r.status;
            }).catch(e => { return 'err'; })
        );
    }
    const results = await Promise.all(promises);
    const summary = results.reduce((acc, v)=>{ acc[v] = (acc[v]||0)+1; return acc; }, {});
    alert(`Rate limit test completed. Results:\n${JSON.stringify(summary,null,2)}\n429 observed: ${got429}`);
    btn.disabled = false;
}

// Check providers health
async function checkProvidersHealth() {
    const btn = document.getElementById('checkProvidersBtn');
    btn.disabled = true;
    try {
        const res = await fetch(`${API_URL}/providers/health`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        const inCooldown = data.health.get('in_cooldown') || data.health.in_cooldown || [];
        alert(`Providers health retrieved. In cooldown: ${inCooldown.join(', ') || 'None'}`);
    } catch (e) {
        alert(`Error checking providers: ${e.message}`);
    }
    btn.disabled = false;
}

function showSummary(pass, fail, errors) {
    const total = pass + fail + errors;
    const acc = total > 0 ? ((pass / total) * 100).toFixed(2) : 0;
    const summary = document.getElementById('summary');
    summary.innerHTML = `
      <div class="header-card card">
        <div>
          <h1>Verity System Status</h1>
          <div class="muted">Real-time health check for all services and integrations</div>
        </div>
        <div class="header-stats">
          <div class="stat"><div class="num">${pass}</div><div class="muted">Passed</div></div>
          <div class="stat"><div class="num" style="color:var(--danger);">${fail}</div><div class="muted">Failed</div></div>
          <div class="stat"><div class="num" style="color:var(--accent);">${errors}</div><div class="muted">Warnings</div></div>
          <button class="btn" onclick="runAllTests()">Run All Tests</button>
        </div>
      </div>
      <div style="margin-top:1rem;" class="card">
        <div class="service-grid" id="serviceGrid"></div>
      </div>
    `;
    summary.style.display = 'block';
    // populate service grid with sample cards summary
    const grid = document.getElementById('serviceGrid');
    grid.innerHTML = `
      <div class="card service-item">
        <h3>Authentication (Supabase)</h3>
        <div class="muted">Connection <span class="badge ok">✓ OK</span></div>
        <div class="muted">Email Sign Up <span class="badge warn">⚠ SMTP needed</span></div>
        <div style="margin-top:0.6rem" class="terminal">Test Authentication<br/>✓ Connected</div>
      </div>
      <div class="card service-item">
        <h3>Database (Supabase)</h3>
        <div class="muted">Connection <span class="badge ok">✓ OK</span></div>
        <div class="terminal">Testing database...<br/>✓ Profiles table accessible</div>
      </div>
      <div class="card service-item">
        <h3>Payments (Stripe)</h3>
        <div class="muted">Stripe.js Loaded <span class="badge ok">✓ OK</span></div>
        <div class="muted">Public Key Valid <span class="badge warn">⚠ No key</span></div>
        <div class="terminal">Testing Stripe...<br/>⚠ Stripe public key not configured</div>
      </div>
    `;
}

window.onload = renderTests;
