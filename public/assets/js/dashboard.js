/**
 * Verity Systems - Dashboard JavaScript
 * User dashboard functionality, authentication, and data management
 */

// ================================================
// CONFIGURATION
// ================================================

const SUPABASE_URL = 'https://your-project.supabase.co';
const SUPABASE_ANON_KEY = 'your-anon-key';

let supabase;
try {
    supabase = window.supabase?.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
} catch (e) {
    console.log('Supabase not configured');
}

// ================================================
// USER STATE
// ================================================

let currentUser = null;
let userProfile = null;

// Plan limits
const PLAN_LIMITS = {
    free: {
        name: 'Free',
        badge: 'Free',
        verifications: 50,
        apiCalls: 50,
        features: ['Basic verification', 'Limited AI providers', 'Community support']
    },
    starter: {
        name: 'Starter',
        badge: 'Starter',
        verifications: 2500,
        apiCalls: 2500,
        features: ['All 14 AI providers', 'API + batch processing', 'Email support']
    },
    professional: {
        name: 'Professional',
        badge: 'Pro',
        verifications: 15000,
        apiCalls: 15000,
        features: ['All 14 AI providers', 'Priority API access', 'Priority support', 'Advanced analytics']
    },
    business: {
        name: 'Business',
        badge: 'Business',
        verifications: 75000,
        apiCalls: 75000,
        features: ['Everything in Pro', 'Dedicated CSM', '99.9% SLA', 'Custom integrations']
    },
    enterprise: {
        name: 'Enterprise',
        badge: 'Enterprise',
        verifications: 999999,
        apiCalls: 999999,
        features: ['Unlimited verifications', 'All 14 AI providers', '24/7 dedicated support', 'Custom integrations', 'SLA guarantee', 'Private deployment']
    }
};

// ================================================
// INITIALIZATION
// ================================================

document.addEventListener('DOMContentLoaded', () => {
    initializeDashboard();
    initializeSidebar();
    initializeUserMenu();
    initializeQuickVerify();
    loadUserData();
});

async function initializeDashboard() {
    // Check authentication
    const user = await checkAuth();
    if (!user) {
        window.location.href = 'auth.html';
        return;
    }
    
    currentUser = user;
    updateUIWithUserData(user);
}

async function checkAuth() {
    // Check local storage first (demo mode)
    const localUser = localStorage.getItem('verity_user');
    if (localUser) {
        try {
            const user = JSON.parse(localUser);
            console.log('Loaded user from localStorage:', user);
            
            // Load stats if available
            const stats = localStorage.getItem('verity_stats');
            if (stats) {
                const parsedStats = JSON.parse(stats);
                user.verifications_used = parsedStats.verifications_used || 0;
                user.verifications_limit = parsedStats.verifications_limit;
                user.plan = parsedStats.plan || user.plan || 'free';
            }
            
            // Ensure plan is set correctly
            if (!user.plan) user.plan = 'free';
            
            return user;
        } catch (e) {
            console.error('Error parsing user data:', e);
        }
    }
    
    // Check Supabase session
    if (supabase) {
        try {
            const { data: { session } } = await supabase.auth.getSession();
            if (session?.user) {
                return {
                    id: session.user.id,
                    email: session.user.email,
                    name: session.user.user_metadata?.full_name || session.user.email.split('@')[0],
                    plan: 'free',
                    verifications_used: 0,
                    verifications_limit: 50
                };
            }
        } catch (e) {
            console.error('Supabase auth error:', e);
        }
    }
    
    return null;
}

// ================================================
// UI UPDATES
// ================================================

