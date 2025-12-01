/* script.js */

// --- DOM Elements ---
const els = {
    input: document.getElementById('chat-input'),
    sendBtn: document.getElementById('send-btn'),
    messagesList: document.getElementById('messages-list'),
    welcomeScreen: document.getElementById('welcome-screen'),
    thinkingIndicator: document.getElementById('thinking-indicator'),
    thinkingText: document.getElementById('thinking-text'),
    scrollAnchor: document.getElementById('scroll-anchor'),
    sidebar: document.getElementById('sidebar'),
    sidebarOverlay: document.getElementById('sidebar-overlay'),
    openSidebarBtn: document.getElementById('open-sidebar'),
    closeSidebarBtn: document.getElementById('close-sidebar'),
    moduleCard: document.getElementById('module-card'),
    newChatBtn: document.getElementById('new-chat-btn'),
    suggestionBtns: document.querySelectorAll('.suggestion-btn'),
    chatContainer: document.getElementById('chat-container'),
    themeToggle: document.getElementById('theme-toggle')
};

let isTyping = false;
let hasMessages = false;
let currentChatName = null;
let isGeneratingName = false;

// --- Initialization ---
document.addEventListener('DOMContentLoaded', () => {
    // Initialize Lucide Icons
    lucide.createIcons();
    // Initialize theme
    initializeTheme();
});

// --- Core Functions ---

// Simple Markdown formatter
function formatText(text) {
    return text.split('\n').map(paragraph => {
        if (!paragraph) return '<div class="h-2"></div>';
        
        // Bold (**text**)
        let formatted = paragraph.replace(/\*\*(.*?)\*\*/g, '<strong class="font-bold" style="color: var(--text-primary);">$1</strong>');
        // Italic (*text*)
        formatted = formatted.replace(/\*(.*?)\*/g, '<em class="italic" style="color: var(--text-secondary);">$1</em>');
        
        return `<p class="mb-3 leading-relaxed last:mb-0">${formatted}</p>`;
    }).join('');
}

// Create Message Element
function createMessageElement(role, content, sources = []) {
    const isAI = role === 'ai';
    const wrapper = document.createElement('div');
    wrapper.className = `flex w-full ${isAI ? 'justify-start' : 'justify-end'} mb-6 group animate-fade-in`;

    const bubble = document.createElement('div');
    bubble.className = `max-w-[85%] md:max-w-[75%] rounded-2xl px-5 py-4 shadow-sm relative ${isAI ? 'rounded-tl-sm' : 'rounded-tr-sm'}`;
    bubble.style.cssText = isAI 
        ? 'background-color: var(--surface); border: 1px solid var(--border); color: var(--text-primary);' 
        : 'background-color: var(--border); color: var(--text-primary);';

    // Avatar Icon
    const iconHtml = isAI 
        ? '<i data-lucide="scroll" width="14" style="color: var(--accent);"></i>' 
        : '<i data-lucide="user" width="14" style="color: var(--text-secondary);"></i>';
    
    const avatar = document.createElement('div');
    avatar.className = `absolute -top-6 ${isAI ? '-left-2' : '-right-2'} opacity-0 group-hover:opacity-100 transition-opacity duration-300`;
    avatar.innerHTML = `<div class="p-1 rounded-full" style="background-color: var(--bg); border: 1px solid var(--border);">${iconHtml}</div>`;

    // Content
    const textDiv = document.createElement('div');
    textDiv.className = `text-[0.95rem] ${isAI ? 'font-serif text-lg tracking-wide' : 'font-sans'}`;
    textDiv.innerHTML = formatText(content);

    bubble.appendChild(avatar);
    bubble.appendChild(textDiv);

    // Sources Section (AI only)
    // Sources Section (AI only)
    if (isAI && sources.length > 0) {
        const sourceSection = document.createElement('div');
        sourceSection.className = "mt-4 pt-3 border-t";
        sourceSection.style.borderColor = 'var(--border)';
        
        const toggleBtn = document.createElement('button');
        toggleBtn.className = "flex items-center gap-1.5 text-xs font-semibold transition-colors w-full text-left";
        toggleBtn.style.color = 'var(--accent)';
        toggleBtn.onmouseover = function() { this.style.opacity = '0.75'; };
        toggleBtn.onmouseout = function() { this.style.opacity = '1'; };
        
        // Initial state text
        toggleBtn.innerHTML = `
            <i data-lucide="chevron-down" width="14" class="transition-transform duration-300"></i>
            <span class="btn-text">View ${sources.length} Sources</span>
        `;

        const sourcesList = document.createElement('div');
        // CHANGE 1: Added 'hidden' and 'mt-3' to start closed and add spacing when open
        sourcesList.className = "source-container flex flex-col gap-1 max-h-[300px] overflow-y-auto hidden mt-3 transition-all";
        
        sources.forEach(src => {
            const card = document.createElement('div');
            card.className = "flex items-start gap-2 text-xs p-2 rounded";
            card.style.cssText = 'background-color: var(--bg); border: 1px solid var(--border); color: var(--text-secondary);';
            card.innerHTML = `
                <i data-lucide="scroll" width="12" class="mt-0.5" style="color: var(--accent);"></i>
                <div>
                    <span class="font-semibold" style="color: var(--text-primary);">${src.text}</span>
                    ${src.author ? `<span class="mx-1">•</span><span>${src.author}</span>` : ''}
                    ${src.page ? `<span class="opacity-75"> (p. ${src.page})</span>` : ''}
                </div>
            `;
            sourcesList.appendChild(card);
        });

        // CHANGE 2: Updated Toggle Logic to use Tailwind's 'hidden' class
        toggleBtn.addEventListener('click', () => {
            // Check if currently hidden
            const isHidden = sourcesList.classList.contains('hidden');
            const icon = toggleBtn.querySelector('i');
            const textSpan = toggleBtn.querySelector('.btn-text');
            
            if (isHidden) {
                // Open it
                sourcesList.classList.remove('hidden');
                icon.style.transform = 'rotate(180deg)';
                textSpan.textContent = 'Hide Sources';
            } else {
                // Close it
                sourcesList.classList.add('hidden');
                icon.style.transform = 'rotate(0deg)';
                textSpan.textContent = `View ${sources.length} Sources`;
            }
        });

        sourceSection.appendChild(toggleBtn);
        sourceSection.appendChild(sourcesList);
        bubble.appendChild(sourceSection);
    }

    wrapper.appendChild(bubble);
    return wrapper;
}

