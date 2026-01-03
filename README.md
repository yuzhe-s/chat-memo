# 💬 聊天备忘录 (Chat Memo)

一个基于 Web 的实时对话笔记应用，让用户可以创建持久化的纸条并进行多轮对话。

## ✨ 特性

- 📝 **纸条创建** - 创建带标题、内容和标签的纸条
- 💬 **实时对话** - 每个纸条支持类似聊天室的多轮对话
- 🔔 **实时同步** - 使用 WebSocket (Socket.IO) 实现实时消息推送
- 🏷️ **标签系统** - 灵活的多标签分类和筛选
- 🔍 **全文搜索** - 支持标题、内容和标签的组合搜索
- 🔗 **分享链接** - 每个纸条都有唯一的分享秘钥
- 👤 **用户识别** - 使用昵称和用户ID识别消息发送者
- 📊 **管理后台** - 密码保护的管理界面，支持纸条和标签管理
- 👥 **无需登录** - 所有用户共享内容，使用匿名昵称

## 🎨 界面预览

- **首页**: 浏览所有纸条，按标签筛选
- **创建**: 创建新纸条并选择或创建标签
- **对话**: 在纸条中进行实时对话，消息持久化保存
- **搜索**: 通过关键词和标签搜索纸条
- **管理**: 管理所有纸条、标签和统计数据

## 🚀 快速开始

### 前置要求

- Python 3.10+
- pip

### 本地运行

```bash
# 1. 克隆仓库
git clone https://github.com/yuzhe-s/chat-memo.git
cd chat-memo

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动应用（默认端口 5001）
python app.py

# 4. 访问应用
# 打开浏览器访问 http://localhost:5001

# 5. 访问管理后台
# http://localhost:5001/admin?password=admin123
```

### 测试多用户场景

打开多个浏览器窗口或使用无痕模式，模拟不同用户：
- 窗口A: 创建纸条
- 窗口B: 查看纸条并发送消息
- 窗口A: 实时接收窗口B的消息

## 🌐 部署到 Render

### 步骤 1: 准备 GitHub 仓库

```bash
# 如果还没有推送到 GitHub
git add .
git commit -m "Update application"
git push origin main
```

### 步骤 2: 在 Render 上创建项目

