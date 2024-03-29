from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app import db
from app import app # 从app包中导入 app这个实例
from app.email import send_password_reset_email
from app.forms import LoginForm, RegistrationForm, EditProfileForm, ResetPasswordRequestForm, ResetPasswordForm, PostForm
from app.models import User, Post
from datetime import datetime
from flask_babel import _



# 最后一次登录的时间视图函数
@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

#3个路由视图函数
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods= ['GET', 'POST'])
@login_required
def index():
    # user = {'username': 'Miguel'}     title='Home'
    form = PostForm()
    if form.validate_on_submit():   #post请求
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash(_('Your post is now live!'))
        return redirect(url_for('index'))   # redirect 重定向 两次请求; 避免无意中刷新页面时，插入重复的帖子
    #get 请求
    # posts = [  # 创建一个列表：帖子。里面元素是两个字典，每个字典里元素还是字典，分别作者、帖子内容。
    #     {
    #         'author': {'username': 'John'},
    #         'body': 'Beautiful day in Portland!'
    #     },
    # {
    #     'author': {'username': 'Susan'},
    #     'body': 'The Avengers movie was so cool!'
    # }
    # ]

# #   循环当前用户所发的帖子
#     posts = current_user.followed_posts().all()

    # return render_template('index.html', user=user,posts=posts,title='Home')

    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) if posts.has_prev else None
    # render_template 一次请求
    return render_template('index.html', title='Home Page', form=form, posts=posts.items, next_url=next_url,prev_url=prev_url)


# 前台帖子展示视图函数
@app.route('/explore')
@login_required
def explore():
    #每页显示3条帖子, 帖子配置数据在 config.py
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('explore', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) if posts.has_prev else None
    return render_template('index.html', title='Explore', posts=posts.items, next_url=next_url, prev_url=prev_url)

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
            flash(_('Invalid username or password'))
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


# 注册页视图函数
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
        # msg = 'Congratulations, you are now a registered user!'
        flash(_('Congratulations, you are now a registered user!'))
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


# 用户展示页面视图函数
@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    # posts = [
    #     {'author': user, 'body': 'Test post #1'},
    #     {'author': user, 'body': 'Test post #2'}
    # ]

    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('user', username=user.username, page=posts.next_num) if posts.has_next else None
    prev_url = url_for('user', username=user.username, page=posts.prev_num) if posts.has_prev else None
    return render_template('user.html', user=user, posts=posts.items, next_url=next_url, prev_url=prev_url)


# 用户编辑页视图函数
@app.route('/edit_profile',methods=['GET','POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()

        flash(_('Your changes have been saved.'))
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)

# 关注页视图函数
@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash(_('You cannot follow yourself!'))
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('user', username=username))

# 取消关注页视图函数
@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    #current_user 判断是否为当前用户
    if user == current_user:
        flash(_('You cannot unfollow yourself!'))
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(username))
    return redirect(url_for('user', username=username))

# 重置用户密码请求视图函数
@app.route('/reset_password_request', methods=['GET','POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash(_('Check your email for the instructions to reset your password'))
        return redirect(url_for('login'))
    return render_template('reset_password_request.html', title='Reset Password', form=form)

# 重置用户密码视图函数
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)  #staticmethod 静态方法 验证用户的 token
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():   #进行表单验证
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been reset.'))
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)