// Sending Logic
async function handleSend(text) {
    if (!text.trim() || isTyping) return;

    const isFirstMessage = !hasMessages;

    // UI Updates: Hide welcome screen if first message
    if (!hasMessages) {
        hasMessages = true;
        els.welcomeScreen.classList.add('hidden');
        els.messagesList.classList.remove('hidden');
    }

    // 1. Add User Message
    const userMsg = createMessageElement('user', text);
    els.messagesList.appendChild(userMsg);
    lucide.createIcons();
    els.scrollAnchor.scrollIntoView({ behavior: 'smooth' });

    // Reset Input
    els.input.value = '';
    els.input.style.height = 'auto'; // Reset height
    toggleSendButton();

    // 2. Start Thinking
    isTyping = true;
    els.thinkingIndicator.classList.remove('hidden');
    els.thinkingIndicator.classList.add('flex');
    els.scrollAnchor.scrollIntoView({ behavior: 'smooth' });
    
    els.thinkingText.textContent = "Consulting archives...";
    
    // Simulation Stages
    setTimeout(() => { if(isTyping) els.thinkingText.textContent = "Analyzing historical contexts..."; }, 1000);
    setTimeout(() => { if(isTyping) els.thinkingText.textContent = "Formatting response..."; }, 2000);

    // 3. Get Response from Backend
    try {
        const response = await window.apiService.sendMessage(text);

        // 4. Add AI Message
        isTyping = false;
        els.thinkingIndicator.classList.add('hidden');
        els.thinkingIndicator.classList.remove('flex');
        
        const aiMsg = createMessageElement('ai', response.answer, response.sources);
        els.messagesList.appendChild(aiMsg);
        lucide.createIcons(); // Re-render icons for new content
        els.scrollAnchor.scrollIntoView({ behavior: 'smooth' });

        // Generate chat name for first message
        if (isFirstMessage && !isGeneratingName) {
            generateAndDisplayChatName(text);
        }
    } catch (error) {
        // Handle error
        isTyping = false;
        els.thinkingIndicator.classList.add('hidden');
        els.thinkingIndicator.classList.remove('flex');
        
        const errorMsg = createMessageElement('ai', 'Apologies, I cannot access the archives right now. Please try again later.');
        els.messagesList.appendChild(errorMsg);
        lucide.createIcons();
        els.scrollAnchor.scrollIntoView({ behavior: 'smooth' });
    }
}

