from app import app, db, cli
from app.models import User, Post


@app.shell_context_processor
def make_shell_context():
    """配置“shell上下文”,预先导入一份对象列表"""
    # 该函数没起作用(windows 10 64bit)
    return {'db': db, 'User': User, 'Post': Post}
