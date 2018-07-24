from flask import render_template
from app import db
from app.errors import bp

@bp.app_errorhandler(404)
def not_found_error(error):
    """404错误"""
    # 自定义处理器用到了@errorhandler装饰器
    # 需要额外返回状态码（默认是200）
    return render_template('/errors/404.html'), 404

@bp.app_errorhandler(500)
def internal_error(error):
    """500错误"""
    # 数据库事务回滚
    db.session.rollback()
    return render_template('/errors/500.html'), 500
