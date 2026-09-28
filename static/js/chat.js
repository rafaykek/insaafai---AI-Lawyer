/**
 * InsaafAI - Consultation Chat Client Logic (Vanilla JS + Marked Markdown Support)
 */
document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatMessages = document.getElementById('chat-messages');
    const sendBtn = document.getElementById('send-btn');

    if (!chatForm || !chatInput || !chatMessages) return;

    // Render markdown for pre-rendered historical messages on page load
    renderExistingMessages();

    // Scroll chat window to the bottom on load
    scrollToBottom();

    // Auto-expand input height
    chatInput.addEventListener('input', () => {
        chatInput.style.height = 'auto';
        chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + 'px';
    });

    // Handle Enter key for submission (Shift+Enter for newline)
    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            chatForm.dispatchEvent(new Event('submit'));
        }
    });

    // Handle Form Submit asynchronously
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const content = chatInput.value.trim();
        if (!content) return;

        const caseId = window.CASE_ID;
        const customerName = window.CUSTOMER_NAME || 'You';

        // 1. Immediately append User Message to DOM
        appendMessage('user', customerName, content);

        // Reset input field and disable submit button
        chatInput.value = '';
        chatInput.style.height = 'auto';
        setLoadingState(true);

        // 2. Add Typing Indicator for Asad
        const typingElem = appendTypingIndicator();

        try {
            const response = await fetch(`/chat/${caseId}/message`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({ content: content })
            });

            if (!response.ok) {
                throw new Error(`Server returned HTTP status ${response.status}`);
            }

            const data = await response.json();

            // Remove typing indicator
            if (typingElem) typingElem.remove();

            if (data.status === 'success' && data.assistant_message) {
                // 3. Append Assistant Grounded Response to DOM
                appendMessage('assistant', 'Asad', data.assistant_message.content);
            } else {
                appendMessage('assistant', 'Asad', 'Sorry, an error occurred while processing your message.');
            }
        } catch (err) {
            if (typingElem) typingElem.remove();
            console.error('Failed to send message:', err);
            appendMessage('assistant', 'Asad', 'Connection error. Please check your connection and try again.');
        } finally {
            setLoadingState(false);
            scrollToBottom();
        }
    });

    function renderExistingMessages() {
        const assistantBubbles = document.querySelectorAll('.message-bubble.assistant .msg-content');
        assistantBubbles.forEach(bubble => {
            if (bubble.dataset.rendered !== 'true') {
                const rawText = bubble.innerText || bubble.textContent;
                bubble.innerHTML = parseMarkdown(rawText);
                bubble.dataset.rendered = 'true';
            }
        });
    }

    function parseMarkdown(text) {
        if (typeof marked !== 'undefined' && marked.parse) {
            try {
                return marked.parse(text);
            } catch (err) {
                console.error("Markdown parse error:", err);
            }
        }
        return escapeHtml(text).replace(/\n/g, '<br>');
    }

    function appendMessage(role, senderLabel, text) {
        const row = document.createElement('div');
        row.className = `message-row ${role === 'user' ? 'user-row' : 'assistant-row'}`;

        const now = new Date();
        const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        let avatarHtml = '';
        let contentHtml = '';

        if (role === 'assistant') {
            avatarHtml = `<div class="msg-avatar">⚖️</div>`;
            contentHtml = parseMarkdown(text);
        } else {
            contentHtml = escapeHtml(text).replace(/\n/g, '<br>');
        }

        row.innerHTML = `
            ${avatarHtml}
            <div class="message-bubble ${role}">
                <div class="sender-label">${escapeHtml(senderLabel)}</div>
                <div class="msg-content">${contentHtml}</div>
                <div class="msg-time">${timeStr}</div>
            </div>
        `;

        chatMessages.appendChild(row);
        scrollToBottom();
    }

    function appendTypingIndicator() {
        const row = document.createElement('div');
        row.className = 'message-row assistant-row typing-row';
        row.innerHTML = `
            <div class="msg-avatar">⚖️</div>
            <div class="message-bubble assistant">
                <div class="sender-label">Asad</div>
                <div class="msg-content" style="font-style: italic; color: #64748b;">Asad is analyzing your case documents...</div>
            </div>
        `;
        chatMessages.appendChild(row);
        scrollToBottom();
        return row;
    }

    function scrollToBottom() {
        setTimeout(() => {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }, 50);
    }

    function setLoadingState(isLoading) {
        sendBtn.disabled = isLoading;
        chatInput.disabled = isLoading;
        if (!isLoading) chatInput.focus();
    }

    function escapeHtml(str) {
        return str
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
});
