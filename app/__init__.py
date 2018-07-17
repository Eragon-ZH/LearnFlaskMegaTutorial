from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

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
# 使用login_required装饰器需要指定login_view
login.login_view = 'login'

from app import routes, models
