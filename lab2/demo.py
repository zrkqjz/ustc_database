from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.sql import text
import pymysql
import os

app = Flask(__name__)

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

@app.route('/sql')
def execute_sql():
    # 执行存储过程
    p1 = 'R006'
    p2 = 'R999'
    db.session.execute(text(f"CALL updateReaderID('{p1}', '{p2}', @outputMessage)").execution_options(autocommit=True))
    out = db.session.execute(text("SELECT @outputMessage")).fetchall()
    # 创建参数化查询的查询字符串
    ret = db.session.execute(text("SELECT * FROM reader")).fetchall()
    # 处理执行结果
    rows = []
    rows.append(out)
    for row in ret:
        rows.append(row)

    return str(rows)

# 假设你有一个 allowed_file 函数来检查文件类型
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    file = request.files.get('image')
    if request.method == 'POST':
        if file and allowed_file(file.filename):
            file.save(os.path.join(file.filename))
            return 'file uploaded successfully'
        else:
            return 'no file uploaded'
    
    return '''
    <form method="post" action="/" enctype="multipart/form-data">
        <input type="file" name="image" accept="image/*">
        <input type="submit" value="Submit">
    </form>
    '''

if __name__ == '__main__':
    app.run(debug=True)


