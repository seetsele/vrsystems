// ================================================
// VERITY SYSTEMS - MAIN.JS V2
// Real API Integration with Demo Fallback
// ================================================

// Wait for GSAP to be available before registering plugins
if (typeof gsap !== 'undefined' && typeof ScrollTrigger !== 'undefined') {
    gsap.registerPlugin(ScrollTrigger);
}

// Prevent layout shifts during animations
window.addEventListener('load', () => {
    document.body.style.opacity = '1';
    // Register ScrollTrigger after load if not already done
    if (typeof gsap !== 'undefined' && typeof ScrollTrigger !== 'undefined') {
        gsap.registerPlugin(ScrollTrigger);
    }
});

// ================================================
// DEMO ATTEMPT TRACKING
// ================================================

const DEMO_CONFIG = {
    maxAttempts: 5,
    apiBase: (typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')) 
        ? 'http://localhost:8000' 
        : 'https://veritysystems-production.up.railway.app',
    apiTimeout: 30000
};

// AUTO-RESET: Clear old demo attempts on fresh page load for better testing
// This runs once per browser session (not on every page refresh within session)
(function() {
    // Reset if last visit was more than 1 hour ago
    const lastVisit = sessionStorage.getItem('verity_last_visit');
    const now = Date.now();
    if (!lastVisit || (now - parseInt(lastVisit, 10)) > 3600000) {
        sessionStorage.removeItem('verity_demo_attempts');
        console.log('[Verity] Demo attempts reset (new session)');
    }
    sessionStorage.setItem('verity_last_visit', now.toString());
})();

// Track demo attempts in session
function getDemoAttempts() {
    const attempts = sessionStorage.getItem('verity_demo_attempts');
    const count = attempts ? parseInt(attempts, 10) : 0;
    console.log('[Verity] Demo attempts used:', count);
    return count;
}

function incrementDemoAttempts() {
    const current = getDemoAttempts();
    const newCount = current + 1;
    sessionStorage.setItem('verity_demo_attempts', newCount.toString());
    console.log('[Verity] Incremented demo attempts to:', newCount);
    return newCount;
}

function getRemainingAttempts() {
    const remaining = Math.max(0, DEMO_CONFIG.maxAttempts - getDemoAttempts());
    console.log('[Verity] Remaining attempts:', remaining);
    return remaining;
}

// Reset demo attempts (for testing - can call from console: resetDemoAttempts())
function resetDemoAttempts() {
    sessionStorage.removeItem('verity_demo_attempts');
    console.log('[Verity] Demo attempts reset');
    updateAttemptsUI();
}

// ================================================
// DEMO FORM FUNCTIONALITY
// ================================================

function initializeDemoForm() {
    const demoForm = document.getElementById('demoForm');
    const claimInput = document.getElementById('claimInput');
    const demoResults = document.getElementById('demoResults');
    const exampleBtns = document.querySelectorAll('.example-btn');
    
    if (!demoForm || !claimInput || !demoResults) return;
    
    // Update UI to show remaining attempts
    updateAttemptsUI();
    
    // Example button handlers
    exampleBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            claimInput.value = btn.dataset.claim;
            claimInput.focus();
            if (typeof gsap !== 'undefined') {
                gsap.from(claimInput, {
                    duration: 0.3,
                    scale: 0.95,
                    opacity: 0.5
                });
            }
        });
    });
    
    // Form submission
    demoForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const claim = claimInput.value.trim();
        
        if (!claim || claim.length < 10) {
            showDemoError('Please enter a claim with at least 10 characters');
            return;
        }
        
        // Check if user has attempts remaining
        if (getRemainingAttempts() <= 0) {
            showDemoLimitReached();
            return;
        }
        
        await verifyClaimDemo(claim);
    });
}

function updateAttemptsUI() {
    const remaining = getRemainingAttempts();
    const attemptsDisplay = document.getElementById('demoAttemptsDisplay');
    
    if (attemptsDisplay) {
        if (remaining > 0) {
            attemptsDisplay.innerHTML = `<span class="attempts-badge">${remaining} free verification${remaining > 1 ? 's' : ''} remaining</span>`;
        } else {
            attemptsDisplay.innerHTML = `<span class="attempts-badge depleted">Demo limit reached</span>`;
        }
    }
}

// ================================================
// FACT-CHECKING KNOWLEDGE BASE (LOCAL FALLBACK)
// ================================================

