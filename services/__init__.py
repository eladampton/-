# -*- coding: utf-8 -*-
"""
服务层 - 业务逻辑封装
"""
from models import db, User, Resume, Job, Delivery, MatchResult, SystemLog
from sqlalchemy import func, and_
import json


class UserService:
    """用户服务"""

    @staticmethod
    def create_user(username, password, name, phone='', email='', role='user', company=None):
        """创建用户"""
        user = User(
            username=username,
            password=password,
            name=name,
            phone=phone,
            email=email,
            role=role,
            company=company
        )
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def get_user_stats():
        """获取用户统计"""
        # 简化查询
        total = User.query.count()
        candidates = User.query.filter_by(role='user').count()
        hrs = User.query.filter_by(role='hr').count()
        return {'total': total, 'candidates': candidates, 'hrs': hrs}

    @staticmethod
    def toggle_status(user_id):
        """切换用户状态"""
        user = User.query.get(user_id)
        if user and user.role != 'admin':
            user.is_active = not user.is_active
            db.session.commit()
            return True
        return False


class JobService:
    """岗位服务"""

    @staticmethod
    def get_active_jobs(page=1, per_page=12, keyword='', city='', education=''):
        """获取招聘中的岗位"""
        query = Job.query.filter_by(status='招聘中')

        if keyword:
            query = query.filter(
                db.or_(
                    Job.title.contains(keyword),
                    Job.skills_req.contains(keyword)
                )
            )
        if city:
            query = query.filter(Job.city.contains(city))
        if education:
            query = query.filter(Job.education_req.contains(education))

        return query.order_by(Job.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

    @staticmethod
    def get_cities():
        """获取所有城市列表"""
        cities = db.session.query(Job.city).distinct().filter(
            Job.city.isnot(None),
            Job.status == '招聘中'
        ).all()
        return [c[0] for c in cities]

    @staticmethod
    def increment_views(job_id):
        """增加浏览次数"""
        job = Job.query.get(job_id)
        if job:
            job.views = (job.views or 0) + 1
            db.session.commit()

    @staticmethod
    def get_popular_jobs(limit=5):
        """获取热门岗位"""
        return db.session.query(
            Job, func.count(Delivery.id).label('count')
        ).join(Delivery).group_by(Job.id).order_by(func.count(Delivery.id).desc()).limit(limit).all()


class ResumeService:
    """简历服务"""

    @staticmethod
    def get_user_resumes(user_id):
        """获取用户的简历"""
        return Resume.query.filter_by(user_id=user_id).order_by(Resume.created_at.desc()).all()

    @staticmethod
    def check_user_has_resume(user_id):
        """检查用户是否有简历"""
        return db.session.query(func.count(Resume.id)).filter_by(user_id=user_id).scalar() > 0


class DeliveryService:
    """投递服务"""

    @staticmethod
    def check_already_delivered(user_id, job_id):
        """检查是否已投递"""
        return Delivery.query.filter_by(user_id=user_id, job_id=job_id).first() is not None

    @staticmethod
    def get_user_deliveries(user_id, page=1, per_page=10):
        """获取用户的投递记录"""
        return Delivery.query.filter_by(user_id=user_id).order_by(
            Delivery.created_at.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def get_hr_deliveries(hr_id, page=1, per_page=15, sort='match_desc'):
        """获取HR收到的投递"""
        query = Delivery.query.join(Job).filter(Job.hr_id == hr_id)

        if sort == 'match_desc':
            query = query.order_by(Delivery.match_score.desc())
        elif sort == 'time_desc':
            query = query.order_by(Delivery.created_at.desc())
        elif sort == 'time_asc':
            query = query.order_by(Delivery.created_at.asc())

        return query.paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def create_delivery(user_id, job_id, resume_id, match_result):
        """创建投递记录"""
        delivery = Delivery(
            user_id=user_id,
            job_id=job_id,
            resume_id=resume_id,
            match_score=match_result['final_score'],
            status='待查看'
        )
        db.session.add(delivery)
        db.session.flush()

        # 保存匹配结果
        match_record = MatchResult(
            resume_id=resume_id,
            job_id=job_id,
            similarity_score=match_result['similarity_score'],
            final_score=match_result['final_score'],
            education_score=match_result['education_score'],
            skill_score=match_result['skill_score'],
            experience_score=match_result['experience_score'],
            match_details=match_result['match_details']
        )
        db.session.add(match_record)

        # 更新简历状态
        resume = Resume.query.get(resume_id)
        if resume:
            resume.status = '已投递'

        db.session.commit()
        return delivery

    @staticmethod
    def get_stats(hr_id=None):
        """获取投递统计"""
        if hr_id:
            total = Delivery.query.join(Job).filter(Job.hr_id == hr_id).count()
            pending = Delivery.query.join(Job).filter(
                Job.hr_id == hr_id,
                Delivery.status == '待查看'
            ).count()
            avg_score = db.session.query(func.avg(Delivery.match_score)).join(Job).filter(
                Job.hr_id == hr_id
            ).scalar() or 0
        else:
            total = Delivery.query.count()
            pending = Delivery.query.filter_by(status='待查看').count()
            avg_score = db.session.query(func.avg(Delivery.match_score)).scalar() or 0

        return {
            'total': total,
            'pending': pending,
            'avg_score': round(avg_score, 2)
        }


class StatsService:
    """统计服务"""

    @staticmethod
    def get_system_stats():
        """获取系统统计"""
        return {
            'total_users': User.query.filter_by(role='user').count(),
            'total_jobs': Job.query.filter_by(status='招聘中').count(),
            'total_resumes': Resume.query.count(),
            'total_deliveries': Delivery.query.count()
        }

    @staticmethod
    def get_match_distribution():
        """获取匹配分数分布"""
        return {
            'high': Delivery.query.filter(Delivery.match_score >= 80).count(),
            'medium': Delivery.query.filter(
                and_(Delivery.match_score >= 60, Delivery.match_score < 80)
            ).count(),
            'low': Delivery.query.filter(Delivery.match_score < 60).count()
        }

    @staticmethod
    def get_city_distribution():
        """获取城市分布"""
        return db.session.query(
            Job.city, func.count(Job.id)
        ).filter(
            Job.status == '招聘中',
            Job.city.isnot(None)
        ).group_by(Job.city).all()

    @staticmethod
    def get_education_distribution():
        """获取学历分布"""
        return db.session.query(
            Resume.education, func.count(Resume.id)
        ).filter(
            Resume.education.isnot(None)
        ).group_by(Resume.education).all()


class LogService:
    """日志服务"""

    @staticmethod
    def log_action(user_id, action, target_type=None, target_id=None, details=None, ip_address=None):
        """记录日志"""
        try:
            log = SystemLog(
                user_id=user_id,
                action=action,
                target_type=target_type,
                target_id=target_id,
                details=details,
                ip_address=ip_address
            )
            db.session.add(log)
            db.session.commit()
        except:
            db.session.rollback()