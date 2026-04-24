# -*- coding: utf-8 -*-
"""
清空数据库并重新精确导入CSV数据
"""
import csv
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = r'C:\Users\DELL\Downloads\岗位数据\岗位数据'

sys.path.insert(0, BASE_DIR)
from app import create_app
from models import db, User, Resume, Job, Delivery, MatchResult, Favorite, BrowseHistory, Analytics, SystemLog, Message
from werkzeug.security import generate_password_hash

app = create_app()


def clear_all_data():
    """清空所有数据（保持表结构）"""
    with app.app_context():
        print("\n清空所有数据...")

        # 删除顺序：先删子表，再删父表
        MatchResult.query.delete()
        Delivery.query.delete()
        Favorite.query.delete()
        BrowseHistory.query.delete()
        Analytics.query.delete()
        SystemLog.query.delete()
        Message.query.delete()
        Resume.query.delete()
        Job.query.delete()
        User.query.filter_by(role='user').delete()
        db.session.commit()

        print("  已清空所有投递、简历、岗位和求职者数据")

        # 确认清空
        print(f"\n确认清空后:")
        print(f"  Jobs: {Job.query.count()}")
        print(f"  Users(candidates): {User.query.filter_by(role='user').count()}")
        print(f"  Resumes: {Resume.query.count()}")
        print(f"  Deliveries: {Delivery.query.count()}")


def import_jobs():
    """导入岗位数据"""
    jobs_file = os.path.join(DATA_DIR, 'jobs.csv')
    count = 0

    with app.app_context():
        # 获取HR用户
        hr_user = User.query.filter_by(role='hr').first()
        if not hr_user:
            hr_user = User(
                username='hr',
                password=generate_password_hash('hr123'),
                name='企业HR',
                phone='13800138001',
                email='hr@company.com',
                role='hr',
                company='招聘公司'
            )
            db.session.add(hr_user)
            db.session.commit()
            db.session.refresh(hr_user)

        print(f"\n导入岗位数据...")
        batch = []

        with open(jobs_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)

            for row in reader:
                try:
                    salary_min = int(float(row.get('salary_min', 0))) if row.get('salary_min') else None
                    salary_max = int(float(row.get('salary_max', 0))) if row.get('salary_max') else None
                    salary_avg = int(float(row.get('salary_avg', 0))) if row.get('salary_avg') else None
                    views = int(float(row.get('views', 0))) if row.get('views') else 0

                    job = Job(
                        hr_id=hr_user.id,
                        original_id=row.get('job_id', '').strip(),  # 保存原始ID用于匹配
                        title=row.get('job_title', '').strip(),
                        city=row.get('city', '').strip(),
                        salary_min=salary_min,
                        salary_max=salary_max,
                        salary_avg=salary_avg,
                        company_name=row.get('company_name', '').strip(),
                        company_size=row.get('company_size', '').strip(),
                        company_type=row.get('company_type', '').strip(),
                        job_category=row.get('job_category', '').strip(),
                        education_req=row.get('education', '').strip(),
                        experience_req=row.get('experience', '').strip(),
                        skills_req=row.get('skills', '').strip(),
                        responsibilities=row.get('job_description', '').strip(),
                        requirements=row.get('requirements', '').strip(),
                        views=views,
                        publish_date=row.get('publish_date', '').strip(),
                        status='招聘中'
                    )
                    batch.append(job)
                    count += 1

                    if count % 500 == 0:
                        db.session.add_all(batch)
                        db.session.commit()
                        batch = []
                        print(f"  已导入 {count} 个岗位...")

                except Exception as e:
                    continue

            if batch:
                db.session.add_all(batch)
                db.session.commit()

        print(f"\n岗位导入完成: {count} 个")
        return count


