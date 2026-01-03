from flask import Flask, render_template, session, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_session import Session
from models import db, Note, NoteMessage, Tag
from config import Config
from utils.share_key_generator import ShareKeyGenerator
import uuid
import os

# 初始化Flask应用
app = Flask(__name__)
app.config.from_object(Config)

# 初始化扩展
db.init_app(app)
Session(app)
socketio = SocketIO(app, cors_allowed_origins="*", manage_session=False)

# 全局在线用户追踪 {note_id: {user_id: {'sid': session_id, 'name': name}}}
note_users = {}


@app.route('/')
def index():
    """首页 - 纸条列表"""
    # 生成用户ID
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())[:8]

    notes = Note.query.filter_by(is_public=True).order_by(Note.updated_at.desc()).limit(50).all()
    all_tags = Tag.query.all()

    return render_template('index.html',
                         user_id=session['user_id'],
                         notes=notes,
                         tags=all_tags)


@app.route('/create')
def create():
    """创建纸条页面"""
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())[:8]

    all_tags = Tag.query.all()
    return render_template('create.html', user_id=session['user_id'], tags=all_tags)


@app.route('/note/<int:note_id>')
def view_note(note_id):
    """查看纸条"""
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())[:8]

    note = Note.query.get_or_404(note_id)
    note.view_count += 1
    db.session.commit()

    return render_template('view.html', note=note, user_id=session['user_id'])


@app.route('/share/<share_key>')
def share_note(share_key):
    """通过分享秘钥访问纸条"""
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())[:8]

    note = Note.query.filter_by(share_key=share_key).first_or_404()
    note.view_count += 1
    db.session.commit()

    return render_template('view.html', note=note, user_id=session['user_id'])


@app.route('/search')
def search():
    """搜索页面"""
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())[:8]

    all_tags = Tag.query.all()
    return render_template('search.html', user_id=session['user_id'], tags=all_tags)


@app.route('/api/search')
def api_search():
    """搜索纸条API"""
    query = request.args.get('q', '')
    tags = request.args.getlist('tags')

    # 基础查询
    notes_query = Note.query.filter_by(is_public=True)

    # 关键词搜索
    if query:
        notes_query = notes_query.filter(
            db.or_(
                Note.title.contains(query),
                Note.content.contains(query)
            )
        )

    # 标签筛选 - 修复多标签筛选逻辑
    if tags:
        # 使用子查询，找到包含所有指定标签的纸条
        for tag_name in tags:
            notes_query = notes_query.filter(
                Note.tags.any(Tag.name == tag_name)
            )

    notes = notes_query.distinct().order_by(Note.updated_at.desc()).limit(50).all()
    return jsonify({'notes': [note.to_dict() for note in notes]})


@app.route('/admin')
def admin():
    """管理后台 - 密码保护"""
    password = request.args.get('password')
    if password != os.environ.get('ADMIN_PASSWORD', 'admin123'):
        return "未授权访问", 401

    # 统计数据
    stats = {
        'total_notes': Note.query.count(),
        'total_messages': NoteMessage.query.count(),
        'active_tags': Tag.query.count()
    }

    notes = Note.query.order_by(Note.created_at.desc()).all()
    tags = Tag.query.order_by(Tag.name).all()
    return render_template('admin.html', stats=stats, notes=notes, tags=tags)


# ========== Socket.IO 事件处理 ==========

@socketio.on('connect')
def handle_connect():
    """处理WebSocket连接"""
    user_id = session.get('user_id')
    if user_id:
        print(f"用户 {user_id} 已连接")


@socketio.on('disconnect')
def handle_disconnect():
    """处理连接断开"""
    user_id = session.get('user_id')
    if not user_id:
        return

    # 从所有纸条中移除用户
    for note_id in list(note_users.keys()):
        if user_id in note_users[note_id]:
            del note_users[note_id][user_id]

            # 通知其他用户
            socketio.emit('viewer_count_changed', {
                'note_id': note_id,
                'count': len(note_users[note_id])
            }, room=note_id)

    print(f"用户 {user_id} 已断开连接")


@socketio.on('create_note')
def handle_create_note(data):
    """创建新纸条"""
    user_id = session.get('user_id')
    if not user_id:
        emit('error', {'message': '无效的用户ID'})
        return

    title = data.get('title', '').strip()
    content = data.get('content', '').strip()
    tag_names = data.get('tags', [])
    is_public = data.get('is_public', True)

    if not title:
        emit('error', {'message': '标题不能为空'})
        return

    # 生成唯一分享秘钥
    existing_keys = set(n.share_key for n in Note.query.filter(Note.share_key.isnot(None)).all())
    share_key = ShareKeyGenerator.generate_unique_key(existing_keys)

    # 创建纸条
    note = Note(
        title=title,
        content=content,
        share_key=share_key,
        is_public=is_public
    )

    # 处理标签
    for tag_name in tag_names:
        tag = Tag.query.filter_by(name=tag_name).first()
        if not tag:
            tag = Tag(name=tag_name)
            db.session.add(tag)
        note.tags.append(tag)

    db.session.add(note)
    db.session.commit()

    emit('note_created', {'note': note.to_dict()})


