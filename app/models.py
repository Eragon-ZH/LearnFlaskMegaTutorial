from datetime import datetime
from werkzeug import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5

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
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        """保存密码的哈希"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """检查密码"""
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        """使用用户的邮箱从gravatar网站获取头像"""
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def __repr__(self):
        """打印"""
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
    """借助@login.user_loader装饰器注册到Flask-Login"""
    # id是作为字符串传入的，所以查询的时候需要转换成int
    return User.query.get(int(id))
