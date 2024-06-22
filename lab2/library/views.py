from flask import render_template, request, url_for, redirect, flash
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy import and_
from sqlalchemy.sql import text
import os

from library import app, db, login_manager, static_path
from library.models import *

@app.route('/myerror', methods=['GET', 'POST'])
def myerror(msg):
    return render_template('myerror.html', message=msg)

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if not current_user.is_authenticated:
            return redirect(url_for('index'))

        title = request.form['title']

        if not title or len(title) > 60:
            flash('Invalid input.')
            return redirect(url_for('index'))

        book = Book(bname=title)
        db.session.add(book)
        db.session.commit()
        flash('Item created.')
        return redirect(url_for('index'))

    books = Book.query.all()
    return render_template('index.html', user=current_user, books=books)

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if not current_user.is_admin:
        return myerror('Permission denied.')
    
    users = User.query.all()
    books = Book.query.all()
    borrows = db.session.query(
        User.id.label('user_id'), 
        User.name.label('name'),
        Book.bname.label('bname'),
        BorrowRecord.id.label('id'),
        BorrowRecord.book_id.label('bid'),
        BorrowRecord.borrow_date.label('borrow_date'),
        BorrowRecord.return_date.label('return_date'),
    ).\
        join(Book, BorrowRecord.book_id == Book.bid).\
        join(User, BorrowRecord.user_id == User.id).all()
    
    reserves = db.session.query(
        User.id.label('user_id'), 
        User.name.label('name'),
        Book.bname.label('bname'),
        Reserve.id.label('id'),
        Reserve.book_id.label('bid'),
        Reserve.reserve_date.label('reserve_date'),
        Reserve.expire_date.label('expire_date'),
    ).\
        join(Book, Reserve.book_id == Book.bid).\
        join(User, Reserve.user_id == User.id).all()
    
    rates = db.session.query(
        User.id.label('user_id'), 
        User.name.label('name'),
        Book.bname.label('bname'),
        Rate.id.label('id'),
        Rate.book_id.label('bid'),
        Rate.score.label('score'),
    ).\
        join(Book, Rate.book_id == Book.bid).\
        join(User, Rate.user_id == User.id).all()
    return render_template('admin.html', users=users, borrows=borrows, reserves=reserves, books=books, rates=rates)

@app.route('/Book/edit/<int:book_id>', methods=['GET', 'POST'])
@login_required
def edit_book(book_id):
    book = Book.query.get_or_404(book_id)

    if request.method == 'POST':
        bname = request.form.get('bname')
        author = request.form.get('author')
        description = request.form.get('description')
        total_num = request.form.get('total_num')
        borrow_num = request.form.get('borrow_num')
        reserve_num = request.form.get('reserve_num')
        rating = request.form.get('rating')
        image = request.files.get('image')
        if bname:
            book.bname = bname
        if author:
            book.author = author
        if description:
            book.description = description
        if total_num:
            book.total_num = total_num
        if borrow_num:
            book.borrow_num = borrow_num
        if reserve_num:
            book.reserve_num = reserve_num
        if rating:
            book.rating = rating
        if image:
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])  # 自动创建目录
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], str(book.bid) + '.' + image.filename.rsplit('.', 1)[1].lower()))
        db.session.commit()
        flash('Item updated.')
        return redirect(url_for('index'))

    return render_template('edit_book.html', book=book)

