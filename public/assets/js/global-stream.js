/* =============================================
   GLOBAL INTELLIGENCE STREAM - JAVASCRIPT
   Real-time Verification System
   ============================================= */

// Configuration
const CONFIG = {
    feedUpdateInterval: 3000,
    trendingUpdateInterval: 30000,
    maxFeedItems: 50,
    sources: ['Twitter/X', 'Reddit', 'Facebook', 'TikTok', 'News', 'YouTube'],
    topics: ['Politics', 'Health', 'Science', 'Technology', 'Finance', 'Climate', 'Entertainment']
};

// Sample data for trending claims
const TRENDING_CLAIMS = [
    { claim: "New study claims coffee consumption linked to longer lifespan", source: "Twitter/X", shares: "234K", topic: "Health", verdict: "mixed", score: 67 },
    { claim: "Major tech company announces 50% workforce reduction", source: "Reddit", shares: "189K", topic: "Technology", verdict: "false", score: 12 },
    { claim: "Scientists discover high-speed solar wind anomaly", source: "News", shares: "156K", topic: "Science", verdict: "true", score: 94 },
    { claim: "Government passes new cryptocurrency regulation bill", source: "Twitter/X", shares: "143K", topic: "Finance", verdict: "true", score: 89 },
    { claim: "Viral video shows extreme weather event in Australia", source: "TikTok", shares: "128K", topic: "Climate", verdict: "true", score: 91 },
    { claim: "Celebrity announces presidential campaign", source: "Facebook", shares: "112K", topic: "Politics", verdict: "false", score: 8 },
    { claim: "New AI system passes advanced reasoning test", source: "News", shares: "98K", topic: "Technology", verdict: "mixed", score: 72 },
    { claim: "Breakthrough vaccine shows 95% effectiveness", source: "Twitter/X", shares: "87K", topic: "Health", verdict: "true", score: 96 }
];

// Sample live feed data generator
const FEED_TEMPLATES = [
    { claim: "Breaking: {topic} expert claims major development in {field}", topics: ["Science", "Technology"] },
    { claim: "Viral post alleges {company} involved in {action}", topics: ["Finance", "Technology"] },
    { claim: "New report suggests {percentage}% increase in {metric}", topics: ["Health", "Climate"] },
    { claim: "Government official announces {policy} changes", topics: ["Politics"] },
    { claim: "Study reveals connection between {factor1} and {factor2}", topics: ["Health", "Science"] }
];

// State management
let state = {
    isPaused: false,
    selectedClaim: null,
    activeSource: 'all',
    activeTopic: 'all',
    feedItems: []
};

// DOM Elements
let elements = {};

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    initializeElements();
    initializeEventListeners();
    renderTrendingClaims();
    startLiveFeed();
    animateCounters();
    startTerminalSimulation();
});

function initializeElements() {
    elements = {
        trendingList: document.getElementById('trending-claims'),
        liveFeed: document.getElementById('live-feed'),
        detailsPanel: document.getElementById('details-panel'),
        terminalOutput: document.getElementById('terminal-output'),
        pauseBtn: document.getElementById('pause-feed'),
        clearBtn: document.getElementById('clear-feed')
    };
}

function initializeEventListeners() {
    // Source filters
    document.querySelectorAll('.source-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.source-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            state.activeSource = btn.dataset.source;
        });
    });

    // Topic filters
    document.querySelectorAll('.topic-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.topic-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            state.activeTopic = btn.dataset.topic;
        });
    });

    // Pause/Resume feed
    if (elements.pauseBtn) {
        elements.pauseBtn.addEventListener('click', togglePause);
    }

    // Clear feed
    if (elements.clearBtn) {
        elements.clearBtn.addEventListener('click', clearFeed);
    }

    // Hotspot tooltips
    document.querySelectorAll('.hotspot').forEach(hotspot => {
        hotspot.addEventListener('mouseenter', showHotspotInfo);
        hotspot.addEventListener('mouseleave', hideHotspotInfo);
    });
}

function renderTrendingClaims() {
    if (!elements.trendingList) return;

    elements.trendingList.innerHTML = TRENDING_CLAIMS.map((item, index) => `
        <div class="trending-item" data-index="${index}">
            <div class="trending-rank">${index + 1}</div>
            <div class="trending-content">
                <div class="trending-claim">${item.claim}</div>
                <div class="trending-meta">
                    <span class="trending-source">
                        ${getSourceIcon(item.source)}
                        ${item.source}
                    </span>
                    <span class="trending-shares">
                        <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"/>
                            <polyline points="16 6 12 2 8 6"/>
                            <line x1="12" y1="2" x2="12" y2="15"/>
                        </svg>
                        ${item.shares}
                    </span>
                </div>
            </div>
        </div>
    `).join('');

    // Add click handlers
    document.querySelectorAll('.trending-item').forEach(item => {
        item.addEventListener('click', () => selectClaim(parseInt(item.dataset.index), 'trending'));
    });
}

