from _md5 import md5
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db,login





# 用户模型
# 混入类 多继承，用户登陆模型
class User(UserMixin,db.Model):     #有current_user的属性
    # 4个字段值
    id = db.Column(db.Integer, primary_key=True)    # primary_key 主键
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)   # String 64 => 最多120个字符，unique 唯一的
    password_hash = db.Column(db.String(128))    # 加密后的hash密码 最多128个字符
    posts = db.relationship('Post', backref='author', lazy='dynamic')   # lazy = 'dynamic'动态加载

    about_me = db.Column(db.String(140))    #个人签名
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)     #上一次登录时间  (utcnow 世界时间)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):   # 加密密码
        self.password_hash = generate_password_hash(password)

    def check_password(self,password):  # 验证密码
        return check_password_hash(self.password_hash, password)

# 添加头像，头像与用户相关联，因此将生成头像的URL的逻辑添加到User 用户模型中是很重要的。
    def avatar(self, size):
        # lower() 转成小写; encode字符串转字节;(dencode 字节转字符串)
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)





# 帖子模型
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        # return '<Post {}'.format(self.body)
        return '<User {}, Email {}, Password_Hash {}, Posts {}'.format(self.username, self.email, self.password_hash,self.posts)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))




# 数据库实例化对象过程
    # 简要解释: db=>模型名
    # 1.flask db init
    # 2.flask db migrate -m "create user"
    # 3.flask db upgrade

# 添加新的字段，做好数据库的迁移
# 4.flask db migrate -m "add post"
# 5.flask db upgrade

    # 数据库：1：n 需要在 多 的那端创建外键作为 1 那端的主键

# python 命令行数据库插入数据步骤:

# 1.from app import db
# 2.from app.models import User,Post
# 3.u=User(username='zhangsan',email="888666@qq.com")
# 4.db.session.add(u)
# 5.db.session.commit()

# 为用户添加帖子
# p=Post(body='zhangsan ni hao',author=user2)

#
# u2=User(username='lisi',email="66666@qq.com")
# db.session.add(u2)
# db.session.commit()


# 删除上述创建的测试用户、帖子，以便数据库干净，并为下一章做准备：
#
# >>> users = User.query.all()
# >>> for u in users:
# ...     db.session.delete(u)
# ...
# >>> posts = Post.query.all()
# >>> for p in posts:
# ...     db.session.delete(p)
# ...
# >>> db.session.commit()