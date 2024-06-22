# -*- coding: utf-8 -*-
import json
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Text
from datetime import datetime, timedelta

from library import db

# 抽取之前的爬虫信息
def get_book_info():
    path = "bookData.json"
    # 读取json文件
    with open(path, 'r', encoding='utf-8') as f:
        book_info = json.load(f)
    return book_info

def parse_info(mystr, prefix, suffix):
    'example : parse_info(mystr, "作者", "出版社")'
    mystr = mystr.replace("\n", "")
    start_index = mystr.find(prefix)
    if start_index != -1:
        # 找到终止符的位置
        end_index = mystr.find(suffix, start_index)
        if end_index != -1:
            # 提取作者名或其他
            result = mystr[start_index + len(prefix):end_index]
            # 删除出现的所有空格
            result = result.replace(" ", "")
            result = result.replace(":", "")
            return result

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    username = db.Column(db.String(20))
    password_hash = db.Column(Text)
    is_admin = db.Column(db.Boolean, default=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)

class Book(db.Model):
    # 主键是 BID
    bid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 书名 bname 不能为空；
    bname = db.Column(db.String(100), nullable=False, default='未知')
    author = db.Column(db.String(50), default='未知')
    description = db.Column(db.Text)
    # 馆藏数量，借出数量和预约数量，默认值为 0；
    total_num = db.Column(db.Integer, default=0)
    borrow_num = db.Column(db.Integer, default=0)
    reserve_num = db.Column(db.Integer, default=0)
    # rating 表示图书的评分，默认为0.0
    rating = db.Column(db.Float, default=0.0)
    # rating_num 表示评分的人数，默认为10
    rating_num = db.Column(db.Integer, default=0)

    # 定义 CHECK 约束的替代方法，在 SQLAlchemy 中通常使用自定义的验证函数或属性观察者
    @property
    def status(self):
        return self.bstatus

    @status.setter
    def status(self, value):
        if not (0 <= value <= 2):
            raise ValueError("bstatus must be between 0 and 2")
        self.bstatus = value

class Rate(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 评分的用户 UID
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE', onupdate='CASCADE'))
    # 评分的书籍 BID
    book_id = db.Column(db.Integer, db.ForeignKey('book.bid', ondelete='CASCADE', onupdate='CASCADE'))
    # 评分的数值，范围为 0-10
    score = db.Column(db.Float, nullable=False)

    user = db.relationship('User', backref=db.backref('ratings', lazy='dynamic'))
    book = db.relationship('Book', backref=db.backref('ratings', lazy='dynamic'))

    def __repr__(self):
        return f'<Rating {self.user} rated {self.book} as {self.score}>'
    
# 声明借书表
class BorrowRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.bid', onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    borrow_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    return_date = db.Column(db.DateTime, default=datetime.now() + timedelta(days=7))

"""     # 定义关系
    user = db.relationship("User", backref=db.backref("borrow_records"))
    book = db.relationship("Book", backref=db.backref("borrow_records")) """

class Reserve(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.bid', onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    reserve_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    expire_date = db.Column(db.DateTime, nullable=False, default=datetime.now() + timedelta(days=7))
    status = db.Column(db.String(20), default='pending')

class overdue_borrow(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('borrow_record.id', onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)

class overdue_reserve(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('reserve.id', onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    