function startLiveFeed() {
    // Initial items
    for (let i = 0; i < 5; i++) {
        addFeedItem();
    }

    // Continue adding items
    setInterval(() => {
        if (!state.isPaused) {
            addFeedItem();
        }
    }, CONFIG.feedUpdateInterval);
}

function addFeedItem() {
    const item = generateFeedItem();
    state.feedItems.unshift(item);

    // Limit feed size
    if (state.feedItems.length > CONFIG.maxFeedItems) {
        state.feedItems.pop();
    }

    renderFeedItem(item, true);
    addTerminalLine(item);
}

function generateFeedItem() {
    const sources = CONFIG.sources;
    const verdicts = ['true', 'false', 'mixed', 'unverified'];
    const claims = [
        "New research suggests link between social media use and sleep patterns",
        "Government announces new infrastructure spending plan",
        "Tech company reports record quarterly earnings",
        "Scientists observe unusual seismic activity",
        "Central bank hints at interest rate changes",
        "Viral video claims to show rare natural phenomenon",
        "Report alleges data privacy violations at major platform",
        "Health officials issue advisory on seasonal illness",
        "Environmental study reveals concerning pollution levels",
        "Political figure makes controversial policy statement",
        "Breakthrough announced in renewable energy storage",
        "Stock market reacts to trade policy announcement",
        "New species discovered in remote region",
        "Celebrity endorsement sparks product sales surge",
        "Cybersecurity experts warn of new threat vector"
    ];

    const verdict = verdicts[Math.floor(Math.random() * verdicts.length)];
    let score;
    switch(verdict) {
        case 'true': score = 80 + Math.floor(Math.random() * 20); break;
        case 'false': score = Math.floor(Math.random() * 25); break;
        case 'mixed': score = 40 + Math.floor(Math.random() * 30); break;
        default: score = null;
    }

    return {
        id: Date.now() + Math.random(),
        claim: claims[Math.floor(Math.random() * claims.length)],
        source: sources[Math.floor(Math.random() * sources.length)],
        topic: CONFIG.topics[Math.floor(Math.random() * CONFIG.topics.length)],
        verdict: verdict,
        score: score,
        time: new Date(),
        shares: Math.floor(Math.random() * 50000) + 1000,
        sources: generateVerificationSources()
    };
}

function generateVerificationSources() {
    const sources = [
        { name: "Associated Press", type: "news" },
        { name: "Reuters", type: "news" },
        { name: "Nature Journal", type: "academic" },
        { name: "CDC", type: "government" },
        { name: "WHO", type: "government" },
        { name: "PubMed", type: "academic" },
        { name: "Snopes", type: "factcheck" },
        { name: "PolitiFact", type: "factcheck" }
    ];
    
    const count = 2 + Math.floor(Math.random() * 3);
    const selected = [];
    const available = [...sources];
    
    for (let i = 0; i < count; i++) {
        const idx = Math.floor(Math.random() * available.length);
        selected.push(available.splice(idx, 1)[0]);
    }
    
    return selected;
}

function renderFeedItem(item, prepend = false) {
    if (!elements.liveFeed) return;

    const itemHtml = `
        <div class="feed-item" data-id="${item.id}">
            <div class="feed-header">
                <span class="feed-source">
                    ${getSourceIcon(item.source)}
                    ${item.source}
                </span>
                <span class="feed-time">${formatTime(item.time)}</span>
            </div>
            <div class="feed-claim">${item.claim}</div>
            <div class="feed-footer">
                <span class="feed-verdict verdict-${item.verdict}">
                    ${getVerdictIcon(item.verdict)}
                    ${capitalizeFirst(item.verdict)}
                </span>
                ${item.score !== null ? `<span class="feed-score">${item.score}% confidence</span>` : ''}
            </div>
        </div>
    `;

    if (prepend) {
        elements.liveFeed.insertAdjacentHTML('afterbegin', itemHtml);
    } else {
        elements.liveFeed.insertAdjacentHTML('beforeend', itemHtml);
    }

    // Add click handler
    const newItem = elements.liveFeed.querySelector(`[data-id="${item.id}"]`);
    if (newItem) {
        newItem.addEventListener('click', () => selectFeedItem(item));
    }

    // Remove excess items from DOM
    const items = elements.liveFeed.querySelectorAll('.feed-item');
    if (items.length > CONFIG.maxFeedItems) {
        items[items.length - 1].remove();
    }
}

