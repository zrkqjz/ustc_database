 -- 2（1） 查询读者 Rose 借过的书（包括已还和未还）的图书号、书名和借期；
 Select 
	Book.BID,
    Book.bname,
    Borrow.borrow_Date
 From Book, Borrow, Reader
 where
	Book.BID = Borrow.book_ID
    AND Borrow.reader_ID = Reader.RID
    AND Reader.rname = 'Rose'
    ;
 -- 2（2） 查询从没有借过图书也从没有预约过图书的读者号和读者姓名；
 SELECT DISTINCT Reader.RID, Reader.rname
 FROM Reader, Borrow, Reserve
 WHERE Reader.RID NOT IN (
    SELECT Reader.RID
    FROM Reader, Borrow
    WHERE Reader.RID = Borrow.reader_ID
 )
    AND Reader.RID NOT IN (
        SELECT Reader.RID
        FROM Reader, Reserve
        WHERE Reader.RID = Reserve.reader_ID
    )
    ;

-- 2（3）查询被借阅次数最多的作者
-- A.使用借阅表 borrow 中的借书记录； 
SELECT b.author, COUNT(*) as total_borrow_times
FROM Book b
JOIN Borrow br ON b.BID = br.book_ID
GROUP BY b.author
ORDER BY total_borrow_times DESC
LIMIT 1;
-- B.使用图书表 book 中的 borrow_times 
SELECT author, SUM(borrow_times) as total_borrow_times
FROM Book
GROUP BY author
ORDER BY total_borrow_times DESC
LIMIT 1;

-- 2 （4）查询目前借阅未还的书名中包含“MySQL”的图书号和书名； 
SELECT b.BID AS book_ID, b.bname AS book_name
FROM Book b
JOIN Borrow br ON b.BID = br.book_ID
WHERE b.bname LIKE '%MySQL%' AND br.return_date IS NULL;

-- 2 （5） 查询借阅图书数目（多次借同一本书需重复计入）超过 3 本的读者姓名；
SELECT r.rname AS reader_name
FROM reader r
JOIN Borrow br ON r.RID = br.reader_id
GROUP BY r.RID
HAVING COUNT(*) > 3;

-- 2 （6） 查询没有借阅过任何一本 J.K. Rowling 所著的图书的读者号和姓名； 
SELECT DISTINCT Reader.RID AS reader_ID, Reader.rname AS reader_name
 FROM Reader
 WHERE NOT EXISTS (
    SELECT *
    FROM Borrow, Book
    WHERE
        Borrow.reader_ID = Reader.RID
        AND Borrow.book_ID = Book.BID
        AND Book.author = 'J.K. Rowling'
 );
 
 -- 2 （7） 查询 2024 年借阅图书数目排名前 3 名的读者号、姓名以及借阅图书数；
 SELECT r.RID AS reader_ID, r.rname AS reader_name, COUNT(br.book_ID) AS borrow_book_count
 FROM reader r
 JOIN borrow br ON br.reader_ID = r.RID
 GROUP BY r.RID
 ORDER BY borrow_book_count DESC
 LIMIT 3;
 
 -- 2 （8） 创建一个读者借书信息的视图，该视图包含读者号、姓名、所借图书号、
 -- 图书名和借期（对于没有借过图书的读者，是否包含在该视图中均可）；
 -- 并使用该视图查询2024年所有读者的读者号以及所借阅的不同图书数； 
 CREATE VIEW ReaderBorrowInfo AS
 SELECT 
	r.RID AS reader_ID,
    r.rname AS reader_name,
    br.book_ID AS book_ID,
    b.bname AS book_name,
    br.borrow_date AS borrow_data
FROM reader r
JOIN borrow br ON br.reader_ID = r.RID
JOIN book b ON b.BID = br.book_ID;

select 
	myview.reader_ID,
	COUNT(DISTINCT myview.book_ID) AS distinct_book_num
FROM ReaderBorrowInfo myview
WHERE YEAR(myview.borrow_data) = 2024
group by myview.reader_ID;