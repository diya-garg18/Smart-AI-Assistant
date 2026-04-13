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

    // Create and inject re-indexing overlay for file list
    const reindexOverlay = document.createElement('div');
    reindexOverlay.className = 'file-list-loading-overlay';
    reindexOverlay.innerHTML = `
        <div class="reindex-spinner"></div>
        <div class="reindex-text">Updating Index...</div>
    `;
    fileList.appendChild(reindexOverlay);

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
        console.log(`[ui] Updating file list with ${filenames ? filenames.length : 0} items:`, filenames);
        // Keep the loading overlay if it exists
        const overlay = fileList.querySelector('.file-list-loading-overlay');
        
        if (!filenames || filenames.length === 0) {
            fileList.innerHTML = '<p style="text-align:center; color: var(--text-muted); font-size: 0.8rem; padding: 1rem;">No documents loaded yet.</p>';
            if (overlay) fileList.appendChild(overlay);
            return;
        }

        const itemsHtml = filenames.map(name => `
            <div class="file-item" data-filename="${name}">
                <i class="fas fa-file-alt"></i>
                <span class="file-name" title="${name}">${name.length > 25 ? name.substring(0, 22) + '...' : name}</span>
                <button class="btn-delete-file" title="Delete file" data-filename="${name}">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `).join('');

        fileList.innerHTML = itemsHtml;
        if (overlay) fileList.appendChild(overlay);
    }

    async function deleteFile(filename) {
        console.log(`[delete] Requesting deletion of: ${filename}`);
        fileList.classList.add('loading');
        try {
            const response = await fetch(`${API_BASE}/delete-file`, {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ filename })
            });

            let data = {};
            try { data = await response.json(); } catch (_) {}
            console.log(`[delete] Server responded:`, data);

            if (response.ok) {
                showNotification(`Deleted file "${filename.split('_').slice(1).join('_') || filename}"`, 'success');
                updateFileList(data.filenames || []);
            } else {
                showNotification(data.detail || `Delete failed (${response.status})`, 'error');
            }
        } catch (err) {
            showNotification('Network error — check backend connection', 'error');
        } finally {
            fileList.classList.remove('loading');
        }
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
                fileList.classList.remove('loading');
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
                fileList.classList.remove('loading');
                showNotification('Error uploading files', 'error');
                reject(new Error('Network error'));
            };

            xhr.open('POST', `${API_BASE}/upload`);
            fileList.classList.add('loading');
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

    // Per-file delete (event delegation)
    fileList.addEventListener('click', (e) => {
        const btn = e.target.closest('.btn-delete-file');
        if (!btn) return;
        const filename = btn.dataset.filename;
        if (filename && confirm(`Remove "${filename.split('_').slice(1).join('_') || filename}" from the knowledge base?`)) {
            deleteFile(filename);
        }
    });

    // Initial load
    checkStatus();
    setInterval(checkStatus, 30000); // Check every 30s
});