function selectClaim(index, type) {
    const item = type === 'trending' ? TRENDING_CLAIMS[index] : state.feedItems[index];
    state.selectedClaim = item;

    // Update UI
    document.querySelectorAll('.trending-item, .feed-item').forEach(el => el.classList.remove('selected'));
    
    if (type === 'trending') {
        document.querySelectorAll('.trending-item')[index]?.classList.add('selected');
    }

    renderDetails(item);
}

function selectFeedItem(item) {
    state.selectedClaim = item;

    // Update UI
    document.querySelectorAll('.trending-item, .feed-item').forEach(el => el.classList.remove('selected'));
    document.querySelector(`[data-id="${item.id}"]`)?.classList.add('selected');

    renderDetails(item);
}

function renderDetails(item) {
    if (!elements.detailsPanel) return;

    const verdictClass = item.verdict || 'unverified';
    const verdictLabel = item.verdict ? capitalizeFirst(item.verdict) : 'Analyzing...';
    const verdictColor = {
        true: '#22c55e',
        false: '#ef4444',
        mixed: '#fbbf24',
        unverified: '#9ca3af'
    }[verdictClass];

    elements.detailsPanel.innerHTML = `
        <div class="details-claim">${item.claim}</div>
        
        <div class="details-verdict-box ${verdictClass}">
            <div class="verdict-label">Verification Result</div>
            <div class="verdict-value" style="color: ${verdictColor}">
                ${getVerdictIcon(verdictClass)} ${verdictLabel}
                ${item.score !== null ? `<span style="font-size: 0.875rem; opacity: 0.7; margin-left: 0.5rem;">(${item.score}% confidence)</span>` : ''}
            </div>
        </div>

        <div class="details-section">
            <div class="details-section-title">Source Information</div>
            <div class="source-item">
                ${getSourceIcon(item.source)}
                <span>Detected on ${item.source}</span>
            </div>
            ${item.shares ? `
            <div class="source-item" style="margin-top: 0.5rem;">
                <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                    <circle cx="9" cy="7" r="4"/>
                    <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                    <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                </svg>
                <span>${typeof item.shares === 'number' ? item.shares.toLocaleString() : item.shares} shares/engagements</span>
            </div>
            ` : ''}
        </div>

        <div class="details-section">
            <div class="details-section-title">Verification Sources</div>
            <div class="details-sources">
                ${(item.sources || generateVerificationSources()).map(src => `
                    <div class="source-item">
                        <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M9 12l2 2 4-4"/>
                            <circle cx="12" cy="12" r="10"/>
                        </svg>
                        <span>${src.name}</span>
                    </div>
                `).join('')}
            </div>
        </div>

        <div class="details-section">
            <div class="details-section-title">Analysis Summary</div>
            <p style="font-size: 0.875rem; color: rgba(255,255,255,0.7); line-height: 1.6;">
                ${generateAnalysisSummary(item)}
            </p>
        </div>
    `;
}

function generateAnalysisSummary(item) {
    const summaries = {
        true: `This claim has been verified as accurate based on cross-referencing with ${item.sources?.length || 3} authoritative sources. The information aligns with established facts and credible reporting.`,
        false: `This claim appears to be inaccurate or misleading. Our analysis found contradicting evidence from multiple reliable sources. Exercise caution when sharing this information.`,
        mixed: `This claim contains elements of truth but is partially misleading or lacks important context. Some aspects are accurate while others require clarification or are exaggerated.`,
        unverified: `This claim is currently being analyzed. Our AI systems are cross-referencing multiple sources to determine its accuracy. Check back shortly for results.`
    };
    return summaries[item.verdict] || summaries.unverified;
}

function togglePause() {
    state.isPaused = !state.isPaused;
    
    if (elements.pauseBtn) {
        elements.pauseBtn.innerHTML = state.isPaused 
            ? `<svg class="icon-sm" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg>`
            : `<svg class="icon-sm" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>`;
    }
}

function clearFeed() {
    state.feedItems = [];
    if (elements.liveFeed) {
        elements.liveFeed.innerHTML = '';
    }
}

function animateCounters() {
    document.querySelectorAll('[data-count]').forEach(el => {
        const target = parseInt(el.dataset.count);
        const duration = 2000;
        const start = performance.now();
        
        function update(currentTime) {
            const elapsed = currentTime - start;
            const progress = Math.min(elapsed / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3);
            const current = Math.floor(target * eased);
            
            el.textContent = current.toLocaleString();
            
            if (progress < 1) {
                requestAnimationFrame(update);
            }
        }
        
        requestAnimationFrame(update);
    });
}

