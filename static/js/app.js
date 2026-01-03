// 初始化Socket.IO连接
const socket = io();

// 全局变量
let currentNoteId = null;
let currentSenderName = '';
let currentShareKey = null;
let myUserId = null;  // 用于识别自己的消息

// HTML转义，防止XSS攻击
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ========== 首页 ==========

// 首页不需要特殊逻辑，直接使用链接导航


// ========== 创建纸条页面 ==========

const createForm = document.getElementById('create-form');
if (createForm) {
    createForm.addEventListener('submit', (e) => {
        e.preventDefault();

        const title = document.getElementById('note-title').value.trim();
        const content = document.getElementById('note-content').value.trim();

        // 获取选中的标签
        const selectedTags = Array.from(document.querySelectorAll('input[name="tags"]:checked'))
            .map(cb => cb.value);

        if (!title) {
            alert('请输入标题');
            return;
        }

        socket.emit('create_note', {
            title: title,
            content: content,
            tags: selectedTags,
            is_public: true
        });
    });

    // 添加新标签
    const addTagBtn = document.getElementById('add-tag-btn');
    const newTagInput = document.getElementById('new-tag-input');

    if (addTagBtn && newTagInput) {
        addTagBtn.addEventListener('click', () => {
            const tagName = newTagInput.value.trim();
            if (!tagName) return;

            // 创建新的标签复选框
            const label = document.createElement('label');
            label.className = 'tag-checkbox';
            label.innerHTML = `
                <input type="checkbox" name="tags" value="${tagName}" checked>
                <span class="tag-label" style="background-color: #667eea20; color: #667eea; border: 1px solid #667eea;">
                    ${tagName}
                </span>
            `;

            document.querySelector('.existing-tags').appendChild(label);
            newTagInput.value = '';
        });
    }
}

// Socket.IO: 纸条创建成功
socket.on('note_created', (data) => {
    alert('纸条创建成功！');
    window.location.href = `/note/${data.note.id}`;
});


// ========== 查看纸条页面 ==========

const messagesContainer = document.getElementById('messages');
const messageInput = document.getElementById('message-input');
const senderNameInput = document.getElementById('sender-name');
const sendBtn = document.getElementById('send-btn');

if (window.currentNoteId) {
    currentNoteId = window.currentNoteId;
    currentShareKey = window.currentShareKey;
    myUserId = window.currentUserId;

    // 从本地存储获取昵称
    const savedName = localStorage.getItem('sender_name');
    let hasJoined = false;  // 标记是否已加入房间

    // 加入纸条
    function joinNote() {
        const name = senderNameInput ? senderNameInput.value.trim() : '';

        if (!name) {
            // 还没有输入昵称，不加入
            return;
        }

        currentSenderName = name;
        hasJoined = true;

        socket.emit('join_note', {
            note_id: currentNoteId,
            sender_name: currentSenderName
        });
    }

    // 初始化昵称输入框
    if (savedName && senderNameInput) {
        senderNameInput.value = savedName;
        currentSenderName = savedName;
        // 如果有保存的昵称，立即加入房间
        joinNote();
    } else if (senderNameInput) {
        // 如果没有昵称，显示输入提示
        senderNameInput.placeholder = "请输入你的昵称...";
        senderNameInput.focus();
    }

    // 监听昵称输入，完成时才加入
    if (senderNameInput) {
        senderNameInput.addEventListener('blur', () => {
            const name = senderNameInput.value.trim();
            if (name && !hasJoined) {
                localStorage.setItem('sender_name', name);
                joinNote();
            }
        });

        senderNameInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && senderNameInput.value.trim() && !hasJoined) {
                localStorage.setItem('sender_name', senderNameInput.value.trim());
                joinNote();
                messageInput.focus();
            }
        });
    }

    // 发送消息
    function sendMessage() {
        const content = messageInput.value.trim();

        if (!content || !currentNoteId) return;

        socket.emit('send_note_message', {
            note_id: currentNoteId,
            sender_name: currentSenderName,
            content: content
        });

        messageInput.value = '';
    }

    // 发送按钮点击
    if (sendBtn) {
        sendBtn.addEventListener('click', sendMessage);
    }

    // 回车发送消息
    if (messageInput) {
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }

    // 分享按钮
    const shareBtn = document.getElementById('share-btn');
    if (shareBtn) {
        shareBtn.addEventListener('click', () => {
            const shareUrl = `${window.location.origin}/share/${currentShareKey}`;
            navigator.clipboard.writeText(shareUrl).then(() => {
                alert(`分享链接已复制！\n\n${shareUrl}`);
            }).catch(() => {
                prompt('请复制分享链接:', shareUrl);
            });
        });
    }
}

