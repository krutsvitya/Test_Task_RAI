function showLoginForm() {
    document.getElementById('login-form').style.display = 'block';
    document.getElementById('register-form').style.display = 'none';
    document.getElementById('login-tab').classList.add('active');
    document.getElementById('register-tab').classList.remove('active');
}

function showRegisterForm() {
    document.getElementById('register-form').style.display = 'block';
    document.getElementById('login-form').style.display = 'none';
    document.getElementById('register-tab').classList.add('active');
    document.getElementById('login-tab').classList.remove('active');
}

async function login(event) {
    event.preventDefault();

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    try {
        const response = await fetch('/auth/token', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: new URLSearchParams({
                username,
                password
            })
        });

        const data = await response.json();

        if (response.status === 200) {
            localStorage.setItem('access_token', data.access_token);
            localStorage.setItem('refresh_token', data.refresh_token);
            localStorage.setItem('username', username);
            
            document.getElementById('auth-container').style.display = 'none';
            document.getElementById('chat-container').style.display = 'flex';

            setUserDisplay(username);

            await loadAllChats();

            if (document.getElementById('chat-list').children.length === 0) {
                await createNewChat();
            }
        } else {
            showAlert('Ошибка авторизации: ' + (data.detail || 'Неверные учетные данные'));
        }
    } catch (error) {
        console.error('Error during login:', error);
        showAlert('Произошла ошибка при входе. Пожалуйста, попробуйте позже.');
    }
}

async function register(event) {
    event.preventDefault();

    const username = document.getElementById('register-username').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('register-password').value;

    try {
        const response = await fetch('/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username,
                email,
                password
            })
        });

        if (response.status === 200) {
            const data = await response.json();
            showAlert('Регистрация успешна! Пожалуйста, войдите.', 'success');
            showLoginForm();
        } else {
            const errorData = await response.json();
            const errorDetail = errorData.detail || 'Пожалуйста, проверьте введенные данные';
            showAlert('Ошибка регистрации: ' + errorDetail);
        }
    } catch (error) {
        console.error('Error during registration:', error);
        showAlert('Произошла ошибка при регистрации. Пожалуйста, попробуйте позже.');
    }
}

function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('current_chat_id');
    localStorage.removeItem('username');

    document.getElementById('messages').innerHTML = '';
    document.getElementById('chat-list').innerHTML = '';
    document.getElementById('chat-container').style.display = 'none';
    document.getElementById('auth-container').style.display = 'block';

    showLoginForm();
}

