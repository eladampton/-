# -*- coding: utf-8 -*-
"""
API路由模块 - 提供JSON API接口
"""
from flask import Blueprint, jsonify, request, make_response
from flask_login import login_required, current_user
from models import db, User, Resume, Job, Delivery, MatchResult, Message
from utils import get_matcher
from functools import wraps
import json

api_bp = Blueprint('api', __name__, url_prefix='/api')


def api_response(f):
    """API响应装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            result = f(*args, **kwargs)
            return jsonify(result)
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'message': '服务器内部错误'
            }), 500
    return decorated


@api_bp.route('/match/<int:resume_id>/<int:job_id>')
@login_required
@api_response
def match_resume_job(resume_id, job_id):
    """计算匹配度"""
    resume = Resume.query.get_or_404(resume_id)
    job = Job.query.get_or_404(job_id)

    matcher = get_matcher()
    result = matcher.calculate_match_score(resume, job)

    return {'success': True, 'data': result}


@api_bp.route('/stats')
@api_response
def api_stats():
    """系统统计"""
    stats = {
        'total_users': User.query.filter_by(role='user').count(),
        'total_jobs': Job.query.filter_by(status='招聘中').count(),
        'total_resumes': Resume.query.count(),
        'total_deliveries': Delivery.query.count()
    }
    return stats


@api_bp.route('/analytics')
@api_response
def api_analytics():
    """数据分析（带缓存）"""
    from datetime import datetime, timedelta
    from sqlalchemy import func

    # 尝试从缓存获取
    cache_key = 'analytics_data'
    cached = _get_cache(cache_key)
    if cached:
        return cached

    # 城市分布
    city_stats = db.session.query(
        Job.city, func.count(Job.id)
    ).filter(Job.status == '招聘中').group_by(Job.city).all()

    # 学历分布
    edu_stats = db.session.query(
        Resume.education, func.count(Resume.id)
    ).group_by(Resume.education).all()

    # 投递状态
    delivery_stats = db.session.query(
        Delivery.status, func.count(Delivery.id)
    ).group_by(Delivery.status).all()
    total = sum(s[1] for s in delivery_stats)
    interview_count = sum(s[1] for s in delivery_stats if s[0] in ['面试中', '已录用'])

    # 7天趋势
    seven_days_ago = datetime.now() - timedelta(days=7)
    trend_stats = db.session.query(
        func.date(Delivery.created_at).label('date'),
        func.count(Delivery.id)
    ).filter(Delivery.created_at >= seven_days_ago).group_by(
        func.date(Delivery.created_at)
    ).all()

    # 匹配分布
    match_distribution = {
        'high': Delivery.query.filter(Delivery.match_score >= 70).count(),
        'medium': Delivery.query.filter(
            Delivery.match_score >= 40, Delivery.match_score < 70
        ).count(),
        'low': Delivery.query.filter(Delivery.match_score < 40).count()
    }

    result = {
        'city_distribution': [{'city': c[0], 'count': c[1]} for c in city_stats if c[0]],
        'resume_education': [{'education': e[0], 'count': e[1]} for e in edu_stats if e[0]],
        'delivery_status': [{'status': s[0], 'count': s[1]} for s in delivery_stats],
        'trend': [{'date': str(t[0]), 'count': t[1]} for t in trend_stats],
        'match_distribution': match_distribution,
        'total_jobs': Job.query.filter_by(status='招聘中').count(),
        'total_applications': Delivery.query.count(),
        'total_candidates': User.query.filter_by(role='user').count(),
        'interview_rate': round(interview_count / max(total, 1) * 100, 2)
    }

    # 缓存5分钟
    _set_cache(cache_key, result, timeout=300)
    return result


@api_bp.route('/search/jobs')
@api_response
def search_jobs():
    """高级搜索"""
    keyword = request.args.get('keyword', '')
    city = request.args.get('city', '')
    education = request.args.get('education', '')
    salary_min = request.args.get('salary_min', type=int)
    salary_max = request.args.get('salary_max', type=int)
    skills = request.args.get('skills', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = Job.query.filter_by(status='招聘中')

    if keyword:
        query = query.filter(Job.title.contains(keyword))
    if city:
        query = query.filter(Job.city == city)
    if education:
        query = query.filter(Job.education_req == education)
    if salary_min:
        query = query.filter(Job.salary_max >= salary_min)
    if salary_max:
        query = query.filter(Job.salary_min <= salary_max)
    if skills:
        query = query.filter(Job.skills_req.contains(skills))

    pagination = query.order_by(Job.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return {
        'jobs': [j.to_dict() for j in pagination.items],
        'total': pagination.total,
        'page': page,
        'pages': pagination.pages
    }


@api_bp.route('/export/jobs')
@login_required
def export_jobs():
    """导出岗位CSV"""
    if current_user.role not in ['admin', 'hr']:
        return jsonify({'error': '无权限'}), 403

    import csv
    from io import StringIO

    jobs = Job.query.filter_by(status='招聘中').all()

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['岗位名称', '城市', '薪资范围', '学历要求', '技能要求', '公司', '发布时间'])

    for job in jobs:
        salary_range = f"{job.salary_min}-{job.salary_max}" if job.salary_min and job.salary_max else "面议"
        writer.writerow([
            job.title,
            job.city or '',
            salary_range,
            job.education_req or '',
            job.skills_req or '',
            getattr(job, 'company_name', '') or '',
            job.created_at.strftime('%Y-%m-%d') if job.created_at else ''
        ])

    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=jobs.csv'
    return response


@api_bp.route('/export/deliveries')
@login_required
def export_deliveries():
    """导出投递记录CSV"""
    if current_user.role not in ['admin', 'hr']:
        return jsonify({'error': '无权限'}), 403

    import csv
    from io import StringIO

    query = Delivery.query
    if current_user.role == 'hr':
        query = query.join(Job).filter(Job.hr_id == current_user.id)

    deliveries = query.all()

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['求职者', '岗位', '匹配分数', '状态', '投递时间'])

    for d in deliveries:
        writer.writerow([
            d.job_seeker.name if d.job_seeker else '',
            d.job.title if d.job else '',
            f"{d.match_score:.1f}" if d.match_score else 0,
            d.status,
            d.created_at.strftime('%Y-%m-%d %H:%M') if d.created_at else ''
        ])

    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=deliveries.csv'
    return response


@api_bp.route('/send_message', methods=['POST'])
@login_required
@api_response
def send_message():
    """发送消息"""
    user_id = request.form.get('user_id', type=int)
    title = request.form.get('title')
    content = request.form.get('content')
    message_type = request.form.get('message_type', 'system')

    if not all([user_id, title, content]):
        return {'success': False, 'message': '缺少必要参数'}

    msg = Message(
        user_id=user_id,
        sender_id=current_user.id,
        title=title,
        content=content,
        message_type=message_type
    )
    db.session.add(msg)
    db.session.commit()

    return {'success': True, 'message': '消息发送成功'}


# 简单的内存缓存
_cache_store = {}


def _get_cache(key):
    return _cache_store.get(key)


def _set_cache(key, value, timeout=300):
    _cache_store[key] = value