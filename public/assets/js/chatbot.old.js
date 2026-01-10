/**
 * Verity AI Chatbot Component
 * A floating chatbot powered by the Verity verification API
 */

(function() {
    'use strict';

    const CHATBOT_CONFIG = {
        apiUrl: 'https://veritysystems-production.up.railway.app',
        botName: 'Verity AI',
        welcomeMessage: 'Hi! I\'m Verity AI. I can help you verify claims, answer questions about our platform, or explain how fact-checking works. What would you like to know?',
        placeholderText: 'Ask me anything or verify a claim...',
        primaryColor: '#22d3ee',
        secondaryColor: '#6366f1'
    };

    // Inject styles
    const styles = `
        .verity-chatbot-toggle {
            position: fixed;
            bottom: 24px;
            right: 24px;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: linear-gradient(135deg, ${CHATBOT_CONFIG.primaryColor}, ${CHATBOT_CONFIG.secondaryColor});
            border: none;
            cursor: pointer;
            box-shadow: 0 8px 32px rgba(34, 211, 238, 0.4);
            z-index: 10000;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .verity-chatbot-toggle:hover {
            transform: scale(1.1);
            box-shadow: 0 12px 40px rgba(34, 211, 238, 0.5);
        }

        .verity-chatbot-toggle svg {
            width: 28px;
            height: 28px;
            color: white;
            transition: transform 0.3s ease;
        }

        .verity-chatbot-toggle.open svg {
            transform: rotate(45deg);
        }

        .verity-chatbot-toggle .notification-dot {
            position: absolute;
            top: 8px;
            right: 8px;
            width: 12px;
            height: 12px;
            background: #10b981;
            border-radius: 50%;
            border: 2px solid #050505;
            animation: pulse-dot 2s infinite;
        }

        @keyframes pulse-dot {
            0%, 100% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.2); opacity: 0.8; }
        }

        .verity-chatbot-window {
            position: fixed;
            bottom: 100px;
            right: 24px;
            width: 380px;
            max-width: calc(100vw - 48px);
            height: 520px;
            max-height: calc(100vh - 140px);
            background: #0a0a0b;
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            box-shadow: 0 25px 80px rgba(0, 0, 0, 0.5), 0 0 1px rgba(255, 255, 255, 0.1);
            z-index: 9999;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            opacity: 0;
            visibility: hidden;
            transform: translateY(20px) scale(0.95);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .verity-chatbot-window.open {
            opacity: 1;
            visibility: visible;
            transform: translateY(0) scale(1);
        }

        .verity-chatbot-header {
            padding: 16px 20px;
            background: linear-gradient(135deg, rgba(34, 211, 238, 0.1), rgba(99, 102, 241, 0.05));
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .verity-chatbot-avatar {
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, ${CHATBOT_CONFIG.primaryColor}, ${CHATBOT_CONFIG.secondaryColor});
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .verity-chatbot-avatar svg {
            width: 22px;
            height: 22px;
            color: white;
        }

        .verity-chatbot-title {
            flex: 1;
        }

        .verity-chatbot-title h4 {
            font-size: 0.95rem;
            font-weight: 600;
            color: white;
            margin: 0;
        }

        .verity-chatbot-title span {
            font-size: 0.75rem;
            color: #10b981;
            display: flex;
            align-items: center;
            gap: 4px;
        }

        .verity-chatbot-title span::before {
            content: '';
            width: 6px;
            height: 6px;
            background: #10b981;
            border-radius: 50%;
        }

        .verity-chatbot-close {
            width: 32px;
            height: 32px;
            border: none;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            color: rgba(255, 255, 255, 0.6);
            transition: all 0.2s ease;
        }

        .verity-chatbot-close:hover {
            background: rgba(255, 255, 255, 0.1);
            color: white;
        }

        .verity-chatbot-messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 16px;
        }

        .verity-chatbot-messages::-webkit-scrollbar {
            width: 4px;
        }

        .verity-chatbot-messages::-webkit-scrollbar-track {
            background: transparent;
        }

        .verity-chatbot-messages::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
        }

        .verity-chat-message {
            display: flex;
            gap: 10px;
            max-width: 85%;
            animation: message-in 0.3s ease;
        }

        @keyframes message-in {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .verity-chat-message.user {
            margin-left: auto;
            flex-direction: row-reverse;
        }

        .verity-chat-message-avatar {
            width: 28px;
            height: 28px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }

        .verity-chat-message.bot .verity-chat-message-avatar {
            background: linear-gradient(135deg, ${CHATBOT_CONFIG.primaryColor}, ${CHATBOT_CONFIG.secondaryColor});
        }

        .verity-chat-message.user .verity-chat-message-avatar {
            background: rgba(255, 255, 255, 0.1);
        }

        .verity-chat-message-avatar svg {
            width: 14px;
            height: 14px;
            color: white;
        }

        .verity-chat-message-content {
            padding: 12px 16px;
            border-radius: 16px;
            font-size: 0.9rem;
            line-height: 1.5;
        }

        .verity-chat-message.bot .verity-chat-message-content {
            background: rgba(255, 255, 255, 0.05);
            color: rgba(255, 255, 255, 0.9);
            border-bottom-left-radius: 4px;
        }

        .verity-chat-message.user .verity-chat-message-content {
            background: linear-gradient(135deg, ${CHATBOT_CONFIG.primaryColor}, ${CHATBOT_CONFIG.secondaryColor});
            color: white;
            border-bottom-right-radius: 4px;
        }

        .verity-chat-verification {
            margin-top: 12px;
            padding: 12px;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 12px;
            border-left: 3px solid;
        }

        .verity-chat-verification.true {
            border-color: #10b981;
        }

        .verity-chat-verification.false {
            border-color: #ef4444;
        }

        .verity-chat-verification.partially_true {
            border-color: #f59e0b;
        }

        .verity-chat-verification-verdict {
            display: flex;
            align-items: center;
            gap: 8px;
            font-weight: 600;
            font-size: 0.85rem;
            margin-bottom: 6px;
        }

        .verity-chat-verification.true .verity-chat-verification-verdict {
            color: #10b981;
        }

        .verity-chat-verification.false .verity-chat-verification-verdict {
            color: #ef4444;
        }

        .verity-chat-verification.partially_true .verity-chat-verification-verdict {
            color: #f59e0b;
        }

        .verity-chat-verification-confidence {
            font-size: 0.75rem;
            color: rgba(255, 255, 255, 0.5);
        }

        .verity-chatbot-input-container {
            padding: 16px 20px;
            border-top: 1px solid rgba(255, 255, 255, 0.08);
            background: rgba(0, 0, 0, 0.3);
        }

        .verity-chatbot-input-wrapper {
            display: flex;
            gap: 10px;
            align-items: center;
        }

        .verity-chatbot-input {
            flex: 1;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 12px 16px;
            color: white;
            font-size: 0.9rem;
            outline: none;
            transition: all 0.2s ease;
        }

        .verity-chatbot-input::placeholder {
            color: rgba(255, 255, 255, 0.4);
        }

        .verity-chatbot-input:focus {
            border-color: ${CHATBOT_CONFIG.primaryColor};
            box-shadow: 0 0 0 3px rgba(34, 211, 238, 0.1);
        }

        .verity-chatbot-send {
            width: 44px;
            height: 44px;
            border: none;
            background: linear-gradient(135deg, ${CHATBOT_CONFIG.primaryColor}, ${CHATBOT_CONFIG.secondaryColor});
            border-radius: 12px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            transition: all 0.2s ease;
        }

        .verity-chatbot-send:hover {
            transform: scale(1.05);
            box-shadow: 0 4px 20px rgba(34, 211, 238, 0.4);
        }

        .verity-chatbot-send:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }

        .verity-chatbot-send svg {
            width: 18px;
            height: 18px;
        }

        .verity-chatbot-quick-actions {
            display: flex;
            gap: 8px;
            margin-top: 12px;
            flex-wrap: wrap;
        }

        .verity-chatbot-quick-action {
            padding: 6px 12px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            color: rgba(255, 255, 255, 0.7);
            font-size: 0.75rem;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .verity-chatbot-quick-action:hover {
            background: rgba(34, 211, 238, 0.1);
            border-color: rgba(34, 211, 238, 0.3);
            color: ${CHATBOT_CONFIG.primaryColor};
        }

        .verity-typing-indicator {
            display: flex;
            gap: 4px;
            padding: 8px 0;
        }

        .verity-typing-indicator span {
            width: 6px;
            height: 6px;
            background: rgba(255, 255, 255, 0.4);
            border-radius: 50%;
            animation: typing-bounce 1.4s ease-in-out infinite;
        }

        .verity-typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
        .verity-typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

        @keyframes typing-bounce {
            0%, 60%, 100% { transform: translateY(0); }
            30% { transform: translateY(-6px); }
        }

        @media (max-width: 480px) {
            .verity-chatbot-window {
                bottom: 80px;
                right: 12px;
                left: 12px;
                width: auto;
                max-width: none;
                height: calc(100vh - 100px);
            }

            .verity-chatbot-toggle {
                bottom: 16px;
                right: 16px;
            }
        }
    `;

    // Create style element
    const styleSheet = document.createElement('style');
    styleSheet.textContent = styles;
    document.head.appendChild(styleSheet);

    // Create chatbot HTML
    const chatbotHTML = `
        <button class="verity-chatbot-toggle" id="verityChatbotToggle" aria-label="Open chat">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
            </svg>
            <span class="notification-dot"></span>
        </button>

        <div class="verity-chatbot-window" id="verityChatbotWindow">
            <div class="verity-chatbot-header">
                <div class="verity-chatbot-avatar">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                        <path d="M9 12l2 2 4-4"/>
                    </svg>
                </div>
                <div class="verity-chatbot-title">
                    <h4>${CHATBOT_CONFIG.botName}</h4>
                    <span>Online</span>
                </div>
                <button class="verity-chatbot-close" id="verityChatbotClose" aria-label="Close chat">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M18 6L6 18M6 6l12 12"/>
                    </svg>
                </button>
            </div>

            <div class="verity-chatbot-messages" id="verityChatbotMessages">
                <!-- Messages will be inserted here -->
            </div>

            <div class="verity-chatbot-input-container">
                <div class="verity-chatbot-input-wrapper">
                    <input type="text" class="verity-chatbot-input" id="verityChatbotInput" placeholder="${CHATBOT_CONFIG.placeholderText}" autocomplete="off">
                    <button class="verity-chatbot-send" id="verityChatbotSend" aria-label="Send message">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/>
                        </svg>
                    </button>
                </div>
                <div class="verity-chatbot-quick-actions">
                    <button class="verity-chatbot-quick-action" data-message="Verify a claim">🔍 Verify claim</button>
                    <button class="verity-chatbot-quick-action" data-message="How does Verity work?">❓ How it works</button>
                    <button class="verity-chatbot-quick-action" data-message="Show me pricing">💰 Pricing</button>
                </div>
            </div>
        </div>
    `;

    // Inject chatbot into page
    const chatbotContainer = document.createElement('div');
    chatbotContainer.innerHTML = chatbotHTML;
    document.body.appendChild(chatbotContainer);

    // Get elements
    const toggle = document.getElementById('verityChatbotToggle');
    const window = document.getElementById('verityChatbotWindow');
    const closeBtn = document.getElementById('verityChatbotClose');
    const messages = document.getElementById('verityChatbotMessages');
    const input = document.getElementById('verityChatbotInput');
    const sendBtn = document.getElementById('verityChatbotSend');
    const quickActions = document.querySelectorAll('.verity-chatbot-quick-action');

    let isOpen = false;
    let isTyping = false;

    // Toggle chatbot
    function toggleChatbot() {
        isOpen = !isOpen;
        window.classList.toggle('open', isOpen);
        toggle.classList.toggle('open', isOpen);
        
        // Remove notification dot after first open
        const dot = toggle.querySelector('.notification-dot');
        if (dot && isOpen) {
            setTimeout(() => dot.remove(), 500);
        }

        if (isOpen && messages.children.length === 0) {
            addBotMessage(CHATBOT_CONFIG.welcomeMessage);
        }

        if (isOpen) {
            input.focus();
        }
    }

    toggle.addEventListener('click', toggleChatbot);
    closeBtn.addEventListener('click', toggleChatbot);

    // Add message
    function addMessage(content, isUser = false, verificationResult = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `verity-chat-message ${isUser ? 'user' : 'bot'}`;

        const avatarIcon = isUser 
            ? '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>'
            : '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="M9 12l2 2 4-4"/></svg>';

        let verificationHTML = '';
        if (verificationResult) {
            const verdictClass = verificationResult.verdict.toLowerCase().replace(' ', '_');
            verificationHTML = `
                <div class="verity-chat-verification ${verdictClass}">
                    <div class="verity-chat-verification-verdict">
                        ${getVerdictIcon(verificationResult.verdict)} ${verificationResult.verdict.toUpperCase()}
                    </div>
                    <div class="verity-chat-verification-confidence">
                        Confidence: ${Math.round(verificationResult.confidence * 100)}%
                    </div>
                </div>
            `;
        }

        messageDiv.innerHTML = `
            <div class="verity-chat-message-avatar">${avatarIcon}</div>
            <div class="verity-chat-message-content">
                ${content}
                ${verificationHTML}
            </div>
        `;

        messages.appendChild(messageDiv);
        messages.scrollTop = messages.scrollHeight;
    }

    function addBotMessage(content, verificationResult = null) {
        addMessage(content, false, verificationResult);
    }

    function addUserMessage(content) {
        addMessage(content, true);
    }

    function getVerdictIcon(verdict) {
        const v = verdict.toLowerCase();
        if (v === 'true') return '✅';
        if (v === 'false') return '❌';
        if (v.includes('partial')) return '⚠️';
        return '❓';
    }

    function showTyping() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'verity-chat-message bot';
        typingDiv.id = 'typing-indicator';
        typingDiv.innerHTML = `
            <div class="verity-chat-message-avatar">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                    <path d="M9 12l2 2 4-4"/>
                </svg>
            </div>
            <div class="verity-chat-message-content">
                <div class="verity-typing-indicator">
                    <span></span><span></span><span></span>
                </div>
            </div>
        `;
        messages.appendChild(typingDiv);
        messages.scrollTop = messages.scrollHeight;
    }

    function hideTyping() {
        const typing = document.getElementById('typing-indicator');
        if (typing) typing.remove();
    }

    // Send message
    async function sendMessage() {
        const text = input.value.trim();
        if (!text || isTyping) return;

        addUserMessage(text);
        input.value = '';
        isTyping = true;
        sendBtn.disabled = true;

        showTyping();

        try {
            // Check if this looks like a verification request
            const isVerification = text.toLowerCase().includes('verify') || 
                                   text.toLowerCase().includes('is it true') ||
                                   text.toLowerCase().includes('fact check') ||
                                   text.endsWith('?') && text.length > 20;

            if (isVerification || text.length > 30) {
                // Extract claim to verify
                let claim = text
                    .replace(/^(verify|fact check|is it true that|check if)\s*/i, '')
                    .replace(/\?$/, '');

                if (claim.length < 10) claim = text;

                // Call verification API
                const response = await fetch(`${CHATBOT_CONFIG.apiUrl}/v3/verify`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ claim })
                });

                const result = await response.json();

                hideTyping();
                addBotMessage(result.explanation || 'I verified this claim for you.', result);
            } else {
                // Handle general questions
                hideTyping();
                const responses = getGeneralResponse(text);
                addBotMessage(responses);
            }
        } catch (error) {
            hideTyping();
            addBotMessage('I apologize, but I encountered an error. Please try again or visit our verification page directly.');
        }

        isTyping = false;
        sendBtn.disabled = false;
    }

    function getGeneralResponse(text) {
        const lower = text.toLowerCase();
        
        if (lower.includes('pricing') || lower.includes('cost') || lower.includes('price')) {
            return 'We offer flexible pricing plans! <br><br>• <strong>Free:</strong> 300 verifications/month<br>• <strong>Starter:</strong> $49/month for 2,000 verifications<br>• <strong>Pro:</strong> $99/month for 5,000 verifications<br>• <strong>Professional:</strong> $199/month for 15,000 verifications<br>• <strong>Enterprise:</strong> Custom pricing<br><br>Visit our <a href="/pricing.html" style="color:#22d3ee">pricing page</a> for details!';
        }
        
        if (lower.includes('how') && (lower.includes('work') || lower.includes('does'))) {
            return 'Verity uses <strong>multiple AI models</strong> to verify claims through multi-source consensus. Here\'s how:<br><br>1. Submit a claim via our API or interface<br>2. We query multiple AI providers simultaneously<br>3. Our Bayesian consensus engine synthesizes results<br>4. You get a verdict, confidence score, and sources<br><br>Try it at our <a href="/verify.html" style="color:#22d3ee">verification page</a>.';
        }
        
        if (lower.includes('api') || lower.includes('integrate')) {
            return 'Our REST API is simple to integrate! Get started in 3 steps:<br><br>1. Get your free API key at <a href="/api-keys.html" style="color:#22d3ee">api-keys</a><br>2. Make a POST request to /v3/verify<br>3. Receive JSON with verdict + confidence<br><br>Check our <a href="/api-docs.html" style="color:#22d3ee">API documentation</a> for full details.';
        }
        
        if (lower.includes('hello') || lower.includes('hi') || lower.includes('hey')) {
            return 'Hello! 👋 How can I help you today? I can verify claims, explain how Verity works, or answer questions about our pricing and features.';
        }

        if (lower.includes('thank')) {
            return 'You\'re welcome! 😊 Is there anything else I can help you with?';
        }

        return 'I can help you with:<br><br>• <strong>Verifying claims</strong> - Just type a statement to fact-check<br>• <strong>Platform questions</strong> - Ask about features, pricing, or API<br>• <strong>Getting started</strong> - I\'ll guide you through the process<br><br>What would you like to know?';
    }

    // Event listeners
    sendBtn.addEventListener('click', sendMessage);
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    quickActions.forEach(btn => {
        btn.addEventListener('click', () => {
            input.value = btn.dataset.message;
            sendMessage();
        });
    });

    // Keyboard shortcut to open/close chatbot
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && isOpen) {
            toggleChatbot();
        }
    });

    console.log('✓ Verity Chatbot loaded');
})();
