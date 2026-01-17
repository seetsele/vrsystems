/**
 * Verity AI Chatbot Component - Desktop Edition
 * A floating chatbot powered by the Verity verification API
 * Optimized for Electron desktop application
 */

(function() {
    'use strict';

    const CHATBOT_CONFIG = {
        apiUrl: 'https://veritysystems-production.up.railway.app',
        botName: 'Verity AI',
        welcomeMessage: 'Hi! I\'m Verity AI, your desktop verification assistant. I can help you verify claims, answer questions about our platform, or explain how fact-checking works. What would you like to know?',
        placeholderText: 'Ask me anything or verify a claim...',
        primaryColor: '#f59e0b',
        secondaryColor: '#fbbf24'
    };

    // Logger: use preload logger when available
    let log = console;
    try { log = window.verity?.logger || console; } catch (e) { log = console; }

    // Inject styles
    const styles = `
        .verity-chatbot-toggle {
            position: fixed;
            bottom: 24px;
            right: 24px;
            width: 56px;
            height: 56px;
            border-radius: 50%;
            background: linear-gradient(135deg, ${CHATBOT_CONFIG.primaryColor}, ${CHATBOT_CONFIG.secondaryColor});
            border: none;
            cursor: pointer;
            box-shadow: 0 8px 32px rgba(245, 158, 11, 0.4);
            z-index: 10000;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .verity-chatbot-toggle:hover {
            transform: scale(1.1);
            box-shadow: 0 12px 40px rgba(245, 158, 11, 0.5);
        }

        .verity-chatbot-toggle svg {
            width: 26px;
            height: 26px;
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
            width: 10px;
            height: 10px;
            background: #10b981;
            border-radius: 50%;
            border: 2px solid #0a0a0b;
            animation: pulse-dot 2s infinite;
        }

        @keyframes pulse-dot {
            0%, 100% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.2); opacity: 0.8; }
        }

        .verity-chatbot-window {
            position: fixed;
            bottom: 96px;
            right: 24px;
            width: 360px;
            max-width: calc(100vw - 48px);
            height: 480px;
            max-height: calc(100vh - 180px);
            background: #0a0a0b;
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            box-shadow: 0 25px 80px rgba(0, 0, 0, 0.6), 0 0 1px rgba(255, 255, 255, 0.1);
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
            padding: 14px 18px;
            background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(251, 191, 36, 0.05));
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .verity-chatbot-avatar {
            width: 36px;
            height: 36px;
            background: linear-gradient(135deg, ${CHATBOT_CONFIG.primaryColor}, ${CHATBOT_CONFIG.secondaryColor});
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .verity-chatbot-avatar svg {
            width: 20px;
            height: 20px;
            color: white;
        }

        .verity-chatbot-title {
            flex: 1;
        }

        .verity-chatbot-title h4 {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            font-size: 0.9rem;
            font-weight: 600;
            color: white;
            margin: 0;
        }

        .verity-chatbot-title span {
            font-size: 0.7rem;
            color: #10b981;
            display: flex;
            align-items: center;
            gap: 4px;
        }

        .verity-chatbot-title span::before {
            content: '';
            width: 5px;
            height: 5px;
            background: #10b981;
            border-radius: 50%;
        }

        .verity-chatbot-close {
            width: 28px;
            height: 28px;
            border: none;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 6px;
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
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 12px;
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
            gap: 8px;
            max-width: 90%;
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
            width: 26px;
            height: 26px;
            border-radius: 6px;
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
            width: 12px;
            height: 12px;
            color: white;
        }

        .verity-chat-message-content {
            padding: 10px 14px;
            border-radius: 14px;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            font-size: 0.85rem;
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
            margin-top: 10px;
            padding: 10px;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 10px;
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
            gap: 6px;
            font-weight: 600;
            font-size: 0.8rem;
            margin-bottom: 4px;
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
            font-size: 0.7rem;
            color: rgba(255, 255, 255, 0.5);
        }

        .verity-chatbot-input-container {
            padding: 14px 16px;
            border-top: 1px solid rgba(255, 255, 255, 0.08);
            background: rgba(0, 0, 0, 0.3);
        }

        .verity-chatbot-input-wrapper {
            display: flex;
            gap: 8px;
            align-items: center;
        }

        .verity-chatbot-input {
            flex: 1;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 10px 14px;
            color: white;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            font-size: 0.85rem;
            /* Keep native outline for accessibility; :focus style applies a visible box-shadow */
            transition: all 0.2s ease;
        }

        .verity-chatbot-input::placeholder {
            color: rgba(255, 255, 255, 0.4);
        }

        .verity-chatbot-input:focus {
            border-color: ${CHATBOT_CONFIG.primaryColor};
            box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.1);
        }

        .verity-chatbot-send {
            width: 40px;
            height: 40px;
            border: none;
            background: linear-gradient(135deg, ${CHATBOT_CONFIG.primaryColor}, ${CHATBOT_CONFIG.secondaryColor});
            border-radius: 10px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            transition: all 0.2s ease;
        }

        .verity-chatbot-send:hover {
            transform: scale(1.05);
            box-shadow: 0 4px 20px rgba(245, 158, 11, 0.4);
        }

        .verity-chatbot-send:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }

        .verity-chatbot-send svg {
            width: 16px;
            height: 16px;
        }

        .verity-chatbot-quick-actions {
            display: flex;
            gap: 6px;
            margin-top: 10px;
            flex-wrap: wrap;
        }

        .verity-chatbot-quick-action {
            padding: 5px 10px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            color: rgba(255, 255, 255, 0.7);
            font-size: 0.7rem;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .verity-chatbot-quick-action:hover {
            background: rgba(245, 158, 11, 0.1);
            border-color: rgba(245, 158, 11, 0.3);
            color: ${CHATBOT_CONFIG.primaryColor};
        }

        .verity-typing-indicator {
            display: flex;
            gap: 4px;
            padding: 6px 0;
        }

        .verity-typing-indicator span {
            width: 5px;
            height: 5px;
            background: rgba(255, 255, 255, 0.4);
            border-radius: 50%;
            animation: typing-bounce 1.4s ease-in-out infinite;
        }

        .verity-typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
        .verity-typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

        @keyframes typing-bounce {
            0%, 60%, 100% { transform: translateY(0); }
            30% { transform: translateY(-5px); }
        }

        /* Desktop-specific styles */
        .verity-chatbot-toggle.minimized {
            width: 44px;
            height: 44px;
        }

        .verity-chatbot-toggle.minimized svg {
            width: 20px;
            height: 20px;
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
                    <span>Desktop Assistant</span>
                </div>
                <button class="verity-chatbot-close" id="verityChatbotClose" aria-label="Close chat">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
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
                    <button class="verity-chatbot-quick-action" data-message="Verify a claim">🔍 Verify</button>
                    <button class="verity-chatbot-quick-action" data-message="How does Verity work?">❓ How it works</button>
                    <button class="verity-chatbot-quick-action" data-message="What features are available?">✨ Features</button>
                </div>
            </div>
        </div>
    `;

    // Wait for DOM to be ready
    function init() {
        // Inject chatbot into page
        const chatbotContainer = document.createElement('div');
        chatbotContainer.id = 'verity-chatbot-container';
        chatbotContainer.innerHTML = chatbotHTML;
        document.body.appendChild(chatbotContainer);

        // Get elements
        const toggle = document.getElementById('verityChatbotToggle');
        const chatWindow = document.getElementById('verityChatbotWindow');
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
            chatWindow.classList.toggle('open', isOpen);
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
                addBotMessage('I apologize, but I encountered an error connecting to the API. Please check your internet connection or try again later.');
            }

            isTyping = false;
            sendBtn.disabled = false;
        }

        function getGeneralResponse(text) {
            const lower = text.toLowerCase();
            
            if (lower.includes('feature') || lower.includes('what can')) {
                return 'The Verity Desktop app includes:<br><br>• <strong>Claim Verification</strong> - Verify any statement with AI consensus<br>• <strong>Source Analysis</strong> - Evaluate source credibility<br>• <strong>Content Moderation</strong> - Detect harmful content<br>• <strong>Research Mode</strong> - Deep-dive investigations<br>• <strong>Social Media Scanner</strong> - Analyze tweets & posts<br>• <strong>Real-time Stream</strong> - Monitor global misinformation<br><br>Use the sidebar to explore all features!';
            }
            
            if (lower.includes('how') && (lower.includes('work') || lower.includes('does'))) {
                return 'Verity uses <strong>20+ AI models</strong> for multi-source consensus verification:<br><br>1. Submit any claim or content<br>2. Multiple AI providers analyze it simultaneously<br>3. Our Bayesian consensus engine synthesizes results<br>4. You get a verdict, confidence score, and sources<br><br>The desktop app gives you full access to all verification features!';
            }
            
            if (lower.includes('hello') || lower.includes('hi') || lower.includes('hey')) {
                return 'Hello! 👋 Welcome to Verity Desktop. I can help you verify claims, explain features, or guide you through the app. What would you like to do?';
            }

            if (lower.includes('thank')) {
                return 'You\'re welcome! 😊 Is there anything else I can help you with?';
            }

            if (lower.includes('shortcut') || lower.includes('keyboard')) {
                return 'Useful keyboard shortcuts:<br><br>• <strong>Ctrl+K</strong> - Open search<br>• <strong>Ctrl+Enter</strong> - Submit verification<br>• <strong>Esc</strong> - Close dialogs<br>• <strong>1-9</strong> - Quick navigation<br><br>The app is designed for power users!';
            }

            return 'I can help you with:<br><br>• <strong>Verifying claims</strong> - Just type a statement<br>• <strong>Desktop features</strong> - Ask about capabilities<br>• <strong>Keyboard shortcuts</strong> - Work faster<br>• <strong>Navigation</strong> - Find any feature<br><br>What would you like to know?';
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
            // Ctrl+Shift+C to toggle chatbot
            if (e.ctrlKey && e.shiftKey && e.key === 'C') {
                toggleChatbot();
            }
        });

        try { log.info && log.info('✓ Verity Desktop Chatbot loaded'); } catch (e) { console.info('Chatbot loaded'); }
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
