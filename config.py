import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
# 从文件中导入环境变量
load_dotenv(os.path.join(basedir, '.env'))

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
    # 每页显示的post数量
    POSTS_PRE_PAGE = 25
    # 语言
    LANGUAGES = ['en' , 'cn', 'zh_CN']
    # 腾讯翻译的key
    TC_TRANSLATOR_ID = os.environ.get('TC_TRANSLATOR_ID')
    TC_TRANSLATOR_KEY = os.environ.get('TC_TRANSLATOR_KEY')
    # Elasticsearch配置
    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')
