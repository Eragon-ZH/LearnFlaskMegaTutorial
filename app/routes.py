from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.models import User
from app.forms import LoginForm, RegistrationForm

@app.route('/')
@app.route('/index')
@login_required
def index():
    # user = { 'username': 'Dovahkiin' }
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
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET','POST'])
def login():
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
    logout_user()
    return redirect(url_for('index'))
