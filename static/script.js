document.addEventListener('DOMContentLoaded', () => {
    const backendStatus = document.getElementById('backend-status');
    const statusText = document.getElementById('status-text');
    const statusDot = backendStatus.querySelector('.status-dot');
    
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const fileList = document.getElementById('file-list');
    const resetBtn = document.getElementById('reset-btn');
    
    const chatContainer = document.getElementById('chat-container');
    const questionInput = document.getElementById('question-input');
    const sendBtn = document.getElementById('send-btn');
    
    const notificationContainer = document.getElementById('notification-container');

    const API_BASE = ''; // Backend is on the same origin

    // --- UTILS ---

    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        
        let icon = 'info-circle';
        if (type === 'success') icon = 'check-circle';
        if (type === 'error') icon = 'exclamation-circle';

        notification.innerHTML = `<i class="fas fa-${icon}"></i> <span>${message}</span>`;
        notificationContainer.appendChild(notification);

        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(20px)';
            setTimeout(() => notification.remove(), 300);
        }, 4000);
    }

    function addMessage(content, type, sources = []) {
        const welcome = document.querySelector('.welcome-message');
        if (welcome) welcome.style.display = 'none';

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        
        let messageHtml = `<p>${content}</p>`;
        
        if (sources.length > 0) {
            messageHtml += `
                <div class="sources">
                    <strong>Sources:</strong><br>
                    ${sources.map(s => `<span>${s}</span>`).join('')}
                </div>
            `;
        }
        
        messageDiv.innerHTML = messageHtml;
        chatContainer.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
        return messageDiv;
    }

    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message ai typing-indicator';
        typingDiv.innerHTML = '<div class="typing"><span></span><span></span><span></span></div>';
        chatContainer.appendChild(typingDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
        return typingDiv;
    }

    // --- API CALLS ---

    async function checkStatus() {
        try {
            const response = await fetch(`${API_BASE}/status`);
            if (response.ok) {
                const data = await response.json();
                statusText.innerText = 'Backend Connected';
                statusDot.className = 'status-dot online';
                
                // Update file list
                updateFileList(data.filenames);
            } else {
                throw new Error('Offline');
            }
        } catch (error) {
            statusText.innerText = 'Backend Offline';
            statusDot.className = 'status-dot offline';
        }
    }

    function updateFileList(filenames) {
        if (!filenames || filenames.length === 0) {
            fileList.innerHTML = '<p style="text-align:center; color: var(--text-muted); font-size: 0.8rem;">No documents loaded yet.</p>';
            return;
        }

        fileList.innerHTML = filenames.map(name => `
            <div class="file-item">
                <i class="fas fa-file-alt"></i>
                <span title="${name}">${name.length > 25 ? name.substring(0, 22) + '...' : name}</span>
            </div>
        `).join('');
    }

    async function uploadFiles(files) {
        if (files.length === 0) return;

        const formData = new FormData();
        for (const file of files) {
            formData.append('files', file);
        }

        const progressContainer = document.getElementById('upload-progress-container');
        const progressFill = document.getElementById('progress-fill');
        const progressText = document.getElementById('progress-text');
        const progressPercent = document.getElementById('progress-percent');

        progressContainer.style.display = 'block';
        progressFill.style.width = '0%';
        progressFill.classList.remove('processing');
        progressText.innerText = `Uploading ${files.length} file(s)...`;
        progressPercent.innerText = '0%';

        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            
            xhr.upload.onprogress = (event) => {
                if (event.lengthComputable) {
                    const percent = Math.round((event.loaded / event.total) * 100);
                    progressFill.style.width = percent + '%';
                    progressPercent.innerText = percent + '%';
                    
                    if (percent === 100) {
                        progressText.innerText = 'Processing & Indexing...';
                        progressFill.classList.add('processing');
                    }
                }
            };

            xhr.onload = () => {
                progressContainer.style.display = 'none';
                if (xhr.status >= 200 && xhr.status < 300) {
                    const data = JSON.parse(xhr.responseText);
                    showNotification(data.message, 'success');
                    checkStatus();
                    resolve(data);
                } else {
                    let errorData = { detail: 'Upload failed' };
                    try { errorData = JSON.parse(xhr.responseText); } catch(e) {}
                    showNotification(errorData.detail || 'Upload failed', 'error');
                    reject(errorData);
                }
            };

            xhr.onerror = () => {
                progressContainer.style.display = 'none';
                showNotification('Error uploading files', 'error');
                reject(new Error('Network error'));
            };

            xhr.open('POST', `${API_BASE}/upload`);
            xhr.send(formData);
        });
    }

    async function askQuestion() {
        const question = questionInput.value.trim();
        if (!question) return;

        addMessage(question, 'user');
        questionInput.value = '';
        
        const typing = showTypingIndicator();
        sendBtn.disabled = true;

        try {
            const response = await fetch(`${API_BASE}/ask`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question })
            });

            const data = await response.json();
            typing.remove();
            sendBtn.disabled = false;

            if (response.ok) {
                addMessage(data.answer, 'ai', data.sources);
                if (data.debug && data.debug.length > 0) {
                    const dbg = data.debug.map(e => `${e.source} / p${e.page} (score ${e.score.toFixed(3)})`).join('\n');
                    console.log('Vector search hit details:\n' + dbg);
                }
            } else {
                showNotification(data.detail || 'Failed to get answer', 'error');
                addMessage('Sorry, I couldn\'t process that question. Error: ' + (data.detail || 'Internal Server Error'), 'ai');
            }
        } catch (error) {
            typing.remove();
            sendBtn.disabled = false;
            showNotification('Communication error', 'error');
        }
    }

    async function resetDocuments() {
        if (!confirm('Are you sure you want to clear all documents and conversation history?')) return;

        try {
            const response = await fetch(`${API_BASE}/reset`, { method: 'DELETE' });
            if (response.ok) {
                showNotification('All documents and history cleared', 'success');
                chatContainer.innerHTML = `
                    <div class="welcome-message">
                        <i class="fas fa-robot"></i>
                        <p>Hello! Upload your documents and ask me anything about them. I'll provide answers based strictly on your content.</p>
                    </div>
                `;
                checkStatus();
            } else {
                showNotification('Reset failed', 'error');
            }
        } catch (error) {
            showNotification('Error resetting documents', 'error');
        }
    }

    // --- EVENTS ---

    // Drag and Drop
    dropZone.addEventListener('click', () => fileInput.click());
    
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('active');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('active');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('active');
        uploadFiles(e.dataTransfer.files);
    });

    fileInput.addEventListener('change', () => {
        uploadFiles(fileInput.files);
        fileInput.value = ''; // Reset
    });

    // Chat
    sendBtn.addEventListener('click', askQuestion);
    questionInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') askQuestion();
    });

    // Reset
    resetBtn.addEventListener('click', resetDocuments);

    // Initial load
    checkStatus();
    setInterval(checkStatus, 30000); // Check every 30s
});
