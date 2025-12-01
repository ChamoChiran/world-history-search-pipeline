/**
 * js/api.js
 * API Service for Chronos - Connects to Python Backend
 */

class ApiService {
    constructor() {
        this.baseUrl = CONFIG.apiBaseUrl;
    }

    async sendMessage(message) {
        try {
            const response = await fetch(`${this.baseUrl}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query: message })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            // Backend now returns data in the correct format
            // Check if response has sources
            if (!data.sources || data.sources.length === 0) {
                return {
                    answer: data.answer,
                    sources: []  // Empty array for no sources
                };
            }
            
            // Return data directly from backend
            return {
                answer: data.answer,
                sources: data.sources
            };
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    async generateChatName(message) {
        try {
            const response = await fetch(`${this.baseUrl}/chat/generate-name`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data.name;
        } catch (error) {
            console.error('API Error generating chat name:', error);
            // Return a fallback name
            return message.substring(0, 40) + (message.length > 40 ? '...' : '');
        }
    }
}

// Export for use in app.js (In vanilla JS without modules, this attaches to window)
window.apiService = new ApiService();