function startTerminalSimulation() {
    const messages = [
        { type: 'info', text: 'Scanning Twitter/X for trending claims...' },
        { type: 'success', text: '✓ Detected 47 new claims in the last minute' },
        { type: 'info', text: 'Running verification against 18 AI models...' },
        { type: 'warning', text: '⚠ High misinformation activity detected in Politics category' },
        { type: 'success', text: '✓ Batch verification complete: 42/47 claims processed' },
        { type: 'info', text: 'Updating global heatmap data...' },
        { type: 'success', text: '✓ Connected to additional news sources' },
        { type: 'info', text: 'Analyzing viral content spread patterns...' }
    ];

    let index = 0;
    
    setInterval(() => {
        if (!state.isPaused && elements.terminalOutput) {
            const msg = messages[index % messages.length];
            const time = new Date().toTimeString().split(' ')[0];
            
            const line = document.createElement('div');
            line.className = `term-line ${msg.type}`;
            line.innerHTML = `<span class="term-time">[${time}]</span><span>${msg.text}</span>`;
            
            elements.terminalOutput.appendChild(line);
            elements.terminalOutput.scrollTop = elements.terminalOutput.scrollHeight;
            
            // Keep terminal output manageable
            const lines = elements.terminalOutput.querySelectorAll('.term-line');
            if (lines.length > 20) {
                lines[0].remove();
            }
            
            index++;
        }
    }, 4000);
}

function addTerminalLine(item) {
    if (!elements.terminalOutput) return;

    const time = new Date().toTimeString().split(' ')[0];
    const verdictEmoji = { true: '✓', false: '✗', mixed: '~', unverified: '?' }[item.verdict] || '?';
    const type = item.verdict === 'true' ? 'success' : item.verdict === 'false' ? 'error' : 'info';
    
    const line = document.createElement('div');
    line.className = `term-line ${type}`;
    line.innerHTML = `<span class="term-time">[${time}]</span><span>${verdictEmoji} [${item.source}] "${item.claim.substring(0, 50)}..."</span>`;
    
    elements.terminalOutput.appendChild(line);
    elements.terminalOutput.scrollTop = elements.terminalOutput.scrollHeight;
}

// Helper functions
function getSourceIcon(source) {
    const icons = {
        'Twitter/X': '<svg class="icon-sm" viewBox="0 0 24 24" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>',
        'Reddit': '<svg class="icon-sm" viewBox="0 0 24 24" fill="currentColor"><path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z"/></svg>',
        'Facebook': '<svg class="icon-sm" viewBox="0 0 24 24" fill="currentColor"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>',
        'TikTok': '<svg class="icon-sm" viewBox="0 0 24 24" fill="currentColor"><path d="M19.59 6.69a4.83 4.83 0 0 1-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 0 1-5.2 1.74 2.89 2.89 0 0 1 2.31-4.64 2.93 2.93 0 0 1 .88.13V9.4a6.84 6.84 0 0 0-1-.05A6.33 6.33 0 0 0 5 20.1a6.34 6.34 0 0 0 10.86-4.43v-7a8.16 8.16 0 0 0 4.77 1.52v-3.4a4.85 4.85 0 0 1-1-.1z"/></svg>',
        'News': '<svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 1-2 2zm0 0a2 2 0 0 1-2-2v-9c0-1.1.9-2 2-2h2"/></svg>',
        'YouTube': '<svg class="icon-sm" viewBox="0 0 24 24" fill="currentColor"><path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>'
    };
    return icons[source] || icons['News'];
}

function getVerdictIcon(verdict) {
    const icons = {
        true: '<svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
        false: '<svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>',
        mixed: '<svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>',
        unverified: '<svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>'
    };
    return icons[verdict] || icons.unverified;
}

function formatTime(date) {
    const now = new Date();
    const diff = Math.floor((now - date) / 1000);
    
    if (diff < 60) return 'Just now';
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return date.toLocaleDateString();
}

function capitalizeFirst(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

function showHotspotInfo(e) {
    const hotspot = e.target;
    const region = hotspot.dataset.region;
    const count = hotspot.dataset.count;
    
    // Create tooltip
    const tooltip = document.createElement('div');
    tooltip.className = 'hotspot-tooltip';
    tooltip.innerHTML = `<strong>${region}</strong><br>${count} claims analyzed`;
    tooltip.style.cssText = `
        position: absolute;
        left: ${hotspot.style.left};
        top: calc(${hotspot.style.top} - 50px);
        transform: translateX(-50%);
        background: rgba(0,0,0,0.9);
        padding: 0.5rem 0.75rem;
        border-radius: 6px;
        font-size: 0.75rem;
        white-space: nowrap;
        z-index: 100;
        pointer-events: none;
    `;
    
    hotspot.parentElement.appendChild(tooltip);
}

function hideHotspotInfo(e) {
    const tooltip = document.querySelector('.hotspot-tooltip');
    if (tooltip) tooltip.remove();
}
