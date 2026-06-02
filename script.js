/**
 * Chatbot Frontend Logic (Vanilla JS)
 */

// --- DOM Elements Selection ---
const chatHistory = document.getElementById('chatHistory');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');

/**
 * Creates and appends a new message to the chat window.
 * @param {string} sender - Who sent the message ('user' or 'bot').
 * @param {string} text - The message content.
 */
function appendMessage(sender, text) {
    // 1. Create the main message container
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message');
    messageDiv.classList.add(sender === 'user' ? 'user-message' : 'bot-message');

    // 2. Create the content wrapper
    const contentDiv = document.createElement('div');
    contentDiv.classList.add('message-content');

    // 3. Create paragraph for text to prevent XSS (using textContent)
    const textPara = document.createElement('p');
    textPara.textContent = text;

    // 4. Assemble the elements
    contentDiv.appendChild(textPara);
    messageDiv.appendChild(contentDiv);
    
    // 5. Append to the chat window
    chatHistory.appendChild(messageDiv);

    // 6. Force scroll to the bottom
    scrollToBottom();
}

/**
 * Shows a typing indicator to simulate bot processing
 * @returns {HTMLElement} The typing indicator element (useful for removing it later)
 */
function showTypingIndicator() {
    const indicator = document.createElement('div');
    indicator.classList.add('message', 'bot-message', 'typing-container');
    
    indicator.innerHTML = `
        <div class="typing-indicator">
            <span class="dot"></span>
            <span class="dot"></span>
            <span class="dot"></span>
        </div>
    `;
    
    chatHistory.appendChild(indicator);
    scrollToBottom();
    
    return indicator;
}

/**
 * Helper to smoothly scroll the chat history to the very bottom.
 */
function scrollToBottom() {
    chatHistory.scrollTo({
        top: chatHistory.scrollHeight,
        behavior: 'smooth'
    });
}

/**
 * Core function to handle sending a message.
 */
async function handleSendMessage() {
    const text = userInput.value.trim();
    
    // Don't do anything if the input is empty
    if (!text) return;

    // 1. Append the user's message to the UI immediately
    appendMessage('user', text);

    // 2. Clear the input field for the next message
    userInput.value = '';

    // 3. Optional visual flair: Show a typing indicator
    const typingIndicator = showTypingIndicator();

    try {
        // 4. Call the FastAPI backend
        const response = await fetch('http://127.0.0.1:8000/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: text })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        // 5. Remove the typing indicator once the bot is ready to reply
        if (chatHistory.contains(typingIndicator)) {
            chatHistory.removeChild(typingIndicator);
        }
        
        // 6. Append the bot's response
        appendMessage('bot', data.response);

    } catch (error) {
        console.error("Error communicating with the backend:", error);
        
        // Remove the typing indicator on error
        if (chatHistory.contains(typingIndicator)) {
            chatHistory.removeChild(typingIndicator);
        }
        
        appendMessage('bot', "Oops! I'm having trouble connecting to the server. Please try again later.");
    }
}

// --- Event Listeners ---

// Trigger send on button click
sendBtn.addEventListener('click', handleSendMessage);

// Trigger send on "Enter" key press inside the input field
userInput.addEventListener('keypress', (event) => {
    if (event.key === 'Enter') {
        event.preventDefault(); // Prevent default browser behavior
        handleSendMessage();
    }
});

// Focus the input field when the page first loads
window.addEventListener('DOMContentLoaded', () => {
    userInput.focus();
});