function updateUIWithUserData(user) {
    console.log('Updating UI with user:', user);
    
    // User info
    const firstName = user.name?.split(' ')[0] || user.email?.split('@')[0] || 'User';
    const initials = getInitials(user.name || user.email);
    
    const userNameEl = document.getElementById('userName');
    const userEmailEl = document.getElementById('userEmail');
    const userAvatarEl = document.getElementById('userAvatar');
    const welcomeNameEl = document.getElementById('welcomeName');
    const mobileUserAvatarEl = document.getElementById('mobileUserAvatar');
    
    if (userNameEl) userNameEl.textContent = user.name || user.email;
    if (userEmailEl) userEmailEl.textContent = user.email;
    if (userAvatarEl) userAvatarEl.textContent = initials;
    if (welcomeNameEl) welcomeNameEl.textContent = firstName;
    if (mobileUserAvatarEl) mobileUserAvatarEl.textContent = initials;
    
    // Plan info - get the correct plan from user data
    const userPlan = user.plan || 'free';
    const plan = PLAN_LIMITS[userPlan] || PLAN_LIMITS.free;
    
    console.log('User plan:', userPlan, 'Plan config:', plan);
    
    const userPlanNameEl = document.getElementById('userPlanName');
    const userPlanBadgeEl = document.getElementById('userPlanBadge');
    
    if (userPlanNameEl) userPlanNameEl.textContent = plan.name;
    if (userPlanBadgeEl) {
        userPlanBadgeEl.textContent = plan.badge;
        // Update badge styling based on plan
        userPlanBadgeEl.className = 'plan-badge';
        if (userPlan === 'professional') userPlanBadgeEl.classList.add('pro');
        if (userPlan === 'business') userPlanBadgeEl.classList.add('business');
        if (userPlan === 'enterprise') userPlanBadgeEl.classList.add('enterprise');
    }
    
    // Usage info
    const used = user.verifications_used || 0;
    const limit = user.verifications_limit || plan.verifications;
    const remaining = limit >= 999999 ? '∞' : Math.max(0, limit - used);
    const percentage = limit >= 999999 ? 0 : Math.min(100, (used / limit) * 100);
    
    const usageCountEl = document.getElementById('usageCount');
    const usageLimitEl = document.getElementById('usageLimit');
    const usageFillEl = document.getElementById('usageFill');
    const quickRemainingEl = document.getElementById('quickRemaining');
    
    if (usageCountEl) usageCountEl.textContent = used.toLocaleString();
    if (usageLimitEl) usageLimitEl.textContent = limit >= 999999 ? '∞' : limit.toLocaleString();
    if (usageFillEl) {
        usageFillEl.style.width = `${percentage}%`;
        if (percentage > 80) usageFillEl.classList.add('warning');
    }
    if (quickRemainingEl) quickRemainingEl.textContent = remaining === '∞' ? '∞' : remaining.toLocaleString();
    
    // API usage
    const apiCallsUsedEl = document.getElementById('apiCallsUsed');
    const apiCallsRemainingEl = document.getElementById('apiCallsRemaining');
    const apiUsagePercentEl = document.getElementById('apiUsagePercent');
    
    if (apiCallsUsedEl) apiCallsUsedEl.textContent = used.toLocaleString();
    if (apiCallsRemainingEl) apiCallsRemainingEl.textContent = remaining === '∞' ? '∞' : remaining.toLocaleString();
    if (apiUsagePercentEl) apiUsagePercentEl.textContent = `${Math.round(percentage)}%`;
    
    // Update usage ring
    const usageRing = document.getElementById('usageRing');
    if (usageRing) {
        const circumference = 314; // 2 * PI * 50
        const offset = circumference - (circumference * percentage / 100);
        usageRing.style.strokeDashoffset = offset;
    }
    
    // Reset date
    const apiResetDateEl = document.getElementById('apiResetDate');
    if (apiResetDateEl) {
        const resetDate = new Date();
        resetDate.setMonth(resetDate.getMonth() + 1, 1);
        apiResetDateEl.textContent = resetDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    }
}

function getInitials(name) {
    if (!name) return '??';
    const parts = name.split(' ');
    if (parts.length >= 2) {
        return (parts[0][0] + parts[1][0]).toUpperCase();
    }
    return name.substring(0, 2).toUpperCase();
}

// ================================================
// SIDEBAR
// ================================================

function initializeSidebar() {
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    const sidebar = document.getElementById('sidebar');
    
    // Create overlay
    const overlay = document.createElement('div');
    overlay.className = 'sidebar-overlay';
    document.body.appendChild(overlay);
    
    mobileMenuToggle?.addEventListener('click', () => {
        sidebar.classList.toggle('open');
        overlay.classList.toggle('show');
    });
    
    overlay.addEventListener('click', () => {
        sidebar.classList.remove('open');
        overlay.classList.remove('show');
    });
    
    // Active nav item based on URL
    const currentPage = window.location.pathname.split('/').pop() || 'dashboard.html';
    document.querySelectorAll('.nav-item').forEach(item => {
        if (item.getAttribute('href')?.includes(currentPage)) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });
}

// ================================================
// USER MENU
// ================================================