1. 访问 [Render](https://render.com)
2. 注册/登录账号
3. 点击 **"New +"** → **"Web Service"**
4. 连接你的 GitHub 仓库 `yuzhe-s/chat-memo`
5. Render 会自动检测并使用 `render.yaml` 配置

### 步骤 3: 配置环境变量

在 Render 的环境变量设置中添加：

```bash
# Python 版本（自动检测）
PYTHON_VERSION=3.10.6

# 管理员密码（可选，默认为 admin123）
ADMIN_PASSWORD=your_secure_password

# 数据库 URL（Render 自动创建 PostgreSQL 数据库）
# Render 会自动设置 DATABASE_URL

# 端口（可选，默认 5001）
PORT=5001

# 保持单进程（重要！用于共享内存状态）
WEB_CONCURRENCY=1
```

### 步骤 4: 创建 PostgreSQL 数据库

1. 在 Render 项目中，点击 **"New +"** → **"PostgreSQL"**
2. 选择免费套餐
3. 数据库创建后，Render 会自动设置 `DATABASE_URL` 环境变量

### 步骤 5: 部署

1. 点击 **"Deploy"** 或 **"Deploy Site"**
2. 等待部署完成（大约 2-3 分钟）
3. 访问你的应用 URL: `https://chat-memo.onrender.com`
4. 管理后台: `https://chat-memo.onrender.com/admin?password=admin123`

### 步骤 6: 配置自动更新

Render 默认会在你推送代码到 GitHub 时自动重新部署。

如需手动部署：
- 在 Render Dashboard 点击 **"Manual Deploy"** → **"Deploy latest commit"**

## 🛠️ 技术栈

- **后端框架**: Flask 3.0
- **实时通信**: Flask-SocketIO + Socket.IO
- **数据库 ORM**: SQLAlchemy
- **数据库**: PostgreSQL (生产) / SQLite (开发)
- **WSGI 服务器**: Gunicorn + eventlet
- **前端**: 原生 JavaScript + Socket.IO Client
- **样式**: CSS3 (渐变、动画、响应式设计)
- **部署平台**: Render

## 📖 功能详解

### 用户识别机制

- **首次访问**: 用户需要输入昵称，昵称保存在浏览器本地存储
- **后续访问**: 自动使用保存的昵称，无需重复输入
- **消息归属**: 每条消息保存 `sender_id`，即使更改昵称也能正确识别自己的消息
- **实时在线**: 显示当前在线人数

### 标签系统

- **创建标签**: 在创建纸条时可以输入新标签名
- **多标签**: 一个纸条可以有多个标签
- **标签搜索**: 支持多标签组合筛选（AND 逻辑）
- **标签管理**: 在管理后台可以查看和删除标签

### 搜索功能

- **关键词搜索**: 搜索标题和内容
- **标签筛选**: 选择多个标签进行筛选
- **组合查询**: 关键词 + 标签组合搜索

### 管理后台

- **统计数据**: 总纸条数、总消息数、活跃标签数
- **纸条管理**: 查看所有纸条，删除不当内容
- **标签管理**: 查看所有标签，删除不需要的标签
- **密码保护**: 通过 URL 参数 `?password=xxx` 访问

## 📁 项目结构

```
chat-memo/
├── app.py                      # Flask 主应用（路由 + Socket.IO）
├── models.py                   # 数据库模型（Note, NoteMessage, Tag）
├── config.py                   # 配置管理（数据库、Session）
├── wsgi.py                     # WSGI 入口（生产环境）
├── render.yaml                 # Render 部署配置
├── requirements.txt            # Python 依赖
├── requirements-prod.txt       # 生产环境依赖
├── runtime.txt                 # Python 版本
├── start.sh                    # 启动脚本
├── migrate_db.py              # 数据库迁移脚本
├── utils/
│   ├── __init__.py
│   └── share_key_generator.py  # 分享秘钥生成工具
├── static/
│   ├── css/
│   │   └── style.css          # 样式文件（响应式、动画）
│   └── js/
│       └── app.js             # 前端逻辑（Socket.IO、UI交互）
├── templates/
│   ├── index.html             # 首页（纸条列表）
│   ├── create.html            # 创建纸条
│   ├── view.html              # 查看纸条（聊天界面）
│   ├── search.html            # 搜索页面
│   └── admin.html             # 管理后台
├── instance/
│   └── chat.db                # SQLite 数据库（本地开发）
├── CLAUDE.md                   # 开发指南（详细）
└── README.md                   # 本文件
```

## 🔧 开发指南

详见 [CLAUDE.md](CLAUDE.md) 获取完整的开发指南，包括：

- 数据库模型详解
- Socket.IO 事件列表
- 在线用户追踪机制
- 常见问题解决
- 性能优化建议
- 安全考虑

### 添加新功能

1. **数据库模型**: 在 `models.py` 中定义或修改模型
2. **后端 API**: 在 `app.py` 中添加路由或 Socket.IO 事件
3. **前端界面**: 在 `templates/` 中创建或修改 HTML
4. **前端逻辑**: 在 `static/js/app.js` 中添加事件处理
5. **样式调整**: 在 `static/css/style.css` 中修改样式

### 数据库迁移

如果修改了数据库模型：

```bash
# 开发环境（SQLite）
# 直接删除数据库，重启应用自动创建
rm instance/chat.db
python app.py

# 生产环境（PostgreSQL）
# 需要手动执行 SQL 迁移或使用 Flask-Migrate
```

## 🔒 安全建议

1. **修改默认密码**: 在生产环境设置强密码作为 `ADMIN_PASSWORD`
2. **内容审核**: 定期检查并删除不当内容
3. **频率限制**: 考虑添加创建和发送消息的频率限制
4. **HTTPS**: Render 自动提供 SSL 证书
5. **XSS 防护**: 前端已实现 HTML 转义

## 🐛 常见问题

### 1. 实时消息不显示

- 检查浏览器控制台是否有 Socket.IO 连接错误
- 确认用户已加入纸条房间
- 查看消息是否成功保存到数据库

### 2. 数据库连接错误

- 检查 `DATABASE_URL` 格式是否正确
- Render 上确保 PostgreSQL 数据库已创建
- 本地开发确保 SQLite 数据库文件存在

### 3. 标签搜索无结果

- 确认纸条的 `is_public` 字段为 `True`
- 检查标签名称是否正确
- 尝试使用单个标签筛选

### 4. 消息发送者显示错误

- 清除浏览器 localStorage: `localStorage.clear()`
- 刷新页面重新输入昵称

## 📊 性能优化

1. **分页加载**: 纸条列表限制 50 条
2. **数据库索引**: `share_key`, `is_public`, `tags.name` 已建立索引
3. **缓存优化**: 考虑使用 Redis 缓存热门纸条
4. **静态资源**: 考虑使用 CDN 加速

## 📝 更新日志

### v1.1.0 (2025-01-03)
- ✅ 修复用户名变更导致历史消息显示错误的问题
- ✅ 修复标签搜索功能
- ✅ 优化 UI 设计，采用淡色背景
- ✅ 添加管理后台标签管理功能
- ✅ 改进用户识别机制，使用 sender_id
- ✅ 优化昵称输入体验，首次设置后自动保存

### v1.0.0
- ✅ 基础纸条和消息功能
- ✅ 实时对话和在线人数显示
- ✅ 标签系统和搜索功能
- ✅ 管理后台基础功能

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📧 联系方式

- GitHub Issues: [提交问题](https://github.com/yuzhe-s/chat-memo/issues)
- 作者: yuzhe-s

---

**⭐ 如果这个项目对你有帮助，请给一个 Star！**
