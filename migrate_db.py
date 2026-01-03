"""
数据库迁移脚本：为 note_messages 表添加 sender_id 字段
"""
import sqlite3
import os

def migrate_database():
    db_path = 'instance/chat.db'

    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # 检查 sender_id 字段是否已存在
        cursor.execute("PRAGMA table_info(note_messages)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'sender_id' in columns:
            print("sender_id 字段已存在，无需迁移")
            return

        # 添加 sender_id 字段（允许为 NULL，为了兼容旧数据）
        print("正在添加 sender_id 字段...")
        cursor.execute("ALTER TABLE note_messages ADD COLUMN sender_id VARCHAR(50)")

        # 为现有消息设置一个默认的 sender_id（基于 note_id）
        print("正在为现有消息设置 sender_id...")
        cursor.execute("""
            UPDATE note_messages
            SET sender_id = 'legacy_' || id
            WHERE sender_id IS NULL
        """)

        conn.commit()
        print("✅ 数据库迁移成功！")

        # 显示统计信息
        cursor.execute("SELECT COUNT(*) FROM note_messages")
        total = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM note_messages WHERE sender_id LIKE 'legacy_%'")
        migrated = cursor.fetchone()[0]

        print(f"总共 {total} 条消息，其中 {migrated} 条已迁移")

    except Exception as e:
        conn.rollback()
        print(f"❌ 迁移失败: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_database()
