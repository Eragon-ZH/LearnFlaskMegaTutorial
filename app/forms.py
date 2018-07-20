from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField,\
                    TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo,\
                    Length
from flask_babel import _, lazy_gettext as _l
from app.models import User

class LoginForm(FlaskForm):
    """登录表单"""
    username = StringField(_l('Username'), validators=[DataRequired()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    remember_me = BooleanField(_l('Remember Me'))
    submit = SubmitField(_l('Sign In'))

class RegistrationForm(FlaskForm):
    """注册表单"""
    username = StringField(_l('Username'), validators=[DataRequired()])
    email = StringField(_l('Email'), validators=[DataRequired(),Email()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    password2 = PasswordField(_l('Repeat Password'),
        validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_l('Register'))

    # 通过定义validate开头的类方法自定义验证器
    def validate_username(self, username):
        """验证用户名是否已被注册"""
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError(_('Please use a different username.'))

    def validate_email(self, email):
        """验证邮箱是否已被注册"""
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError(_('Email had been used'))

class ResetPasswordRequestForm(FlaskForm):
    """重置密码请求表单"""
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    submit = SubmitField(_l('Request Password Reset'))

class ResetPasswordForm(FlaskForm):
    """重置密码表单"""
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    password2 = PasswordField(_l('Repeat Password'),
                            validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_l('Request Password Reset'))

class EditProfileForm(FlaskForm):
    """个人资料编辑表单"""
    username = StringField(_l('Username'), validators=[DataRequired()])
    about_me = TextAreaField(_l('About me'),
                                validators=[Length(min=0, max=140)])
    submit = SubmitField(_l('Submit'))

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        """检查名字是否合法"""
        # 同时多个进程同时读取数据库的时候可能仍会存在问题
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError(_('Username had been used.'))

class PostForm(FlaskForm):
    """发表微博表单"""
    post = TextAreaField(_l('Say someting'), validators=[
        DataRequired(), Length(min=1, max=140)])
    submit = SubmitField(_l('Submit'))