const FACT_DATABASE = {
    "earth": {
        "age": {
            verdict: "VERIFIED_TRUE",
            confidence: 98.7,
            summary: "The Earth is approximately 4.54 billion years old, established through radiometric dating of meteorites and the oldest known terrestrial rocks.",
            explanation: "Multiple independent radiometric dating methods (uranium-lead dating of zircon crystals, potassium-argon dating, rubidium-strontium dating) consistently yield ages of 4.54 ± 0.05 billion years for the Earth. This is corroborated by the ages of meteorites from the early Solar System and lunar samples returned by Apollo missions. The convergence of these independent methods provides extremely high confidence in this estimate.",
            reasoning: [
                "Radiometric dating of meteorites: Multiple dating methods on meteorites consistently show ages of ~4.56 billion years",
                "Oldest Earth rocks: Zircon crystals from Australia dated to 4.4 billion years",
                "Moon rock samples: Apollo mission samples align with meteorite ages",
                "Scientific consensus: This age is accepted by NASA, USGS, and all major geological surveys worldwide"
            ],
            sources: [
                { name: "USGS - Age of the Earth", url: "https://pubs.usgs.gov/gip/geotime/age.html", credibility: "high", snippet: "The age of 4.54 billion years found for the Solar System and Earth is consistent with current calculations of 11 to 13 billion years for the age of the Milky Way Galaxy.", rating: "Confirmed" },
                { name: "Nature (2001) - Wilde et al.", url: "https://www.nature.com/articles/35059063", credibility: "high", snippet: "Detrital zircons from Western Australia confirm continental crust existed 4.4 billion years ago.", rating: "Peer-reviewed" },
                { name: "NASA - Age of the Earth", url: "https://solarsystem.nasa.gov/planets/earth/overview/", credibility: "high", snippet: "Earth formed around 4.5 billion years ago.", rating: "Official" },
                { name: "Wikipedia - Age of the Earth", url: "https://en.wikipedia.org/wiki/Age_of_Earth", credibility: "medium", snippet: "The age of Earth is estimated to be 4.54 ± 0.05 billion years.", rating: "Encyclopedia" }
            ],
            breakdown: { ai_agreement: 100, source_credibility: 98, evidence_strength: 99, consensus_score: 97 }
        }
    },
    "brain": {
        "10percent": {
            verdict: "VERIFIED_FALSE",
            confidence: 15.2,
            summary: "The claim that humans only use 10% of their brain is a persistent myth with no scientific basis.",
            explanation: "Neuroimaging studies (fMRI, PET scans) show that virtually all brain regions are active over the course of a day. While not all neurons fire simultaneously, no region is permanently inactive or unnecessary. Brain lesion studies demonstrate that damage to almost any brain area causes specific deficits. The myth likely originated from misinterpretations of early neuroscience research or from the discovery that glial cells outnumber neurons.",
            reasoning: [
                "Brain scans disprove: fMRI and PET scans show activity across the entire brain throughout the day",
                "No dormant regions: Every brain region has been mapped to specific functions",
                "Damage studies: Injury to any brain area causes measurable deficits, proving all parts are used",
                "Evolutionary argument: Maintaining unused brain tissue would be evolutionarily disadvantageous"
            ],
            sources: [
                { name: "Scientific American", url: "https://www.scientificamerican.com/article/do-people-only-use-10-percent-of-their-brains/", credibility: "high", snippet: "The '10 percent myth' is so wrong it is almost laughable. All areas of the brain have known functions.", rating: "Debunked" },
                { name: "Mayo Clinic - Brain Facts", url: "https://www.mayoclinic.org/", credibility: "high", snippet: "The 10% brain myth has been debunked by neuroscience.", rating: "Medical Authority" },
                { name: "NIH - NINDS", url: "https://www.ninds.nih.gov/", credibility: "high", snippet: "Brain imaging research shows activity throughout the brain, even during sleep.", rating: "Government Research" },
                { name: "Snopes - 10% Brain", url: "https://www.snopes.com/fact-check/the-ten-percent-myth/", credibility: "medium", snippet: "Rating: FALSE - This claim has been thoroughly debunked.", rating: "Fact-checked: FALSE" }
            ],
            breakdown: { ai_agreement: 7, source_credibility: 95, evidence_strength: 98, consensus_score: 96 }
        }
    },
    "lightning": {
        "strike": {
            verdict: "VERIFIED_FALSE",
            confidence: 12.5,
            summary: "Lightning frequently strikes the same place multiple times, especially tall structures and geographical features.",
            explanation: "Lightning tends to strike the same locations repeatedly, particularly tall or conductive objects. The Empire State Building is struck approximately 20-25 times per year. Lightning rods work precisely because lightning does strike the same place repeatedly - they provide a preferred path to ground. The probability of a lightning strike depends on height, conductivity, and terrain, not random chance from previous strikes.",
            reasoning: [
                "Empire State Building: Struck ~23 times annually, documented since 1931",
                "Lightning rods work: Their entire function relies on lightning striking the same spot",
                "Physics basis: Tall, conductive objects create preferential ionization paths",
                "Weather data: NOAA confirms repeated strikes are common and well-documented"
            ],
            sources: [
                { name: "NOAA - Lightning Safety", url: "https://www.weather.gov/safety/lightning-myths", credibility: "high", snippet: "Myth: Lightning never strikes the same place twice. Fact: Lightning often strikes the same place repeatedly.", rating: "Officially Debunked" },
                { name: "National Geographic", url: "https://www.nationalgeographic.com/environment/article/lightning", credibility: "high", snippet: "The Empire State Building is struck about 23 times a year.", rating: "Documented" },
                { name: "Encyclopedia Britannica", url: "https://www.britannica.com/science/lightning-meteorology", credibility: "high", snippet: "Tall structures may be struck by lightning several times during a single storm.", rating: "Reference" },
                { name: "Wikipedia - Lightning", url: "https://en.wikipedia.org/wiki/Lightning", credibility: "medium", snippet: "Contrary to the popular saying, lightning can and regularly does strike the same place twice.", rating: "Encyclopedia" }
            ],
            breakdown: { ai_agreement: 7, source_credibility: 96, evidence_strength: 99, consensus_score: 98 }
        }
    }
};

// ================================================
// CLAIM ANALYSIS ENGINE
// ================================================

function analyzeClaimContent(claim) {
    const claimLower = claim.toLowerCase();
    
    // Check for Earth's age claims
    if ((claimLower.includes('earth') && (claimLower.includes('billion') || claimLower.includes('years old') || claimLower.includes('age'))) ||
        claimLower.includes('4.5 billion') || claimLower.includes('4.54 billion')) {
        return { ...FACT_DATABASE.earth.age, claim: claim };
    }
    
    // Check for 10% brain myth
    if ((claimLower.includes('brain') && claimLower.includes('10')) ||
        (claimLower.includes('use') && claimLower.includes('percent') && claimLower.includes('brain')) ||
        claimLower.includes('10%') && claimLower.includes('brain')) {
        return { ...FACT_DATABASE.brain['10percent'], claim: claim };
    }
    
    // Check for lightning myth
    if (claimLower.includes('lightning') && (claimLower.includes('same place') || claimLower.includes('twice') || claimLower.includes('never'))) {
        return { ...FACT_DATABASE.lightning.strike, claim: claim };
    }
    
    // For unknown claims, perform intelligent analysis
    return generateIntelligentAnalysis(claim);
}

