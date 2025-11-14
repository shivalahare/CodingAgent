class ChatApp {
    constructor() {
        this.chatMessages = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.messageCount = 0;
        
        this.initializeEventListeners();
    }
    
    initializeEventListeners() {
        // Send message on button click
        this.sendButton.addEventListener('click', () => this.sendMessage());
        
        // Send message on Enter key
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });
        
        // Auto-focus input
        this.messageInput.focus();
    }
    
    sendMessage() {
        const message = this.messageInput.value.trim();
        
        if (message === '') {
            return;
        }
        
        // Add user message
        this.addMessage(message, 'user');
        
        // Clear input
        this.messageInput.value = '';
        
        // Simulate bot response after a short delay
        setTimeout(() => {
            this.generateBotResponse(message);
        }, 1000);
    }
    
    addMessage(text, type) {
        this.messageCount++;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;
        
        // Add timestamp
        const timestamp = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        messageDiv.innerHTML = `
            <div class="message-text">${this.escapeHtml(text)}</div>
            <div class="message-time">${timestamp}</div>
        `;
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    generateBotResponse(userMessage) {
        const responses = [
            "That's interesting! Tell me more.",
            "I see what you mean. Could you elaborate?",
            "Thanks for sharing that with me!",
            "I'm learning from our conversation. What else would you like to discuss?",
            "That's a great point!",
            "I appreciate your perspective on this.",
            "Let me think about that...",
            "That's something worth considering.",
            "I understand. Is there anything specific you'd like to know?",
            "Fascinating! I'd love to hear more about your thoughts."
        ];
        
        // Simple keyword-based responses
        const lowerMessage = userMessage.toLowerCase();
        let response;
        
        if (lowerMessage.includes('hello') || lowerMessage.includes('hi') || lowerMessage.includes('hey')) {
            response = "Hello! How are you doing today?";
        } else if (lowerMessage.includes('how are you')) {
            response = "I'm doing great, thanks for asking! How about you?";
        } else if (lowerMessage.includes('thank')) {
            response = "You're welcome! Is there anything else I can help with?";
        } else if (lowerMessage.includes('bye') || lowerMessage.includes('goodbye')) {
            response = "Goodbye! It was nice chatting with you!";
        } else if (lowerMessage.includes('name')) {
            response = "I'm your friendly chat assistant! What's your name?";
        } else if (lowerMessage.includes('help')) {
            response = "I'm here to chat with you! Just type your messages and I'll respond.";
        } else {
            // Random response from the array
            response = responses[Math.floor(Math.random() * responses.length)];
        }
        
        this.addMessage(response, 'bot');
    }
    
    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize the chat app when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new ChatApp();
});

// Add some additional interactive features
window.addEventListener('load', () => {
    // Add a welcome animation
    setTimeout(() => {
        const welcomeMessage = document.querySelector('.system-message');
        if (welcomeMessage) {
            welcomeMessage.style.opacity = '1';
            welcomeMessage.style.transform = 'translateY(0)';
        }
    }, 500);
});