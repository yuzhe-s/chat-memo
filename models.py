from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

db = SQLAlchemy()


def get_beijing_time():
    """获取北京时间 (UTC+8)"""
    utc_now = datetime.utcnow()
    beijing_tz = timedelta(hours=8)
    return utc_now + beijing_tz


# 纸条-标签关联表（多对多）
note_tags = db.Table('note_tags',
    db.Column('note_id', db.Integer, db.ForeignKey('notes.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
)


class Note(db.Model):
    """纸条模型"""
    __tablename__ = 'notes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=True)
    share_key = db.Column(db.String(20), unique=True, nullable=True, index=True)
    is_public = db.Column(db.Boolean, default=True, index=True)
    view_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=get_beijing_time)
    updated_at = db.Column(db.DateTime, default=get_beijing_time, onupdate=get_beijing_time)

    # 关联关系
    messages = db.relationship('NoteMessage', backref='note', lazy=True, cascade='all, delete-orphan')
    tags = db.relationship('Tag', secondary=note_tags, backref=db.backref('notes', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'share_key': self.share_key,
            'is_public': self.is_public,
            'view_count': self.view_count,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'message_count': len(self.messages),
            'tags': [tag.to_dict() for tag in self.tags]
        }


class NoteMessage(db.Model):
    """纸条消息模型"""
    __tablename__ = 'note_messages'

    id = db.Column(db.Integer, primary_key=True)
    note_id = db.Column(db.Integer, db.ForeignKey('notes.id'), nullable=False)
    sender_name = db.Column(db.String(100), nullable=False)
    sender_id = db.Column(db.String(50), nullable=False)  # 添加发送者ID字段
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=get_beijing_time)
    message_type = db.Column(db.String(20), default='text')

    def to_dict(self):
        return {
            'id': self.id,
            'note_id': self.note_id,
            'sender_name': self.sender_name,
            'sender_id': self.sender_id,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'message_type': self.message_type
        }


class Tag(db.Model):
    """标签模型"""
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    color = db.Column(db.String(7), default='#667eea')
    created_at = db.Column(db.DateTime, default=get_beijing_time)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'color': self.color,
            'note_count': len(self.notes)
        }
