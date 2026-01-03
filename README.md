# 💬 聊天备忘录 (Chat Memo)

一个基于 Web 的实时对话笔记应用，让用户可以创建持久化的纸条并进行多轮对话。

## ✨ 特性

- 📝 **纸条创建** - 创建带标题、内容和标签的纸条
- 💬 **实时对话** - 每个纸条支持类似聊天室的多轮对话
- 🏷️ **标签系统** - 灵活的多标签分类和筛选
- 🔍 **全文搜索** - 支持标题、内容和标签的组合搜索
- 🔗 **分享链接** - 每个纸条都有唯一的分享链接
- 👥 **无需登录** - 所有用户共享内容，使用匿名昵称
- 📊 **管理后台** - 密码保护的管理界面

## 🚀 快速开始

### 本地运行

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动应用
python app.py

# 3. 访问应用
# 打开浏览器访问 http://localhost:5000
```

### 部署到 Render

1. Fork 或克隆此仓库到你的 GitHub
2. 在 [Render](https://render.com) 上创建新的 Web Service
3. 连接你的 GitHub 仓库
4. Render 会自动检测 `render.yaml` 配置并部署
5. 设置环境变量 `ADMIN_PASSWORD`（可选，默认为 admin123）

## 📸 应用截图

- **首页**: 浏览所有纸条
- **创建**: 创建新纸条并选择标签
- **对话**: 在纸条中进行实时对话
- **搜索**: 通过关键词和标签搜索纸条
- **管理**: 管理所有纸条和统计数据

## 🛠️ 技术栈

- **后端**: Flask 3.0 + Flask-SocketIO + SQLAlchemy
- **前端**: 原生 JavaScript + Socket.IO Client
- **数据库**: PostgreSQL / SQLite
- **部署**: Render + gunicorn + eventlet

## 📖 使用指南

### 创建纸条

1. 点击"创建纸条"按钮
2. 输入标题（必填）和初始内容（可选）
3. 选择或创建标签
4. 点击"创建纸条"

### 查看和对话

1. 在首页点击任意纸条
2. 输入你的昵称
3. 在输入框中发送消息
4. 实时看到其他人的消息

### 分享纸条

1. 在纸条页面点击"分享"按钮
2. 复制分享链接
3. 发送给朋友，他们可以通过链接访问

### 搜索纸条

1. 点击"搜索"按钮
2. 输入关键词
3. 选择标签筛选（可选）
4. 查看搜索结果

### 管理后台

1. 访问 `/admin?password=admin123`
2. 查看统计数据
3. 删除不当内容

## 🔧 开发

详见 [CLAUDE.md](CLAUDE.md) 获取完整的开发指南。

### 项目结构

```
chat-memo/
├── app.py                      # Flask 主应用
├── models.py                   # 数据库模型
├── config.py                   # 配置管理
├── utils/                      # 工具模块
│   └── share_key_generator.py  # 分享秘钥生成
├── static/
│   ├── css/style.css          # 样式文件
│   └── js/app.js              # 前端逻辑
├── templates/                  # HTML 模板
│   ├── index.html             # 首页
│   ├── create.html            # 创建纸条
│   ├── view.html              # 查看纸条
│   ├── search.html            # 搜索页面
│   └── admin.html             # 管理后台
├── CLAUDE.md                   # 开发指南
└── README.md                   # 本文件
```

## 📝 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

如有问题或建议，请提交 Issue。
