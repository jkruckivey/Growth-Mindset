// Application state
let conversationHistory = [];
let sessionId = 'session_' + Date.now(); // Unique session ID

// API Configuration
const API_BASE_URL = 'https://growth-mindset.onrender.com';

// Format current time
function getCurrentTime() {
    return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

// Add message to chat UI
function addMessage(content, isStudent = false) {
    const chatMessages = document.getElementById('chatMessages');
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isStudent ? 'student-message' : 'professor-message'}`;
    
    messageDiv.innerHTML = `
        <div class="message-avatar">${isStudent ? '' : '🎓'}</div>
        <div class="message-content">
            <div class="message-header">
                <span class="message-sender">${isStudent ? 'You' : 'Professor Claude'}</span>
                <span class="message-time">${getCurrentTime()}</span>
            </div>
            <div class="message-text">${content}</div>
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Send message to AI
async function sendMessage() {
    const chatInput = document.getElementById('chatInput');
    const sendButton = document.getElementById('sendButton');
    const sendText = document.getElementById('sendText');
    const sendSpinner = document.getElementById('sendSpinner');
    
    const message = chatInput.value.trim();
    
    if (!message) {
        return;
    }
    
    // Add user message to UI
    addMessage(message, true);
    
    // Clear input and show loading
    chatInput.value = '';
    sendButton.disabled = true;
    sendText.textContent = 'Thinking...';
    sendSpinner.style.display = 'block';
    
    try {
        // Send to API
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                session_id: sessionId,
                conversation_history: conversationHistory
            })
        });

        if (!response.ok) {
            throw new Error(`API request failed: ${response.status}`);
        }

        const data = await response.json();
        
        // Add AI response to UI
        addMessage(data.response, false);
        
        // Update conversation history
        conversationHistory.push(
            { role: "user", content: message },
            { role: "assistant", content: data.response }
        );
        
    } catch (error) {
        console.error('Error sending message:', error);
        addMessage("I apologize, but I'm having trouble connecting right now. Please try again in a moment.", false);
    } finally {
        // Reset button state
        sendButton.disabled = false;
        sendText.textContent = 'Send';
        sendSpinner.style.display = 'none';
        chatInput.focus();
    }
}

// Handle Enter key in textarea
document.addEventListener('DOMContentLoaded', function() {
    const chatInput = document.getElementById('chatInput');
    
    chatInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // Auto-resize textarea
    chatInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 120) + 'px';
    });
    
    // Focus on input
    chatInput.focus();
});