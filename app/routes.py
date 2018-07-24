from flask import render_template, flash, redirect, url_for, request, g, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime
from flask_babel import _, get_locale
from guess_language import guess_language

from app import app, db
from app.models import User, Post
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm, \
                        ResetPasswordRequestForm, ResetPasswordForm
from app.email import send_password_reset_email
from app.translate import translate

@app.before_request
def before_request():
    """设置last_seen"""
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    # 明明get_locale那是'zh_CN'，到这就变成'zh_Hans_CN'了
    g.locale = str(get_locale())
    # 经实验发现moment.lang设置为'zh_Hans_CN'不管用，设置成'zh_CN'才管用
    if g.locale == 'zh_Hans_CN':
        g.locale = 'zh'

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    """主页"""
    form = PostForm()
    if form.validate_on_submit():
        language = guess_language(form.post.data)
        if language == 'UNKNOW' or len(language) > 5:
            language = ''
        post = Post(body=form.post.data, author=current_user, language=language)
        db.session.add(post)
        db.session.commit()
        flash(_('Your post is now live!'))
        return redirect(url_for('index'))
    # 从request.args获取页码
    page = request.args.get('page', 1, type=int)
    # 获取posts。paginate(页码，每页条目数，True返回404错误|False返回空列表)
    posts = current_user.followed_posts().paginate(
        page, app.config['POSTS_PRE_PAGE'], False)
    # paginate()返回Pagination对象具有items、next_num、has_next等属性
    next_url = url_for('index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title=_('Home'), form=form,
                            posts=posts.items, next_url=next_url,
                            prev_url=prev_url)

@app.route('/explore')
@login_required
def explore():
    """探索，显示所有post"""
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PRE_PAGE'], False)
    next_url = url_for('explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title=_('Explore'), posts=posts.items,
                            next_url=next_url, prev_url=prev_url)

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
        flash(_('Congratulations, you are now a registered user!'))
        return redirect(url_for('login'))
    return render_template('register.html', title=_('Register'), form=form)

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
            flash(_('Invalid username or password'))
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
    return render_template('login.html', title=_('Sign In'), form=form)

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
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PRE_PAGE'], False)
    next_url = url_for('user', username=username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('user', username=username, page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('user.html', user=user, posts=posts.items,
                            next_url=next_url, prev_url=prev_url)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """编辑个人资料"""
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('edit_profile'))
    # 第一次请求时重定向并用现在的资料填充
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title=_('Edit Profile'),
                            form=form)

@app.route('/follow/<username>')
@login_required
def follow(username):
    """关注"""
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('index'))
    if user == current_user:
        flash(_('You cannot follow yourself!'))
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(_('You are following %(username)s!', username=username))
    return redirect(url_for('user', username=username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    """取消关注"""
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('index'))
    if user == current_user:
        flash(_('You cannot unfollow yourself!'))
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(_('You are not following %(username)s.', username=username))
    return redirect(url_for('user', username=username))

@app.route('/reset_password_request', methods=['GET','POST'])
def reset_password_request():
    """重置密码请求"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        # 邮箱没有被注册也提示消息，避免从客户端获取邮箱是否已经被使用
        flash(_('Check your email for the instructions to reset your password'))
        return redirect(url_for('index'))
    return render_template('reset_password_request.html',
                            title=_('Reset Password'), form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """重置密码"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    # 通过令牌验证用户身份
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been reset.'))
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

@app.route('/translate', methods=['POST'])
@login_required
def translate_text():
    return jsonify({'text': translate(request.form['text'],
                                      request.form['source_language'],
                                      request.form['dest_language'])})
