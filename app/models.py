from datetime import datetime
from app import db

class User(db.Model):
    """用户"""
    # 唯一索引
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    # 在一对多中的‘一’定义relationship，backref定义‘多’对象字段的名称
    # lazy定义关系数据库查询将如何发布
    posts = db.relationship('Post', backref='author', lazy='dynamic')

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
