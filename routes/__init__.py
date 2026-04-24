# -*- coding: utf-8 -*-
"""
路由模块 - 注册所有蓝图
"""
from .public import public_bp
from .seeker import seeker_bp
from .hr import hr_bp
from .admin import admin_bp
from .api import api_bp


def register_blueprints(app):
    """注册所有蓝图"""
    app.register_blueprint(public_bp)
    app.register_blueprint(seeker_bp)
    app.register_blueprint(hr_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)