async function loadAllChats() {
    const token = localStorage.getItem('access_token');
    try {
        const response = await fetch('/chats/list', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        const data = await response.json();
        if (response.status === 200) {
            const chatList = document.getElementById('chat-list');
            chatList.innerHTML = '';

            data.chats.forEach(chat => {
                addChatToSidebar(chat);
            });

            if (data.chats.length > 0) {
                selectChat(data.chats[0].id);
            }
        }
    } catch (error) {
        console.error('Error loading chats:', error);
        showAlert('Не удалось загрузить список чатов');
    }
}

function addChatToSidebar(chat) {
    const chatList = document.getElementById('chat-list');
    const chatItem = document.createElement('div');
    chatItem.classList.add('chat-item');
    chatItem.id = `chat-${chat.id}`;
    chatItem.onclick = () => selectChat(chat.id);

    let previewText = 'Новый чат';
    if (chat.preview) {
        previewText = chat.preview;
    }

    chatItem.innerHTML = `
        <div class="chat-item-preview">${chat.name || 'Новый чат'}</div>
    `;

    chatList.prepend(chatItem);
}

function selectChat(chatId) {
    document.querySelectorAll('.chat-item').forEach(item => {
        item.classList.remove('selected');
    });

    const chatItem = document.getElementById(`chat-${chatId}`);
    if (chatItem) {
        chatItem.classList.add('selected');
    }

    localStorage.setItem('current_chat_id', chatId);
    loadChatHistory(chatId);

    updateCurrentChatName();
}

function updateCurrentChatName() {
    const chatId = localStorage.getItem('current_chat_id');
    const chatItem = document.getElementById(`chat-${chatId}`);

    if (chatItem) {
        const chatName = chatItem.querySelector('.chat-item-preview').textContent;
        document.getElementById('current-chat-name').textContent = chatName;
    }
}

async function createNewChat() {
    const token = localStorage.getItem('access_token');
    try {
        const response = await fetch('/chat/new', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();
        if (response.status === 200) {
            const newChat = {
                id: data.chat_id,
                name: 'Новый чат',
                preview: 'Новый чат'
            };

            addChatToSidebar(newChat);
            selectChat(data.chat_id);
            return data.chat_id;
        } else {
            console.error('Error creating chat:', data);
            showAlert('Не удалось создать новый чат');
            return null;
        }
    } catch (error) {
        console.error('Error creating chat:', error);
        showAlert('Не удалось создать новый чат');
        return null;
    }
}

async function loadChatHistory(chatId) {
    const token = localStorage.getItem('access_token');
    try {
        const response = await fetch(`/chat/${chatId}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        const data = await response.json();
        if (response.status === 200) {
            const messagesContainer = document.getElementById('messages');
            messagesContainer.innerHTML = '';

            data.messages.forEach(msg => {
                addMessageToUI(msg.text, msg.sender);
            });

            scrollToBottom();
        }
    } catch (error) {
        console.error('Error loading chat history:', error);
        showAlert('Не удалось загрузить историю чата');
    }
}

async function sendMessage() {
    const messageInput = document.getElementById('message');
    const userMessage = messageInput.value.trim();

    if (!userMessage) return;

    messageInput.value = '';
    messageInput.style.height = 'auto';

    const chatId = localStorage.getItem('current_chat_id');
    if (!chatId) {
        const newChatId = await createNewChat();
        if (!newChatId) {
            showAlert('Ошибка при создании чата. Пожалуйста, попробуйте позже.');
            return;
        }
    }

    addMessageToUI(userMessage, 'user');

    showTypingIndicator();

    const token = localStorage.getItem('access_token');
    try {
        const response = await fetch(`/chat/${chatId}/send`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text: userMessage })
        });

        hideTypingIndicator();

        const data = await response.json();
        if (response.status === 200) {
            addMessageToUI(data.response, 'bot');

            updateChatPreview(chatId, userMessage);
        } else {
            showAlert('Ошибка при отправке сообщения: ' + (data.detail || 'Пожалуйста, попробуйте позже'));
        }
    } catch (error) {
        hideTypingIndicator();

        console.error('Error sending message:', error);
        showAlert('Не удалось отправить сообщение. Пожалуйста, попробуйте позже.');
    }
}

function addMessageToUI(text, sender) {
    const messagesContainer = document.getElementById('messages');
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', sender, 'fade-in');

    const formattedText = formatMessageText(text);

    messageDiv.innerHTML = `
        <div class="sender">${sender === 'user' ? 'Вы' : 'AI Assistant'}</div>
        <div class="message-content">${formattedText}</div>
    `;

    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
}

function formatMessageText(text) {
    let formatted = text.replace(/\n/g, '<br>');
    return formatted;
}

function showTypingIndicator() {
    const messagesContainer = document.getElementById('messages');
    const typingIndicator = document.createElement('div');
    typingIndicator.id = 'typing-indicator';
    typingIndicator.classList.add('typing-indicator');
    typingIndicator.innerHTML = `
        <span></span>
        <span></span>
        <span></span>
    `;
    messagesContainer.appendChild(typingIndicator);
    scrollToBottom();
}

function hideTypingIndicator() {
    const typingIndicator = document.getElementById('typing-indicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

function scrollToBottom() {
    const messagesContainer = document.getElementById('messages');
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function showAlert(message, type = 'error') {
    const alertDiv = document.createElement('div');
    alertDiv.classList.add('alert', `alert-${type}`, 'fade-in');
    alertDiv.textContent = message;

    document.body.appendChild(alertDiv);

    setTimeout(() => {
        alertDiv.classList.add('fade-out');
        setTimeout(() => {
            alertDiv.remove();
        }, 300);
    }, 5000);
}

async function updateChatPreview(chatId, message) {
    const chatItem = document.getElementById(`chat-${chatId}`);
    if (chatItem) {
        const previewElement = chatItem.querySelector('.chat-item-preview');
        if (previewElement.textContent === 'Новый чат') {
            const chatName = message.length > 25 ? message.substring(0, 22) + '...' : message;
            previewElement.textContent = chatName;

            await updateChatName(chatId, chatName);

            updateCurrentChatName();
        }
    }
}

async function updateChatName(chatId, newName) {
    const token = localStorage.getItem('access_token');
    try {
        const response = await fetch(`/chat/${chatId}/rename`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name: newName })
        });

        if (response.status !== 200) {
            console.error('Error updating chat name');
        }
    } catch (error) {
        console.error('Error updating chat name:', error);
    }
}

function showRenameDialog() {
    const chatId = localStorage.getItem('current_chat_id');
    const chatItem = document.getElementById(`chat-${chatId}`);

    if (chatItem) {
        const currentName = chatItem.querySelector('.chat-item-preview').textContent;
        document.getElementById('chat-name-input').value = currentName;
        document.getElementById('rename-dialog').style.display = 'flex';
    }
}

function closeRenameDialog() {
    document.getElementById('rename-dialog').style.display = 'none';
}

async function renameChatConfirm() {
    const chatId = localStorage.getItem('current_chat_id');
    const newName = document.getElementById('chat-name-input').value.trim();

    if (!newName) {
        showAlert('Имя чата не может быть пустым');
        return;
    }

    await updateChatName(chatId, newName);

    const chatItem = document.getElementById(`chat-${chatId}`);
    if (chatItem) {
        chatItem.querySelector('.chat-item-preview').textContent = newName;
    }

    document.getElementById('current-chat-name').textContent = newName;
    closeRenameDialog();
}

function handleKeyDown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    } else if (event.key === 'Enter' && event.shiftKey) {
        // Allow Shift+Enter for new line
        const messageInput = document.getElementById('message');
        if (messageInput.value.length > 0) {
            adjustTextareaHeight(messageInput);
        }
    }
}

function adjustTextareaHeight(textarea) {
    textarea.style.height = 'auto';
    const scrollHeight = textarea.scrollHeight;
    if (scrollHeight > 150) {
        textarea.style.height = '150px';
    } else if (scrollHeight < 24) {
        textarea.style.height = '24px';
    } else {
        textarea.style.height = scrollHeight + 'px';
    }
}

function setUserDisplay(username) {
    document.getElementById('username-display').textContent = username;

    const avatar = document.getElementById('user-avatar');
    if (avatar) {
        avatar.textContent = username.charAt(0).toUpperCase();
    }
}

async function deleteChat(chatId) {
    const token = localStorage.getItem('access_token');
    try {
        const response = await fetch(`/chat/${chatId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.status === 200) {
            const chatItem = document.getElementById(`chat-${chatId}`);
            if (chatItem) {
                chatItem.remove();
            }

            // После удаления текущего чата выбираем другой или создаем новый
            if (localStorage.getItem('current_chat_id') === chatId) {
                const chatItems = document.querySelectorAll('.chat-item');
                if (chatItems.length > 0) {
                    const firstChatId = chatItems[0].id.replace('chat-', '');
                    selectChat(firstChatId);
                } else {
                    createNewChat();
                }
            }

            showAlert('Чат удален', 'success');
        } else {
            showAlert('Не удалось удалить чат');
        }
    } catch (error) {
        console.error('Error deleting chat:', error);
        showAlert('Не удалось удалить чат');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('access_token');
    const username = localStorage.getItem('username');

    if (token && username) {
        document.getElementById('auth-container').style.display = 'none';
        document.getElementById('chat-container').style.display = 'flex';
        setUserDisplay(username);
        loadAllChats();
    } else {
        showLoginForm();
    }

    document.getElementById('login-form-element').addEventListener('submit', login);
    document.getElementById('register-form-element').addEventListener('submit', register);

    const messageInput = document.getElementById('message');
    messageInput.addEventListener('input', function() {
        adjustTextareaHeight(this);
    });

    document.addEventListener('contextmenu', function(event) {
        let target = event.target;
        while (target && !target.classList.contains('chat-item') && target !== document.body) {
            target = target.parentElement;
        }

        if (target && target.classList.contains('chat-item')) {
            event.preventDefault();
            const chatId = target.id.replace('chat-', '');

            if (confirm('Удалить этот чат?')) {
                deleteChat(chatId);
            }
        }
    });
});

async function refreshToken() {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
        logout();
        return;
    }

    try {
        const response = await fetch('/auth/refresh_token', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ refresh_token: refreshToken })
        });

        const data = await response.json();
        if (response.status === 200) {
            localStorage.setItem('access_token', data.access_token);
            localStorage.setItem('refresh_token', data.refresh_token);
            return true;
        } else {
            logout();
            return false;
        }
    } catch (error) {
        console.error('Error refreshing token:', error);
        logout();
        return false;
    }
}

function showDeleteConfirmation() {
    document.getElementById('delete-dialog').style.display = 'flex';
}

function closeDeleteDialog() {
    document.getElementById('delete-dialog').style.display = 'none';
}

function deleteChatConfirm() {
    const chatId = localStorage.getItem('current_chat_id');
    deleteChat(chatId);
    closeDeleteDialog();
}

setInterval(refreshToken, 55 * 60 * 1000);

