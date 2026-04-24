# -*- coding: utf-8 -*-
"""
数据库模型模块 - 使用 SQLAlchemy ORM 定义数据表结构
包含：用户表、简历表、岗位表、投递表、匹配结果表、系统配置表
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

# 初始化 SQLAlchemy 实例
db = SQLAlchemy()


class User(db.Model, UserMixin):
    """
    用户表 - 存储系统所有用户信息
    支持三种角色：admin(管理员)、hr(企业HR)、user(求职者)
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)  # 用户名
    password = db.Column(db.String(255), nullable=False)  # 加密后的密码
    name = db.Column(db.String(50), nullable=False)  # 真实姓名
    phone = db.Column(db.String(20))  # 联系电话
    email = db.Column(db.String(100))  # 邮箱
    role = db.Column(db.String(20), nullable=False, default='user')  # 角色：admin/hr/user
    avatar = db.Column(db.String(255), default='default_avatar.png')  # 头像路径
    company = db.Column(db.String(100))  # 公司名称（HR角色使用）
    is_active = db.Column(db.Boolean, default=True)  # 账号状态
    created_at = db.Column(db.DateTime, default=datetime.now)  # 注册时间

    # 关联关系
    resumes = db.relationship('Resume', backref='user', lazy=True, cascade='all, delete-orphan')
    jobs = db.relationship('Job', backref='hr', lazy=True, cascade='all, delete-orphan')
    deliveries = db.relationship('Delivery', foreign_keys='Delivery.user_id', backref='job_seeker', lazy=True)

    def __repr__(self):
        return f'<User {self.username}({self.role})>'

    def to_dict(self):
        """将用户对象转换为字典，方便JSON序列化"""
        return {
            'id': self.id,
            'username': self.username,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'role': self.role,
            'avatar': self.avatar,
            'company': self.company,
            'is_active': self.is_active,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


class Resume(db.Model):
    """
    简历表 - 存储求职者的简历信息
    支持在线填写和文件上传两种方式
    """
    __tablename__ = 'resumes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)  # 关联用户

    # 基本信息
    real_name = db.Column(db.String(50), nullable=False)  # 真实姓名
    gender = db.Column(db.String(10))  # 性别
    age = db.Column(db.Integer)  # 年龄
    phone = db.Column(db.String(20))  # 联系电话
    email = db.Column(db.String(100))  # 邮箱

    # 教育背景
    education = db.Column(db.String(20))  # 学历（博士/硕士/本科/大专）
    school = db.Column(db.String(100))  # 毕业院校
    major = db.Column(db.String(100))  # 专业

    # 能力与经历
    skills = db.Column(db.Text)  # 技能标签（逗号分隔）
    project_exp = db.Column(db.Text)  # 项目经验
    internship_exp = db.Column(db.Text)  # 实习经验
    awards = db.Column(db.Text)  # 获奖情况
    self_eval = db.Column(db.Text)  # 自我评价
    experience = db.Column(db.Text)  # 工作经验

    # 求职意向
    current_city = db.Column(db.String(50))  # 当前城市
    expected_city = db.Column(db.String(100))  # 期望城市
    expected_salary_min = db.Column(db.Integer)  # 期望最低薪资
    expected_salary_max = db.Column(db.Integer)  # 期望最高薪资
    preferred_categories = db.Column(db.Text)  # 期望岗位类别

    # 文件简历
    file_path = db.Column(db.String(255))  # 上传的简历文件路径
    file_content = db.Column(db.Text)  # 解析后的简历文本内容

    # 状态管理
    status = db.Column(db.String(20), default='待投递')  # 简历状态：待投递/已投递/已匹配
    created_at = db.Column(db.DateTime, default=datetime.now)  # 创建时间
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)  # 更新时间

    # 关联关系
    match_results = db.relationship('MatchResult', backref='resume', lazy=True, cascade='all, delete-orphan')
    deliveries = db.relationship('Delivery', backref='resume', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Resume {self.real_name}({self.school})>'

    def to_dict(self):
        """将简历对象转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'real_name': self.real_name,
            'gender': self.gender,
            'age': self.age,
            'phone': self.phone,
            'email': self.email,
            'education': self.education,
            'school': self.school,
            'major': self.major,
            'skills': self.skills,
            'project_exp': self.project_exp,
            'internship_exp': self.internship_exp,
            'awards': self.awards,
            'self_eval': self.self_eval,
            'experience': self.experience,
            'current_city': self.current_city,
            'expected_city': self.expected_city,
            'expected_salary_min': self.expected_salary_min,
            'expected_salary_max': self.expected_salary_max,
            'preferred_categories': self.preferred_categories,
            'file_path': self.file_path,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }

    def get_full_text(self):
        """获取简历完整文本，用于智能匹配"""
        text_parts = [
            self.real_name or '',
            self.education or '',
            self.school or '',
            self.major or '',
            self.skills or '',
            self.project_exp or '',
            self.internship_exp or '',
            self.awards or '',
            self.self_eval or '',
            self.experience or '',
            self.current_city or '',
            self.expected_city or '',
            self.preferred_categories or '',
            self.file_content or ''
        ]
        return ' '.join(filter(None, text_parts))


class Job(db.Model):
    """
    岗位表 - 存储HR发布的校招岗位信息
    """
    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    original_id = db.Column(db.String(20), index=True)  # CSV原始ID (如: JOB770487)
    hr_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)  # 发布者HR

    # 岗位基本信息
    title = db.Column(db.String(100), nullable=False)  # 岗位名称
    city = db.Column(db.String(50))  # 工作城市
    salary_min = db.Column(db.Integer)  # 最低薪资
    salary_max = db.Column(db.Integer)  # 最高薪资
    salary_avg = db.Column(db.Integer)  # 平均薪资

    # 公司信息
    company_name = db.Column(db.String(100))  # 公司名称
    company_size = db.Column(db.String(50))  # 公司规模
    company_type = db.Column(db.String(50))  # 公司类型
    job_category = db.Column(db.String(50))  # 岗位类别

    # 要求条件
    education_req = db.Column(db.String(50))  # 学历要求
    major_req = db.Column(db.String(200))  # 专业要求
    skills_req = db.Column(db.Text)  # 技能要求
    experience_req = db.Column(db.String(50))  # 经验要求

    # 岗位描述
    responsibilities = db.Column(db.Text)  # 岗位职责
    requirements = db.Column(db.Text)  # 任职要求

    # 其他信息
    recruit_num = db.Column(db.Integer, default=1)  # 招聘人数
    status = db.Column(db.String(20), default='招聘中')  # 状态：招聘中/已下架
    views = db.Column(db.Integer, default=0)  # 浏览次数
    publish_date = db.Column(db.String(20))  # 发布日期

    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.now)  # 发布时间
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)  # 更新时间

    # 关联关系
    match_results = db.relationship('MatchResult', backref='job', lazy=True, cascade='all, delete-orphan')
    deliveries = db.relationship('Delivery', backref='job', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Job {self.title}({self.city})>'

    def to_dict(self):
        """将岗位对象转换为字典"""
        return {
            'id': self.id,
            'original_id': self.original_id,
            'hr_id': self.hr_id,
            'title': self.title,
            'city': self.city,
            'salary_min': self.salary_min,
            'salary_max': self.salary_max,
            'salary_avg': self.salary_avg,
            'company_name': self.company_name,
            'company_size': self.company_size,
            'company_type': self.company_type,
            'job_category': self.job_category,
            'education_req': self.education_req,
            'major_req': self.major_req,
            'skills_req': self.skills_req,
            'experience_req': self.experience_req,
            'responsibilities': self.responsibilities,
            'requirements': self.requirements,
            'recruit_num': self.recruit_num,
            'status': self.status,
            'views': self.views,
            'publish_date': self.publish_date,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

    def get_full_text(self):
        """获取岗位完整文本，用于智能匹配"""
        text_parts = [
            self.title or '',
            self.education_req or '',
            self.major_req or '',
            self.skills_req or '',
            self.experience_req or '',
            self.company_name or '',
            self.job_category or '',
            self.responsibilities or '',
            self.requirements or ''
        ]
        return ' '.join(filter(None, text_parts))


class Delivery(db.Model):
    """
    投递表 - 记录求职者投递简历到岗位的记录
    """
    __tablename__ = 'deliveries'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)  # 求职者
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False, index=True)  # 岗位
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id'), nullable=False)  # 简历

    # 匹配相关
    match_score = db.Column(db.Float, default=0.0)  # 匹配分数（0-100）
    skill_match_score = db.Column(db.Float, default=0.0)  # 技能匹配分
    salary_match_score = db.Column(db.Float, default=0.0)  # 薪资匹配分
    education_match_score = db.Column(db.Float, default=0.0)  # 学历匹配分
    experience_match_score = db.Column(db.Float, default=0.0)  # 经验匹配分
    is_matched = db.Column(db.Boolean, default=False)  # 是否匹配成功

    # 状态
    status = db.Column(db.String(20), default='待查看')  # 状态：待查看/已查看/已联系/不合适

    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.now)  # 投递时间

    # 唯一约束：同一用户不能重复投递同一岗位
    __table_args__ = (
        db.UniqueConstraint('user_id', 'job_id', name='unique_delivery'),
    )

    def __repr__(self):
        return f'<Delivery user={self.user_id} job={self.job_id}>'

    def to_dict(self):
        """将投递记录转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'job_id': self.job_id,
            'resume_id': self.resume_id,
            'match_score': self.match_score,
            'skill_match_score': self.skill_match_score,
            'salary_match_score': self.salary_match_score,
            'education_match_score': self.education_match_score,
            'experience_match_score': self.experience_match_score,
            'is_matched': self.is_matched,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


class MatchResult(db.Model):
    """
    匹配结果表 - 存储简历与岗位的匹配计算结果
    智能匹配算法的核心数据表
    """
    __tablename__ = 'match_results'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id'), nullable=False, index=True)  # 简历
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False, index=True)  # 岗位

    # 匹配分数
    similarity_score = db.Column(db.Float, nullable=False)  # 相似度分数（0-1）
    final_score = db.Column(db.Float, nullable=False)  # 最终分数（0-100）

    # 详细匹配报告（JSON格式存储）
    match_details = db.Column(db.Text)  # 匹配详情：匹配项、不匹配项、优势、劣势等

    # 各维度分数
    education_score = db.Column(db.Float, default=0)  # 学历匹配分
    skill_score = db.Column(db.Float, default=0)  # 技能匹配分
    experience_score = db.Column(db.Float, default=0)  # 经验匹配分

    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.now)  # 计算时间

    # 唯一约束：同一简历和岗位的匹配结果唯一
    __table_args__ = (
        db.UniqueConstraint('resume_id', 'job_id', name='unique_match'),
    )

    def __repr__(self):
        return f'<MatchResult resume={self.resume_id} job={self.job_id} score={self.final_score}>'

    def to_dict(self):
        """将匹配结果转换为字典"""
        return {
            'id': self.id,
            'resume_id': self.resume_id,
            'job_id': self.job_id,
            'similarity_score': self.similarity_score,
            'final_score': self.final_score,
            'match_details': self.match_details,
            'education_score': self.education_score,
            'skill_score': self.skill_score,
            'experience_score': self.experience_score,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


class SystemConfig(db.Model):
    """
    系统配置表 - 存储系统参数配置
    """
    __tablename__ = 'system_config'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    param_name = db.Column(db.String(50), unique=True, nullable=False)  # 参数名
    param_value = db.Column(db.Text)  # 参数值
    description = db.Column(db.String(255))  # 参数描述
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f'<SystemConfig {self.param_name}={self.param_value}>'


class SystemLog(db.Model):
    """
    系统日志表 - 记录系统操作日志
    """
    __tablename__ = 'system_logs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # 操作用户
    action = db.Column(db.String(50), nullable=False)  # 操作类型
    target_type = db.Column(db.String(50))  # 操作对象类型
    target_id = db.Column(db.Integer)  # 操作对象ID
    details = db.Column(db.Text)  # 操作详情
    ip_address = db.Column(db.String(50))  # IP地址
    created_at = db.Column(db.DateTime, default=datetime.now)  # 操作时间

    def __repr__(self):
        return f'<SystemLog {self.action} by user={self.user_id}>'


def init_db(app):
    """
    初始化数据库
    创建所有数据表，并添加默认管理员账号
    """
    with app.app_context():
        # 创建所有表
        db.create_all()

        # 检查是否已有管理员账号，没有则创建默认管理员
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            from werkzeug.security import generate_password_hash
            default_admin = User(
                username='admin',
                password=generate_password_hash('admin123'),
                name='系统管理员',
                phone='13800138000',
                email='admin@system.com',
                role='admin'
            )
            db.session.add(default_admin)

            # 创建测试HR账号
            test_hr = User(
                username='hr',
                password=generate_password_hash('hr123'),
                name='测试HR',
                phone='13800138001',
                email='hr@test.com',
                role='hr',
                company='测试科技有限公司'
            )
            db.session.add(test_hr)

            # 创建测试求职者账号
            test_user = User(
                username='user',
                password=generate_password_hash('user123'),
                name='测试求职者',
                phone='13800138002',
                email='user@test.com',
                role='user'
            )
            db.session.add(test_user)

            db.session.commit()
            print("数据库初始化完成，已创建默认账号")
            print("管理员: admin / admin123")
            print("HR: hr / hr123")
            print("求职者: user / user123")


class Message(db.Model):
    """消息通知表"""
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(20), default='system')  # system/delivery/application
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f'<Message {self.title}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'sender_id': self.sender_id,
            'title': self.title,
            'content': self.content,
            'message_type': self.message_type,
            'is_read': self.is_read,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


