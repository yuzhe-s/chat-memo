# CLAUDE.md - 聊天备忘录项目指南

这个文件为 Claude Code (claude.ai/code) 提供项目指导，帮助理解代码结构和开发流程。

## 项目概述

**聊天备忘录** 是一个基于 Web 的实时对话笔记应用。用户可以创建持久化的"纸条"，在纸条中进行多轮对话，所有内容共享给所有用户，支持标签分类、全文搜索和分享功能。

## 核心特性

- ✅ **纸条创建**：用户可以创建带标题、内容和标签的纸条
- ✅ **多轮对话**：每个纸条支持类似聊天室的实时消息
- ✅ **实时同步**：使用 WebSocket (Socket.IO) 实现实时消息推送
- ✅ **标签系统**：灵活的多标签分类和筛选
- ✅ **全文搜索**：支持标题、内容和标签的组合搜索
- ✅ **分享链接**：每个纸条有唯一的分享秘钥
- ✅ **管理后台**：密码保护的管理界面，支持删除纸条
- ❌ **无需登录**：所有用户共享内容，使用匿名昵称

## 技术栈

- **后端**: Flask 3.0 + Flask-SocketIO + SQLAlchemy
- **前端**: 原生 JavaScript + Socket.IO Client
- **数据库**: PostgreSQL (生产) / SQLite (开发)
- **部署**: Render (eventlet + gunicorn)
- **实时通信**: WebSocket via Socket.IO

## 本地开发

### 安装依赖
```bash
pip install -r requirements.txt
```

### 启动开发服务器
```bash
python app.py
# 应用运行在 http://localhost:5000
```

### 测试多用户场景
打开多个浏览器窗口或使用无痕模式，模拟不同用户：
1. 窗口A: 创建纸条
2. 窗口B: 查看纸条并发送消息
3. 窗口A: 实时接收窗口B的消息

### 数据库操作
```bash
# 数据库表在首次运行时自动创建 (db.create_all() in app.py)

# 重置本地数据库
rm chat_memo.db  # 或在Windows上手动删除
python app.py  # 表将自动重建
```

## 部署到 Render

### 准备工作
```bash
# 1. 创建 GitHub 仓库并推送代码
git init
git add .
git commit -m "Initial commit: Chat Memo app"
git remote add origin <your-repo-url>
git push -u origin main

# 2. 在 Render 上创建新项目
# - 选择 "Web Service"
# - 连接 GitHub 仓库
# - 使用以下配置（自动从 render.yaml 读取）
```

### 环境变量（在 Render 上设置）
```
SECRET_KEY=<自动生成>
DATABASE_URL=<自动创建PostgreSQL数据库>
ADMIN_PASSWORD=admin123  # 可修改
WEB_CONCURRENCY=1  # 保持单进程以共享内存状态
```

### 访问应用
- 首页: `https://chat-memo.onrender.com`
- 管理后台: `https://chat-memo.onrender.com/admin?password=admin123`

## 项目架构

### 数据库模型 (models.py)

```python
# Note - 纸条模型
class Note(db.Model):
    id: Integer, PK
    title: String(200), 必填
    content: Text, 可选
    share_key: String(20), unique, 分享秘钥
    is_public: Boolean, default=True
    view_count: Integer, default=0
    created_at: DateTime, 北京时间
    updated_at: DateTime, 北京时间
    messages: Relationship -> NoteMessage
    tags: Relationship -> Tag (多对多)

# NoteMessage - 消息模型
class NoteMessage(db.Model):
    id: Integer, PK
    note_id: Integer, FK(notes.id)
    sender_name: String(100), 匿名昵称
    content: Text, 必填
    timestamp: DateTime, 北京时间
    message_type: String(20), default='text'

# Tag - 标签模型
class Tag(db.Model):
    id: Integer, PK
    name: String(50), unique
    color: String(7), default='#667eea'
    notes: Relationship -> Note (多对多)
```

### Socket.IO 事件 (app.py)

**客户端 → 服务器**:
- `create_note` - 创建新纸条
- `join_note` - 加入纸条（接收实时消息）
- `leave_note` - 离开纸条
- `send_note_message` - 发送消息
- `get_all_tags` - 获取所有标签
- `create_tag` - 创建新标签
- `delete_note` - 删除纸条（管理员）

**服务器 → 客户端**:
- `note_created` - 纸条创建成功
- `note_joined` - 成功加入纸条，返回历史消息
- `new_note_message` - 新消息广播
- `viewer_count_changed` - 在线人数变化
- `all_tags` - 所有标签列表
- `tag_created` - 标签创建成功
- `note_deleted` - 纸条删除成功
- `error` - 错误提示

### 在线用户追踪

```python
# 全局字典 {note_id: {user_id: {'sid': session_id, 'name': name}}}
note_users = {}

# 用户加入纸条
@socketio.on('join_note')
def handle_join_note(data):
    note_users[note_id][user_id] = {
        'sid': request.sid,
        'name': sender_name
    }

# 广播时使用房间
socketio.emit('new_note_message', {...}, room=note_id)
```

### 前端状态管理 (static/js/app.js)

```javascript
// 全局变量
let currentNoteId = null;
let currentSenderName = '';
let currentShareKey = null;

// 页面识别
if (window.currentNoteId) {
    // 查看纸条页面逻辑
    joinNote();
}

// Socket.IO 事件监听
socket.on('note_joined', (data) => {
    displayMessages(data.messages);
});
```

## 核心文件说明

### 后端文件

- **app.py** - Flask 主应用
  - 路由定义（/, /create, /note/<id>, /share/<key>, /search, /admin）
  - Socket.IO 事件处理
  - 在线用户管理

- **models.py** - 数据库模型
  - Note, NoteMessage, Tag 模型
  - get_beijing_time() 时间处理函数
  - to_dict() 序列化方法

- **config.py** - 配置管理
  - SQLAlchemy 配置（使用 NullPool 兼容 eventlet）
  - Session 配置
  - 数据库 URL 处理

- **utils/share_key_generator.py** - 分享秘钥生成
  - 复用 RoomKeyGenerator 逻辑
  - 生成 8 位唯一秘钥
  - 避免易混淆字符（0OI1l）

### 前端文件

- **templates/index.html** - 首页（纸条列表）
- **templates/create.html** - 创建纸条表单
- **templates/view.html** - 查看纸条（聊天界面）
- **templates/search.html** - 搜索页面
- **templates/admin.html** - 管理后台
- **static/js/app.js** - 前端逻辑
- **static/css/style.css** - 样式文件

### 部署文件

- **wsgi.py** - WSGI 入口
- **render.yaml** - Render 配置
- **requirements.txt** - Python 依赖
- **runtime.txt** - Python 版本 (3.10.6)
- **start.sh** - 启动脚本

## 关键配置细节

### eventlet 兼容性 (config.py)

```python
SQLALCHEMY_ENGINE_OPTIONS = {
    'poolclass': NullPool,  # 必须使用 NullPool
    'pool_pre_ping': True
}
```

**重要**: QueuePool 与 eventlet green threads 不兼容，必须使用 NullPool。

### 时间处理

所有时间戳使用北京时区 (UTC+8)：
```python
def get_beijing_time():
    utc_now = datetime.utcnow()
    beijing_tz = timedelta(hours=8)
    return utc_now + beijing_tz
```

### 分享秘钥生成

```python
# 生成唯一秘钥
existing_keys = set(n.share_key for n in Note.query.filter(...))
share_key = ShareKeyGenerator.generate_unique_key(existing_keys)

# 访问: /share/<share_key>
```

## 常见问题

### 1. 实时消息不显示

检查：
- Socket.IO 连接是否建立（浏览器控制台）
- 用户是否已加入纸条房间
- 消息是否成功保存到数据库

### 2. 数据库连接错误

检查 config.py 中数据库 URL 格式：
```python
# Render 提供 postgres://，需替换为 postgresql://
database_url = database_url.replace('postgres://', 'postgresql://', 1)
```

### 3. 标签不显示

确保标签关联正确：
```python
note.tags.append(tag)  # 多对多关系
db.session.commit()
```

### 4. 搜索无结果

检查：
- 纸条的 is_public 字段是否为 True
- 搜索关键词是否正确
- 标签名称是否匹配

## 开发建议

### 添加新功能时

1. **数据库模型**: 先在 models.py 中定义或修改模型
2. **后端 API**: 在 app.py 中添加路由或 Socket.IO 事件
3. **前端界面**: 在 templates/ 中创建或修改 HTML
4. **前端逻辑**: 在 static/js/app.js 中添加事件处理
5. **样式调整**: 在 static/css/style.css 中修改样式

### 调试技巧

```python
# 打印调试信息
print(f"用户 {user_id} 已连接")

# 查看数据库查询
from sqlalchemy import print_sql
# 在查询前使用

# 浏览器控制台
console.log('调试信息', data);
```

## 性能优化建议

1. **分页加载**: 纸条列表使用分页（当前限制 50 条）
2. **数据库索引**: 为常用查询字段添加索引
   - `share_key`, `is_public`, `tags.name` 已有索引
3. **缓存**: 考虑使用 Redis 缓存热门纸条
4. **全文搜索**: 大量数据时考虑使用 Elasticsearch

## 安全考虑

1. **XSS 防护**: 前端使用 `escapeHtml()` 转义用户输入
2. **CSRF**: 关键操作考虑添加 token 验证
3. **SQL 注入**: 使用 SQLAlchemy ORM 自动防护
4. **内容审核**: 可添加敏感词过滤
5. **频率限制**: 防止滥用（创建、发送消息）

## 项目对比

与原匿名聊天项目的区别：

| 特性 | 匿名聊天 | 聊天备忘录 |
|------|---------|-----------|
| 数据持久化 | 临时 | 永久保存 |
| 用户匹配 | 需要匹配队列 | 直接创建 |
| 内容可见性 | 仅聊天双方 | 所有用户共享 |
| 搜索功能 | 无 | 全文搜索 |
| 标签系统 | 无 | 多标签分类 |
| 分享机制 | 私密房间秘钥 | 公开分享链接 |

## 维护建议

1. 定期备份数据库
2. 监控应用性能和错误日志
3. 定期清理无用的旧纸条（可选）
4. 根据用户反馈优化功能
5. 保持依赖包更新

## 联系与支持

如有问题，请查看：
- Render 部署日志
- 浏览器控制台错误
- Python 错误输出

祝开发顺利！🎉
