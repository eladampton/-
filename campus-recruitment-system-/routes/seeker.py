# -*- coding: utf-8 -*-
"""
求职者路由模块
"""
import logging
import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db, User, Resume, Job, Delivery, MatchResult, SystemLog, Favorite, BrowseHistory
from utils import ResumeParser, get_matcher
from datetime import datetime
import json

seeker_bp = Blueprint('seeker', __name__, url_prefix='/job-seeker')


@seeker_bp.route('/dashboard')
@login_required
def seeker_dashboard():
    """求职者仪表盘"""
    resume_count = Resume.query.filter_by(user_id=current_user.id).count()
    delivery_count = Delivery.query.filter_by(user_id=current_user.id).count()
    pending_count = Delivery.query.filter_by(
        user_id=current_user.id, status='待查看'
    ).count()

    recent_deliveries = Delivery.query.filter_by(
        user_id=current_user.id
    ).order_by(Delivery.created_at.desc()).limit(5).all()

    recommended_jobs = Job.query.filter_by(
        status='招聘中'
    ).order_by(Job.created_at.desc()).limit(5).all()

    return render_template('job_seeker/dashboard.html',
                          resume_count=resume_count,
                          delivery_count=delivery_count,
                          pending_count=pending_count,
                          recent_deliveries=recent_deliveries,
                          recommended_jobs=recommended_jobs)


@seeker_bp.route('/resumes')
@login_required
def job_seeker_resumes():
    """简历列表"""
    resumes = Resume.query.filter_by(
        user_id=current_user.id
    ).order_by(Resume.created_at.desc()).all()
    return render_template('job_seeker/resumes.html', resumes=resumes)


@seeker_bp.route('/resume/create', methods=['GET', 'POST'])
@login_required
def resume_create():
    """创建简历"""
    if request.method == 'POST':
        resume = Resume(
            user_id=current_user.id,
            real_name=request.form.get('real_name', '').strip(),
            gender=request.form.get('gender', '').strip(),
            age=request.form.get('age', type=int),
            phone=request.form.get('phone', '').strip(),
            email=request.form.get('email', '').strip(),
            education=request.form.get('education', '').strip(),
            school=request.form.get('school', '').strip(),
            major=request.form.get('major', '').strip(),
            skills=request.form.get('skills', '').strip(),
            project_exp=request.form.get('project_exp', '').strip(),
            internship_exp=request.form.get('internship_exp', '').strip(),
            awards=request.form.get('awards', '').strip(),
            self_eval=request.form.get('self_eval', '').strip(),
            status='未投递'
        )

        try:
            db.session.add(resume)
            db.session.commit()
            _log_action('创建简历', 'Resume', resume.id)
            flash('简历创建成功', 'success')
            return redirect(url_for('seeker.job_seeker_resumes'))
        except Exception as e:
            db.session.rollback()
            logging.warning(f'Resume create failed: {e}')
            flash('创建失败', 'danger')

    return render_template('job_seeker/resume_form.html')


@seeker_bp.route('/resume/upload', methods=['GET', 'POST'])
@login_required
def resume_upload():
    """上传简历"""
    if request.method == 'POST':
        if 'resume_file' not in request.files:
            flash('请选择文件', 'warning')
            return redirect(url_for('seeker.resume_upload'))

        file = request.files['resume_file']
        if file.filename == '':
            flash('请选择文件', 'warning')
            return redirect(url_for('seeker.resume_upload'))

        if _allowed_file(file.filename, {'pdf', 'doc', 'docx'}):
            filename = secure_filename(f"resume_{current_user.id}_{file.filename}")
            upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'resumes')
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)

            parser = ResumeParser()
            parse_result = parser.parse_file(file_path)

            if parse_result['success']:
                text_content = parse_result['text']
                extracted_info = ResumeParser.extract_info(text_content)

                resume = Resume(
                    user_id=current_user.id,
                    real_name=extracted_info.get('name') or current_user.name,
                    phone=extracted_info.get('phone') or current_user.phone,
                    email=extracted_info.get('email') or current_user.email,
                    education=extracted_info.get('education', ''),
                    skills=', '.join(extracted_info.get('skills', [])),
                    file_path=f'uploads/resumes/{filename}',
                    file_content=text_content[:2000],
                    status='未投递'
                )

                try:
                    db.session.add(resume)
                    db.session.commit()
                    _log_action('上传简历', 'Resume', resume.id)
                    flash('简历上传成功', 'success')
                    return redirect(url_for('seeker.job_seeker_resumes'))
                except Exception as e:
                    db.session.rollback()
                    logging.warning(f'Resume save failed: {e}')
                    flash('保存失败', 'danger')
            else:
                flash(f'简历解析失败：{parse_result.get("error", "未知错误")}', 'warning')
        else:
            flash('仅支持PDF、Word格式文件', 'warning')

    return render_template('job_seeker/resume_upload.html')