@app.route('/User/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        name = request.form.get('name')
        if username:
            user.username = username
        if password:
            user.set_password(password)
        if name:
            user.name = name
        db.session.commit()
        flash('Item updated.')
        return redirect(url_for('user_info'))

    return render_template('edit_user.html', user=user)

@app.route('/Borrow/edit/<int:borrow_id>', methods=['GET', 'POST'])
@login_required
def edit_borrow(borrow_id):
    borrow = BorrowRecord.query.filter_by(id=borrow_id).first()
    if request.method == 'POST':
        book_id = request.form.get('book_id')
        user_id = request.form.get('user_id')
        borrow_date = request.form.get('borrow_date')
        return_date = request.form.get('return_date')
        if book_id:
            borrow.book_id = book_id
        if user_id:
            borrow.user_id = user_id
        if borrow_date:
            borrow.borrow_date = borrow_date
        if return_date:
            borrow.return_date = return_date
        db.session.commit()
        flash('Item updated.')
        return redirect(url_for('admin'))

    return render_template('edit_borrow.html', borrow=borrow)

@app.route('/Reserve/edit/<int:reserve_id>', methods=['GET', 'POST'])
@login_required
def edit_reserve(reserve_id):
    reserve = Reserve.query.filter_by(id=reserve_id).first()
    if request.method == 'POST':
        book_id = request.form.get('book_id')
        user_id = request.form.get('user_id')
        reserve_date = request.form.get('reserve_date')
        expire_date = request.form.get('expire_date')
        if book_id:
            reserve.book_id = book_id
        if user_id:
            reserve.user_id = user_id
        if reserve_date:
            reserve.reserve_date = reserve_date
        if expire_date:
            reserve.expire_date = expire_date
        db.session.commit()
        flash('Item updated.')
        return redirect(url_for('admin'))

    return render_template('edit_reserve.html', reserve=reserve)

@app.route('/Rate/edit/<int:rate_id>', methods=['GET', 'POST'])
@login_required
def edit_rate(rate_id):
    rate = Rate.query.filter_by(id=rate_id).first()
    if request.method == 'POST':
        book_id = request.form.get('book_id')
        user_id = request.form.get('user_id')
        score = request.form.get('score')
        if book_id:
            rate.book_id = book_id
        if user_id:
            rate.user_id = user_id
        if score:
            rate.score = score
        db.session.commit()
        flash('Item updated.')
        return redirect(url_for('index'))

    return render_template('edit_rate.html', rate=rate)

@app.route('/Book/delete/<int:book_id>', methods=['POST'])
@login_required
def delete_book(book_id):
    book = Book.query.filter_by(bid=book_id).first()
    if book:
        db.session.delete(book)
        db.session.commit()
    flash('Book deleted.')
    return redirect(url_for('index'))

@app.route('/User/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user:
        db.session.delete(user)
        db.session.commit()
    flash('User deleted.')
    return redirect(url_for('admin'))

@app.route('/Borrow/delete/<int:borrow_id>', methods=['GET', 'POST'])
@login_required
def delete_borrow(borrow_id):
    borrow = BorrowRecord.query.filter_by(id=borrow_id).first()
    if borrow:
        db.session.delete(borrow)
        db.session.commit()
    flash('Borrow record deleted.')
    return redirect(url_for('admin'))

@app.route('/Reserve/delete/<int:reserve_id>', methods=['GET', 'POST'])
@login_required
def delete_reserve(reserve_id):
    reserve = Reserve.query.filter_by(id=reserve_id).first()
    if reserve:
        db.session.delete(reserve)
        db.session.commit()
    flash('Reserve record deleted.')
    return redirect(url_for('admin'))

@app.route('/Rate/delete/<int:rate_id>', methods=['GET', 'POST'])
@login_required
def delete_rate(rate_id):
    rate = Rate.query.filter_by(id=rate_id).first()
    if rate:
        db.session.delete(rate)
        db.session.commit()
    flash('Rate record deleted.')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']

        if not username or not password or not name:
            flash('Invalid input.')
            return redirect(url_for('register'))

        user = User(username=username, name=name)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Register success.')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/addbook', methods=['GET', 'POST'])
def addbook():
    if request.method == 'POST':
        bname = request.form.get('bname')
        author = request.form.get('author')
        description = request.form.get('description')
        total_num = request.form.get('total_num')
        borrow_num = request.form.get('borrow_num')
        reserve_num = request.form.get('reserve_num')
        rating = request.form.get('rating')
        image = request.files.get('image')
        book = Book()
        if bname:
            book.bname = bname
        if author:
            book.author = author
        if description:
            book.description = description
        if total_num:
            book.total_num = total_num
        if borrow_num:
            book.borrow_num = borrow_num
        if reserve_num:
            book.reserve_num = reserve_num
        if rating:
            book.rating = rating
        db.session.add(book)
        db.session.commit()
        if image:
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])  # 自动创建目录
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], str(book.bid) + '.' + image.filename.rsplit('.', 1)[1].lower()))
        db.session.commit()
        flash('Add book success.')
        return redirect(url_for('admin'))
    return render_template('addbook.html')

@app.route('/rate/<int:book_id>', methods=['GET', 'POST'])
def rate(book_id):
    if request.method == 'POST':
        user_id = current_user.id
        score = request.form.get('score')
        rate = Rate()
        db.session.add(rate)
        if book_id:
            rate.book_id = book_id
        if user_id:
            rate.user_id = user_id
        if score:
            rate.score = score
        db.session.commit()
        flash('Rate success.')
        return redirect(url_for('index'))
    return render_template('rate.html', book_id=book_id)

