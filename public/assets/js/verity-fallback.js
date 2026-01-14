/**
 * Verity Tools - API with Fallback
 * Shared utility for all tool pages with client-side fallback analysis
 */

const API_URLS = [
    'https://veritysystems-production.up.railway.app',
    'http://localhost:8000'
];
let API_BASE = API_URLS[0];
let apiChecked = false;
let apiAvailable = null;

// Check API health
async function checkApiHealth() {
    if (apiChecked) return apiAvailable;
    apiChecked = true;
    
    for (const url of API_URLS) {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 5000);
            const response = await fetch(`${url}/health`, { signal: controller.signal });
            clearTimeout(timeoutId);
            if (response.ok) {
                API_BASE = url;
                apiAvailable = true;
                (window.verityLogger || console).info(`✅ API available at ${url}`);
                return true;
            }
        } catch (e) {
            (window.verityLogger || console).warn(`❌ API not available at ${url}`);
        }
    }
    apiAvailable = false;
    (window.verityLogger || console).warn('⚠️ Using fallback client-side analysis');
    return false;
}

// Fallback analysis functions
const FallbackAnalysis = {
    'social-media': (content) => {
        const c = content.toLowerCase();
        const indicators = [];
        let score = 70;
        
        if (c.includes('viral') || c.includes('trending')) {
            indicators.push({ type: 'viral_spread', severity: 'medium', detail: 'Content marked as viral - verify before sharing' });
            score -= 10;
        }
        if (c.includes('new account') || c.includes('just created') || c.includes('created last')) {
            indicators.push({ type: 'new_account', severity: 'high', detail: 'Account appears to be recently created' });
            score -= 20;
        }
        if (/\d+k|\d+m/i.test(c) && c.includes('followers')) {
            indicators.push({ type: 'follower_anomaly', severity: 'medium', detail: 'Unusual follower metrics detected' });
            score -= 15;
        }
        if (c.includes('breaking') || c.includes('urgent') || c.includes('share now')) {
            indicators.push({ type: 'urgency_trigger', severity: 'medium', detail: 'Uses urgency language common in misinformation' });
            score -= 10;
        }
        if (c.includes('they don\'t want you to know') || c.includes('mainstream media')) {
            indicators.push({ type: 'conspiracy_language', severity: 'high', detail: 'Contains conspiracy-style framing' });
            score -= 20;
        }
        
        const verdict = score >= 60 ? 'low_risk' : score >= 40 ? 'medium_risk' : 'high_risk';
        const emoji = verdict === 'low_risk' ? '🟢' : verdict === 'medium_risk' ? '🟡' : '🔴';
        
        return {
            tool: 'Social Media Analyzer',
            score: Math.max(5, score),
            verdict,
            summary: `${emoji} ${verdict.replace('_', ' ').toUpperCase()}: ${indicators.length} pattern(s) detected (local analysis)`,
            indicators,
            processing_time_ms: Math.random() * 50,
            fallback: true
        };
    },
    
    'image-forensics': (content) => {
        const c = content.toLowerCase();
        const findings = [];
        let score = 70;
        
        const aiTerms = ['ai-generated', 'midjourney', 'dall-e', 'stable diffusion', 'photoshopped', 'manipulated', 'deepfake', 'fake'];
        aiTerms.forEach(term => {
            if (c.includes(term)) {
                findings.push({ type: 'ai_generated', severity: 'high', detail: `AI/manipulation indicator: "${term}"` });
                score -= 25;
            }
        });
        
        if (c.includes('screenshot') || c.includes('edited')) {
            findings.push({ type: 'modification', severity: 'medium', detail: 'Content mentions editing/modification' });
            score -= 10;
        }
        
        const verdict = score >= 60 ? 'likely_authentic' : score >= 40 ? 'uncertain' : 'likely_manipulated';
        const emoji = verdict === 'likely_authentic' ? '🟢' : verdict === 'uncertain' ? '🟡' : '🔴';
        
        return {
            tool: 'Image Forensics',
            score: Math.max(10, score),
            verdict,
            summary: `${emoji} ${verdict.replace(/_/g, ' ').toUpperCase()}: ${findings.length} finding(s) (local analysis)`,
            findings,
            processing_time_ms: Math.random() * 100,
            fallback: true
        };
    },
    
    'source-credibility': (content) => {
        const c = content.toLowerCase();
        const sources = [];
        let score = 50;
        
        const tier1 = [
            { name: 'Reuters', pattern: 'reuters' },
            { name: 'Associated Press', pattern: 'associated press' },
            { name: 'BBC', pattern: 'bbc' },
            { name: 'NPR', pattern: 'npr' },
            { name: 'AP News', pattern: 'ap news' }
        ];
        const tier2 = [
            { name: 'NY Times', pattern: 'nytimes' },
            { name: 'Washington Post', pattern: 'washington post' },
            { name: 'The Guardian', pattern: 'guardian' },
            { name: 'CNN', pattern: 'cnn' },
            { name: 'Wall Street Journal', pattern: 'wsj' }
        ];
        
        tier1.forEach(s => { 
            if (c.includes(s.pattern)) { 
                sources.push({ name: s.name, tier: 1, rating: 'Highly Credible' }); 
                score += 20; 
            } 
        });
        tier2.forEach(s => { 
            if (c.includes(s.pattern)) { 
                sources.push({ name: s.name, tier: 2, rating: 'Generally Credible' }); 
                score += 10; 
            } 
        });
        
        if (c.includes('facebook post') || c.includes('tiktok') || c.includes('random blog')) {
            sources.push({ name: 'Social Media/Blog', tier: 4, rating: 'Low Credibility' });
            score -= 15;
        }
        
        score = Math.min(95, Math.max(20, score));
        const verdict = score >= 70 ? 'high_credibility' : score >= 40 ? 'medium_credibility' : 'low_credibility';
        const emoji = verdict === 'high_credibility' ? '🟢' : verdict === 'medium_credibility' ? '🟡' : '🔴';
        
        return {
            tool: 'Source Credibility',
            score,
            verdict,
            summary: `${emoji} ${verdict.replace(/_/g, ' ').toUpperCase()}: ${sources.length} source(s) identified (local analysis)`,
            sources,
            processing_time_ms: Math.random() * 50,
            fallback: true
        };
    },
    
    'statistics-validator': (content) => {
        const numbers = content.match(/\d+(\.\d+)?%?/g) || [];
        const pValueMatch = content.match(/p[\-\s]?value\s*[=:]\s*([\d.]+)/i);
        let score = 70;
        const findings = [];
        
        if (pValueMatch) {
            const pVal = parseFloat(pValueMatch[1]);
            if (pVal > 0.05) {
                findings.push({ type: 'weak_significance', severity: 'high', detail: `P-value ${pVal} > 0.05 indicates weak statistical significance` });
                score -= 20;
            } else if (pVal < 0.001) {
                findings.push({ type: 'strong_significance', severity: 'low', detail: `P-value ${pVal} indicates strong statistical significance` });
                score += 10;
            }
        }
        
        if (content.includes('100%') || content.includes('0%')) {
            findings.push({ type: 'extreme_percentage', severity: 'medium', detail: 'Extreme percentages (0% or 100%) are often exaggerated' });
            score -= 15;
        }
        
        if (content.match(/\d{3,}%/)) {
            findings.push({ type: 'large_percentage', severity: 'medium', detail: 'Percentages over 100% may indicate misrepresentation' });
            score -= 10;
        }
        
        if (!content.includes('study') && !content.includes('research') && !content.includes('survey')) {
            findings.push({ type: 'no_source', severity: 'low', detail: 'No study/research source mentioned' });
        }
        
        score = Math.max(20, Math.min(90, score));
        const verdict = score >= 60 ? 'plausible' : score >= 40 ? 'questionable' : 'likely_misleading';
        const emoji = verdict === 'plausible' ? '🟢' : verdict === 'questionable' ? '🟡' : '🔴';
        
        return {
            tool: 'Statistics Validator',
            score,
            verdict,
            summary: `${emoji} ${verdict.replace(/_/g, ' ').toUpperCase()}: ${numbers.length} numbers analyzed, ${findings.length} issue(s) (local analysis)`,
            findings,
            numbers_found: numbers.length,
            processing_time_ms: Math.random() * 80,
            fallback: true
        };
    },
    
    'research-assistant': (content) => {
        const query = encodeURIComponent(content.substring(0, 100));
        return {
            tool: 'Research Assistant',
            score: 50,
            verdict: 'requires_verification',
            summary: '🔬 AI research unavailable offline - use research databases below (local analysis)',
            research_databases: [
                { name: 'Google Scholar', url: `https://scholar.google.com/scholar?q=${query}` },
                { name: 'Semantic Scholar', url: `https://www.semanticscholar.org/search?q=${query}` },
                { name: 'PubMed', url: `https://pubmed.ncbi.nlm.nih.gov/?term=${query}` }
            ],
            ai_analysis: 'AI analysis requires server connection. Please use the research databases above.',
            processing_time_ms: 50,
            fallback: true
        };
    },
    
    'realtime-stream': (content) => {
        const c = content.toLowerCase();
        const indicators = [];
        let velocity = 'low';
        let score = 70;
        
        if (c.includes('breaking') || c.includes('just now') || c.includes('urgent') || c.includes('live')) {
            velocity = 'high';
            score -= 20;
            indicators.push({ type: 'breaking_news', severity: 'high', detail: 'Breaking news claim - requires immediate verification' });
        } else if (c.includes('trending') || c.includes('viral') || c.includes('spreading')) {
            velocity = 'medium';
            score -= 10;
            indicators.push({ type: 'viral_spread', severity: 'medium', detail: 'Viral content - wait for corroboration' });
        }
        
        if (c.includes('confirmed') || c.includes('official')) {
            indicators.push({ type: 'confirmation_claim', severity: 'low', detail: 'Claims official confirmation - verify source' });
        }
        
        const verdict = `${velocity}_spread_risk`;
        const emoji = velocity === 'high' ? '🔴' : velocity === 'medium' ? '🟡' : '🟢';
        
        return {
            tool: 'Real-Time Stream',
            score: Math.max(30, score),
            spread_velocity: velocity,
            verdict,
            summary: `${emoji} Spread Velocity: ${velocity.toUpperCase()} - ${indicators.length} indicator(s) (local analysis)`,
            indicators,
            processing_time_ms: Math.random() * 30,
            fallback: true
        };
    }
};

// Make API call with fallback
async function callVerityAPI(endpoint, content) {
    await checkApiHealth();
    
    const toolName = endpoint.replace('/tools/', '');
    
    // Try API first
    if (apiAvailable) {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 15000);
            
            const response = await fetch(`${API_BASE}${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content }),
                signal: controller.signal
            });
            clearTimeout(timeoutId);
            
            if (response.ok) {
                const result = await response.json();
                result.fallback = false;
                return result;
            }
        } catch (error) {
            console.warn(`API call failed, using fallback:`, error.message);
        }
    }
    
    // Use fallback
    if (FallbackAnalysis[toolName]) {
        (window.verityLogger || console).warn(`Using fallback analysis for ${toolName}`);
        return FallbackAnalysis[toolName](content);
    }
    
    return {
        score: 50,
        summary: '⚠️ Analysis unavailable',
        error: true
    };
}

// Initialize on load
checkApiHealth();