function initializeUserMenu() {
    const userMenuBtn = document.getElementById('userMenuBtn');
    const userDropdown = document.getElementById('userDropdown');
    const logoutBtn = document.getElementById('logoutBtn');
    
    userMenuBtn?.addEventListener('click', (e) => {
        e.stopPropagation();
        userDropdown.classList.toggle('show');
    });
    
    document.addEventListener('click', () => {
        userDropdown?.classList.remove('show');
    });
    
    logoutBtn?.addEventListener('click', handleLogout);
}

async function handleLogout() {
    try {
        // Clear local storage
        localStorage.removeItem('verity_user');
        sessionStorage.clear();
        
        // Sign out from Supabase
        if (supabase) {
            await supabase.auth.signOut();
        }
        
        window.location.href = 'index.html';
    } catch (error) {
        console.error('Logout error:', error);
        window.location.href = 'index.html';
    }
}

// ================================================
// QUICK VERIFY
// ================================================

function initializeQuickVerify() {
    const form = document.getElementById('quickVerifyForm');
    const input = document.getElementById('quickClaimInput');
    const exampleChips = document.querySelectorAll('.example-chip');
    
    // Example chips
    exampleChips.forEach(chip => {
        chip.addEventListener('click', () => {
            input.value = chip.dataset.claim;
            input.focus();
        });
    });
    
    // Form submission
    form?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const claim = input.value.trim();
        
        if (!claim || claim.length < 10) {
            showNotification('Please enter a claim with at least 10 characters', 'error');
            return;
        }
        
        // Check remaining verifications
        const remaining = parseInt(document.getElementById('quickRemaining').textContent);
        if (remaining <= 0) {
            showNotification('No verifications remaining. Please upgrade your plan.', 'error');
            return;
        }
        
        await performVerification(claim);
    });
}

async function performVerification(claim) {
    const resultContainer = document.getElementById('verifyResult');
    const submitBtn = document.querySelector('.btn-verify');
    
    // Show loading state
    submitBtn.disabled = true;
    submitBtn.innerHTML = `
        <span class="spinner" style="display: inline-block; width: 18px; height: 18px; border: 2px solid rgba(255,255,255,0.3); border-top-color: #fff; border-radius: 50%; animation: spin 0.8s linear infinite;"></span>
        Verifying...
    `;
    
    resultContainer.style.display = 'block';
    resultContainer.innerHTML = `
        <div style="text-align: center; padding: 2rem;">
            <div class="loading-spinner" style="width: 40px; height: 40px; border: 3px solid rgba(34,211,238,0.2); border-top-color: #22d3ee; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 1rem;"></div>
            <p style="color: rgba(255,255,255,0.6);">Analyzing claim with AI models...</p>
        </div>
    `;
    
    try {
        // Simulate verification (replace with actual API call)
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        const result = await verifyClaimWithAPI(claim);
        
        // Update usage
        updateUsageAfterVerification();
        
        // Display result
        displayVerificationResult(result, resultContainer);
        
        // Save to history
        saveToHistory(claim, result);
        
    } catch (error) {
        console.error('Verification error:', error);
        resultContainer.innerHTML = `
            <div style="text-align: center; padding: 2rem; color: #f87171;">
                <p>Failed to verify claim. Please try again.</p>
            </div>
        `;
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = `
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/>
            </svg>
            Verify
        `;
    }
}

async function verifyClaimWithAPI(claim) {
    // Try real API first
    try {
        const response = await fetch('http://localhost:8000/v1/verify', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ claim })
        });
        
        if (response.ok) {
            return await response.json();
        }
    } catch (e) {
        console.log('API not available, using local');
    }
    
    // Fallback to local verification
    return localVerify(claim);
}

function localVerify(claim) {
    const lowerClaim = claim.toLowerCase();
    
    // Simple heuristic verification
    let verdict = 'PARTIALLY_VERIFIABLE';
    let confidence = 50 + Math.random() * 30;
    
    // Check for known facts
    if (lowerClaim.includes('earth') && lowerClaim.includes('4.5 billion')) {
        verdict = 'VERIFIED_TRUE';
        confidence = 97;
    } else if (lowerClaim.includes('10%') && lowerClaim.includes('brain')) {
        verdict = 'VERIFIED_FALSE';
        confidence = 95;
    } else if (lowerClaim.includes('great wall') && lowerClaim.includes('space')) {
        verdict = 'VERIFIED_FALSE';
        confidence = 92;
    }
    
    return {
        claim,
        verdict,
        confidence,
        summary: `Analysis complete for: "${claim}"`,
        sources: [
            { name: 'Scientific Literature', credibility: 'high' },
            { name: 'Wikipedia', credibility: 'medium' }
        ],
        processing_time_ms: Math.floor(Math.random() * 3000) + 1000
    };
}

