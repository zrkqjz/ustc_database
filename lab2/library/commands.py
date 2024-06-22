# -*- coding: utf-8 -*-
import click
import json
import random
from faker import Faker
from sqlalchemy import text

from library import app, db
from library.models import *
from datetime import datetime, timedelta

@app.cli.command()
@click.option('--drop', is_flag=True, help='Create after drop.')
def initdb(drop):
    """Initialize the database."""
    db.drop_all()
    db.create_all()
    click.echo('Initialized database.')

@app.cli.command()
@click.option('--username', prompt=True, help='The username used to login.')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The password used to login.')
def admin(username, password):
    """Create user."""
    db.create_all()

    user = User.query.first()
    if user is not None:
        click.echo('Updating user...')
        user.username = username
        user.set_password(password)
    else:
        click.echo('Creating user...')
        user = User(username=username, name='Admin')
        user.set_password(password)
        db.session.add(user)

    db.session.commit()
    click.echo('Done.')

@app.cli.command()
def exct():
    click.echo('Executing...')



@app.cli.command()
def initbook():
    """Initialize the book database."""
    # 抽取之前的爬虫信息
    def get_book_info():
        path = "bookData.json"
        # 读取json文件
        with open(path, 'r', encoding='utf-8') as f:
            book_info = json.load(f)
        return book_info

    def parse_info(mystr, prefix, suffix):
        'example : parse_info(mystr, "作者", "出版社")'
        if mystr is None:
            return "None"
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

    db.create_all()
    book_info = get_book_info()
    for book in book_info[0:20]:
        bname = book['title']
        if bname == []:
            continue
        author = parse_info(book['info'], "作者", "出版社")
        price = float(random.uniform(50, 100))
        bstatus = 0
        borrow_Times = 0
        reserve_Times = 0
        rating = float(book['rating'][0].strip())
        book = Book(bname=bname, author=author, price=price, bstatus=bstatus, borrow_Times=borrow_Times, reserve_Times=reserve_Times, rating=rating)
        db.session.add(book)
    db.session.commit()
    click.echo('Done.')

@app.cli.command()
def initborrow():
    # 假设的用户和书籍ID
    user_ids = [1, 2, 3]
    book_ids = [10, 11, 12]
    
    # 创建测试数据
    test_cases = [
        {'user_id': user_ids[0], 'book_id': book_ids[0], 'borrow_date': datetime.now(), 'return_date': None},
        {'user_id': user_ids[0], 'book_id': book_ids[1], 'borrow_date': datetime.now() - timedelta(days=15), 'return_date': datetime.now() - timedelta(days=1)},
        {'user_id': user_ids[0], 'book_id': book_ids[2], 'borrow_date': datetime.now() - timedelta(days=30), 'return_date': None},
    ]

    # 插入数据
    for case in test_cases:
        borrow_record = BorrowRecord(**case)
        db.session.add(borrow_record)
    db.session.commit()
    click.echo('Done.')

@app.cli.command()
def initreserve():
    # 假设的用户和书籍ID
    user_ids = [1, 2, 3]
    book_ids = [10, 11, 12]
    
    # 创建测试数据
    test_cases = [
        {'user_id': user_ids[0], 'book_id': book_ids[0], 'reserve_date': datetime.now(), 'expire_date': datetime.now() + timedelta(days=7)},
        {'user_id': user_ids[0], 'book_id': book_ids[1], 'reserve_date': datetime.now() - timedelta(days=15), 'expire_date': datetime.now() - timedelta(days=8)},
        {'user_id': user_ids[0], 'book_id': book_ids[2], 'reserve_date': datetime.now() - timedelta(days=30), 'expire_date': datetime.now() - timedelta(days=23)},
    ]

    # 插入数据
    for case in test_cases:
        reserve_record = Reserve(**case)
        db.session.add(reserve_record)
    db.session.commit()
    click.echo('Done.')