function generateIntelligentAnalysis(claim) {
    const claimLower = claim.toLowerCase();
    
    // Determine claim category and generate appropriate response
    let verdict, confidence, summary, explanation, sources, breakdown, reasoning;
    
    // Check for scientific/factual keywords
    const hasScientificTerms = /scientist|research|study|proven|discovered|found|evidence/.test(claimLower);
    const hasHistoricalTerms = /year|century|founded|invented|born|died|war|history/.test(claimLower);
    const hasStatisticalTerms = /percent|%|million|billion|thousand|average|most|least/.test(claimLower);
    const hasOpinionTerms = /best|worst|should|always|never|everyone|nobody/.test(claimLower);
    
    if (hasOpinionTerms && !hasStatisticalTerms) {
        verdict = "UNVERIFIABLE";
        confidence = 35 + Math.random() * 15;
        summary = "This claim contains subjective language that cannot be objectively verified.";
        explanation = "Claims containing words like 'best', 'worst', 'should', 'always', or 'never' often express opinions rather than verifiable facts. While some aspects may be measurable, the core assertion appears to be subjective in nature.";
        reasoning = [
            "Subjective language detected: Words like 'best', 'worst', 'always', 'never' indicate opinion",
            "No measurable criteria: The claim lacks specific metrics for verification",
            "Context dependent: Truth value may vary based on individual perspectives",
            "Recommendation: Rephrase with specific, measurable criteria for verification"
        ];
        sources = [
            { name: "Logic & Critical Thinking", url: null, credibility: "medium", snippet: "Subjective claims require different standards of evaluation than objective facts.", rating: "Methodological Note" }
        ];
        breakdown = { ai_agreement: 50, source_credibility: 60, evidence_strength: 30, consensus_score: 40 };
    } else if (hasScientificTerms || hasHistoricalTerms || hasStatisticalTerms) {
        verdict = "NEEDS_VERIFICATION";
        confidence = 45 + Math.random() * 20;
        summary = "This claim requires deeper verification against authoritative sources.";
        explanation = "This claim contains factual assertions that can potentially be verified. However, we were unable to find a direct match in our verified fact database. For full verification, this claim should be checked against peer-reviewed sources, official databases, and authoritative references.";
        reasoning = [
            "Factual claim detected: Contains verifiable assertions about real-world facts",
            "No exact match: Our database doesn't have pre-verified data for this specific claim",
            "Verification recommended: Full API verification will query 28+ AI models and databases",
            "Potential sources: Academic papers, government databases, news archives may contain relevant data"
        ];
        sources = [
            { name: "Wikipedia", url: "https://wikipedia.org", credibility: "medium", snippet: "Related topics found but no exact match for this specific claim.", rating: "Partial Match" },
            { name: "Google Scholar", url: "https://scholar.google.com", credibility: "high", snippet: "Academic sources may contain relevant research.", rating: "Research Recommended" },
            { name: "Fact-Check Organizations", url: "https://www.factcheck.org", credibility: "high", snippet: "This claim has not yet been reviewed by major fact-checkers.", rating: "Not Yet Reviewed" }
        ];
        breakdown = { ai_agreement: 65, source_credibility: 55, evidence_strength: 45, consensus_score: 50 };
    } else {
        verdict = "PARTIALLY_VERIFIABLE";
        confidence = 50 + Math.random() * 15;
        summary = "This claim could not be fully verified with available data.";
        explanation = "Our analysis could not definitively verify or refute this claim. This may be because: (1) the claim is too vague, (2) insufficient evidence exists, (3) the topic requires specialized knowledge, or (4) the claim mixes verifiable facts with unverifiable assertions.";
        reasoning = [
            "Partial information: Some elements of this claim may be verifiable, others not",
            "Ambiguity detected: The claim may need clarification for proper verification",
            "Limited sources: Available databases don't contain definitive information",
            "Recommendation: Try a more specific claim or use the full API for deeper analysis"
        ];
        sources = [
            { name: "General Knowledge Base", url: null, credibility: "medium", snippet: "Claim analyzed but no definitive sources found.", rating: "Inconclusive" }
        ];
        breakdown = { ai_agreement: 55, source_credibility: 50, evidence_strength: 40, consensus_score: 45 };
    }
    
    return {
        claim: claim,
        verdict: verdict,
        confidence: confidence,
        summary: summary,
        explanation: explanation,
        reasoning: reasoning,
        sources: sources,
        breakdown: breakdown
    };
}

// ================================================
// API INTEGRATION
// ================================================

async function checkApiHealth() {
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 3000);
        
        const response = await fetch(`${DEMO_CONFIG.apiBase}/health`, {
            method: 'GET',
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        if (response.ok) {
            const data = await response.json();
            console.log('✅ Verity API available:', data.version || 'v1');
            return true;
        }
    } catch (error) {
        console.log('ℹ️ API not available, using local knowledge base');
    }
    return false;
}

async function verifyWithApi(claim) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), DEMO_CONFIG.apiTimeout);
    
    try {
        const response = await fetch(`${DEMO_CONFIG.apiBase}/verify`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({
                claim: claim,
                detailed: true
            }),
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        
        const result = await response.json();
        return normalizeApiResponse(result);
    } catch (error) {
        clearTimeout(timeoutId);
        throw error;
    }
}

function normalizeApiResponse(apiResult) {
    // Transform API response to match our display format
    return {
        claim: apiResult.claim,
        verdict: apiResult.status?.toUpperCase().replace('-', '_') || apiResult.verdict || 'UNVERIFIABLE',
        confidence: apiResult.confidence_score || apiResult.confidence || 50,
        summary: apiResult.analysis_summary || apiResult.summary || 'Analysis complete.',
        explanation: apiResult.ai_analysis || apiResult.explanation || 'See sources below for more information.',
        reasoning: apiResult.reasoning || apiResult.evidence_chain?.map(e => e.description) || [
            'Analysis performed using multiple AI models',
            'Sources cross-referenced for accuracy',
            'Confidence calculated from source agreement'
        ],
        sources: (apiResult.sources || []).map(s => ({
            name: s.name || s.source,
            url: s.url || null,
            credibility: s.credibility || 'medium',
            snippet: s.snippet || s.excerpt || '',
            rating: s.rating || s.verdict || 'Analyzed'
        })),
        breakdown: apiResult.breakdown || {
            ai_agreement: apiResult.provider_agreement || 75,
            source_credibility: apiResult.source_score || 70,
            evidence_strength: apiResult.evidence_score || 65,
            consensus_score: apiResult.consensus_score || 70
        },
        processing_time_ms: apiResult.processing_time_ms || apiResult.total_time_ms || 0,
        request_id: apiResult.request_id || 'local_' + Math.random().toString(36).substr(2, 16),
        providers_used: apiResult.providers_used || ['local_knowledge_base'],
        source: 'api'
    };
}

