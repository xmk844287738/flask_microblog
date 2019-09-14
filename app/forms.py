# form表单

from flask_wtf import FlaskForm #从flask_wtf包中导入FlaskForm类
from wtforms import StringField, PasswordField, BooleanField, TextAreaField , SubmitField  # 导入这些类
from wtforms.validators import DataRequired, EqualTo, ValidationError, Length
from app.models import User
from wtforms.validators import Email


# 登陆表单
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()]) #用户名验证
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')   #复选框，checkbox
    submit = SubmitField('Sign In')     #提交表单按钮


# 注册表单
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    # 双重验证
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        # 向数据库查询,如果查询到数据中的有此用户名的信息,则向前端页面发送 'Please use a different username.' 的错误消息
        user = User.query.filter_by(username=username.data).first()
        # print(username)
        if user is not None:
            raise ValidationError('Please use a different username.')


# 无法查询数据库的用户邮箱信息!!
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        # print(user)
        # 向数据库查询,如果查询到数据中的有此用户邮箱的信息,则向前端页面发送 'Please use a different email address.' 的错误消息
        if user is not None:
            raise ValidationError('Please use a different email address.')

# 重置用户密码请求表单
class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

# 重置用户密码表单
class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')


# 编辑用户信息页表单
class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About_me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

# 博客帖子表单
class PostForm(FlaskForm):
    post = TextAreaField('Say something', validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit')