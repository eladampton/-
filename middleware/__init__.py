# -*- coding: utf-8 -*-
"""
中间件模块 - 添加安全头和性能优化
"""
from flask import request, g
import time
import structlog

logger = structlog.get_logger()


def add_security_headers(response):
    """添加安全响应头"""
    # 生产环境建议启用完整CSP，开发环境使用宽松配置
    # XSS防护
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response


def before_request():
    """请求开始时的处理"""
    g.start_time = time.time()


def after_request(response):
    """请求结束时的处理"""
    # 计算请求耗时
    if hasattr(g, 'start_time'):
        duration = time.time() - g.start_time
        response.headers['X-Response-Time'] = f'{duration:.3f}s'

    # 缓存控制 - 静态资源长期缓存
    if request.path.startswith('/static/'):
        response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
        response.headers['Expires'] = 'Thu, 31 Dec 2037 23:55:55 GMT'

    # 添加安全头
    response = add_security_headers(response)

    return response


def register_middleware(app):
    """注册中间件"""
    app.before_request(before_request)
    app.after_request(after_request)
