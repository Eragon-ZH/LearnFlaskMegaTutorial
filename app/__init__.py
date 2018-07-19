from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import logging
from logging.handlers import RotatingFileHandler
from logging.handlers import SMTPHandler
from flask_mail import Mail
from flask_bootstrap import Bootstrap
import os

# flask对象
app = Flask(__name__)
# 配置对象
app.config.from_object(Config)
# 数据库对象
db = SQLAlchemy(app)
# 迁移引擎对象
migrate = Migrate(app, db)
# 登录管理对象
login = LoginManager(app)
# 使用login_required装饰器需要指定login_view（登录的视图函数）
login.login_view = 'login'
# 邮件对象
mail = Mail(app)
# Bootstrap对象
bootstrap = Bootstrap(app)

# 应用实例创建后导入模块
from app import routes, models, errors

# 不以调试模式启动时获取日志
if not app.debug:
    # 配置中存在邮件服务器启用邮件日志记录器
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME']), app.config['MAIL_PASSWORD']
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        # 实例化一个SMTPHandler
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no-reply@' + app.config['MAIL_SERVER'],
            toaddrs=app.config['ADMINS'], subject='Microblog Failure',
            credentials=auth, secure=secure)
        # 报告错误以上的信息
        mail_handler.setLevel(logging.ERROR)
        # 添加到app.logger对象中
        app.logger.addHandler(mail_handler)
    # 创建日志文件
    # 目录不存在就创建
    if not os.path.exists('logs'):
        os.mkdir('logs')
    # 日志最大文件大小为10kb，只保存最近的10个文件
    file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240,
                                        backupCount=10)
    # Fromatter提供日志消息的自定义模式
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    # 输出一条消息表示应用已经启动了，可以作为服务器重启的标志
    app.logger.setLevel(logging.INFO)
    app.logger.info('Microblog startup')