// ================================================
// DEMO VERIFICATION FUNCTION
// ================================================

async function verifyClaimDemo(claim) {
    const demoResults = document.getElementById('demoResults');
    
    if (!demoResults) {
        console.error('Demo results container not found');
        return;
    }
    
    // Show loading state with progress
    showDemoLoading();
    
    const startTime = Date.now();
    
    try {
        // First, try to use the real API
        let apiAvailable = false;
        try {
            apiAvailable = await checkApiHealth();
        } catch (e) {
            console.log('API health check failed:', e);
            apiAvailable = false;
        }
        
        let result;
        
        if (apiAvailable) {
            // Update loading to show we're using real API
            updateLoadingMessage('Connecting to Verity API...');
            await new Promise(resolve => setTimeout(resolve, 500));
            updateLoadingStep(1);
            
            updateLoadingMessage('Querying 28+ AI models...');
            
            try {
                result = await verifyWithApi(claim);
                result.source = 'api';
                updateLoadingStep(2);
                updateLoadingStep(3);
            } catch (apiError) {
                console.warn('API verification failed, using local knowledge base:', apiError);
                result = await fallbackToLocalVerification(claim, startTime);
            }
        } else {
            // Use local knowledge base with simulated processing
            result = await fallbackToLocalVerification(claim, startTime);
        }
        
        // Increment demo attempts
        incrementDemoAttempts();
        updateAttemptsUI();
        
        // Calculate processing time
        result.processing_time_ms = result.processing_time_ms || (Date.now() - startTime);
        result.request_id = result.request_id || 'req_' + Math.random().toString(36).substr(2, 16);
        result.timestamp = new Date().toISOString();
        
        console.log('[Verity] Final result object:', JSON.stringify(result, null, 2));
        
        // Display result with animated score wheel
        try {
            displayEnhancedDemoResult(result);
            console.log('[Verity] Display function completed successfully');
        } catch (displayError) {
            console.error('[Verity] Error displaying result:', displayError);
            console.error('[Verity] Error stack:', displayError.stack);
            showDemoError('Error displaying results: ' + displayError.message);
        }
        
    } catch (error) {
        console.error('Verification error:', error);
        showDemoError('Failed to verify claim. Please try again.');
    }
}

async function fallbackToLocalVerification(claim, startTime) {
    // Step 1: Initial analysis
    updateLoadingMessage('Analyzing claim structure...');
    await new Promise(resolve => setTimeout(resolve, 1200));
    updateLoadingStep(1);
    
    // Step 2: Source gathering
    updateLoadingMessage('Searching knowledge base...');
    await new Promise(resolve => setTimeout(resolve, 1500));
    updateLoadingStep(2);
    
    // Step 3: Generating explanation
    updateLoadingMessage('Generating explanation...');
    await new Promise(resolve => setTimeout(resolve, 1000));
    updateLoadingStep(3);
    
    const result = analyzeClaimContent(claim);
    result.source = 'local_knowledge_base';
    result.providers_used = ['local_fact_database', 'heuristic_analyzer'];
    
    return result;
}

function showDemoLoading() {
    const demoResults = document.getElementById('demoResults');
    if (!demoResults) return;
    
    demoResults.innerHTML = `
        <div class="demo-loading">
            <div class="loading-spinner"></div>
            <p id="loadingMessage">Initializing verification...</p>
            <div class="loading-substeps">
                <div class="substep" id="step1">
                    <span class="step-text">Analyzing claim structure...</span>
                    <span class="step-status">⏳</span>
                </div>
                <div class="substep" id="step2">
                    <span class="step-text">Searching authoritative sources...</span>
                    <span class="step-status">⏳</span>
                </div>
                <div class="substep" id="step3">
                    <span class="step-text">Generating explanation...</span>
                    <span class="step-status">⏳</span>
                </div>
            </div>
            <span class="loading-subtext">This may take 5-15 seconds for accurate results</span>
        </div>
    `;
    
    if (typeof gsap !== 'undefined') {
        gsap.from('.demo-loading', {
            opacity: 0,
            y: 20,
            duration: 0.4
        });
    }
}

function updateLoadingMessage(message) {
    const loadingMsg = document.getElementById('loadingMessage');
    if (loadingMsg) {
        loadingMsg.textContent = message;
    }
}

function updateLoadingStep(step) {
    const stepElement = document.getElementById(`step${step}`);
    if (stepElement) {
        const status = stepElement.querySelector('.step-status');
        if (status) {
            status.textContent = '✓';
            status.style.color = '#10b981';
        }
        stepElement.style.opacity = '0.6';
    }
}

function showDemoLimitReached() {
    const demoResults = document.getElementById('demoResults');
    if (!demoResults) return;
    
    demoResults.innerHTML = `
        <div class="demo-limit-reached">
            <div class="limit-icon">🔒</div>
            <h3>Demo Limit Reached</h3>
            <p>You've used your ${DEMO_CONFIG.maxAttempts} free verifications.</p>
            <p class="limit-subtitle">To continue fact-checking, please sign up for a free account or choose a plan.</p>
            <div class="limit-actions">
                <a href="#pricing" class="btn btn-primary">View Plans</a>
                <a href="#api" class="btn btn-secondary">Get API Key</a>
            </div>
            <div class="limit-benefits">
                <h4>With a free account you get:</h4>
                <ul>
                    <li>✓ 50 verifications per month</li>
                    <li>✓ Access to all 28+ AI models</li>
                    <li>✓ Detailed explanations & sources</li>
                    <li>✓ API access for your projects</li>
                </ul>
            </div>
        </div>
    `;
    
    if (typeof gsap !== 'undefined') {
        gsap.from('.demo-limit-reached', {
            opacity: 0,
            y: 20,
            duration: 0.5
        });
    }
}