@seeker_bp.route('/resume/edit/<int:resume_id>', methods=['GET', 'POST'])
@login_required
def resume_edit(resume_id):
    """编辑简历"""
    resume = Resume.query.get_or_404(resume_id)

    if resume.user_id != current_user.id:
        flash('无权操作', 'danger')
        return redirect(url_for('seeker.job_seeker_resumes'))

    if request.method == 'POST':
        resume.real_name = request.form.get('real_name', resume.real_name).strip()
        resume.gender = request.form.get('gender', '').strip()
        resume.age = request.form.get('age', type=int)
        resume.phone = request.form.get('phone', '').strip()
        resume.email = request.form.get('email', '').strip()
        resume.education = request.form.get('education', '').strip()
        resume.school = request.form.get('school', '').strip()
        resume.major = request.form.get('major', '').strip()
        resume.skills = request.form.get('skills', '').strip()
        resume.project_exp = request.form.get('project_exp', '').strip()
        resume.internship_exp = request.form.get('internship_exp', '').strip()
        resume.awards = request.form.get('awards', '').strip()
        resume.self_eval = request.form.get('self_eval', '').strip()

        try:
            db.session.commit()
            _log_action('编辑简历', 'Resume', resume.id)
            flash('简历更新成功', 'success')
            return redirect(url_for('seeker.job_seeker_resumes'))
        except Exception as e:
            db.session.rollback()
            logging.warning(f'Resume edit failed: {e}')
            flash('更新失败', 'danger')

    return render_template('job_seeker/resume_form.html', resume=resume)


@seeker_bp.route('/resume/delete/<int:resume_id>', methods=['POST'])
@login_required
def resume_delete(resume_id):
    """删除简历"""
    resume = Resume.query.get_or_404(resume_id)

    if resume.user_id != current_user.id:
        flash('无权操作', 'danger')
        return redirect(url_for('seeker.job_seeker_resumes'))

    try:
        db.session.delete(resume)
        db.session.commit()
        _log_action('删除简历', 'Resume', resume_id)
        flash('简历已删除', 'success')
    except Exception as e:
        db.session.rollback()
        logging.warning(f'Resume delete failed: {e}')
        flash('删除失败', 'danger')

    return redirect(url_for('seeker.job_seeker_resumes'))


@seeker_bp.route('/deliver', methods=['POST'])
@login_required
def job_seeker_deliver():
    """投递简历"""
    job_id = request.form.get('job_id', type=int)
    resume_id = request.form.get('resume_id', type=int)

    if not job_id or not resume_id:
        flash('参数错误', 'danger')
        return redirect(url_for('public.jobs'))

    job = Job.query.get_or_404(job_id)
    resume = Resume.query.get_or_404(resume_id)

    if resume.user_id != current_user.id:
        flash('无权操作', 'danger')
        return redirect(url_for('public.jobs'))

    existing = Delivery.query.filter_by(
        user_id=current_user.id, job_id=job_id
    ).first()
    if existing:
        flash('您已经投递过该岗位', 'warning')
        return redirect(url_for('public.job_detail', job_id=job_id))

    matcher = get_matcher()
    match_result = matcher.calculate_match_score(resume, job)

    delivery = Delivery(
        user_id=current_user.id,
        job_id=job_id,
        resume_id=resume_id,
        match_score=match_result['final_score'],
        status='待查看'
    )

    try:
        db.session.add(delivery)
        db.session.flush()

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

        resume.status = '已投递'
        db.session.commit()

        _log_action('投递简历', 'Delivery', delivery.id)
        flash(f'投递成功！您的匹配分数为：{match_result["final_score"]}分', 'success')
    except Exception as e:
        db.session.rollback()
        logging.warning(f'Delivery failed: {e}')
        flash('投递失败', 'danger')

    return redirect(url_for('public.job_detail', job_id=job_id))


