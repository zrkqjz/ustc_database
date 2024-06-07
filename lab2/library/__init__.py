from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import pymysql

app = Flask(__name__, template_folder='templates', static_folder='..\\Anchor-Bootstrap-UI-Kit-master\\assets')

pymysql.install_as_MySQLdb()
class Config(object):
    """配置参数"""
    # 设置连接数据库的URL
    user = 'root'
    password = 'root'
    database = 'flask_app'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://%s:%s@127.0.0.1:3306/%s' % (user,password,database)
    app.config['SECRET_KEY'] = 'super-secret-key'
    app.config['SECURITY_PASSWORD_SALT'] = 'salt'
    # 设置sqlalchemy自动更跟踪数据库
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # 查询时会显示原始SQL语句
    app.config['SQLALCHEMY_ECHO'] = True

    # 禁止自动提交数据处理
    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = False

# 读取配置
app.config.from_object(Config)

# 创建数据库sqlalchemy工具对象
db = SQLAlchemy(app)

login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    from library.models import User
    user = User.query.get(int(user_id))
    return user

login_manager.login_view = 'login'

@app.context_processor
def inject_user():
    from library.models import User
    user = User.query.first()
    return dict(user=user)

from library import views, errors, commands

if __name__ == '__main__':
    app.run(debug=True)