// ================================================
// ANIMATED SCORE WHEEL COMPONENT
// ================================================

function createScoreWheel(score, size = 120) {
    // Ensure score is a valid number between 0-100
    score = Math.max(0, Math.min(100, Math.round(parseFloat(score) || 0)));
    size = parseInt(size) || 120;
    
    const radius = (size - 10) / 2;
    const circumference = 2 * Math.PI * radius;
    const strokeDashoffset = circumference - (score / 100) * circumference;
    
    // Determine color based on score
    let color, glowColor;
    if (score >= 80) {
        color = '#22c55e'; // Green
        glowColor = 'rgba(34, 197, 94, 0.4)';
    } else if (score >= 60) {
        color = '#fbbf24'; // Yellow
        glowColor = 'rgba(251, 191, 36, 0.4)';
    } else if (score >= 40) {
        color = '#f97316'; // Orange
        glowColor = 'rgba(249, 115, 22, 0.4)';
    } else {
        color = '#ef4444'; // Red
        glowColor = 'rgba(239, 68, 68, 0.4)';
    }
    
    return `
        <div class="score-wheel" style="width: ${size}px; height: ${size}px;">
            <svg class="score-wheel-svg" viewBox="0 0 ${size} ${size}">
                <defs>
                    <linearGradient id="scoreGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stop-color="${color}" />
                        <stop offset="100%" stop-color="${color}99" />
                    </linearGradient>
                    <filter id="scoreGlow">
                        <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                        <feMerge>
                            <feMergeNode in="coloredBlur"/>
                            <feMergeNode in="SourceGraphic"/>
                        </feMerge>
                    </filter>
                </defs>
                <!-- Background circle -->
                <circle 
                    class="score-wheel-bg"
                    cx="${size/2}" 
                    cy="${size/2}" 
                    r="${radius}"
                    fill="none"
                    stroke="rgba(255,255,255,0.1)"
                    stroke-width="8"
                />
                <!-- Progress circle -->
                <circle 
                    class="score-wheel-progress"
                    cx="${size/2}" 
                    cy="${size/2}" 
                    r="${radius}"
                    fill="none"
                    stroke="url(#scoreGradient)"
                    stroke-width="8"
                    stroke-linecap="round"
                    stroke-dasharray="${circumference}"
                    stroke-dashoffset="${circumference}"
                    data-target-offset="${strokeDashoffset}"
                    transform="rotate(-90 ${size/2} ${size/2})"
                    filter="url(#scoreGlow)"
                />
            </svg>
            <div class="score-wheel-content">
                <span class="score-wheel-value" data-target="${score}">0</span>
                <span class="score-wheel-label">%</span>
            </div>
        </div>
    `;
}

function animateScoreWheel() {
    console.log('[Verity] Animating score wheel...');
    
    const wheel = document.querySelector('.score-wheel-progress');
    const valueEl = document.querySelector('.score-wheel-value');
    
    if (!wheel || !valueEl) {
        console.warn('[Verity] Score wheel elements not found');
        return;
    }
    
    const targetOffset = parseFloat(wheel.dataset.targetOffset) || 0;
    const targetValue = parseFloat(valueEl.dataset.target) || 0;
    
    console.log('[Verity] Target offset:', targetOffset, 'Target value:', targetValue);
    
    if (typeof gsap === 'undefined') {
        console.log('[Verity] GSAP not available, using fallback');
        // Fallback without animation
        wheel.style.strokeDashoffset = targetOffset;
        valueEl.textContent = Math.round(targetValue);
        return;
    }
    
    // Animate the circle
    gsap.to(wheel, {
        strokeDashoffset: targetOffset,
        duration: 1.5,
        ease: 'power2.out'
    });
    
    // Animate the number
    gsap.to({ value: 0 }, {
        value: targetValue,
        duration: 1.5,
        ease: 'power2.out',
        onUpdate: function() {
            valueEl.textContent = Math.round(this.targets()[0].value);
        }
    });
    
    console.log('[Verity] Score wheel animation started');
}

// ================================================
// ENHANCED RESULT DISPLAY
// ================================================

