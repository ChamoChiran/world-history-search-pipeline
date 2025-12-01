/**
 * js/app.js
 * Main Application Logic
 */

class ChronosApp {
    constructor() {
        // DOM Elements
        this.elements = {
            chatContainer: document.getElementById('chatContainer'),
            messagesList: document.getElementById('messagesList'),
            userInput: document.getElementById('userInput'),
            sendBtn: document.getElementById('sendBtn'),
            emptyState: document.getElementById('emptyState'),
            thinkingIndicator: document.getElementById('thinkingIndicator'),
            thinkingText: document.getElementById('thinkingText'),
            suggestionChips: document.getElementById('suggestionChips'),
            sidebar: document.getElementById('sidebar'),
            overlay: document.getElementById('overlay'),
            menuBtn: document.getElementById('menuBtn'),
            closeSidebarBtn: document.getElementById('closeSidebar')
        };

        this.suggestions = [
            "Tell me about Ancient Egyptian pyramids",
            "How did the Nile shape Egyptian civilization?",
            "What was daily life like in Ancient Egypt?"
        ];

        this.init();
    }

    init() {
        // Initialize Icons
        lucide.createIcons();

        // Render Suggestion Chips
        this.renderSuggestions();

        // Event Listeners
        this.elements.sendBtn.addEventListener('click', () => this.handleSend());
        this.elements.userInput.addEventListener('input', (e) => this.handleInput(e));
        this.elements.userInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.handleSend();
            }
        });

        // Sidebar Toggles
        this.elements.menuBtn.addEventListener('click', () => this.toggleSidebar(true));
        this.elements.closeSidebarBtn.addEventListener('click', () => this.toggleSidebar(false));
        this.elements.overlay.addEventListener('click', () => this.toggleSidebar(false));
    }

    renderSuggestions() {
        this.elements.suggestionChips.innerHTML = this.suggestions.map(text => `
            <button class="chip">${text}</button>
        `).join('');

        // Add listeners to chips
        this.elements.suggestionChips.querySelectorAll('.chip').forEach(btn => {
            btn.addEventListener('click', (e) => this.handleSend(e.target.innerText));
        });
    }

    toggleSidebar(isOpen) {
        if (isOpen) {
            this.elements.sidebar.classList.add('open');
            this.elements.overlay.classList.add('open');
        } else {
            this.elements.sidebar.classList.remove('open');
            this.elements.overlay.classList.remove('open');
        }
    }

    handleInput(e) {
        const input = e.target;
        // Auto-resize textarea
        input.style.height = 'auto';
        input.style.height = Math.min(input.scrollHeight, 120) + 'px';
        
        // Enable/Disable button
        this.elements.sendBtn.disabled = !input.value.trim();
    }

    async handleSend(text = null) {
        const messageText = text || this.elements.userInput.value.trim();
        if (!messageText) return;

        // 1. Reset UI
        this.elements.userInput.value = '';
        this.elements.userInput.style.height = 'auto';
        this.elements.sendBtn.disabled = true;
        this.elements.emptyState.classList.add('hidden');

        // 2. Add User Message
        this.addMessage(messageText, 'user');

        // 3. Show Thinking
        this.elements.thinkingIndicator.classList.remove('hidden');
        this.elements.chatArea.scrollTop = this.elements.chatArea.scrollHeight; // Scroll to bottom
        
        // Simulate RAG steps
        setTimeout(() => this.elements.thinkingText.innerText = "Analyzing historical contexts...", 1000);
        setTimeout(() => this.elements.thinkingText.innerText = "Formatting response...", 2000);

        try {
            // 4. API Call
            const response = await window.apiService.sendMessage(messageText);
            
            // 5. Hide Thinking & Add AI Message
            this.elements.thinkingIndicator.classList.add('hidden');
            this.elements.thinkingText.innerText = "Consulting archives..."; // Reset text
            this.addMessage(response.answer, 'ai', response.sources);
        } catch (err) {
            this.elements.thinkingIndicator.classList.add('hidden');
            this.addMessage("Apologies, I cannot access the archives right now.", 'ai');
        }
    }

    addMessage(content, role, sources = []) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${role}`;
        
        let processedContent = this.formatText(content);
        
        let sourcesHtml = '';
        // Only show sources if they exist
        if (role === 'ai' && sources && sources.length > 0) {
            const sourcesList = sources.map(s => {
                const authorText = s.author ? ` • ${s.author}` : '';
                const pageText = s.page ? ` (p. ${s.page})` : '';
                return `
                    <div class="source-card">
                        <i data-lucide="scroll" width="12"></i>
                        <span><strong>${s.text}</strong>${authorText}${pageText}</span>
                    </div>
                `;
            }).join('');

            sourcesHtml = `
                <div class="source-container">
                    <button class="source-toggle" onclick="this.nextElementSibling.classList.toggle('show')">
                        <i data-lucide="chevron-down" width="14"></i> View ${sources.length} Sources
                    </button>
                    <div class="sources-list">${sourcesList}</div>
                </div>
            `;
        }

        msgDiv.innerHTML = `
            <div class="message-bubble">
                <div>${processedContent}</div>
                ${sourcesHtml}
            </div>
        `;

        this.elements.messagesList.appendChild(msgDiv);
        
        // Re-initialize icons for new content
        lucide.createIcons();
        
        // Scroll to bottom
        this.elements.chatArea.scrollTop = this.elements.chatArea.scrollHeight;
    }

    // Simple Markdown Parser (**bold**, *italic*, \n)
    formatText(text) {
        return text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n/g, '<br>');
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // We add chatArea to elements dynamically here or in constructor
    const app = new ChronosApp();
    app.elements.chatArea = document.getElementById('chatArea');
});