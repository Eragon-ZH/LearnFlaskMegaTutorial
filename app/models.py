from datetime import datetime
from werkzeug import generate_password_hash, check_password_hash
from flask_login import UserMixin

from app import db, login

class User(UserMixin, db.Model):
    """用户"""
    """flask_login需要实现is_authenticated,is_activate,is_anonymous,get_id,
    借助UserMixin进行通常实现"""
    # 唯一索引
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    # 在一对多中的‘一’定义relationship，backref定义‘多’对象字段的名称
    # lazy定义关系数据库查询将如何发布
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # 打印
    def __repr__(self):
        return '<User {}>'.format(self.username)

class Post(db.Model):
    """博文"""
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    # post的id作为外键关联到user的id
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