// Generate and Display Chat Name
async function generateAndDisplayChatName(firstMessage) {
    isGeneratingName = true;
    
    // Show loading state
    const sessionContainer = document.getElementById('current-session');
    sessionContainer.innerHTML = `
        <div class="px-3 py-2 text-sm flex items-center gap-2" style="color: var(--text-secondary);">
            <i data-lucide="loader-2" class="animate-spin" width="14"></i>
            Generating chat name...
        </div>
    `;
    lucide.createIcons();

    try {
        // Call backend to generate chat name
        const chatName = await window.apiService.generateChatName(firstMessage);
        currentChatName = chatName;
        
        // Display the chat name
        sessionContainer.innerHTML = `
            <div class="w-full text-left px-3 py-2 text-sm rounded-md flex items-center gap-2" style="background-color: var(--border); border: 1px solid var(--border); color: var(--text-primary);">
                <i data-lucide="message-square" width="14" style="color: var(--accent);"></i>
                <span class="flex-1 truncate font-medium">${chatName}</span>
            </div>
        `;
        lucide.createIcons();
    } catch (error) {
        console.error('Error generating chat name:', error);
        // Show error state
        sessionContainer.innerHTML = `
            <div class="px-3 py-4 text-xs text-center italic" style="color: var(--text-secondary);">
                Failed to generate chat name
            </div>
        `;
    } finally {
        isGeneratingName = false;
    }
}

// New Chat Functionality
function resetChat() {
    hasMessages = false;
    currentChatName = null;
    isGeneratingName = false;
    els.messagesList.innerHTML = '';
    els.messagesList.classList.add('hidden');
    els.welcomeScreen.classList.remove('hidden');
    els.input.value = '';
    toggleSendButton();
    
    // Clear current session
    const sessionContainer = document.getElementById('current-session');
    sessionContainer.innerHTML = `
        <div class="px-3 py-4 text-xs text-center italic" style="color: var(--text-secondary);">
            No active chat session
        </div>
    `;
    
    if(window.innerWidth < 768) closeSidebar();
}

// Theme Toggle Logic
function initializeTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
}

function updateThemeIcon(theme) {
    const icon = els.themeToggle.querySelector('i');
    if (icon) {
        icon.setAttribute('data-lucide', theme === 'light' ? 'moon' : 'sun');
        lucide.createIcons();
    }
}

// Sidebar Logic
function openSidebar() {
    els.sidebar.classList.remove('-translate-x-full');
    els.sidebarOverlay.classList.remove('opacity-0', 'pointer-events-none');
    els.sidebarOverlay.classList.add('opacity-100', 'pointer-events-auto');
}

function closeSidebar() {
    els.sidebar.classList.add('-translate-x-full');
    els.sidebarOverlay.classList.add('opacity-0', 'pointer-events-none');
    els.sidebarOverlay.classList.remove('opacity-100', 'pointer-events-auto');
}

// Input Handling
function toggleSendButton() {
    if (els.input.value.trim() && !isTyping) {
        els.sendBtn.disabled = false;
        els.sendBtn.classList.remove('cursor-not-allowed');
        els.sendBtn.classList.add('shadow-md');
        els.sendBtn.style.backgroundColor = 'var(--accent)';
        els.sendBtn.style.color = 'var(--surface)';
        els.sendBtn.style.opacity = '1';
        els.sendBtn.onmouseover = function() { this.style.opacity = '0.85'; };
        els.sendBtn.onmouseout = function() { this.style.opacity = '1'; };
    } else {
        els.sendBtn.disabled = true;
        els.sendBtn.classList.add('cursor-not-allowed');
        els.sendBtn.classList.remove('shadow-md');
        els.sendBtn.style.backgroundColor = 'var(--border)';
        els.sendBtn.style.color = 'var(--text-secondary)';
        els.sendBtn.style.opacity = '0.5';
        els.sendBtn.onmouseover = null;
        els.sendBtn.onmouseout = null;
    }
}

// --- Event Listeners ---

els.input.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 120) + 'px';
    toggleSendButton();
});

els.input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSend(els.input.value);
    }
});

els.sendBtn.addEventListener('click', () => handleSend(els.input.value));

els.suggestionBtns.forEach(btn => {
    btn.addEventListener('click', () => handleSend(btn.innerText));
});

els.openSidebarBtn.addEventListener('click', openSidebar);
els.closeSidebarBtn.addEventListener('click', closeSidebar);
els.sidebarOverlay.addEventListener('click', closeSidebar);
els.newChatBtn.addEventListener('click', resetChat);
els.themeToggle.addEventListener('click', toggleTheme);