@app.cli.command()
def forge():
    fake = Faker()

    '''添加管理员账户和普通用户账户'''
    user = User(username='admin', name='Admin', is_admin=True)
    user.set_password('admin')
    db.session.add(user)
    db.session.commit()

    user = User(username='user', name='李华')
    user.set_password('user')
    db.session.add(user)
    db.session.commit()

    """Initialize the book database."""
    # 抽取之前的爬虫信息
    def get_book_info():
        path = "bookData.json"
        # 读取json文件
        with open(path, 'r', encoding='utf-8') as f:
            book_info = json.load(f)
        return book_info

    def parse_info(mystr, prefix, suffix):
        'example : parse_info(mystr, "作者", "出版社")'
        if mystr is None:
            return "None"
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

    book_info = get_book_info()
    for book in book_info[0:20]:
        bname = book['title']
        if bname == []:
            continue
        author = parse_info(book['info'], "作者", "出版社")
        description = book['description'][0:60]+'...'
        total_num = 10
        borrow_num = 0
        reserve_num = 0
        rating = float(book['rating'][0].strip())
        book = Book(bname=bname, author=author, description=description, total_num=total_num, borrow_num=borrow_num, reserve_num=reserve_num, rating=rating, rating_num=10)
        db.session.add(book)
    db.session.commit()
    click.echo('Done.')

    '''初始化借阅记录和预约记录'''
    # 假设的用户和书籍ID
    user_ids = [1, 2, 3]
    book_ids = [8, 9, 10, 11, 12]
    start_date = datetime(2024, 5, 1)
    end_date = datetime(2024, 5, 31)
    borrow_date = [fake.date_time_between(start_date=start_date, end_date=end_date) for i in range(10)]
    # 创建测试数据
    test_cases = [
        {'user_id': user_ids[0], 'book_id': book_ids[0], 'borrow_date': borrow_date[0], 'return_date': borrow_date[0] + timedelta(days=30)},
        {'user_id': user_ids[0], 'book_id': book_ids[1], 'borrow_date': borrow_date[1], 'return_date': borrow_date[1] + timedelta(days=30)},
        {'user_id': user_ids[0], 'book_id': book_ids[2], 'borrow_date': borrow_date[2], 'return_date': borrow_date[2] + timedelta(days=30)},
        {'user_id': user_ids[1], 'book_id': book_ids[3], 'borrow_date': borrow_date[3], 'return_date': borrow_date[3] + timedelta(days=30)},
        {'user_id': user_ids[1], 'book_id': book_ids[4], 'borrow_date': borrow_date[4], 'return_date': borrow_date[4] + timedelta(days=30)},
    ]

    # 插入数据
    for case in test_cases:
        borrow_record = BorrowRecord(**case)
        db.session.add(borrow_record)
        book = db.session.query(Book).filter(Book.bid == case['book_id']).first()
    db.session.commit()
    click.echo('Done.')

    # 假设的用户和书籍ID
    user_ids = [1, 2, 3]
    book_ids = [3, 4, 5, 6, 7]
    start_date = datetime(2024, 5, 25)
    end_date = datetime(2024, 6, 10)
    re_date = [fake.date_time_between(start_date=start_date, end_date=end_date) for i in range(10)]
    # 创建测试数据
    test_cases = [
        {'user_id': user_ids[0], 'book_id': book_ids[0], 'reserve_date': re_date[0], 'expire_date': re_date[0] + timedelta(days=7)},
        {'user_id': user_ids[0], 'book_id': book_ids[1], 'reserve_date': re_date[1], 'expire_date': re_date[1] + timedelta(days=7)},
        {'user_id': user_ids[0], 'book_id': book_ids[2], 'reserve_date': re_date[2], 'expire_date': re_date[2] + timedelta(days=7)},
        {'user_id': user_ids[1], 'book_id': book_ids[3], 'reserve_date': re_date[3], 'expire_date': re_date[3] + timedelta(days=7)},
        {'user_id': user_ids[1], 'book_id': book_ids[4], 'reserve_date': re_date[4], 'expire_date': re_date[4] + timedelta(days=7)},
    ]

    # 插入数据
    for case in test_cases:
        reserve_record = Reserve(**case)
        db.session.add(reserve_record)
        book = db.session.query(Book).filter(Book.bid == case['book_id']).first()
    db.session.commit()
    click.echo('Done.')