def import_candidates():
    """导入求职者数据"""
    candidates_file = os.path.join(DATA_DIR, 'candidates.csv')
    count = 0

    with app.app_context():
        print(f"\n导入求职者数据...")
        users_batch = []
        resumes_batch = []

        with open(candidates_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)

            for row in reader:
                try:
                    candidate_id = row.get('candidate_id', '').strip()
                    username = candidate_id.lower()

                    # 解析期望城市
                    preferred_cities = ''
                    try:
                        pc = row.get('preferred_cities', '')
                        if pc.startswith('['):
                            import ast
                            preferred_cities = ','.join(ast.literal_eval(pc))
                    except:
                        pass

                    # 解析期望岗位类别
                    preferred_categories = ''
                    try:
                        pcat = row.get('preferred_categories', '')
                        if pcat.startswith('['):
                            import ast
                            preferred_categories = ','.join(ast.literal_eval(pcat))
                    except:
                        pass

                    # 解析期望薪资
                    expected_salary_min = None
                    expected_salary_max = None
                    try:
                        if row.get('expected_salary_min'):
                            expected_salary_min = int(float(row.get('expected_salary_min', 0)))
                    except:
                        pass
                    try:
                        if row.get('expected_salary_max'):
                            expected_salary_max = int(float(row.get('expected_salary_max', 0)))
                    except:
                        pass

                    user = User(
                        username=username,
                        password=generate_password_hash('password123'),
                        name=row.get('name', '').strip(),
                        role='user',
                        is_active=True
                    )
                    users_batch.append(user)

                    resume = Resume(
                        user_id=None,  # 稍后设置
                        real_name=row.get('name', '').strip(),
                        gender=row.get('gender', '').strip(),
                        education=row.get('education', '').strip(),
                        skills=row.get('skills', '').strip(),
                        self_eval=row.get('self_introduction', '').strip(),
                        experience=row.get('experience', '').strip(),
                        current_city=row.get('current_city', '').strip(),
                        expected_city=preferred_cities,
                        expected_salary_min=expected_salary_min,
                        expected_salary_max=expected_salary_max,
                        preferred_categories=preferred_categories,
                        status='未投递'
                    )
                    resumes_batch.append(resume)
                    count += 1

                    if count % 200 == 0:
                        db.session.add_all(users_batch)
                        db.session.flush()
                        for i, resume in enumerate(resumes_batch):
                            resume.user_id = users_batch[i].id
                        db.session.add_all(resumes_batch)
                        db.session.commit()
                        users_batch = []
                        resumes_batch = []
                        print(f"  已导入 {count} 个求职者...")

                except Exception as e:
                    continue

            if users_batch:
                db.session.add_all(users_batch)
                db.session.flush()
                for i, resume in enumerate(resumes_batch):
                    resume.user_id = users_batch[i].id
                db.session.add_all(resumes_batch)
                db.session.commit()

        print(f"\n求职者导入完成: {count} 个用户, {count} 份简历")
        return count