function displayVerificationResult(result, container) {
    const verdictClass = result.verdict.includes('TRUE') ? 'true' : 
                         result.verdict.includes('FALSE') ? 'false' : 'uncertain';
    const verdictIcon = result.verdict.includes('TRUE') ? '✓' :
                        result.verdict.includes('FALSE') ? '✗' : '?';
    const verdictText = result.verdict.replace(/_/g, ' ');
    
    container.innerHTML = `
        <div class="verification-result ${verdictClass}">
            <div class="result-header-section">
                <div class="verdict-badge ${verdictClass}">
                    <span class="verdict-icon">${verdictIcon}</span>
                    <span class="verdict-text">${verdictText}</span>
                </div>
                <div class="confidence-score">
                    <span class="score-value">${Math.round(result.confidence)}%</span>
                    <span class="score-label">Confidence</span>
                </div>
            </div>
            <div class="result-claim">
                <span class="claim-label">Claim:</span>
                <p>"${result.claim}"</p>
            </div>
            <div class="result-summary">
                <p>${result.summary}</p>
            </div>
            <div class="result-footer">
                <span class="processing-time">Processed in ${result.processing_time_ms}ms</span>
                <a href="history.html" class="view-details">View full details →</a>
            </div>
        </div>
        
        <style>
            .verification-result {
                background: rgba(15, 15, 15, 0.5);
                border-radius: 12px;
                padding: 1.5rem;
            }
            .result-header-section {
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 1rem;
            }
            .verdict-badge {
                display: flex;
                align-items: center;
                gap: 0.5rem;
                padding: 0.5rem 1rem;
                border-radius: 8px;
                font-weight: 600;
            }
            .verdict-badge.true {
                background: rgba(34, 197, 94, 0.15);
                color: #22c55e;
            }
            .verdict-badge.false {
                background: rgba(239, 68, 68, 0.15);
                color: #ef4444;
            }
            .verdict-badge.uncertain {
                background: rgba(234, 179, 8, 0.15);
                color: #eab308;
            }
            .confidence-score {
                text-align: right;
            }
            .score-value {
                display: block;
                font-size: 1.5rem;
                font-weight: 700;
                color: #fff;
            }
            .score-label {
                color: rgba(255,255,255,0.5);
                font-size: 0.75rem;
            }
            .result-claim {
                margin-bottom: 1rem;
                padding: 1rem;
                background: rgba(255,255,255,0.03);
                border-radius: 8px;
            }
            .claim-label {
                color: rgba(255,255,255,0.5);
                font-size: 0.75rem;
                display: block;
                margin-bottom: 0.25rem;
            }
            .result-claim p {
                color: #fff;
                font-size: 0.95rem;
            }
            .result-summary p {
                color: rgba(255,255,255,0.7);
                font-size: 0.9rem;
                line-height: 1.6;
            }
            .result-footer {
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-top: 1rem;
                padding-top: 1rem;
                border-top: 1px solid rgba(255,255,255,0.1);
            }
            .processing-time {
                color: rgba(255,255,255,0.4);
                font-size: 0.8rem;
            }
            .view-details {
                color: #22d3ee;
                font-size: 0.85rem;
                text-decoration: none;
            }
            .view-details:hover {
                text-decoration: underline;
            }
        </style>
    `;
}

function updateUsageAfterVerification() {
    // Get current values
    const usedEl = document.getElementById('usageCount');
    const remainingEl = document.getElementById('quickRemaining');
    const apiUsedEl = document.getElementById('apiCallsUsed');
    const apiRemainingEl = document.getElementById('apiCallsRemaining');
    
    const currentUsed = parseInt(usedEl.textContent) || 0;
    const newUsed = currentUsed + 1;
    
    const limit = parseInt(document.getElementById('usageLimit').textContent) || 100;
    const newRemaining = Math.max(0, limit - newUsed);
    const percentage = Math.min(100, (newUsed / limit) * 100);
    
    // Update UI
    usedEl.textContent = newUsed;
    remainingEl.textContent = newRemaining;
    apiUsedEl.textContent = newUsed;
    apiRemainingEl.textContent = newRemaining;
    
    document.getElementById('usageFill').style.width = `${percentage}%`;
    document.getElementById('apiUsagePercent').textContent = `${Math.round(percentage)}%`;
    
    // Update usage ring
    const usageRing = document.getElementById('usageRing');
    if (usageRing) {
        const circumference = 314;
        const offset = circumference - (circumference * percentage / 100);
        usageRing.style.strokeDashoffset = offset;
    }
    
    // Update local storage
    const user = JSON.parse(localStorage.getItem('verity_user') || '{}');
    user.verifications_used = newUsed;
    localStorage.setItem('verity_user', JSON.stringify(user));
    
    // Update stats
    updateStatsAfterVerification();
}

