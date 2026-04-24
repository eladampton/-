# -*- coding: utf-8 -*-
"""
Campus Recruitment System - Flask Main Application (Optimized)
"""

import os
import sys
from flask import Flask, render_template, request
from flask_compress import Compress
from flask_login import LoginManager, current_user
from flask_wtf.csrf import CSRFProtect

# Config
from config.settings import config, BASE_DIR

# Models
from models import db, User, init_db

# Blueprints
from routes import public_bp, seeker_bp, hr_bp, admin_bp, api_bp
from middleware import register_middleware


def create_app(config_name='default'):
    """Application factory - Create Flask app"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Ensure upload directories exist
    os.makedirs(os.path.join(BASE_DIR, 'static', 'uploads', 'resumes'), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, 'static', 'uploads', 'avatars'), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, 'logs'), exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    Compress(app)

    # CSRF protection
    csrf = CSRFProtect()
    csrf.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'public.login'
    login_manager.login_message = 'Please login first'
    login_manager.login_message_category = 'warning'

    @login_manager.user_loader
    def load_user(user_id):
        """Load user"""
        return User.query.get(int(user_id))

    # Register blueprints
    app.register_blueprint(public_bp)
    app.register_blueprint(seeker_bp)
    app.register_blueprint(hr_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    # Register middleware
    register_middleware(app)

    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    # Before/After request hooks for performance
    @app.before_request
    def before_request():
        """Log request start"""
        pass

    @app.after_request
    def after_request(response):
        """Add cache headers for static files"""
        if request.path.startswith('/static/'):
            response.headers['Cache-Control'] = 'public, max-age=31536000'
        return response

    return app


def run_app():
    """运行应用"""
    app = create_app('development')

    with app.app_context():
        # 初始化数据库
        init_db(app)

    print("=" * 60)
    print("Campus Recruitment System")
    print("=" * 60)
    print("Running at: http://127.0.0.1:5000")
    print("Admin: admin / admin123")
    print("HR: hr / hr123")
    print("User: user / user123")
    print("=" * 60)

    app.run(debug=True, host='127.0.0.1', port=5000)


if __name__ == '__main__':
    from flask import render_template
    run_app()
