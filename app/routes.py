from flask import render_template, flash, redirect, url_for
from app import app
from app.forms import LoginForm

@app.route('/')
@app.route('/index')
def index():
    user = { 'username': 'Dovahkiin' }
    posts = [
        {
            'auther': {'username': 'John'},
            'body': 'Beautiful day in NewYork!'
        },
        {
            'auther': {'username': 'Finch'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html', title='Home', user=user, posts=posts)

@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    # 如果是POST就会收集所有数据并执行验证方法，如果是GET返回False
    if form.validate_on_submit():
        # 向用户展示一条消息
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)
