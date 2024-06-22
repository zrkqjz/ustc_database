# -*- coding: utf-8 -*-
import unittest

from library import app, db
from library.models import *  # 导入所有模型类
from library.commands import forge, initdb


class MyTestCase(unittest.TestCase):

    def setUp(self):
        # 更新配置
        # 设置连接数据库的URL
        app.config.update(
            TESTING=True,
            SQLALCHEMY_DATABASE_URI='sqlite:///:memory:'
        )
        # 创建数据库和表
        db.create_all()
        # 创建测试数据，一个用户，一个电影条目
        user = User(name='Test', username='test')
        user.set_password('123')
        book = Book(bname='Test Book', author='Test Author')
        # 使用 add_all() 方法一次添加多个模型类实例，传入列表
        db.session.add_all([user, book])
        db.session.commit()

        self.client = app.test_client()  # 创建测试客户端
        self.runner = app.test_cli_runner()  # 创建测试命令运行器

    def tearDown(self):
        db.session.remove()  # 清除数据库会话
        db.drop_all()  # 删除数据库表

    # 测试程序实例是否存在
    def test_app_exist(self):
        self.assertIsNotNone(app)

    # 测试程序是否处于测试模式
    def test_app_is_testing(self):
        self.assertTrue(app.config['TESTING'])

    def login(self):
        self.client.post('/login', data=dict(
            username='test',
            password='123'
        ), follow_redirects=True)

    # 测试主页
    def test_index_page(self):
        response = self.client.get('/')
        data = response.get_data(as_text=True)
        self.assertIn('Test Book', data)

    # 测试删除书籍
    def test_delete_book(self):
        self.login()
        response = self.client.post('/Book/delete/1', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Test Book', data)
    
    # 测试更新书籍
    def test_edit_book(self):
        self.login()
        response = self.client.post('/Book/edit/1', data=dict(
            bname='New Book',
            author='New Author'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('New Book', data)
        self.assertIn('New Author', data)

if __name__ == '__main__':
    with app.app_context():
        unittest.main()