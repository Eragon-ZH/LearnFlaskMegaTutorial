from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime

from app import app, db
from app.models import User
from app.forms import LoginForm, RegistrationForm, EditProfileForm

@app.route('/')
@app.route('/index')
@login_required
def index():
    """主页"""
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in NewYork!'
        },
        {
            'author': {'username': 'Finch'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html', title='Home', posts=posts)

@app.route('/register', methods=['GET','POST'])
def register():
    """注册"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET','POST'])
def login():
    """登录"""
    # 已经登录直接跳转主页
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    # 如果是POST就会收集所有数据并执行验证方法，如果是GET返回False
    if form.validate_on_submit():
        # 从数据库查询用户,只可能有一条所以可以用first,不存在返回None
        user = User.query.filter_by(username=form.username.data).first()
        # 不存在用户或者密码不正确重新登录
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        # 登录后返回主页
        login_user(user, remember=form.remember_me.data)
        # login_required拦截请求时会自动在url中添加查询字符串?next=(之前的url)
        # 获取next并在登录后自动跳转
        next_page = request.args.get('next')
        # 如果url的next参数设置成了包含域名的完整路径，则也会调到主页。这是为了安全.
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    """登出"""
    logout_user()
    return redirect(url_for('index'))

# <>内的值会赋予给username变量传递给函数
@app.route('/user/<username>')
@login_required
def user(username):
    """用户"""
    # 没有结果会向服务器发404错误
    user = User.query.filter_by(username=username).first_or_404()
    posts = [
        {'author': user, 'body': 'Test post#1'},
        {'author': user, 'body': 'Test post#2'},
    ]
    return render_template('user.html', user=user, posts=posts)

@app.before_request
def before_request():
    """设置last_seen"""
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """编辑个人资料"""
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    # 第一次请求时重定向并用现在的资料填充
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)
