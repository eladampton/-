# -*- coding: utf-8 -*-
"""
管理员路由模块
"""
import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, User, Resume, Job, Delivery, MatchResult, SystemLog, SystemConfig, Message, Analytics, Favorite, BrowseHistory
from sqlalchemy import func, desc
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def _log_action(action, target_type=None, target_id=None, details=None):
    try:
        log = SystemLog(
            user_id=current_user.id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            details=details,
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.warning(f'Log action failed: {e}')


@admin_bp.route('/dashboard')
@login_required
def admin_dashboard():
    """管理员仪表盘"""
    total_users = User.query.count()
    admin_count = User.query.filter_by(role='admin').count()
    hr_count = User.query.filter_by(role='hr').count()
    user_count = User.query.filter_by(role='user').count()

    total_jobs = Job.query.count()
    total_resumes = Resume.query.count()
    total_deliveries = Delivery.query.count()
    avg_score = db.session.query(func.avg(Delivery.match_score)).scalar() or 0

    hot_jobs = db.session.query(
        Job, func.count(Delivery.id).label('delivery_count')
    ).join(Delivery).group_by(Job.id).order_by(desc('delivery_count')).limit(5).all()

    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_deliveries = Delivery.query.order_by(Delivery.created_at.desc()).limit(10).all()

    match_distribution = {
        'high': Delivery.query.filter(Delivery.match_score >= 80).count(),
        'medium': Delivery.query.filter(
            Delivery.match_score >= 60, Delivery.match_score < 80
        ).count(),
        'low': Delivery.query.filter(Delivery.match_score < 60).count()
    }

    return render_template('admin/dashboard.html',
                          total_users=total_users,
                          total_jobs=total_jobs,
                          total_resumes=total_resumes,
                          total_deliveries=total_deliveries,
                          avg_score=round(avg_score, 2),
                          admin_count=admin_count,
                          hr_count=hr_count,
                          user_count=user_count,
                          hot_jobs=hot_jobs,
                          recent_users=recent_users,
                          recent_deliveries=recent_deliveries,
                          match_distribution=match_distribution)


@admin_bp.route('/users')
@login_required
def admin_users():
    """用户管理"""
    page = request.args.get('page', 1, type=int)
    per_page = 15
    role_filter = request.args.get('role', '')

    query = User.query
    if role_filter:
        query = query.filter_by(role=role_filter)

    pagination = query.order_by(
        User.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    return render_template('admin/users.html',
                          users=pagination.items,
                          pagination=pagination,
                          role_filter=role_filter)


@admin_bp.route('/user/toggle/<int:user_id>', methods=['POST'])
@login_required
def toggle_user(user_id):
    """切换用户状态"""
    user = User.query.get_or_404(user_id)

    if user.role == 'admin':
        flash('不能禁用管理员账号', 'danger')
        return redirect(url_for('admin.admin_users'))

    user.is_active = not user.is_active

    try:
        db.session.commit()
        _log_action('切换用户状态', 'User', user_id)
        flash(f'用户已{"启用" if user.is_active else "禁用"}', 'success')
    except Exception as e:
        db.session.rollback()
        logging.warning(f'Toggle user failed: {e}')
        flash('操作失败', 'danger')

    return redirect(url_for('admin.admin_users'))


@admin_bp.route('/user/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    """删除用户"""
    user = User.query.get_or_404(user_id)

    if user.role == 'admin':
        flash('不能删除管理员账号', 'danger')
        return redirect(url_for('admin.admin_users'))

    try:
        db.session.delete(user)
        db.session.commit()
        _log_action('删除用户', 'User', user_id)
        flash('用户已删除', 'success')
    except Exception as e:
        db.session.rollback()
        logging.warning(f'Delete user failed: {e}')
        flash('删除失败', 'danger')

    return redirect(url_for('admin.admin_users'))


@admin_bp.route('/jobs')
@login_required
def admin_jobs():
    """岗位管理"""
    page = request.args.get('page', 1, type=int)
    per_page = 15

    pagination = Job.query.order_by(
        Job.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    return render_template('admin/jobs.html',
                          jobs=pagination.items,
                          pagination=pagination)


@admin_bp.route('/job/toggle/<int:job_id>', methods=['POST'])
@login_required
def toggle_job(job_id):
    """切换岗位状态"""
    job = Job.query.get_or_404(job_id)
    job.status = '已下架' if job.status == '招聘中' else '招聘中'

    try:
        db.session.commit()
        _log_action('管理员修改岗位状态', 'Job', job_id)
        flash(f'岗位已{job.status}', 'success')
    except Exception as e:
        db.session.rollback()
        logging.warning(f'Toggle job failed: {e}')
        flash('操作失败', 'danger')

    return redirect(url_for('admin.admin_jobs'))


@admin_bp.route('/job/delete/<int:job_id>', methods=['POST'])
@login_required
def delete_job(job_id):
    """删除岗位"""
    job = Job.query.get_or_404(job_id)

    try:
        db.session.delete(job)
        db.session.commit()
        _log_action('管理员删除岗位', 'Job', job_id)
        flash('岗位已删除', 'success')
    except Exception as e:
        db.session.rollback()
        logging.warning(f'Delete job failed: {e}')
        flash('删除失败', 'danger')

    return redirect(url_for('admin.admin_jobs'))


@admin_bp.route('/resumes')
@login_required
def admin_resumes():
    """简历管理"""
    page = request.args.get('page', 1, type=int)
    per_page = 15

    pagination = Resume.query.order_by(
        Resume.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    return render_template('admin/resumes.html',
                          resumes=pagination.items,
                          pagination=pagination)


@admin_bp.route('/resume/delete/<int:resume_id>', methods=['POST'])
@login_required
def delete_resume(resume_id):
    """删除简历"""
    resume = Resume.query.get_or_404(resume_id)

    try:
        db.session.delete(resume)
        db.session.commit()
        _log_action('管理员删除简历', 'Resume', resume_id)
        flash('简历已删除', 'success')
    except Exception as e:
        db.session.rollback()
        logging.warning(f'Delete resume failed: {e}')
        flash('删除失败', 'danger')

    return redirect(url_for('admin.admin_resumes'))


@admin_bp.route('/deliveries')
@login_required
def admin_deliveries():
    """投递管理"""
    page = request.args.get('page', 1, type=int)
    per_page = 20

    pagination = Delivery.query.order_by(
        Delivery.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    return render_template('admin/deliveries.html',
                          deliveries=pagination.items,
                          pagination=pagination)


@admin_bp.route('/logs')
@login_required
def admin_logs():
    """系统日志"""
    page = request.args.get('page', 1, type=int)
    per_page = 30

    pagination = SystemLog.query.order_by(
        SystemLog.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    return render_template('admin/logs.html',
                          logs=pagination.items,
                          pagination=pagination)


@admin_bp.route('/config', methods=['GET', 'POST'])
@login_required
def system_config():
    """系统配置"""
    if request.method == 'POST':
        param_name = request.form.get('param_name')
        param_value = request.form.get('param_value')

        if param_name:
            config = SystemConfig.query.filter_by(
                param_name=param_name
            ).first()
            if config:
                config.param_value = param_value
            else:
                config = SystemConfig(
                    param_name=param_name,
                    param_value=param_value
                )
                db.session.add(config)

            try:
                db.session.commit()
                _log_action('更新系统配置', 'SystemConfig', config.id)
                flash('配置已保存', 'success')
            except Exception as e:
                db.session.rollback()
                logging.warning(f'Save config failed: {e}')
                flash('保存失败', 'danger')

    configs = SystemConfig.query.all()

    return render_template('admin/config.html', configs=configs)


@admin_bp.route('/analytics')
@login_required
def analytics():
    """数据可视化仪表盘"""
    days = request.args.get('days', 30, type=int)
    start_date = datetime.now() - timedelta(days=days)

    today = datetime.now().date()
    today_users = User.query.filter(
        func.date(User.created_at) == today
    ).count()
    today_jobs = Job.query.filter(
        func.date(Job.created_at) == today
    ).count()
    today_deliveries = Delivery.query.filter(
        func.date(Delivery.created_at) == today
    ).count()

    total_users = User.query.count()
    candidates = User.query.filter_by(role='user').count()
    hrs = User.query.filter_by(role='hr').count()

    total_deliveries = Delivery.query.count()
    avg_score = db.session.query(func.avg(Delivery.match_score)).scalar() or 0
    pending = Delivery.query.filter_by(status='待查看').count()
    viewed = Delivery.query.filter_by(status='已查看').count()
    contacted = Delivery.query.filter_by(status='已联系').count()
    inappropriate = Delivery.query.filter_by(status='不合适').count()

    daily_trend = db.session.query(
        func.date(Delivery.created_at).label('date'),
        func.count(Delivery.id).label('count')
    ).filter(
        Delivery.created_at >= start_date
    ).group_by(func.date(Delivery.created_at)).order_by(func.date(Delivery.created_at)).all()

    trend_labels = [str(t.date) for t in daily_trend]
    trend_data = [t.count for t in daily_trend]

    city_stats_raw = db.session.query(
        Job.city, func.count(Job.id).label('count')
    ).filter(
        Job.status == '招聘中',
        Job.city.isnot(None)
    ).group_by(Job.city).order_by(func.count(Job.id).desc()).limit(10).all()
    city_stats = [{'city': c[0], 'count': c[1]} for c in city_stats_raw if c[0]]

    edu_stats_raw = db.session.query(
        Resume.education, func.count(Resume.id).label('count')
    ).filter(
        Resume.education.isnot(None)
    ).group_by(Resume.education).all()
    edu_stats = [{'education': e[0], 'count': e[1]} for e in edu_stats_raw if e[0]]

    match_dist = {
        'high': Delivery.query.filter(Delivery.match_score >= 80).count(),
        'medium': Delivery.query.filter(
            Delivery.match_score >= 60, Delivery.match_score < 80
        ).count(),
        'low': Delivery.query.filter(
            Delivery.match_score >= 40, Delivery.match_score < 60
        ).count(),
        'very_low': Delivery.query.filter(Delivery.match_score < 40).count()
    }

    hot_jobs = db.session.query(
        Job, func.count(Delivery.id).label('delivery_count')
    ).join(Delivery).group_by(Job.id).order_by(
        func.count(Delivery.id).desc()
    ).limit(10).all()

    total_favorites = Favorite.query.count()
    total_browses = BrowseHistory.query.count()
    today_browses = BrowseHistory.query.filter(
        func.date(BrowseHistory.created_at) == today
    ).count()

    status_dist_raw = db.session.query(
        Delivery.status, func.count(Delivery.id)
    ).group_by(Delivery.status).all()
    status_dist = [{'status': s[0], 'count': s[1]} for s in status_dist_raw]

    return render_template('admin/analytics.html',
                          total_users=total_users,
                          total_jobs=Job.query.count(),
                          total_resumes=Resume.query.count(),
                          total_deliveries=total_deliveries,
                          avg_score=round(avg_score, 2),
                          candidates=candidates,
                          hrs=hrs,
                          today_users=today_users,
                          today_jobs=today_jobs,
                          today_deliveries=today_deliveries,
                          pending=pending,
                          viewed=viewed,
                          contacted=contacted,
                          inappropriate=inappropriate,
                          trend_labels=trend_labels,
                          trend_data=trend_data,
                          city_stats=city_stats,
                          edu_stats=edu_stats,
                          match_dist=match_dist,
                          status_dist=status_dist,
                          hot_jobs=hot_jobs,
                          total_favorites=total_favorites,
                          total_browses=total_browses,
                          today_browses=today_browses,
                          days=days)


@admin_bp.route('/analytics/data')
@login_required
def analytics_data():
    """数据分析API"""
    from flask import jsonify

    days = request.args.get('days', 30, type=int)
    start_date = datetime.now() - timedelta(days=days)

    user_trend = db.session.query(
        func.date(User.created_at).label('date'),
        func.count(User.id)
    ).filter(
        User.created_at >= start_date
    ).group_by(func.date(User.created_at)).all()

    delivery_trend = db.session.query(
        func.date(Delivery.created_at).label('date'),
        func.count(Delivery.id)
    ).filter(
        Delivery.created_at >= start_date
    ).group_by(func.date(Delivery.created_at)).all()

    job_trend = db.session.query(
        func.date(Job.created_at).label('date'),
        func.count(Job.id)
    ).filter(
        Job.created_at >= start_date
    ).group_by(func.date(Job.created_at)).all()

    return jsonify({
        'success': True,
        'data': {
            'user_trend': {
                'labels': [str(d.date) for d in user_trend],
                'values': [d[1] for d in user_trend]
            },
            'delivery_trend': {
                'labels': [str(d.date) for d in delivery_trend],
                'values': [d[1] for d in delivery_trend]
            },
            'job_trend': {
                'labels': [str(d.date) for d in job_trend],
                'values': [d[1] for d in job_trend]
            }
        }
    })