import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from flask import Flask, request, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_babel import Babel, lazy_gettext as _l
from config import Config

# 先在全局创建对象
# 数据库对象
db = SQLAlchemy()
# 迁移引擎对象
migrate = Migrate()
# 登录管理对象
login = LoginManager()
# 使用login_required装饰器需要指定login_view（登录的视图函数）
login.login_view = 'auth.login'
login.login_message = _l('Please log in to access this page')
# 邮件对象
mail = Mail()
# Bootstrap对象
bootstrap = Bootstrap()
# Moment对象
moment = Moment()
# Babel对象
babel = Babel()

def create_app(config_class=Config):
    """应用工厂函数"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 传递参数
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    babel.init_app(app)

    # 向应用注册errors的blueprint
    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)
    # 注册auth的blueprint
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    # 注册maind的blueprint
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    # 不以调试模式启动时获取日志
    if not app.debug and not app.testing:
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

    return app

@babel.localeselector
def get_locale():
    """选择最匹配的语言"""
    return request.accept_languages.best_match(current_app.config['LANGUAGES'])

# 应用实例创建后导入模块
from app import models