def import_applications():
    """精确导入投递记录（使用original_id匹配）"""
    apps_file = os.path.join(DATA_DIR, 'applications.csv')
    count = 0
    skipped = 0
    errors = 0

    with app.app_context():
        print(f"\n精确导入投递记录...")

        # 创建岗位映射: CSV原始ID -> 数据库ID
        job_map = {}
        jobs = Job.query.all()
        for job in jobs:
            if job.original_id:
                job_map[job.original_id] = job.id

        print(f"  已创建岗位映射: {len(job_map)} 个")
        print(f"  CSV岗位ID示例: JOB770487 -> DB ID: {job_map.get('JOB770487', 'N/A')}")

        deliveries_batch = []
        matches_batch = []

        with open(apps_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)

            for row in reader:
                try:
                    # 获取岗位（使用精确匹配）
                    csv_job_id = row.get('job_id', '').strip()
                    db_job_id = job_map.get(csv_job_id)

                    if not db_job_id:
                        skipped += 1
                        continue

                    # 获取用户
                    username = row.get('candidate_id', '').lower().strip()
                    user = User.query.filter_by(username=username).first()
                    if not user:
                        skipped += 1
                        continue

                    # 获取简历
                    resume = Resume.query.filter_by(user_id=user.id).first()
                    if not resume:
                        skipped += 1
                        continue

                    # 检查是否已存在（防止重复）
                    existing = Delivery.query.filter_by(
                        user_id=user.id, job_id=db_job_id
                    ).first()
                    if existing:
                        skipped += 1
                        continue

                    # 解析分数
                    total_score = float(row.get('total_match_score', 0)) * 100
                    skill_score = float(row.get('skill_match_score', 0)) * 100
                    salary_score = float(row.get('salary_match_score', 0)) * 100
                    edu_score = float(row.get('education_match_score', 0)) * 100
                    exp_score = float(row.get('experience_match_score', 0)) * 100

                    # 创建投递
                    delivery = Delivery(
                        user_id=user.id,
                        job_id=db_job_id,
                        resume_id=resume.id,
                        match_score=total_score,
                        skill_match_score=skill_score,
                        salary_match_score=salary_score,
                        education_match_score=edu_score,
                        experience_match_score=exp_score,
                        is_matched=bool(int(row.get('is_matched', 0))),
                        status=row.get('status', '待处理')
                    )
                    deliveries_batch.append(delivery)

                    # 创建匹配结果
                    match = MatchResult(
                        resume_id=resume.id,
                        job_id=db_job_id,
                        similarity_score=float(row.get('total_match_score', 0)),
                        final_score=total_score,
                        education_score=edu_score,
                        skill_score=skill_score,
                        experience_score=exp_score,
                        match_details='{}'
                    )
                    matches_batch.append(match)

                    count += 1

                    # 批量提交
                    if count % 100 == 0:
                        db.session.add_all(deliveries_batch)
                        db.session.add_all(matches_batch)
                        db.session.commit()
                        deliveries_batch = []
                        matches_batch = []
                        if count % 1000 == 0:
                            print(f"  已导入 {count} 条投递记录...")

                except Exception as e:
                    errors += 1
                    if errors <= 5:
                        print(f"  错误: {e}")
                    db.session.rollback()
                    continue

            # 提交剩余
            if deliveries_batch:
                db.session.add_all(deliveries_batch)
                db.session.add_all(matches_batch)
                db.session.commit()

        print(f"\n投递记录导入完成!")
        print(f"  成功: {count} 条")
        print(f"  跳过: {skipped} 条")
        print(f"  错误: {errors} 条")
        return count, skipped, errors


def verify_import():
    """验证导入结果"""
    with app.app_context():
        print("\n" + "=" * 60)
        print("导入验证结果")
        print("=" * 60)
        print(f"岗位: {Job.query.count()} 个")
        print(f"求职者: {User.query.filter_by(role='user').count()} 人")
        print(f"简历: {Resume.query.count()} 份")
        print(f"投递: {Delivery.query.count()} 条")
        print(f"匹配: {MatchResult.query.count()} 条")

        # 验证投递是否正确关联
        print("\n投递关联验证（随机抽取5条）:")
        deliveries = Delivery.query.limit(5).all()
        for d in deliveries:
            user = User.query.get(d.user_id)
            job = Job.query.get(d.job_id)
            resume = Resume.query.get(d.resume_id)

            print(f"  投递ID={d.id}:")
            print(f"    用户: {user.username if user else 'N/A'} ({user.name if user else 'N/A'})")
            print(f"    岗位: {job.original_id if job else 'N/A'} - {job.title[:25] if job else 'N/A'}...")
            print(f"    匹配分: {d.match_score:.1f}")


def main():
    """主函数"""
    print("=" * 60)
    print("精确数据导入工具 - 清空重新导入")
    print("=" * 60)

    # 1. 清空所有数据
    clear_all_data()

    # 2. 导入岗位
    import_jobs()

    # 3. 导入求职者
    import_candidates()

    # 4. 精确导入投递记录
    import_applications()

    # 5. 验证结果
    verify_import()


if __name__ == '__main__':
    main()