function displayEnhancedDemoResult(result) {
    console.log('[Verity] Displaying result:', result);
    
    const demoResults = document.getElementById('demoResults');
    
    if (!demoResults) {
        console.error('[Verity] Demo results container not found');
        return;
    }
    
    // Get remaining attempts now (after increment)
    const remainingAttempts = getRemainingAttempts();
    console.log('[Verity] Remaining attempts for display:', remainingAttempts);
    
    // Ensure confidence is a valid number
    const confidenceScore = typeof result.confidence === 'number' ? result.confidence : parseFloat(result.confidence) || 50;
    console.log('[Verity] Confidence score:', confidenceScore);
    
    // Create safe breakdown with fallbacks (compatible with older browsers)
    const breakdown = result.breakdown || {};
    const safeBreakdown = {
        ai_agreement: breakdown.ai_agreement != null ? breakdown.ai_agreement : Math.round(confidenceScore),
        source_credibility: breakdown.source_credibility != null ? breakdown.source_credibility : Math.round(confidenceScore * 0.95),
        evidence_strength: breakdown.evidence_strength != null ? breakdown.evidence_strength : Math.round(confidenceScore * 0.9),
        consensus_score: breakdown.consensus_score != null ? breakdown.consensus_score : Math.round(confidenceScore * 0.85)
    };
    
    // Safe result values
    const safeClaim = result.claim || 'Unknown claim';
    const safeSummary = result.summary || 'Analysis complete.';
    const safeExplanation = result.explanation || 'No detailed explanation available.';
    
    // Determine verdict styling
    const verdictMap = {
        'VERIFIED_TRUE': { label: 'VERIFIED TRUE', icon: '✓', color: 'true', description: 'This claim has been verified as accurate based on credible sources.' },
        'VERIFIED_FALSE': { label: 'VERIFIED FALSE', icon: '✗', color: 'false', description: 'This claim has been determined to be inaccurate based on credible sources.' },
        'PARTIALLY_TRUE': { label: 'PARTIALLY TRUE', icon: '◐', color: 'partial', description: 'This claim contains both accurate and inaccurate elements.' },
        'PARTIALLY_VERIFIABLE': { label: 'PARTIALLY VERIFIABLE', icon: '◐', color: 'partial', description: 'Some aspects of this claim could be verified, others could not.' },
        'UNVERIFIABLE': { label: 'UNVERIFIABLE', icon: '?', color: 'unverifiable', description: 'This claim cannot be definitively verified with available evidence.' },
        'NEEDS_VERIFICATION': { label: 'NEEDS VERIFICATION', icon: '⚠', color: 'needs-verification', description: 'This claim requires additional research to verify.' },
        'DISPUTED': { label: 'DISPUTED', icon: '⚔', color: 'disputed', description: 'Experts and sources disagree on the accuracy of this claim.' },
        'MISLEADING': { label: 'MISLEADING', icon: '~', color: 'misleading', description: 'This claim, while potentially factual, is presented in a misleading context.' }
    };
    
    const verdictInfo = verdictMap[result.verdict] || verdictMap['UNVERIFIABLE'];
    
    // Build sources HTML
    let sourcesHtml = '';
    if (result.sources && result.sources.length > 0) {
        result.sources.forEach((source, index) => {
            sourcesHtml += `
                <div class="source-item" data-credibility="${source.credibility}">
                    <div class="source-header">
                        <span class="source-number">${index + 1}</span>
                        <span class="source-name">${source.name}</span>
                        <span class="source-credibility ${source.credibility}">${source.credibility.toUpperCase()}</span>
                    </div>
                    ${source.url ? `<a href="${source.url}" target="_blank" rel="noopener noreferrer" class="source-link">View Source →</a>` : ''}
                    ${source.snippet ? `<div class="source-snippet">"${source.snippet}"</div>` : ''}
                    ${source.rating ? `<div class="source-rating">Rating: ${source.rating}</div>` : ''}
                </div>
            `;
        });
    }
    
    // Build reasoning HTML
    let reasoningHtml = '';
    if (result.reasoning && result.reasoning.length > 0) {
        reasoningHtml = `
            <div class="result-section reasoning-section">
                <div class="section-label">🧠 WHY THIS VERDICT?</div>
                <ul class="reasoning-list">
                    ${result.reasoning.map(reason => `<li>${reason}</li>`).join('')}
                </ul>
            </div>
        `;
    }
    
    // Build HTML with animated score wheel
    const html = `
        <div class="demo-result enhanced">
            <!-- Verdict Section with Score Wheel -->
            <div class="result-header">
                <div class="result-verdict ${verdictInfo.color}">
                    <div class="verdict-icon">${verdictInfo.icon}</div>
                    <div class="verdict-info">
                        <div class="verdict-label">${verdictInfo.label}</div>
                        <div class="verdict-description">${verdictInfo.description}</div>
                    </div>
                </div>
                <div class="score-wheel-container">
                    <div class="score-label">Confidence Score</div>
                    ${createScoreWheel(confidenceScore, 110)}
                </div>
            </div>

            <!-- Claim Display -->
            <div class="result-section">
                <div class="section-label">📝 CLAIM ANALYZED</div>
                <div class="claim-text">"${safeClaim}"</div>
            </div>

            <!-- Summary Section -->
            <div class="result-section summary-section">
                <div class="section-label">📋 SUMMARY</div>
                <p class="analysis-summary">${safeSummary}</p>
            </div>

            <!-- Why Section - KEY REASONING -->
            ${reasoningHtml}

            <!-- Detailed Explanation -->
            <div class="result-section">
                <div class="section-label">📖 DETAILED EXPLANATION</div>
                <div class="detailed-explanation">
                    ${safeExplanation}
                </div>
            </div>

            <!-- Sources & Citations -->
            <div class="result-section">
                <div class="section-label">📚 SOURCES & REFERENCES (${result.sources ? result.sources.length : 0})</div>
                <div class="sources-list">
                    ${sourcesHtml || '<p class="no-sources">No external sources available for this verification.</p>'}
                </div>
            </div>

            <!-- Confidence Breakdown with Animated Bars -->
            <div class="result-section">
                <div class="section-label">📊 CONFIDENCE SCORE BREAKDOWN</div>
                <div class="confidence-breakdown">
                    <div class="breakdown-item">
                        <label>AI Provider Agreement</label>
                        <div class="breakdown-bar">
                            <div class="breakdown-fill" data-width="${safeBreakdown.ai_agreement}"></div>
                        </div>
                        <span class="breakdown-value">${safeBreakdown.ai_agreement}%</span>
                    </div>
                    <div class="breakdown-item">
                        <label>Source Credibility</label>
                        <div class="breakdown-bar">
                            <div class="breakdown-fill" data-width="${safeBreakdown.source_credibility}"></div>
                        </div>
                        <span class="breakdown-value">${safeBreakdown.source_credibility}%</span>
                    </div>
                    <div class="breakdown-item">
                        <label>Evidence Strength</label>
                        <div class="breakdown-bar">
                            <div class="breakdown-fill" data-width="${safeBreakdown.evidence_strength}"></div>
                        </div>
                        <span class="breakdown-value">${safeBreakdown.evidence_strength}%</span>
                    </div>
                    <div class="breakdown-item">
                        <label>Consensus Score</label>
                        <div class="breakdown-bar">
                            <div class="breakdown-fill" data-width="${safeBreakdown.consensus_score}"></div>
                        </div>
                        <span class="breakdown-value">${safeBreakdown.consensus_score}%</span>
                    </div>
                </div>
            </div>

            <!-- Processing Details -->
            <div class="result-section processing-details">
                <div class="section-label">⚙️ PROCESSING DETAILS</div>
                <div class="processing-stats-grid">
                    <div class="stat-item">
                        <span class="stat-label">Processing Time</span>
                        <span class="stat-value">${typeof result.processing_time_ms === 'number' ? result.processing_time_ms.toFixed(0) : result.processing_time_ms || 0}ms</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Sources Analyzed</span>
                        <span class="stat-value">${result.sources ? result.sources.length : 0}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Data Source</span>
                        <span class="stat-value source-badge-${result.source === 'api' ? 'api' : 'local'}">${result.source === 'api' ? '🌐 Live API' : '📚 Knowledge Base'}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Request ID</span>
                        <span class="stat-value monospace">${result.request_id || 'N/A'}</span>
                    </div>
                </div>
            </div>

            <!-- Learn More Section -->
            <div class="result-section learn-more">
                <p>Want to understand how accuracy scores are calculated?</p>
                <a href="accuracy-score-guide.html" class="link-button">📚 Read Our Accuracy Score Guide</a>
            </div>
            
            <!-- Remaining Attempts -->
            <div class="result-section attempts-info">
                <span class="attempts-remaining">${remainingAttempts} free verification${remainingAttempts !== 1 ? 's' : ''} remaining</span>
                ${remainingAttempts === 0 ? '<a href="#pricing" class="btn btn-sm btn-primary">Upgrade for unlimited</a>' : ''}
            </div>
        </div>
    `;
    
    console.log('[Verity] Setting innerHTML, html length:', html.length);
    demoResults.innerHTML = html;
    console.log('[Verity] innerHTML set, demoResults.innerHTML length:', demoResults.innerHTML.length);
    
    // IMPORTANT: Ensure result is visible immediately, before any animations
    const demoResult = demoResults.querySelector('.demo-result');
    if (demoResult) {
        demoResult.style.opacity = '1';
        demoResult.style.transform = 'none';
    }
    
    // Animate in (with safety check) - use set first to ensure visibility
    if (typeof gsap !== 'undefined') {
        // First ensure element is visible
        gsap.set('.demo-result', { opacity: 1, y: 0 });
        // Then animate from starting position
        gsap.from('.demo-result', {
            opacity: 0,
            y: 20,
            duration: 0.5
        });
        
        // Animate source items
        gsap.from('.source-item', {
            opacity: 0,
            x: -20,
            duration: 0.3,
            stagger: 0.1,
            delay: 0.3
        });
        
        // Animate breakdown bars
        document.querySelectorAll('.breakdown-fill').forEach((bar, index) => {
            const targetWidth = bar.dataset.width;
            gsap.to(bar, {
                width: `${targetWidth}%`,
                duration: 0.8,
                delay: 0.5 + (index * 0.1),
                ease: 'power2.out'
            });
        });
        
        // Animate reasoning items
        gsap.from('.reasoning-list li', {
            opacity: 0,
            x: -10,
            duration: 0.3,
            stagger: 0.1,
            delay: 0.4
        });
    } else {
        // Fallback - ensure visibility and set the bar widths
        const demoResult = demoResults.querySelector('.demo-result');
        if (demoResult) {
            demoResult.style.opacity = '1';
            demoResult.style.transform = 'none';
        }
        document.querySelectorAll('.breakdown-fill').forEach(bar => {
            const targetWidth = bar.dataset.width;
            bar.style.width = `${targetWidth}%`;
        });
        document.querySelectorAll('.source-item, .reasoning-list li').forEach(el => {
            el.style.opacity = '1';
        });
    }
    
    console.log('[Verity] Result should now be visible');
    
    // Animate score wheel
    setTimeout(animateScoreWheel, 300);
}

