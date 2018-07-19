from datetime import datetime
from werkzeug import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
from time import time
import jwt

from app import app, db, login

# followers关联表
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

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
    # 关注列表
    followed = db.relationship(
        # 自引用，左右两侧都是user，secondary指向关系的关联表(上面定义的followers)
        'User', secondary=followers,
        # 通过关联表关联左侧(关注者)的条件，即follower_id字段与这个user的id匹配
        # followers.c.follower_id表达式引用了该关系表中的follower_id列
        primaryjoin=(followers.c.follower_id == id),
        # 通过关联表关联右侧(被关注者)的条件，
        secondaryjoin=(followers.c.followed_id == id),
        # backref定义右侧实体如何访问该关系。左侧followed，右侧followers
        # lazy参数定义查询的执行方式。backref内应用于右侧，在外应用于左侧
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def set_password(self, password):
        """保存密码的哈希"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """检查密码"""
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        """创建加密令牌"""
        return jwt.encode(
            #有效载荷，到期时间，加密密钥，加密算法
            {'reset_password': self.id, 'exp':time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    # 静态方法不会接受类作为第一个参数，可以直接从类中调用
    @staticmethod
    def verify_reset_password_token(token):
        """验证令牌"""
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithm=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    def avatar(self, size):
        """使用用户的邮箱从gravatar网站获取头像"""
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def follow(self, user):
        """关注"""
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        """取消关注"""
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        """是否关注某用户"""
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        """查询关注用户的posts"""
        # 关注用户的posts
        followed_post = Post.query.join(
        # 先对post进行联结(join)操作，第一个参数是关联表(followers)，第二个参数是
        # 联结条件。会创建一个将posts表数据和followers表数据组合起来的临时表
            followers, (followers.c.followed_id == Post.user_id)).filter(
            # 再过滤(filter)只剩该用户关注的用户的post
                followers.c.follower_id == self.id)
        # 自己的posts
        own_post = Post.query.filter_by(user_id=self.id)
        # 按时间降序返回
        return followed_post.union(own_post).order_by(Post.timestamp.desc())

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
