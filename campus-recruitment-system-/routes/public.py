# -*- coding: utf-8 -*-
"""
公共路由模块 - 处理登录、注册、首页等公共功能
"""
import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Job, Resume, Delivery, SystemLog, Message

public_bp = Blueprint('public', __name__)


@public_bp.route('/')
def index():
    """首页"""
    latest_jobs = Job.query.filter_by(status='招聘中').order_by(
        Job.created_at.desc()
    ).limit(6).all()

    stats = {
        'total_users': User.query.filter_by(role='user').count(),
        'total_jobs': Job.query.filter_by(status='招聘中').count(),
        'total_resumes': Resume.query.count(),
        'total_deliveries': Delivery.query.count()
    }

    return render_template('index.html', jobs=latest_jobs, stats=stats)


@public_bp.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    if current_user.is_authenticated:
        return redirect(url_for('public.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            flash('请输入用户名和密码', 'warning')
            return redirect(url_for('public.login'))

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            if not user.is_active:
                flash('您的账号已被禁用，请联系管理员', 'danger')
                return redirect(url_for('public.login'))

            login_user(user, remember=True)
            _log_action('用户登录')

            flash(f'欢迎回来，{user.name}！', 'success')

            if user.role == 'admin':
                return redirect(url_for('admin.admin_dashboard'))
            elif user.role == 'hr':
                return redirect(url_for('hr.hr_dashboard'))
            else:
                return redirect(url_for('seeker.seeker_dashboard'))

        flash('用户名或密码错误', 'danger')

    return render_template('login.html')


@public_bp.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册"""
    if current_user.is_authenticated:
        return redirect(url_for('public.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        role = request.form.get('role', 'user').strip()
        company = request.form.get('company', '').strip()

        if not all([username, password, confirm_password, name]):
            flash('请填写必填项', 'warning')
            return redirect(url_for('public.register'))

        if password != confirm_password:
            flash('两次输入的密码不一致', 'warning')
            return redirect(url_for('public.register'))

        if len(password) < 6:
            flash('密码长度至少为6位', 'warning')
            return redirect(url_for('public.register'))

        if role == 'admin':
            flash('不能注册管理员账号', 'danger')
            return redirect(url_for('public.register'))

        if User.query.filter_by(username=username).first():
            flash('用户名已存在', 'warning')
            return redirect(url_for('public.register'))

        new_user = User(
            username=username,
            password=generate_password_hash(password),
            name=name,
            phone=phone,
            email=email,
            role=role,
            company=company if role == 'hr' else None
        )

        try:
            db.session.add(new_user)
            db.session.commit()
            _log_action('用户注册', 'User', new_user.id)
            flash('注册成功，请登录', 'success')
            return redirect(url_for('public.login'))
        except Exception as e:
            db.session.rollback()
            logging.warning(f'Registration failed: {e}')
            flash('注册失败，请重试', 'danger')

    return render_template('register.html')


@public_bp.route('/logout')
@login_required
def logout():
    """用户登出"""
    _log_action('用户登出')
    logout_user()
    flash('您已退出登录', 'info')
    return redirect(url_for('public.index'))


@public_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """个人中心"""
    if request.method == 'POST':
        current_user.name = request.form.get('name', current_user.name).strip()
        current_user.phone = request.form.get('phone', current_user.phone).strip()
        current_user.email = request.form.get('email', current_user.email).strip()

        if current_user.role == 'hr':
            current_user.company = request.form.get('company', current_user.company).strip()

        old_password = request.form.get('old_password', '').strip()
        new_password = request.form.get('new_password', '').strip()
        if old_password and new_password:
            if check_password_hash(current_user.password, old_password):
                if len(new_password) >= 6:
                    current_user.password = generate_password_hash(new_password)
                    flash('密码修改成功', 'success')
                else:
                    flash('新密码长度至少6位', 'warning')
            else:
                flash('原密码错误', 'danger')

        try:
            db.session.commit()
            _log_action('更新个人资料', 'User', current_user.id)
            flash('个人资料更新成功', 'success')
        except Exception as e:
            db.session.rollback()
            logging.warning(f'Profile update failed: {e}')
            flash('更新失败', 'danger')

        return redirect(url_for('public.profile'))

    return render_template('profile.html')


@public_bp.route('/jobs')
def jobs():
    """岗位列表"""
    page = request.args.get('page', 1, type=int)
    per_page = 12
    keyword = request.args.get('keyword', '').strip()
    city = request.args.get('city', '').strip()
    education = request.args.get('education', '').strip()
    salary_min = request.args.get('salary_min', type=int)
    salary_max = request.args.get('salary_max', type=int)

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
    if salary_min:
        query = query.filter(Job.salary_min >= salary_min)
    if salary_max:
        query = query.filter(Job.salary_max <= salary_max)

    pagination = query.order_by(Job.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    cities = db.session.query(Job.city).distinct().filter(
        Job.city.isnot(None),
        Job.status == '招聘中'
    ).all()
    cities = [c[0] for c in cities]

    return render_template('jobs/list.html',
                          jobs=pagination.items,
                          pagination=pagination,
                          keyword=keyword, city=city,
                          education=education, cities=cities,
                          salary_min=salary_min, salary_max=salary_max)


@public_bp.route('/jobs/<int:job_id>')
def job_detail(job_id):
    """岗位详情"""
    job = Job.query.get_or_404(job_id)

    has_resume = False
    user_delivery = None

    if current_user.is_authenticated and current_user.role == 'user':
        has_resume = Resume.query.filter_by(user_id=current_user.id).first() is not None
        user_delivery = Delivery.query.filter_by(
            user_id=current_user.id, job_id=job_id
        ).first()

    return render_template('jobs/detail.html',
                           job=job, has_resume=has_resume,
                           user_delivery=user_delivery)


def _log_action(action, target_type=None, target_id=None, details=None):
    """记录系统日志"""
    try:
        log = SystemLog(
            user_id=current_user.id if current_user.is_authenticated else None,
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


@public_bp.route('/messages')
@login_required
def messages():
    """消息通知列表"""
    page = request.args.get('page', 1, type=int)
    per_page = 10

    pagination = Message.query.filter_by(
        user_id=current_user.id
    ).order_by(Message.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template('messages.html',
                          messages=pagination.items,
                          pagination=pagination)


@public_bp.route('/messages/mark-read/<int:msg_id>', methods=['POST'])
@login_required
def mark_read(msg_id):
    """标记消息为已读"""
    message = Message.query.get_or_404(msg_id)

    if message.user_id != current_user.id:
        flash('无权操作', 'danger')
        return redirect(url_for('public.messages'))

    message.is_read = True
    try:
        db.session.commit()
        flash('已标记为已读', 'success')
    except Exception as e:
        db.session.rollback()
        logging.warning(f'Mark read failed: {e}')
        flash('操作失败', 'danger')

    return redirect(url_for('public.messages'))


@public_bp.route('/messages/mark-all-read', methods=['POST'])
@login_required
def mark_all_read():
    """标记全部消息为已读"""
    Message.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).update({'is_read': True})

    try:
        db.session.commit()
        flash('已全部标记为已读', 'success')
    except Exception as e:
        db.session.rollback()
        logging.warning(f'Mark all read failed: {e}')
        flash('操作失败', 'danger')

    return redirect(url_for('public.messages'))


@public_bp.route('/messages/delete/<int:msg_id>', methods=['POST'])
@login_required
def delete_message(msg_id):
    """删除消息"""
    message = Message.query.get_or_404(msg_id)

    if message.user_id != current_user.id:
        flash('无权操作', 'danger')
        return redirect(url_for('public.messages'))

    try:
        db.session.delete(message)
        db.session.commit()
        flash('消息已删除', 'success')
    except Exception as e:
        db.session.rollback()
        logging.warning(f'Delete message failed: {e}')
        flash('删除失败', 'danger')

    return redirect(url_for('public.messages'))