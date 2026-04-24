# -*- coding: utf-8 -*-
"""
HR路由模块
"""
import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, User, Resume, Job, Delivery, MatchResult, SystemLog
from sqlalchemy import func
import json

hr_bp = Blueprint('hr', __name__, url_prefix='/hr')


def _log_action(action, target_type=None, target_id=None):
    try:
        log = SystemLog(
            user_id=current_user.id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.warning(f'Log action failed: {e}')


@hr_bp.route('/dashboard')
@login_required
def hr_dashboard():
    """HR仪表盘"""
    job_count = Job.query.filter_by(hr_id=current_user.id).count()
    active_job_count = Job.query.filter_by(
        hr_id=current_user.id, status='招聘中'
    ).count()

    delivery_count = Delivery.query.join(Job).filter(Job.hr_id == current_user.id).count()
    pending_count = Delivery.query.join(Job).filter(
        Job.hr_id == current_user.id,
        Delivery.status == '待查看'
    ).count()
    avg_score = db.session.query(func.avg(Delivery.match_score)).join(Job).filter(
        Job.hr_id == current_user.id
    ).scalar() or 0

    recent_deliveries = db.session.query(Delivery).join(Job).filter(
        Job.hr_id == current_user.id
    ).order_by(Delivery.created_at.desc()).limit(5).all()

    return render_template('hr/dashboard.html',
                          job_count=job_count,
                          active_job_count=active_job_count,
                          delivery_count=delivery_count,
                          pending_count=pending_count,
                          avg_score=round(avg_score, 2),
                          recent_deliveries=recent_deliveries)


@hr_bp.route('/jobs')
@login_required
def hr_jobs():
    """岗位管理"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    status_filter = request.args.get('status', '')

    query = Job.query.filter_by(hr_id=current_user.id)
    if status_filter == 'active':
        query = query.filter_by(status='招聘中')

    pagination = query.order_by(Job.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template('hr/jobs.html',
                          jobs=pagination.items,
                          pagination=pagination,
                          status_filter=status_filter)


@hr_bp.route('/job/create', methods=['GET', 'POST'])
@login_required
def job_create():
    """发布岗位"""
    if request.method == 'POST':
        job = Job(
            hr_id=current_user.id,
            title=request.form.get('title', '').strip(),
            city=request.form.get('city', '').strip(),
            salary_min=request.form.get('salary_min', type=int),
            salary_max=request.form.get('salary_max', type=int),
            education_req=request.form.get('education_req', '').strip(),
            major_req=request.form.get('major_req', '').strip(),
            skills_req=request.form.get('skills_req', '').strip(),
            responsibilities=request.form.get('responsibilities', '').strip(),
            requirements=request.form.get('requirements', '').strip(),
            recruit_num=request.form.get('recruit_num', 1, type=int),
            status='招聘中'
        )

        try:
            db.session.add(job)
            db.session.commit()
            _log_action('发布岗位', 'Job', job.id)
            flash('岗位发布成功', 'success')
            return redirect(url_for('hr.hr_jobs'))
        except Exception as e:
            db.session.rollback()
            logging.warning(f'Job create failed: {e}')
            flash('发布失败', 'danger')

    return render_template('hr/job_form.html')


@hr_bp.route('/job/edit/<int:job_id>', methods=['GET', 'POST'])
@login_required
def job_edit(job_id):
    """编辑岗位"""
    job = Job.query.get_or_404(job_id)

    if job.hr_id != current_user.id:
        flash('无权操作', 'danger')
        return redirect(url_for('hr.hr_jobs'))

    if request.method == 'POST':
        job.title = request.form.get('title', job.title).strip()
        job.city = request.form.get('city', '').strip()
        job.salary_min = request.form.get('salary_min', type=int)
        job.salary_max = request.form.get('salary_max', type=int)
        job.education_req = request.form.get('education_req', '').strip()
        job.major_req = request.form.get('major_req', '').strip()
        job.skills_req = request.form.get('skills_req', '').strip()
        job.responsibilities = request.form.get('responsibilities', '').strip()
        job.requirements = request.form.get('requirements', '').strip()
        job.recruit_num = request.form.get('recruit_num', 1, type=int)

        try:
            db.session.commit()
            _log_action('编辑岗位', 'Job', job.id)
            flash('岗位更新成功', 'success')
            return redirect(url_for('hr.hr_jobs'))
        except Exception as e:
            db.session.rollback()
            logging.warning(f'Job edit failed: {e}')
            flash('更新失败', 'danger')

    return render_template('hr/job_form.html', job=job)


@hr_bp.route('/job/toggle/<int:job_id>', methods=['POST'])
@login_required
def job_toggle(job_id):
    """切换岗位状态"""
    job = Job.query.get_or_404(job_id)

    if job.hr_id != current_user.id:
        flash('无权操作', 'danger')
        return redirect(url_for('hr.hr_jobs'))

    job.status = '已下架' if job.status == '招聘中' else '招聘中'

    try:
        db.session.commit()
        _log_action('修改岗位状态', 'Job', job.id)
        flash(f'岗位已{job.status}', 'success')
    except Exception as e:
        db.session.rollback()
        logging.warning(f'Job toggle failed: {e}')
        flash('操作失败', 'danger')

    return redirect(url_for('hr.hr_jobs'))


@hr_bp.route('/job/delete/<int:job_id>', methods=['POST'])
@login_required
def job_delete(job_id):
    """删除岗位"""
    job = Job.query.get_or_404(job_id)

    if job.hr_id != current_user.id:
        flash('无权操作', 'danger')
        return redirect(url_for('hr.hr_jobs'))

    try:
        db.session.delete(job)
        db.session.commit()
        _log_action('删除岗位', 'Job', job_id)
        flash('岗位已删除', 'success')
    except Exception as e:
        db.session.rollback()
        logging.warning(f'Job delete failed: {e}')
        flash('删除失败', 'danger')

    return redirect(url_for('hr.hr_jobs'))


@hr_bp.route('/all-deliveries')
@login_required
def all_deliveries():
    """查看所有投递"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    per_page = 15

    query = Delivery.query.join(Job).filter(Job.hr_id == current_user.id)

    if status:
        query = query.filter(Delivery.status == status)

    pagination = query.order_by(Delivery.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template('hr/all_deliveries.html',
                          deliveries=pagination.items,
                          pagination=pagination,
                          filter_status=status)


@hr_bp.route('/deliveries/<int:job_id>')
@login_required
def deliveries(job_id):
    """查看特定岗位的投递"""
    job = Job.query.get_or_404(job_id)

    if job.hr_id != current_user.id:
        flash('无权查看', 'danger')
        return redirect(url_for('hr.hr_jobs'))

    page = request.args.get('page', 1, type=int)
    sort_by = request.args.get('sort', 'match_desc')

    query = Delivery.query.filter_by(job_id=job_id)

    if sort_by == 'match_desc':
        query = query.order_by(Delivery.match_score.desc())
    elif sort_by == 'time_desc':
        query = query.order_by(Delivery.created_at.desc())
    elif sort_by == 'time_asc':
        query = query.order_by(Delivery.created_at.asc())

    pagination = query.paginate(page=page, per_page=15, error_out=False)

    return render_template('hr/deliveries.html',
                          job=job,
                          deliveries=pagination.items,
                          pagination=pagination,
                          sort_by=sort_by)


@hr_bp.route('/resume/<int:delivery_id>')
@login_required
def view_resume(delivery_id):
    """查看简历详情"""
    delivery = Delivery.query.get_or_404(delivery_id)
    job = Job.query.get(delivery.job_id)

    if job.hr_id != current_user.id:
        flash('无权查看', 'danger')
        return redirect(url_for('hr.hr_jobs'))

    if delivery.status == '待查看':
        delivery.status = '已查看'
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logging.warning(f'Update delivery status failed: {e}')

    resume = Resume.query.get(delivery.resume_id)
    match_result = MatchResult.query.filter_by(
        resume_id=delivery.resume_id,
        job_id=delivery.job_id
    ).first()

    match_details = {}
    if match_result and match_result.match_details:
        try:
            match_details = json.loads(match_result.match_details)
        except Exception as e:
            logging.warning(f'Parse match details failed: {e}')

    return render_template('hr/resume_detail.html',
                          delivery=delivery,
                          resume=resume,
                          job=job,
                          match_result=match_result,
                          match_details=match_details)


@hr_bp.route('/delivery/status/<int:delivery_id>', methods=['POST'])
@login_required
def update_delivery_status(delivery_id):
    """更新投递状态"""
    delivery = Delivery.query.get_or_404(delivery_id)
    job = Job.query.get(delivery.job_id)

    if job.hr_id != current_user.id:
        flash('无权操作', 'danger')
        return redirect(url_for('hr.hr_jobs'))

    new_status = request.form.get('status', '').strip()
    valid_statuses = ['待查看', '已查看', '已联系', '不合适']

    if new_status not in valid_statuses:
        flash('无效的状态值', 'danger')
        return redirect(url_for('hr.view_resume', delivery_id=delivery_id))

    if delivery.status == new_status:
        flash('状态未变化', 'info')
        return redirect(url_for('hr.view_resume', delivery_id=delivery_id))

    old_status = delivery.status
    delivery.status = new_status

    try:
        db.session.commit()
        _log_action(f'更新投递状态: {old_status} -> {new_status}', 'Delivery', delivery.id)
        flash(f'状态已更新：{old_status} -> {new_status}', 'success')
    except Exception as e:
        db.session.rollback()
        logging.warning(f'Update status failed: {e}')
        flash(f'更新失败：{str(e)}', 'danger')

    return redirect(url_for('hr.view_resume', delivery_id=delivery_id, return_status=request.args.get('return_status', '')))