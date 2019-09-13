from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app import db
from app import app # 从app包中导入 app这个实例
from app.forms import LoginForm, RegistrationForm,EditProfileForm
from app.models import User,Post
from datetime import datetime



@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

#3个路由
@app.route('/')
@app.route('/index')
@login_required
def index():
    # user = {'username': 'Miguel'}
    # title='Home'
    posts = [  # 创建一个列表：帖子。里面元素是两个字典，每个字典里元素还是字典，分别作者、帖子内容。
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
    {
        'author': {'username': 'Susan'},
        'body': 'The Avengers movie was so cool!'
    }
    ]

    # return render_template('index.html', user=user,posts=posts,title='Home')
    return render_template('index.html', posts=posts)

# 登录视图函数
@app.route('/login',methods=['GET', 'POST'])
def login():
    # print("hi")
    # login_from = LoginForm()
    # # 如果Sing in按钮按下，对表单信息进行重定向校验
    # if login_from.validate_on_submit():
    #     # print('Hi')
    #     # msg = 'Hi Login request for user:'+login_from.username.data
    #     msg = 'Hi Login request for user:{};remember_me:{}'.format(login_from.username.data , login_from.remember_me.data)
    #     flash(msg)
    #     print(msg)
    #     return redirect(url_for('index'))
    # return render_template('login.html', form = login_from , title='Login')

    if current_user.is_authenticated:
        # 如果已登录,重定向至 index.html
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        # 向数据库查询有无当前用户的信息,'form.username.data'用户在表单中输入的用户名
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            # 登陆无效，重定向至登录页
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)    #form.remember_me.data,使用Cookie记住用户信息

        # 重定向到 next 页面
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)

    return render_template('login.html', title='Sign In', form=form)

# 退出登录视图函数
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


# 注册页
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        msg = 'Congratulations, you are now a registered user!'
        flash(msg)
        print(msg)
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


# 用户展示页面
@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('user.html', user=user, posts=posts)


# 用户编辑页
@app.route('/edit_profile',methods=['GET','POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()

        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)