@seeker_bp.route('/deliveries')
@login_required
def job_seeker_deliveries():
    """投递记录"""
    page = request.args.get('page', 1, type=int)
    per_page = 10

    pagination = Delivery.query.filter_by(
        user_id=current_user.id
    ).order_by(Delivery.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template('job_seeker/deliveries.html',
                          deliveries=pagination.items,
                          pagination=pagination)


@seeker_bp.route('/match-result/<int:delivery_id>')
@login_required
def match_result(delivery_id):
    """匹配结果详情"""
    delivery = Delivery.query.get_or_404(delivery_id)

    if delivery.user_id != current_user.id:
        flash('无权查看', 'danger')
        return redirect(url_for('seeker.job_seeker_deliveries'))

    match_result = MatchResult.query.filter_by(
        resume_id=delivery.resume_id,
        job_id=delivery.job_id
    ).first()

    job = Job.query.get(delivery.job_id)
    resume = Resume.query.get(delivery.resume_id)

    match_details = {}
    if match_result and match_result.match_details:
        try:
            match_details = json.loads(match_result.match_details)
        except Exception as e:
            logging.warning(f'Parse match details failed: {e}')

    return render_template('job_seeker/match_result.html',
                          delivery=delivery,
                          match_result=match_result,
                          match_details=match_details,
                          job=job, resume=resume)


@seeker_bp.route('/favorites')
@login_required
def favorites():
    """我的收藏"""
    page = request.args.get('page', 1, type=int)
    per_page = 12

    favorites = Favorite.query.filter_by(user_id=current_user.id).order_by(
        Favorite.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    job_ids = [f.job_id for f in favorites.items]
    jobs = Job.query.filter(Job.id.in_(job_ids)).all() if job_ids else []
    jobs_map = {j.id: j for j in jobs}

    return render_template('job_seeker/favorites.html',
                          favorites=favorites.items,
                          jobs_map=jobs_map,
                          pagination=favorites)


@seeker_bp.route('/favorite/toggle', methods=['POST'])
@login_required
def toggle_favorite():
    """收藏/取消收藏岗位"""
    job_id = request.form.get('job_id', type=int)

    if not job_id:
        return jsonify({'success': False, 'message': '参数错误'})

    job = Job.query.get(job_id)
    if not job:
        return jsonify({'success': False, 'message': '岗位不存在'})

    favorite = Favorite.query.filter_by(
        user_id=current_user.id,
        job_id=job_id
    ).first()

    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({'success': True, 'action': 'removed', 'message': '已取消收藏'})
    else:
        favorite = Favorite(user_id=current_user.id, job_id=job_id)
        db.session.add(favorite)
        db.session.commit()
        return jsonify({'success': True, 'action': 'added', 'message': '已添加收藏'})

    return jsonify({'success': False, 'message': '操作失败'})


@seeker_bp.route('/favorite/check/<int:job_id>')
@login_required
def check_favorite(job_id):
    """检查是否已收藏"""
    favorite = Favorite.query.filter_by(
        user_id=current_user.id,
        job_id=job_id
    ).first()
    return jsonify({'success': True, 'is_favorited': favorite is not None})


@seeker_bp.route('/browse-history')
@login_required
def browse_history():
    """浏览足迹"""
    page = request.args.get('page', 1, type=int)
    per_page = 12

    history = db.session.query(
        BrowseHistory.job_id,
        db.func.max(BrowseHistory.created_at).label('last_view'),
        db.func.sum(BrowseHistory.stay_duration).label('total_duration'),
        db.func.count(BrowseHistory.id).label('view_count')
    ).filter(
        BrowseHistory.user_id == current_user.id
    ).group_by(BrowseHistory.job_id).order_by(
        db.func.max(BrowseHistory.created_at).desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    job_ids = [h.job_id for h in history.items]
    jobs = Job.query.filter(Job.id.in_(job_ids)).all() if job_ids else []
    jobs_map = {j.id: j for j in jobs}

    return render_template('job_seeker/browse_history.html',
                          history=history.items,
                          jobs_map=jobs_map,
                          pagination=history)


@seeker_bp.route('/browse/record', methods=['POST'])
@login_required
def record_browse():
    """记录浏览足迹"""
    job_id = request.form.get('job_id', type=int)
    stay_duration = request.form.get('stay_duration', 0, type=int)

    if not job_id:
        return jsonify({'success': False})

    job = Job.query.get(job_id)
    if not job:
        return jsonify({'success': False})

    history = BrowseHistory(
        user_id=current_user.id,
        job_id=job_id,
        stay_duration=stay_duration
    )
    db.session.add(history)
    job.views = (job.views or 0) + 1

    db.session.commit()
    return jsonify({'success': True})


def _allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


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