class Favorite(db.Model):
    """岗位收藏表"""
    __tablename__ = 'favorites'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

    # 唯一约束
    __table_args__ = (
        db.UniqueConstraint('user_id', 'job_id', name='unique_favorite'),
    )

    def __repr__(self):
        return f'<Favorite user={self.user_id} job={self.job_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'job_id': self.job_id,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


class BrowseHistory(db.Model):
    """浏览足迹表"""
    __tablename__ = 'browse_history'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False, index=True)
    stay_duration = db.Column(db.Integer, default=0)  # 停留时长(秒)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f'<BrowseHistory user={self.user_id} job={self.job_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'job_id': self.job_id,
            'stay_duration': self.stay_duration,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


class Analytics(db.Model):
    """数据统计表 - 存储聚合数据用于仪表盘"""
    __tablename__ = 'analytics'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    stat_date = db.Column(db.Date, nullable=False, index=True)  # 统计日期
    stat_type = db.Column(db.String(50), nullable=False)  # 统计类型: daily_jobs, daily_users, daily_deliveries
    stat_value = db.Column(db.Integer, default=0)  # 统计值
    extra_data = db.Column(db.Text)  # 额外JSON数据

    __table_args__ = (
        db.UniqueConstraint('stat_date', 'stat_type', name='unique_stat'),
    )

    def __repr__(self):
        return f'<Analytics {self.stat_date} {self.stat_type}>'