@app.route('/rate_sql/<int:book_id>', methods=['GET', 'POST'])
def rate_sql(book_id):
    if request.method == 'POST':
        user_id = current_user.id
        score = request.form.get('score')
        rate = Rate()
        db.session.add(rate)
        if book_id and user_id and score:
            db.session.execute(text(f"CALL ADD_RATE('{book_id}', '{user_id}', '{score}')").execution_options(autocommit=True))
        db.session.commit()
        flash('Rate success.')
        return redirect(url_for('index'))
    return render_template('rate.html', book_id=book_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Invalid input.')
            return redirect(url_for('login'))

        user = User.query.filter_by(username=username).first()

        if username == user.username and user.validate_password(password):
            login_user(user)
            flash('Login success.')
            return redirect(url_for('index'))

        flash('Invalid username or password.')
        return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Goodbye.')
    return redirect(url_for('index'))

@app.route('/user_info')
@login_required
def user_info():
    if current_user.is_authenticated:
        user_id = current_user.get_id()
        user = User.query.get(user_id)
        borrows = db.session.query(
                User.id.label('user_id'), 
                User.username.label('username'),
                Book.bname.label('bname'),
                BorrowRecord.book_id.label('bid'),
                BorrowRecord.borrow_date.label('borrow_date'),
                BorrowRecord.return_date.label('return_date'),
            ).\
                join(Book, BorrowRecord.book_id == Book.bid).\
                join(User, BorrowRecord.user_id == User.id).\
                filter(BorrowRecord.user_id == user_id).all()
        reserves = db.session.query(
                User.id.label('user_id'), 
                User.username.label('username'),
                Book.bname.label('bname'),
                Reserve.book_id.label('bid'),
                Reserve.reserve_date.label('reserve_date'),
                Reserve.expire_date.label('expire_date'),
            ).\
                join(Book, Reserve.book_id == Book.bid).\
                join(User, Reserve.user_id == User.id).\
                filter(Reserve.user_id == user_id).all()
        rates = db.session.query(
                User.id.label('user_id'), 
                User.username.label('username'),
                Book.bname.label('bname'),
                Rate.id.label('id'),
                Rate.book_id.label('bid'),
                Rate.score.label('score'),
            ).\
                join(Book, Rate.book_id == Book.bid).\
                join(User, Rate.user_id == User.id).\
                filter(Rate.user_id == user_id).all()
        return render_template('user_info.html', user=user, borrows=borrows, reserves=reserves, rates=rates)
    
@app.route('/search', methods=['POST', 'GET'])
def search():
    author = request.form.get('author')
    title = request.form.get('title')
    # 动态构建查询条件
    query_conditions = []
    if author:
        query_conditions.append(Book.author.like(f"%{author}%"))
    if title:
        query_conditions.append(Book.bname.like(f"%{title}%"))
    books = Book.query.filter(and_(*query_conditions)).all()
    return render_template('search.html', books=books)

@app.route('/borrow/<int:book_id>', methods=['POST', 'GET'])
@login_required
def borrow(book_id):
    book = Book.query.filter_by(bid=book_id).first()
    if book:
        if book.borrow_num + book.reserve_num >= book.total_num:
            return myerror('The book is not available.')
        borrow = BorrowRecord.query.filter_by(user_id=current_user.get_id(), book_id=book_id).first()
        if borrow:
            return myerror('You have borrowed this book.')
        borrow = BorrowRecord(user_id=current_user.get_id(), book_id=book_id)
        db.session.add(borrow)
        reserve = Reserve.query.filter_by(user_id=current_user.get_id(), book_id=book_id).first()
        if reserve:
            db.session.delete(reserve)
        db.session.commit()
    flash('Borrow success.')
    return redirect(url_for('user_info'))

@app.route('/return/<int:book_id>', methods=['POST', 'GET'])
@login_required
def return_book(book_id):
    book = Book.query.filter_by(bid=book_id).first()
    if book:
        borrow = BorrowRecord.query.filter_by(user_id=current_user.get_id(), book_id=book_id).first()
        if borrow:
            db.session.delete(borrow)
            db.session.commit()
    flash('Return success.')
    return redirect(url_for('user_info'))

@app.route('/reserve/<int:book_id>', methods=['POST', 'GET'])
@login_required
def reserve(book_id):
    book = Book.query.filter_by(bid=book_id).first()
    if book:
        if book.borrow_num + book.reserve_num >= book.total_num:
            return myerror('The book is not available.')
        reserve = Reserve.query.filter_by(user_id=current_user.get_id(), book_id=book_id).first()
        if reserve:
            return myerror('You have reserved this book.')
        reserve = Reserve(user_id=current_user.get_id(), book_id=book_id)
        db.session.add(reserve)
        db.session.commit()
    flash('Reserve success.')
    return redirect(url_for('user_info'))

@app.route('/cancel_reserve/<int:book_id>', methods=['POST', 'GET'])
@login_required
def cancel_reserve(book_id):
    book = Book.query.filter_by(bid=book_id).first()
    if book:
        reserve = Reserve.query.filter_by(user_id=current_user.get_id(), book_id=book_id).first()
        if reserve:
            db.session.delete(reserve)
            db.session.commit()
    flash('Cancel reserve success.')
    return redirect(url_for('user_info'))

@app.route('/recommend', methods=['GET', 'POST'])
def recommend():
    db.session.execute(text(f"CALL Most_Popular_Book(@outname, @outrating)").execution_options(autocommit=True))
    out = db.session.execute(text("SELECT @outname;")).fetchall()
    out = str(out)
    return out;
    books = Book.query.filter_by(bname=out).all()
    return render_template('index.html', books=books)