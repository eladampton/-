# -*- coding: utf-8 -*-
"""
MySQL数据库初始化脚本
运行此脚本创建数据库和表结构
"""
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

def create_database_if_not_exists():
    """如果数据库不存在则创建（不删除现有数据）"""
    try:
        import pymysql

        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='lijuan',
            port=3306,
            charset='utf8mb4'
        )
        cursor = conn.cursor()

        # 检查数据库是否已存在
        cursor.execute("SHOW DATABASES LIKE 'campus_recruitment'")
        if cursor.fetchone():
            print("[OK] 数据库 campus_recruitment 已存在（保留现有数据）")
        else:
            cursor.execute("CREATE DATABASE campus_recruitment CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print("[OK] 数据库 campus_recruitment 创建成功")

        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"[FAIL] 数据库操作失败: {e}")
        print("请确保MySQL服务已启动且账号密码正确")
        return False


def init_tables():
    """初始化数据库表"""
    try:
        from app import create_app
        from models import db, init_db

        app = create_app('development')
        with app.app_context():
            db.create_all()
            print("[OK] 数据库表创建成功")

            # 初始化默认用户
            init_db(app)
            print("[OK] 默认用户创建成功")

        return True
    except Exception as e:
        print(f"[FAIL] 初始化表失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("=" * 50)
    print("MySQL数据库初始化工具")
    print("=" * 50)
    print("")

    # 检查依赖
    try:
        import pymysql
        print("[OK] PyMySQL 已安装")
    except ImportError:
        print("[FAIL] 请先安装PyMySQL: pip install PyMySQL cryptography")
        return

    try:
        import flask_sqlalchemy
        print("[OK] Flask-SQLAlchemy 已安装")
    except ImportError:
        print("[FAIL] 请先安装Flask-SQLAlchemy: pip install -r requirements.txt")
        return

    print("")
    print("步骤1: 检查/创建数据库...")
    if not create_database_if_not_exists():
        return

    print("")
    print("步骤2: 初始化表结构...")
    if not init_tables():
        return

    print("")
    print("=" * 50)
    print("数据库初始化完成!")
    print("=" * 50)
    print("")
    print("默认账号:")
    print("  管理员: admin / admin123")
    print("  HR: hr / hr123")
    print("  求职者: user / user123")
    print("")
    print("现在可以运行应用: python app.py")


if __name__ == '__main__':
    main()
