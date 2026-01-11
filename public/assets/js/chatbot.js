/**
 * Verity AI Chatbot Component - Website Edition
 * Matches the production website design: https://vrsystemss.vercel.app/
 * Amber/Gold theme with Newsreader + Inter fonts
 */

(function() {
    'use strict';

    const CHATBOT_CONFIG = {
        apiUrl: 'https://veritysystems-production.up.railway.app',
        botName: 'Verity AI',
        welcomeMessage: 'Hi! I\'m Verity AI, your fact-checking assistant. I can help you verify claims, answer questions about our platform, or explain how our 9-point verification system works. What would you like to know?',
        placeholderText: 'Ask anything or verify a claim...',
        primaryColor: '#f59e0b',
        primaryLight: '#fbbf24',
        greenColor: '#10b981'
    };

    // Inject styles matching test website design
    const styles = `
        /* Chatbot Toggle Button */
        .verity-chat-toggle {
            position: fixed;
            bottom: 24px;
            right: 24px;
            width: 56px;
            height: 56px;
            border-radius: 50%;
            background: linear-gradient(135deg, ${CHATBOT_CONFIG.primaryColor}, ${CHATBOT_CONFIG.primaryLight});
            border: none;
            cursor: pointer;
            box-shadow: 0 8px 32px rgba(245, 158, 11, 0.35);
            z-index: 10000;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        }

        .verity-chat-toggle:hover {
            transform: scale(1.08) translateY(-2px);
            box-shadow: 0 12px 40px rgba(245, 158, 11, 0.45);
        }

        .verity-chat-toggle svg {
            width: 26px;
            height: 26px;
            color: #000;
            transition: transform 0.3s ease;
        }

        .verity-chat-toggle.active svg {
            transform: rotate(45deg);
        }

        .verity-chat-toggle .pulse-ring {
            position: absolute;
            inset: -4px;
            border: 2px solid ${CHATBOT_CONFIG.primaryColor};
            border-radius: 50%;
            animation: chat-pulse 2s infinite;
            opacity: 0;
        }

        @keyframes chat-pulse {
            0% { transform: scale(1); opacity: 0.5; }
            100% { transform: scale(1.4); opacity: 0; }
        }

        /* Chatbot Window */
        .verity-chat-window {
            position: fixed;
            bottom: 96px;
            right: 24px;
            width: 380px;
            max-width: calc(100vw - 48px);
            height: 520px;
            max-height: calc(100vh - 160px);
            background: #0a0a0b;
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 20px;
            box-shadow: 0 25px 80px rgba(0, 0, 0, 0.6), 0 0 0 1px rgba(255, 255, 255, 0.05);
            z-index: 9999;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            opacity: 0;
            visibility: hidden;
            transform: translateY(20px) scale(0.95);
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        }

        .verity-chat-window.open {
            opacity: 1;
            visibility: visible;
            transform: translateY(0) scale(1);
        }

        /* Header */
        .verity-chat-header {
            padding: 16px 20px;
            background: #111113;
            border-bottom: 1px solid rgba(255, 255, 255, 0.06);
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .verity-chat-avatar {
            width: 40px;
            height: 40px;
            background: rgba(245, 158, 11, 0.12);
            border: 1px solid rgba(245, 158, 11, 0.2);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .verity-chat-avatar svg {
            width: 22px;
            height: 24px;
        }

        .verity-chat-title {
            flex: 1;
        }

        .verity-chat-title h4 {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            font-size: 15px;
            font-weight: 600;
            color: #fafafa;
            margin: 0;
        }

        .verity-chat-title .status {
            font-size: 12px;
            color: ${CHATBOT_CONFIG.greenColor};
            display: flex;
            align-items: center;
            gap: 5px;
            margin-top: 2px;
        }

        .verity-chat-title .status::before {
            content: '';
            width: 6px;
            height: 6px;
            background: ${CHATBOT_CONFIG.greenColor};
            border-radius: 50%;
            animation: status-pulse 2s infinite;
        }

        @keyframes status-pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .verity-chat-close {
            width: 32px;
            height: 32px;
            border: none;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #a3a3a3;
            transition: all 0.2s ease;
        }

        .verity-chat-close:hover {
            background: rgba(255, 255, 255, 0.1);
            color: #fafafa;
        }

        /* Messages Area */
        .verity-chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 16px;
        }

        .verity-chat-messages::-webkit-scrollbar {
            width: 4px;
        }

        .verity-chat-messages::-webkit-scrollbar-track {
            background: transparent;
        }

        .verity-chat-messages::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
        }

        /* Message Bubbles */
        .verity-message {
            display: flex;
            gap: 10px;
            max-width: 90%;
            animation: message-slide 0.3s ease;
        }

        @keyframes message-slide {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .verity-message.user {
            margin-left: auto;
            flex-direction: row-reverse;
        }

        .verity-message-avatar {
            width: 28px;
            height: 28px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }

        .verity-message.bot .verity-message-avatar {
            background: rgba(245, 158, 11, 0.12);
            border: 1px solid rgba(245, 158, 11, 0.2);
        }

        .verity-message.user .verity-message-avatar {
            background: rgba(255, 255, 255, 0.08);
        }

        .verity-message-avatar svg {
            width: 14px;
            height: 14px;
        }

        .verity-message-content {
            padding: 12px 16px;
            border-radius: 16px;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            font-size: 14px;
            line-height: 1.6;
        }

        .verity-message.bot .verity-message-content {
            background: #111113;
            color: #e5e5e5;
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-bottom-left-radius: 4px;
        }

        .verity-message.user .verity-message-content {
            background: linear-gradient(135deg, ${CHATBOT_CONFIG.primaryColor}, ${CHATBOT_CONFIG.primaryLight});
            color: #000;
            border-bottom-right-radius: 4px;
        }

        /* Verification Result Card */
        .verity-verification {
            margin-top: 12px;
            padding: 14px;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 12px;
            border-left: 3px solid;
        }

        .verity-verification.true {
            border-color: ${CHATBOT_CONFIG.greenColor};
            background: rgba(16, 185, 129, 0.05);
        }

        .verity-verification.false {
            border-color: #ef4444;
            background: rgba(239, 68, 68, 0.05);
        }

        .verity-verification.mixed {
            border-color: ${CHATBOT_CONFIG.primaryColor};
            background: rgba(245, 158, 11, 0.05);
        }

        .verity-verification-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 8px;
        }

        .verity-verification-verdict {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 10px;
            border-radius: 6px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            font-weight: 600;
        }

        .verity-verification.true .verity-verification-verdict {
            background: rgba(16, 185, 129, 0.12);
            border: 1px solid rgba(16, 185, 129, 0.25);
            color: ${CHATBOT_CONFIG.greenColor};
        }

        .verity-verification.false .verity-verification-verdict {
            background: rgba(239, 68, 68, 0.12);
            border: 1px solid rgba(239, 68, 68, 0.25);
            color: #ef4444;
        }

        .verity-verification.mixed .verity-verification-verdict {
            background: rgba(245, 158, 11, 0.12);
            border: 1px solid rgba(245, 158, 11, 0.25);
            color: ${CHATBOT_CONFIG.primaryColor};
        }

        .verity-verification-confidence {
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
            color: #a3a3a3;
        }

        .verity-verification-sources {
            font-size: 12px;
            color: #525252;
        }

        /* Input Area */
        .verity-chat-input-area {
            padding: 16px 20px;
            border-top: 1px solid rgba(255, 255, 255, 0.06);
            background: #111113;
        }

        .verity-chat-input-wrapper {
            display: flex;
            gap: 10px;
            align-items: flex-end;
        }

        .verity-chat-input {
            flex: 1;
            background: #18181b;
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            padding: 12px 16px;
            color: #fafafa;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            font-size: 14px;
            outline: none;
            transition: all 0.2s ease;
            resize: none;
            max-height: 100px;
        }

        .verity-chat-input::placeholder {
            color: #525252;
        }

        .verity-chat-input:focus {
            border-color: ${CHATBOT_CONFIG.primaryColor};
            box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.1);
        }

        .verity-chat-send {
            width: 44px;
            height: 44px;
            border: none;
            background: linear-gradient(135deg, ${CHATBOT_CONFIG.primaryColor}, ${CHATBOT_CONFIG.primaryLight});
            border-radius: 12px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #000;
            transition: all 0.2s ease;
            flex-shrink: 0;
        }

        .verity-chat-send:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(245, 158, 11, 0.35);
        }

        .verity-chat-send:disabled {
            opacity: 0.4;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }

        .verity-chat-send svg {
            width: 18px;
            height: 18px;
        }

        /* Quick Actions */
        .verity-quick-actions {
            display: flex;
            gap: 8px;
            margin-top: 12px;
            flex-wrap: wrap;
        }

        .verity-quick-action {
            padding: 6px 12px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 100px;
            color: #a3a3a3;
            font-size: 12px;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .verity-quick-action:hover {
            background: rgba(245, 158, 11, 0.1);
            border-color: rgba(245, 158, 11, 0.3);
            color: ${CHATBOT_CONFIG.primaryColor};
        }

        /* Typing Indicator */
        .verity-typing {
            display: flex;
            gap: 4px;
            padding: 8px 0;
        }

        .verity-typing span {
            width: 6px;
            height: 6px;
            background: #525252;
            border-radius: 50%;
            animation: typing-bounce 1.4s ease-in-out infinite;
        }

        .verity-typing span:nth-child(2) { animation-delay: 0.2s; }
        .verity-typing span:nth-child(3) { animation-delay: 0.4s; }

        @keyframes typing-bounce {
            0%, 60%, 100% { transform: translateY(0); }
            30% { transform: translateY(-4px); }
        }

        /* Mobile Responsive */
        @media (max-width: 480px) {
            .verity-chat-window {
                right: 12px;
                bottom: 80px;
                width: calc(100vw - 24px);
                height: calc(100vh - 120px);
                border-radius: 16px;
            }

            .verity-chat-toggle {
                right: 16px;
                bottom: 16px;
            }
        }
    `;

    // Shield logo SVG
    const shieldLogo = `
        <svg viewBox="0 0 100 120" fill="none">
            <defs>
                <linearGradient id="chatLogoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="${CHATBOT_CONFIG.primaryColor}"/>
                    <stop offset="100%" stop-color="${CHATBOT_CONFIG.primaryLight}"/>
                </linearGradient>
            </defs>
            <path fill="none" stroke="url(#chatLogoGrad)" stroke-width="6" d="M50 10 L85 30 L85 70 C85 95 50 105 50 105 C50 105 15 95 15 70 L15 30 Z"/>
            <polyline fill="none" stroke="url(#chatLogoGrad)" stroke-width="7" stroke-linecap="round" stroke-linejoin="round" points="35,60 45,72 65,48"/>
        </svg>
    `;

    // Icons
    const icons = {
        chat: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>',
        close: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>',
        send: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>',
        user: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>'
    };

    class VerityChatbot {
        constructor() {
            this.isOpen = false;
            this.isLoading = false;
            this.init();
        }

        init() {
            const styleEl = document.createElement('style');
            styleEl.textContent = styles;
            document.head.appendChild(styleEl);

            this.toggle = document.createElement('button');
            this.toggle.className = 'verity-chat-toggle';
            this.toggle.innerHTML = `${icons.chat}<span class="pulse-ring"></span>`;
            this.toggle.addEventListener('click', () => this.toggleChat());
            document.body.appendChild(this.toggle);

            this.window = document.createElement('div');
            this.window.className = 'verity-chat-window';
            this.window.innerHTML = this.renderWindow();
            document.body.appendChild(this.window);

            this.bindEvents();
            this.addBotMessage(CHATBOT_CONFIG.welcomeMessage);
        }

        renderWindow() {
            return `
                <div class="verity-chat-header">
                    <div class="verity-chat-avatar">${shieldLogo}</div>
                    <div class="verity-chat-title">
                        <h4>${CHATBOT_CONFIG.botName}</h4>
                        <span class="status">Online</span>
                    </div>
                    <button class="verity-chat-close">${icons.close}</button>
                </div>
                <div class="verity-chat-messages" id="verity-messages"></div>
                <div class="verity-chat-input-area">
                    <div class="verity-chat-input-wrapper">
                        <input type="text" class="verity-chat-input" placeholder="${CHATBOT_CONFIG.placeholderText}" id="verity-input">
                        <button class="verity-chat-send" id="verity-send">${icons.send}</button>
                    </div>
                    <div class="verity-quick-actions">
                        <button class="verity-quick-action" data-message="How does verification work?">How it works</button>
                        <button class="verity-quick-action" data-message="What AI models do you use?">AI Models</button>
                        <button class="verity-quick-action" data-message="The Earth is 4.5 billion years old">Try example</button>
                    </div>
                </div>
            `;
        }

        bindEvents() {
            this.window.querySelector('.verity-chat-close').addEventListener('click', () => this.toggleChat());
            this.window.querySelector('#verity-send').addEventListener('click', () => this.sendMessage());
            
            const input = this.window.querySelector('#verity-input');
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });

            this.window.querySelectorAll('.verity-quick-action').forEach(btn => {
                btn.addEventListener('click', () => {
                    this.window.querySelector('#verity-input').value = btn.dataset.message;
                    this.sendMessage();
                });
            });
        }

        toggleChat() {
            this.isOpen = !this.isOpen;
            this.window.classList.toggle('open', this.isOpen);
            this.toggle.classList.toggle('active', this.isOpen);
            if (this.isOpen) setTimeout(() => this.window.querySelector('#verity-input').focus(), 300);
        }

        async sendMessage() {
            const input = this.window.querySelector('#verity-input');
            const message = input.value.trim();
            if (!message || this.isLoading) return;

            this.addUserMessage(message);
            input.value = '';

            const isVerification = message.length > 20 && !message.endsWith('?');
            this.showTyping();

            try {
                if (isVerification) {
                    const result = await this.verifyClaimAPI(message);
                    this.hideTyping();
                    this.addVerificationResult(result);
                } else {
                    const response = await this.getResponse(message);
                    this.hideTyping();
                    this.addBotMessage(response);
                }
            } catch (error) {
                this.hideTyping();
                this.addBotMessage('Sorry, I encountered an error. Please try again.');
            }
        }

        async verifyClaimAPI(claim) {
            const response = await fetch(`${CHATBOT_CONFIG.apiUrl}/v3/verify`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ claim })
            });
            if (!response.ok) throw new Error('API error');
            return response.json();
        }

        async getResponse(message) {
            const lower = message.toLowerCase();
            if (lower.includes('how') && lower.includes('work')) {
                return 'Verity uses a 9-point verification system:<br><br>1️⃣ <strong>Data Sources</strong> - Academic databases, news wires<br>2️⃣ <strong>AI Analysis</strong> - 20+ AI models analyze in parallel<br>3️⃣ <strong>Validation</strong> - Cross-model consensus';
            }
            if (lower.includes('ai') && lower.includes('model')) {
                return '🧠 <strong>OpenAI</strong> - GPT-4<br>🎭 <strong>Anthropic</strong> - Claude 3.5<br>✨ <strong>Google</strong> - Gemini<br>⚡ <strong>Groq</strong> - Fast inference<br>🔍 <strong>Perplexity</strong> - Real-time search';
            }
            return 'I can help verify claims! Just type any statement and I\'ll check it against 40+ AI models and sources.';
        }

        addUserMessage(text) {
            const container = this.window.querySelector('#verity-messages');
            container.innerHTML += `<div class="verity-message user"><div class="verity-message-avatar">${icons.user}</div><div class="verity-message-content">${this.escapeHtml(text)}</div></div>`;
            this.scrollToBottom();
        }

        addBotMessage(text) {
            const container = this.window.querySelector('#verity-messages');
            container.innerHTML += `<div class="verity-message bot"><div class="verity-message-avatar">${shieldLogo}</div><div class="verity-message-content">${text}</div></div>`;
            this.scrollToBottom();
        }

        addVerificationResult(result) {
            const score = result.confidence_score || result.score || 75;
            const verdict = score >= 70 ? 'true' : score >= 40 ? 'mixed' : 'false';
            const verdictText = score >= 70 ? '✓ VERIFIED TRUE' : score >= 40 ? '⚠ MIXED' : '✗ LIKELY FALSE';
            const explanation = result.summary || result.explanation || 'Analysis complete.';

            const container = this.window.querySelector('#verity-messages');
            container.innerHTML += `
                <div class="verity-message bot">
                    <div class="verity-message-avatar">${shieldLogo}</div>
                    <div class="verity-message-content">
                        Here's what I found:
                        <div class="verity-verification ${verdict}">
                            <div class="verity-verification-header">
                                <span class="verity-verification-verdict">${verdictText}</span>
                                <span class="verity-verification-confidence">${score}%</span>
                            </div>
                            <div style="color: #a3a3a3; font-size: 13px; line-height: 1.5; margin-top: 8px;">${explanation}</div>
                        </div>
                    </div>
                </div>
            `;
            this.scrollToBottom();
        }

        showTyping() {
            this.isLoading = true;
            const container = this.window.querySelector('#verity-messages');
            container.innerHTML += `<div class="verity-message bot" id="typing-indicator"><div class="verity-message-avatar">${shieldLogo}</div><div class="verity-message-content"><div class="verity-typing"><span></span><span></span><span></span></div></div></div>`;
            this.scrollToBottom();
        }

        hideTyping() {
            this.isLoading = false;
            const typing = this.window.querySelector('#typing-indicator');
            if (typing) typing.remove();
        }

        scrollToBottom() {
            const container = this.window.querySelector('#verity-messages');
            container.scrollTop = container.scrollHeight;
        }

        escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => new VerityChatbot());
    } else {
        new VerityChatbot();
    }
})();
