#!/usr/bin/env python3
"""
快速设置脚本 - 创建admin用户
"""

import sqlite3
import bcrypt
import uuid
from datetime import datetime

def setup_admin():
    """设置admin用户"""
    try:
        # 连接数据库
        conn = sqlite3.connect('dev_admin_system.db')
        cursor = conn.cursor()
        
        print("🔍 检查数据库...")
        
        # 创建用户表（如果不存在）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT,
                avatar_url TEXT,
                is_active BOOLEAN DEFAULT 1,
                is_verified BOOLEAN DEFAULT 0,
                is_superuser BOOLEAN DEFAULT 0,
                failed_login_attempts TEXT DEFAULT '0',
                locked_until TIMESTAMP,
                last_login TIMESTAMP,
                verification_token TEXT,
                verification_token_expires TIMESTAMP,
                reset_token TEXT,
                reset_token_expires TIMESTAMP,
                phone TEXT,
                address TEXT,
                bio TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 检查admin用户
        cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        admin_user = cursor.fetchone()
        
        if admin_user:
            print("✅ Admin用户已存在")
            print("   用户名: admin")
            print("   密码: Admin123456")
        else:
            print("👤 创建admin用户...")
            
            # 生成密码哈希
            password = 'Admin123456'
            salt = bcrypt.gensalt()
            password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
            
            # 插入admin用户
            user_id = str(uuid.uuid4())
            cursor.execute('''
                INSERT INTO users (
                    id, username, email, password_hash, full_name,
                    is_active, is_verified, is_superuser, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                'admin',
                'admin@example.com', 
                password_hash,
                '系统管理员',
                1, 1, 1,  # is_active, is_verified, is_superuser
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            print("✅ Admin用户创建成功!")
            print("   用户名: admin")
            print("   密码: Admin123456")
        
        # 检查用户总数
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"📊 数据库中共有 {user_count} 个用户")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 设置失败: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 快速设置Admin用户")
    print("=" * 50)
    
    if setup_admin():
        print("\n✅ 设置完成!")
        print("🌐 现在可以使用以下信息登录:")
        print("   URL: http://127.0.0.1:8050/login")
        print("   用户名: admin")
        print("   密码: Admin123456")
    else:
        print("\n❌ 设置失败!")
    
    print("=" * 50)