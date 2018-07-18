import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    """配置类"""
    # 从环境变量中获取配置，不然就使用默认值
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    # 数据库位置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    # 设置数据变更后是否发送信号给应用
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 添加邮箱来获得bug的log
    # 邮箱服务器
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    # 邮箱端口，默认25
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    # 布尔标志指示加密连接
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    # 用户名和密码可选
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    # 邮箱地址
    ADMINS = ['your-email@example.com']
