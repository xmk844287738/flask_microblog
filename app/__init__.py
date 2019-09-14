from flask import Flask
from flask_mail import Mail
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from config import Config
# from app import routes,models,errors
from flask_bootstrap import Bootstrap



app = Flask(__name__)
app.config.from_object(Config)


# 数据库模型
db =SQLAlchemy(app)     #db 数据库对象
migrate  = Migrate(app,db)  #数据库迁移对象

# 登录验证
login = LoginManager(app)
login.login_view = 'login'

# 创建一个Mail类
mail = Mail(app)

# 引入bootstrap 样式
bootstrap = Bootstrap(app)

# 引入处理时间模块
moment = Moment(app)


# 防止循环导入
# 从app包导入 routes,models
from app import routes,models
