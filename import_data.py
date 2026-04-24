# -*- coding: utf-8 -*-
"""
数据导入脚本
- 导入岗位数据、求职者数据、投递数据到数据库
- 保留现有数据库
- 自动创建不存在的表
"""
import os
import sys
import csv
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

DATA_DIR = r"C:\Users\DELL\Downloads\岗位数据\岗位数据"


def create_database_if_not_exists():
    """如果不存在则创建数据库"""
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

        # 检查数据库是否存在
        cursor.execute("SHOW DATABASES LIKE 'campus_recruitment'")
        if not cursor.fetchone():
            cursor.execute("CREATE DATABASE campus_recruitment CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print("[OK] 数据库 campus_recruitment 创建成功")
        else:
            print("[OK] 数据库 campus_recruitment 已存在")

        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"[FAIL] 数据库操作失败: {e}")
        return False


def import_data():
    """导入CSV数据到数据库"""
    try:
        from app import create_app
        from models import db, User, Job, Resume, Delivery
        from werkzeug.security import generate_password_hash

        app = create_app('development')

        with app.app_context():
            # 创建所有表（如果不存在）
            db.create_all()
            print("[OK] 数据库表创建/更新成功")

            # 检查是否已有HR账号，没有则创建
            hr = User.query.filter_by(role='hr').first()
            if not hr:
                hr = User(
                    username='hr',
                    password=generate_password_hash('hr123'),
                    name='数据HR',
                    phone='13800138001',
                    email='hr@data.com',
                    role='hr',
                    company='数据导入公司'
                )
                db.session.add(hr)
                db.session.commit()
                print(f"[OK] 创建HR账号: hr / hr123 (ID: {hr.id})")
            else:
                print(f"[OK] 使用已有HR账号 (ID: {hr.id})")

            # 导入岗位数据
            jobs_file = os.path.join(DATA_DIR, 'jobs.csv')
            if os.path.exists(jobs_file):
                import_jobs(jobs_file, hr.id)
            else:
                print(f"[WARN] 未找到岗位数据文件: {jobs_file}")

            # 导入求职者数据
            candidates_file = os.path.join(DATA_DIR, 'candidates.csv')
            if os.path.exists(candidates_file):
                import_candidates(candidates_file)
            else:
                print(f"[WARN] 未找到求职者数据文件: {candidates_file}")

            # 导入投递数据
            applications_file = os.path.join(DATA_DIR, 'applications.csv')
            if os.path.exists(applications_file):
                import_applications(applications_file)
            else:
                print(f"[WARN] 未找到投递数据文件: {applications_file}")

        return True
    except Exception as e:
        print(f"[FAIL] 导入数据失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def import_jobs(filepath, hr_id):
    """导入岗位数据"""
    from models import Job, db

    print(f"\n[*] 正在导入岗位数据...")

    count = 0
    existing = Job.query.count()

    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 检查是否已存在（通过original_id）
            if Job.query.filter_by(original_id=row.get('job_id')).first():
                continue

            # 解析薪资
            salary_min = parse_number(row.get('salary_min', 0))
            salary_max = parse_number(row.get('salary_max', 0))
            salary_avg = parse_number(row.get('salary_avg', 0))

            job = Job(
                original_id=row.get('job_id'),
                hr_id=hr_id,
                title=row.get('job_title', ''),
                job_category=row.get('job_category', ''),
                company_name=row.get('company_name', ''),
                company_size=row.get('company_size', ''),
                company_type=row.get('company_type', ''),
                city=row.get('city', ''),
                education_req=row.get('education', ''),
                experience_req=row.get('experience', ''),
                salary_min=salary_min,
                salary_max=salary_max,
                salary_avg=salary_avg,
                skills_req=row.get('skills', ''),
                responsibilities=row.get('job_description', ''),
                requirements=row.get('requirements', ''),
                publish_date=row.get('publish_date', ''),
                views=parse_number(row.get('views', 0)),
                status='招聘中'
            )
            db.session.add(job)
            count += 1

            # 每100条提交一次
            if count % 100 == 0:
                db.session.commit()
                print(f"  ...已导入 {count} 条")

    db.session.commit()
    print(f"[OK] 岗位数据导入完成: {count} 条新记录 (原有 {existing} 条)")


def import_candidates(filepath):
    """导入求职者数据"""
    from models import User, Resume, db
    from werkzeug.security import generate_password_hash

    print(f"\n[*] 正在导入求职者数据...")

    count = 0
    existing = User.query.filter_by(role='user').count()

    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            candidate_id = row.get('candidate_id')

            # 检查是否已存在（通过original_id或用户名）
            if User.query.filter_by(username=candidate_id).first():
                continue

            # 创建用户账号
            user = User(
                username=candidate_id,
                password=generate_password_hash('123456'),
                name=row.get('name', ''),
                phone='13800000000',
                email=f"{candidate_id}@test.com",
                role='user'
            )
            db.session.add(user)
            db.session.flush()  # 获取user.id

            # 创建简历
            resume = Resume(
                user_id=user.id,
                real_name=row.get('name', ''),
                gender=row.get('gender', ''),
                age=parse_number(row.get('age', 0)),
                education=row.get('education', ''),
                current_city=row.get('current_city', ''),
                expected_city=row.get('preferred_cities', ''),
                preferred_categories=row.get('preferred_categories', ''),
                skills=row.get('skills', ''),
                expected_salary_min=parse_number(row.get('expected_salary_min', 0)),
                expected_salary_max=parse_number(row.get('expected_salary_max', 0)),
                experience='应届生' if row.get('experience', '') == '不限' else row.get('experience', ''),
                self_eval=row.get('self_introduction', '')
            )
            db.session.add(resume)
            count += 1

            if count % 100 == 0:
                db.session.commit()
                print(f"  ...已导入 {count} 条")

    db.session.commit()
    print(f"[OK] 求职者数据导入完成: {count} 条新记录 (原有 {existing} 条)")


def import_applications(filepath):
    """导入投递数据"""
    from models import Delivery, Job, User, Resume, db

    print(f"\n[*] 正在导入投递数据...")

    count = 0
    skipped = 0
    existing = Delivery.query.count()

    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            job_original_id = row.get('job_id')
            candidate_id = row.get('candidate_id')

            # 查找对应的job和user
            job = Job.query.filter_by(original_id=job_original_id).first()
            user = User.query.filter_by(username=candidate_id).first()

            if not job or not user:
                skipped += 1
                continue

            # 查找简历
            resume = Resume.query.filter_by(user_id=user.id).first()
            resume_id = resume.id if resume else None

            # 检查是否已存在投递
            existing_delivery = Delivery.query.filter_by(
                user_id=user.id,
                job_id=job.id
            ).first()
            if existing_delivery:
                continue

            # 解析匹配分数
            total_score = float(row.get('total_match_score', 0)) * 100

            # 映射状态
            status_map = {
                '已投递': '待查看',
                '已查看': '已查看',
                '面试中': '面试邀请',
                '已录用': '已录用',
                '已拒绝': '不合适'
            }
            status = status_map.get(row.get('status', ''), '待查看')

            # 判断是否匹配
            is_matched = int(row.get('is_matched', 0)) == 1

            delivery = Delivery(
                user_id=user.id,
                job_id=job.id,
                resume_id=resume_id,
                status=status,
                match_score=round(total_score, 2),
                skill_match_score=float(row.get('skill_match_score', 0)) * 100,
                salary_match_score=float(row.get('salary_match_score', 0)) * 100,
                education_match_score=float(row.get('education_match_score', 0)) * 100,
                experience_match_score=float(row.get('experience_match_score', 0)) * 100,
                is_matched=is_matched
            )
            db.session.add(delivery)
            count += 1

            if count % 100 == 0:
                db.session.commit()
                print(f"  ...已导入 {count} 条 (跳过 {skipped} 条)")

    db.session.commit()
    print(f"[OK] 投递数据导入完成: {count} 条新记录, 跳过 {skipped} 条 (原有 {existing} 条)")


def parse_number(value, default=0):
    """解析数字"""
    if value is None or value == '':
        return default
    try:
        return int(float(value))
    except:
        return default


def init_default_users():
    """初始化默认用户（如果不存在）"""
    try:
        from app import create_app
        from models import db, User, init_db

        app = create_app('development')
        with app.app_context():
            # 检查是否已有管理员账号
            admin = User.query.filter_by(role='admin').first()
            if not admin:
                init_db(app)
                print("[OK] 已创建默认管理员账号: admin / admin123")
            else:
                print("[OK] 管理员账号已存在")

        return True
    except Exception as e:
        print(f"[FAIL] 初始化默认用户失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("=" * 60)
    print("数据导入工具")
    print("=" * 60)
    print("")
    print(f"数据目录: {DATA_DIR}")
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

    # 检查数据目录
    if not os.path.exists(DATA_DIR):
        print(f"[FAIL] 数据目录不存在: {DATA_DIR}")
        print("请确认下载的数据文件位置")
        return

    print("")
    print("步骤1: 检查/创建数据库...")
    if not create_database_if_not_exists():
        return

    print("")
    print("步骤2: 导入CSV数据...")
    if not import_data():
        return

    print("")
    print("步骤3: 检查默认用户...")
    init_default_users()

    print("")
    print("=" * 60)
    print("数据导入完成!")
    print("=" * 60)
    print("")
    print("默认账号:")
    print("  管理员: admin / admin123")
    print("  HR: hr / hr123")
    print("  求职者: user / user123 (或CSV中的候选人ID / 123456)")
    print("")
    print("现在可以运行应用: python app.py")


if __name__ == '__main__':
    main()
