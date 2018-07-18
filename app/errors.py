from flask import render_template
from app import app, db

@app.errorhandler(404)
def not_found_error(error):
    """404错误"""
    # 自定义处理器用到了@errorhandler装饰器
    # 需要额外返回状态码（默认是200）
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """500错误"""
    # 数据库事务回滚
    db.session.rollback()
    return render_template('500.html'), 500
