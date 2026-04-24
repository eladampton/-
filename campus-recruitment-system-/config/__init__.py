# -*- coding: utf-8 -*-
"""
应用配置文件 - 集中管理所有配置
"""
import os
from datetime import timedelta

# 基础目录 - 项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Config:
    """基础配置类"""
    # Flask密钥
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-in-production'

    # 数据库配置 - 使用环境变量更安全
    _db_user = os.environ.get('DB_USER', 'root')
    _db_password = os.environ.get('DB_PASSWORD', '')
    _db_host = os.environ.get('DB_HOST', 'localhost')
    _db_port = os.environ.get('DB_PORT', '3306')
    _db_name = os.environ.get('DB_NAME', 'campus_recruitment')

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'mysql+pymysql://{_db_user}:{_db_password}@{_db_host}:{_db_port}/{_db_name}?charset=utf8mb4'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 数据库连接池配置 (性能优化)
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,           # 连接池大小
        'pool_recycle': 3600,      # 连接回收时间(秒)
        'pool_pre_ping': True,     # 使用前检测连接
        'max_overflow': 20,        # 额外连接数上限
        'echo': False,             # 关闭SQL日志
    }

    # Session配置
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = False  # 生产环境设为True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # 文件上传配置
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

    # 分页配置
    DEFAULT_PAGE_SIZE = 15
    MAX_PAGE_SIZE = 100

    # 缓存配置
    CACHE_TYPE = 'simple'  # simple/redis/memcached
    CACHE_DEFAULT_TIMEOUT = 300

    # 限流配置
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URL = 'memory://'

    # 日志配置
    LOG_LEVEL = 'INFO'
    LOG_FILE = os.path.join(BASE_DIR, 'logs', 'app.log')


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}