// Socket.IO: 成功加入纸条
socket.on('note_joined', (data) => {
    if (messagesContainer) {
        messagesContainer.innerHTML = '';
        data.messages.forEach(msg => {
            addMessageToChat(msg);
        });
    }
});

// Socket.IO: 新消息到达
socket.on('new_note_message', (data) => {
    addMessageToChat(data.message);
});

// Socket.IO: 在线人数变化
socket.on('viewer_count_changed', (data) => {
    const viewerCountEl = document.getElementById('viewer-count');
    if (viewerCountEl) {
        viewerCountEl.textContent = data.count;
    }
});

// 添加消息到聊天界面
function addMessageToChat(message) {
    if (!messagesContainer) return;

    // 使用 sender_id 判断是否是自己的消息
    const isOwn = message.sender_id === myUserId;
    const messageEl = document.createElement('div');

    if (message.message_type === 'system') {
        messageEl.className = 'message system-message';
        messageEl.innerHTML = `<div class="message-content">${escapeHtml(message.content)}</div>`;
    } else {
        messageEl.className = `message ${isOwn ? 'own' : 'other'}`;

        const time = new Date(message.timestamp).toLocaleTimeString('zh-CN', {
            hour: '2-digit',
            minute: '2-digit'
        });

        messageEl.innerHTML = `
            <div class="message-sender">${escapeHtml(message.sender_name)}</div>
            <div class="message-content">${escapeHtml(message.content)}</div>
            <div class="message-time">${time}</div>
        `;
    }

    messagesContainer.appendChild(messageEl);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}


// ========== 搜索页面 ==========

const searchInput = document.getElementById('search-input');
const searchBtn = document.getElementById('search-btn');
const searchResults = document.getElementById('search-results');

if (searchInput && searchBtn) {
    // 搜索按钮点击
    searchBtn.addEventListener('click', performSearch);

    // 回车搜索
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            performSearch();
        }
    });
}

function performSearch() {
    const query = searchInput.value.trim();

    // 获取选中的标签
    const selectedTags = Array.from(document.querySelectorAll('#tag-filters input:checked'))
        .map(cb => cb.value);

    const params = new URLSearchParams();
    if (query) params.append('q', query);
    selectedTags.forEach(tag => params.append('tags', tag));

    fetch(`/api/search?${params.toString()}`)
        .then(res => res.json())
        .then(data => {
            displaySearchResults(data.notes);
        })
        .catch(err => {
            console.error('搜索失败:', err);
            alert('搜索失败，请稍后重试');
        });
}

function displaySearchResults(notes) {
    if (!searchResults) return;

    if (notes.length === 0) {
        searchResults.innerHTML = '<div class="empty-state"><p>没有找到匹配的纸条</p></div>';
        return;
    }

    searchResults.innerHTML = notes.map(note => `
        <div class="note-card" onclick="window.location.href='/note/${note.id}'">
            <div class="note-header">
                <h3 class="note-title">${escapeHtml(note.title)}</h3>
                <div class="note-meta">
                    <span class="note-date">${new Date(note.created_at).toLocaleDateString('zh-CN')}</span>
                    <span class="note-views">👁 ${note.view_count}</span>
                </div>
            </div>
            ${note.content ? `<p class="note-preview">${escapeHtml(note.content.substring(0, 100))}${note.content.length > 100 ? '...' : ''}</p>` : ''}
            <div class="note-footer">
                <div class="note-tags">
                    ${note.tags.map(tag => `<span class="tag-small" style="background-color: ${tag.color}20; color: ${tag.color};">${tag.name}</span>`).join('')}
                </div>
                <div class="note-stats">
                    <span>💬 ${note.message_count} 条消息</span>
                </div>
            </div>
        </div>
    `).join('');
}


// ========== 管理后台 ==========

function deleteNote(noteId) {
    if (!confirm('确定要删除这个纸条吗？此操作不可恢复！')) {
        return;
    }

    socket.emit('delete_note', {note_id: noteId});
}

function deleteTag(tagId, tagName) {
    if (!confirm(`确定要删除标签"${tagName}"吗？\n\n删除后，该标签将从所有关联的纸条中移除。此操作不可恢复！`)) {
        return;
    }

    socket.emit('delete_tag', {tag_id: tagId});
}

// Socket.IO: 纸条删除成功
socket.on('note_deleted', (data) => {
    alert('纸条已删除');
    location.reload();
});

// Socket.IO: 标签删除成功
socket.on('tag_deleted', (data) => {
    alert(`标签"${data.tag_name}"已删除`);
    location.reload();
});


// ========== 错误处理 ==========

socket.on('error', (data) => {
    alert('错误: ' + data.message);
});


// ========== 页面加载完成 ==========

console.log('无则の诗已初始化，用户ID:', window.currentUserId);