@socketio.on('join_note')
def handle_join_note(data):
    """加入纸条（接收实时消息）"""
    user_id = session.get('user_id')
    if not user_id:
        emit('error', {'message': '无效的用户ID'})
        return

    note_id = data['note_id']
    sender_name = data.get('sender_name', f'用户{user_id}').strip()

    if not sender_name:
        sender_name = f'用户{user_id}'

    # 加入 Socket.IO 房间
    join_room(note_id)

    # 记录在线用户
    if note_id not in note_users:
        note_users[note_id] = {}
    note_users[note_id][user_id] = {
        'sid': request.sid,
        'name': sender_name
    }

    # 加载历史消息
    messages = NoteMessage.query.filter_by(note_id=note_id).order_by(NoteMessage.timestamp.asc()).all()

    emit('note_joined', {
        'note_id': note_id,
        'messages': [msg.to_dict() for msg in messages],
        'viewer_count': len(note_users[note_id])
    })

    # 通知其他用户
    socketio.emit('viewer_count_changed', {
        'note_id': note_id,
        'count': len(note_users[note_id])
    }, room=note_id, include_self=False)

    print(f"用户 {user_id} ({sender_name}) 加入纸条 {note_id}")


@socketio.on('leave_note')
def handle_leave_note(data):
    """离开纸条"""
    user_id = session.get('user_id')
    if not user_id:
        return

    note_id = data['note_id']
    leave_room(note_id)

    if note_id in note_users and user_id in note_users[note_id]:
        del note_users[note_id][user_id]

        # 通知其他用户
        socketio.emit('viewer_count_changed', {
            'note_id': note_id,
            'count': len(note_users[note_id])
        }, room=note_id)

    print(f"用户 {user_id} 离开纸条 {note_id}")


@socketio.on('send_note_message')
def handle_send_note_message(data):
    """发送消息到纸条"""
    user_id = session.get('user_id')
    if not user_id:
        emit('error', {'message': '无效的用户ID'})
        return

    note_id = data['note_id']
    sender_name = data.get('sender_name', f'用户{user_id}').strip()
    content = data['content'].strip()

    if not sender_name:
        sender_name = f'用户{user_id}'

    if not content:
        return

    # 消息长度限制
    if len(content) > 500:
        emit('error', {'message': '消息长度不能超过500字符'})
        return

    # 保存消息
    message = NoteMessage(
        note_id=note_id,
        sender_name=sender_name,
        sender_id=user_id,
        content=content
    )
    db.session.add(message)

    # 更新纸条时间
    note = Note.query.get(note_id)
    if note:
        from models import get_beijing_time
        note.updated_at = get_beijing_time()

    db.session.commit()

    # 广播消息
    socketio.emit('new_note_message', {
        'message': message.to_dict()
    }, room=note_id)

    print(f"纸条 {note_id}: {sender_name} 发送消息")


@socketio.on('get_all_tags')
def handle_get_all_tags():
    """获取所有标签"""
    tags = Tag.query.all()
    emit('all_tags', {'tags': [tag.to_dict() for tag in tags]})


@socketio.on('create_tag')
def handle_create_tag(data):
    """创建新标签"""
    tag_name = data.get('name', '').strip()
    color = data.get('color', '#667eea')

    if not tag_name:
        emit('error', {'message': '标签名不能为空'})
        return

    # 检查标签是否已存在
    existing_tag = Tag.query.filter_by(name=tag_name).first()
    if existing_tag:
        emit('error', {'message': '标签已存在'})
        return

    # 创建标签
    tag = Tag(name=tag_name, color=color)
    db.session.add(tag)
    db.session.commit()

    emit('tag_created', {'tag': tag.to_dict()}, broadcast=True)


@socketio.on('delete_note')
def handle_delete_note(data):
    """删除纸条（仅管理员）"""
    note_id = data['note_id']
    note = Note.query.get(note_id)

    if note:
        db.session.delete(note)
        db.session.commit()
        emit('note_deleted', {'note_id': note_id}, broadcast=True)
        print(f"纸条 {note_id} 已删除")
    else:
        emit('error', {'message': '纸条不存在'})


@socketio.on('delete_tag')
def handle_delete_tag(data):
    """删除标签（仅管理员）"""
    tag_id = data['tag_id']
    tag = Tag.query.get(tag_id)

    if tag:
        tag_name = tag.name
        db.session.delete(tag)
        db.session.commit()
        emit('tag_deleted', {'tag_id': tag_id, 'tag_name': tag_name}, broadcast=True)
        print(f"标签 {tag_name} (ID: {tag_id}) 已删除")
    else:
        emit('error', {'message': '标签不存在'})


if __name__ == '__main__':
    # 创建数据库表
    with app.app_context():
        db.create_all()
        print("数据库表已创建")

    # 启动应用
    port = int(os.environ.get('PORT', 5001))  # 默认使用 5001 端口
    print(f"聊天备忘录启动在 http://localhost:{port}")
    socketio.run(app, debug=True, host='0.0.0.0', port=port)