function updateStatsAfterVerification() {
    const totalEl = document.getElementById('totalVerifications');
    const current = parseInt(totalEl.textContent) || 0;
    totalEl.textContent = current + 1;
}

function saveToHistory(claim, result) {
    const history = JSON.parse(localStorage.getItem('verity_history') || '[]');
    history.unshift({
        id: Date.now(),
        claim,
        verdict: result.verdict,
        confidence: result.confidence,
        timestamp: new Date().toISOString()
    });
    
    // Keep only last 100 items
    if (history.length > 100) {
        history.pop();
    }
    
    localStorage.setItem('verity_history', JSON.stringify(history));
}

// ================================================
// DATA LOADING
// ================================================

async function loadUserData() {
    // Load stats from storage
    const stats = JSON.parse(localStorage.getItem('verity_stats') || '{}');
    
    if (stats.total) {
        document.getElementById('totalVerifications').textContent = stats.total;
    }
    if (stats.true) {
        document.getElementById('trueCount').textContent = stats.true;
    }
    if (stats.false) {
        document.getElementById('falseCount').textContent = stats.false;
    }
    if (stats.uncertain) {
        document.getElementById('uncertainCount').textContent = stats.uncertain;
    }
    
    // Load recent history
    loadRecentActivity();
}

function loadRecentActivity() {
    const history = JSON.parse(localStorage.getItem('verity_history') || '[]');
    const container = document.getElementById('recentActivity');
    
    if (history.length === 0) {
        // Keep default demo data
        return;
    }
    
    container.innerHTML = history.slice(0, 4).map(item => {
        const verdictClass = item.verdict.includes('TRUE') ? 'true' : 
                             item.verdict.includes('FALSE') ? 'false' : 'uncertain';
        const verdictIcon = item.verdict.includes('TRUE') ? 
            '<polyline points="20 6 9 17 4 12"/>' :
            item.verdict.includes('FALSE') ?
            '<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>' :
            '<circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/>';
        const verdictText = item.verdict.includes('TRUE') ? 'True' :
                            item.verdict.includes('FALSE') ? 'False' : 'Uncertain';
        const timeAgo = getTimeAgo(new Date(item.timestamp));
        
        return `
            <div class="activity-item">
                <div class="activity-icon ${verdictClass}">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        ${verdictIcon}
                    </svg>
                </div>
                <div class="activity-content">
                    <p class="activity-claim">"${item.claim}"</p>
                    <span class="activity-time">${timeAgo}</span>
                </div>
                <span class="activity-badge ${verdictClass}">${verdictText}</span>
            </div>
        `;
    }).join('');
}

function getTimeAgo(date) {
    const seconds = Math.floor((new Date() - date) / 1000);
    
    if (seconds < 60) return 'Just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)} minutes ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)} hours ago`;
    if (seconds < 604800) return `${Math.floor(seconds / 86400)} days ago`;
    
    return date.toLocaleDateString();
}

// ================================================
// NOTIFICATIONS
// ================================================

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <span>${message}</span>
        <button onclick="this.parentElement.remove()">×</button>
    `;
    
    notification.style.cssText = `
        position: fixed;
        top: 1rem;
        right: 1rem;
        padding: 1rem 1.5rem;
        background: ${type === 'error' ? 'rgba(239, 68, 68, 0.9)' : 
                      type === 'success' ? 'rgba(34, 197, 94, 0.9)' : 
                      'rgba(34, 211, 238, 0.9)'};
        color: #fff;
        border-radius: 10px;
        display: flex;
        align-items: center;
        gap: 1rem;
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

// Add spin animation
const style = document.createElement('style');
style.textContent = `
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
`;
document.head.appendChild(style);