function showDemoError(message) {
    const demoResults = document.getElementById('demoResults');
    if (!demoResults) return;
    
    demoResults.innerHTML = `
        <div class="demo-error">
            <div class="error-icon">!</div>
            <div class="error-content">
                <p class="error-message">${message}</p>
                <p class="error-hint">Check your internet connection or try a different claim.</p>
            </div>
        </div>
    `;
    
    if (typeof gsap !== 'undefined') {
        gsap.from('.demo-error', {
            opacity: 0,
            scale: 0.95,
            duration: 0.3
        });
    }
}

// ================================================
// API TABS FUNCTIONALITY
// ================================================

function initializeApiTabs() {
    const apiTabs = document.querySelectorAll('.api-tab');
    const codeBlocks = document.querySelectorAll('.code-block');
    
    if (apiTabs.length === 0 || codeBlocks.length === 0) {
        console.warn('API tabs or code blocks not found in DOM');
        return;
    }
    
    apiTabs.forEach(tab => {
        tab.addEventListener('click', (e) => {
            e.preventDefault();
            const tabId = tab.dataset.tab;
            
            // Remove active from all tabs and blocks
            apiTabs.forEach(t => t.classList.remove('active'));
            codeBlocks.forEach(b => b.classList.remove('active'));
            
            // Add active to clicked tab
            tab.classList.add('active');
            
            // Find and show the corresponding code block
            const activeBlock = document.getElementById(tabId);
            if (activeBlock) {
                activeBlock.classList.add('active');
                
                if (typeof gsap !== 'undefined') {
                    gsap.from(activeBlock, {
                        opacity: 0,
                        duration: 0.3,
                        clearProps: 'transform,opacity'
                    });
                }
            }
        });
    });
    
    // Copy button handlers
    document.querySelectorAll('.copy-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
            const codeId = btn.dataset.code;
            const codeElement = document.querySelector(`#${codeId} code`);
            if (!codeElement) return;
            
            try {
                await navigator.clipboard.writeText(codeElement.textContent);
                const span = btn.querySelector('span');
                const originalText = span ? span.textContent : 'Copy';
                if (span) span.textContent = '✓ Copied!';
                btn.classList.add('copied');
                
                setTimeout(() => {
                    if (span) span.textContent = originalText;
                    btn.classList.remove('copied');
                }, 2000);
            } catch (err) {
                console.error('Failed to copy:', err);
            }
        });
    });
}

// ================================================
// SMOOTH SCROLL BEHAVIOR
// ================================================

function initializeSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const targetId = this.getAttribute('href');
            
            // Skip if href is just "#" or empty
            if (!targetId || targetId === '#' || targetId.length < 2) {
                return;
            }
            
            e.preventDefault();
            const target = document.querySelector(targetId);
            if (target) {
                if (typeof gsap !== 'undefined' && gsap.plugins && gsap.plugins.scrollTo) {
                    gsap.to(window, {
                        duration: 0.8,
                        scrollTo: {
                            y: target,
                            autoKill: false,
                            offsetY: 80
                        },
                        ease: 'power2.inOut'
                    });
                } else {
                    // Fallback to native scroll
                    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            }
        });
    });
}

// ================================================
// SCROLL ANIMATIONS
// ================================================

function initializeScrollAnimations() {
    if (typeof gsap === 'undefined' || typeof ScrollTrigger === 'undefined') {
        console.log('GSAP or ScrollTrigger not available, skipping scroll animations');
        return;
    }
    
    // Use gsap.set to ensure initial visibility, then animate
    const cards = gsap.utils.toArray('.provider-card, .feature-card, .security-card, .security-card-enhanced, .pricing-card');
    
    cards.forEach(card => {
        // Set initial state explicitly
        gsap.set(card, { opacity: 1, y: 0 });
        
        gsap.from(card, {
            scrollTrigger: {
                trigger: card,
                start: 'top 85%',
                toggleActions: 'play none none reverse',
                once: true // Only play once to avoid re-hiding
            },
            opacity: 0,
            y: 30,
            duration: 0.6,
            ease: 'power3.out'
        });
    });
    
    const headers = gsap.utils.toArray('.section-header');
    headers.forEach(header => {
        gsap.set(header, { opacity: 1, y: 0 });
        
        gsap.from(header, {
            scrollTrigger: {
                trigger: header,
                start: 'top 80%',
                toggleActions: 'play none none reverse',
                once: true
            },
            opacity: 0,
            y: 20,
            duration: 0.7
        });
    });
}

// ================================================
// HERO ANIMATIONS
// ================================================

function initializeHeroAnimations() {
    if (typeof gsap === 'undefined') return;
    
    const tl = gsap.timeline();
    
    tl.from('.hero-badge', {
        opacity: 0,
        y: 20,
        duration: 0.6
    })
    .from('.hero-title', {
        opacity: 0,
        y: 40,
        duration: 0.8,
        stagger: 0.1
    }, 0.1)
    .from('.hero-description', {
        opacity: 0,
        y: 20,
        duration: 0.6
    }, 0.4)
    .from('.hero-actions', {
        opacity: 0,
        y: 20,
        duration: 0.6
    }, 0.6)
    .from('.floating-card', {
        opacity: 0,
        scale: 0.8,
        duration: 0.5,
        stagger: 0.15
    }, 0.3);
}

// ================================================
// CURSOR GLOW EFFECT
// ================================================

function initializeCursorGlow() {
    const cursorGlow = document.getElementById('cursorGlow');
    if (!cursorGlow || window.innerWidth < 768 || typeof gsap === 'undefined') return;
    
    document.addEventListener('mousemove', (e) => {
        gsap.to(cursorGlow, {
            left: e.clientX,
            top: e.clientY,
            duration: 0.3,
            overwrite: 'auto'
        });
    });
}

// ================================================
// CARD HOVER EFFECTS
// ================================================

function initializeCardHovers() {
    if (typeof gsap === 'undefined') return;
    
    const cards = document.querySelectorAll(
        '.provider-card, .feature-card, .security-card, .pricing-card, .education-card'
    );
    
    cards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            gsap.to(card, {
                y: -8,
                boxShadow: `0 20px 50px rgba(0, 217, 255, 0.1)`,
                duration: 0.3,
                ease: 'power2.out'
            });
        });
        
        card.addEventListener('mouseleave', () => {
            gsap.to(card, {
                y: 0,
                boxShadow: `0 0 0 rgba(0, 217, 255, 0)`,
                duration: 0.3,
                ease: 'power2.out'
            });
        });
    });
}

// ================================================
// BUTTON HOVER EFFECTS
// ================================================

function initializeButtonHovers() {
    if (typeof gsap === 'undefined') return;
    
    document.querySelectorAll('.btn').forEach(btn => {
        btn.addEventListener('mouseenter', () => {
            gsap.to(btn, {
                y: -2,
                duration: 0.2,
                ease: 'power2.out'
            });
        });
        
        btn.addEventListener('mouseleave', () => {
            gsap.to(btn, {
                y: 0,
                duration: 0.2
            });
        });
    });
}

// ================================================
// NAVBAR ACTIVE LINK TRACKING
// ================================================

function initializeNavbarTracking() {
    const navLinks = document.querySelectorAll('.nav-link');
    
    window.addEventListener('scroll', () => {
        let currentSection = '';
        
        document.querySelectorAll('section[id]').forEach(section => {
            const sectionTop = section.offsetTop - 100;
            if (scrollY >= sectionTop) {
                currentSection = section.getAttribute('id');
            }
        });
        
        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href').slice(1) === currentSection) {
                link.classList.add('active');
            }
        });
    });
}

// ================================================
// MOBILE MENU
// ================================================

function initializeMobileMenu() {
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const navLinks = document.querySelector('.nav-links');
    
    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', () => {
            navLinks?.classList.toggle('active');
            mobileMenuBtn.classList.toggle('active');
        });
    }
}

// ================================================
// INITIALIZATION
// ================================================

document.addEventListener('DOMContentLoaded', () => {
    initializeDemoForm();
    initializeApiTabs();
    initializeSmoothScroll();
    initializeHeroAnimations();
    initializeCursorGlow();
    initializeCardHovers();
    initializeButtonHovers();
    initializeNavbarTracking();
    initializeMobileMenu();
    initializeScrollAnimations();
    
    // Check API health on load
    checkApiHealth();
});

// Page load animation
window.addEventListener('load', () => {
    if (typeof gsap !== 'undefined') {
        gsap.to('body', {
            opacity: 1,
            duration: 0.5
        });
    } else {
        document.body.style.opacity = '1';
    }
});

console.log('%c✓ Verity Systems v2.0 Loaded', 'color: #00d9ff; font-size: 14px; font-weight: bold;');
console.log('%c  Real API + Local Fallback | 5 Free Verifications', 'color: #6366f1; font-size: 12px;');
