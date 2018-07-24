from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_babel import _
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, \
    ResetPasswordRequestForm, ResetPasswordForm
from app.models import User
from app.auth.email import send_password_reset_email

@bp.route('/login', methods=['GET','POST'])
def login():
    """登录"""
    # 已经登录直接跳转主页
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    # 如果是POST就会收集所有数据并执行验证方法，如果是GET返回False
    if form.validate_on_submit():
        # 从数据库查询用户,只可能有一条所以可以用first,不存在返回None
        user = User.query.filter_by(username=form.username.data).first()
        # 不存在用户或者密码不正确重新登录
        if user is None or not user.check_password(form.password.data):
            flash(_('Invalid username or password'))
            return redirect(url_for('auth.login'))
        # 登录后返回主页
        login_user(user, remember=form.remember_me.data)
        # login_required拦截请求时会自动在url中添加查询字符串?next=(之前的url)
        # 获取next并在登录后自动跳转
        next_page = request.args.get('next')
        # 如果url的next参数设置成了包含域名的完整路径，则也会调到主页。这是为了安全.
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html', title=_('Sign In'), form=form)

@bp.route('/logout')
def logout():
    """登出"""
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET','POST'])
def register():
    """注册"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('Congratulations, you are now a registered user!'))
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title=_('Register'),
                           form=form)

@bp.route('/reset_password_request', methods=['GET','POST'])
def reset_password_request():
    """重置密码请求"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        # 邮箱没有被注册也提示消息，避免从客户端获取邮箱是否已经被使用
        flash(_('Check your email for the instructions to reset your password'))
        return redirect(url_for('main.index'))
    return render_template('auth/reset_password_request.html',
                            title=_('Reset Password'), form=form)

@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """重置密码"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    # 通过令牌验证用户身份
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been reset.'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)
