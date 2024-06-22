use flask_app;
drop table IF EXISTS Reserve;
drop table IF EXISTS Borrow;
drop table IF EXISTS Book;
drop table IF EXISTS Reader;

CREATE TABLE Book(
    -- 主键是 BID
    BID CHAR(8) NOT NULL PRIMARY KEY,
    -- 书名 bname 不能为空；
    bname VARCHAR(100) NOT NULL,
    author VARCHAR(50),
    price FLOAT,
    -- 状态 bstatus 为 0 表示可借，1 表示书被借出，2 表示已被预约，默认值为 0；
    bstatus INT DEFAULT 0,
    -- borrow_Times 表示图书有史以来的总借阅次数, reserve_Times 表示图书当前的预约人数，默认值都为 0； 
    borrow_Times INT DEFAULT 0,
    reserve_Times INT DEFAULT 0,
    CONSTRAINT bstatus CHECK(bstatus >= 0 AND bstatus <= 2)
    );

CREATE TABLE Reader(  
    -- 主键是读者号 RID
    RID CHAR(8) NOT NULL PRIMARY KEY,
    rname VARCHAR(20),
    age INT,
    address VARCHAR(100)
 );

 CREATE TABLE Borrow(  
    book_ID CHAR(8),
    reader_ID CHAR(8),
    borrow_Date DATE,
    -- 还期 return_Date 为 NULL 表示该书未还； 
    return_date DATE,
    -- 主键
    CONSTRAINT PRIMARY KEY (book_ID, reader_ID, borrow_Date),
    -- 外键
    --  图书号book_ID为外键, 引用图书表的图书号；
    CONSTRAINT FK_BKID FOREIGN KEY (book_ID) REFERENCES Book(BID),
    -- 读者号reader_ID为外键, 引用读者表的读者号；
    CONSTRAINT FK_RDID FOREIGN KEY (reader_ID) REFERENCES Reader(RID)
 );

 CREATE TABLE Reserve(
    book_ID CHAR(8),
    reader_ID CHAR(8),
    reserve_Date DATE DEFAULT (CURRENT_DATE),
    take_Date DATE,
    -- 主键
    CONSTRAINT PRIMARY KEY (
        book_ID,
        reader_ID,
        reserve_Date
    ),
    -- 外键
    CONSTRAINT FK_BKID2 FOREIGN KEY (book_ID) REFERENCES Book(BID),
    CONSTRAINT FK_RDID2 FOREIGN KEY (reader_ID) REFERENCES Reader(RID),
    -- 检查：预约取书日期不能晚于预约日期
    CONSTRAINT CHK_TKDATE CHECK (take_Date >= reserve_Date)
 );
 
 Select * from book;
 Select * from Reader;
 

