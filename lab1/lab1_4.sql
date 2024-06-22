--  设计一个存储过程 borrowBook, 当读者借书时调用该存储过程完成借书处理。
DELIMITER //
DROP PROCEDURE IF EXISTS borrowBook;
create procedure borrowBook
(
    IN p_reader_id char(8),
    IN p_book_id char(8),
    IN p_borrow_Date DATE
)
BEGIN
    DECLARE errMsg VARCHAR(255);
    DECLARE exitHandler CONDITION FOR SQLSTATE '45000';
    
	DECLARE existingBorrows INT DEFAULT 0;
    DECLARE duplicateBorrowToday INT DEFAULT 0;
    DECLARE hasReservation INT DEFAULT 0;
    DECLARE isReservedByBorrower INT DEFAULT 0;

    DECLARE EXIT HANDLER FOR NOT FOUND
    BEGIN
        SET errMsg = '图书或读者不存在';
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = errMsg;
    END;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        GET DIAGNOSTICS CONDITION 1 errMsg = MESSAGE_TEXT;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = errMsg;
    END;

    START TRANSACTION;

    -- 检查读者是否存在
    IF NOT EXISTS(SELECT 1 FROM Reader WHERE RID = p_reader_ID) THEN
        SET errMsg = CONCAT('读者不存在: ', p_reader_ID);
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = errMsg;
    END IF;
    
    -- 检查读者是否在同一天重复借阅同一本读书
    SELECT COUNT(*) INTO duplicateBorrowToday FROM Borrow WHERE Reader_ID = p_reader_ID AND Book_ID = p_book_ID AND Borrow_Date = p_borrow_Date;
    IF duplicateBorrowToday > 0 THEN
        SET errMsg = CONCAT('读者在同一天重复借阅同一本书');
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = errMsg;
    END IF;

    -- 检查读者是否借阅了超过3本书
    SELECT COUNT(*) FROM Borrow WHERE Reader_ID = p_reader_ID AND Return_Date IS NULL INTO existingBorrows;
    IF existingBorrows >= 3 THEN
        SET errMsg = CONCAT('读者借阅书籍数量超过3本: ', p_reader_ID);
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = errMsg;
    END IF;

    -- 检查读者是否预约了该书
    SELECT COUNT(*) INTO hasReservation FROM Reserve WHERE book_ID = p_book_ID AND take_date >= current_date();
    IF hasReservation > 0 THEN
        SELECT COUNT(*) INTO isReservedByBorrower FROM Reserve WHERE book_ID = p_book_ID AND reader_ID = p_reader_ID AND take_date >= current_date();
        IF isReservedByBorrower = 0 THEN
            SET errMsg = CONCAT('图书已被他人预约:', p_book_ID);
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = errMsg;
        END IF;
    END IF;
    
    -- 删除预约记录
	DELETE FROM Reserve WHERE book_ID = p_book_ID AND reader_ID = p_reader_ID AND take_date >= current_date();
    UPDATE Book SET bstatus = 0 WHERE BID = p_book_ID;
    
    IF NOT EXISTS(SELECT 1 FROM Book WHERE BID = p_book_ID AND bstatus = 0) THEN
        SET errMsg = CONCAT('图书不可借，已被借出/预约: ', p_book_ID, isReservedByBorrower);
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = errMsg;
    END IF;

    -- 增加图书的借阅次数
    UPDATE Book SET borrow_Times = borrow_Times + 1 WHERE BID = p_book_ID;

    -- 插入借阅记录
    INSERT INTO Borrow (book_ID, reader_ID, borrow_Date) VALUES (p_book_ID, p_reader_ID, p_borrow_Date);
    
    -- 更新图书状态为已借出
    UPDATE Book SET bstatus = 1 WHERE BID = p_book_ID;

    COMMIT;
    SELECT '借书成功' AS messege;
END; 
// DELIMITER ;

call borrowBook('R001', 'B008', '2024-05-10');
SELECT * FROM borrow;

call borrowBook('R001', 'B001', '2024-05-10');
SELECT * FROM borrow;
SELECT * FROM Book WHERE BID = 'B001';
SELECT * FROM Reserve WHERE reader_ID = 'R001';

call borrowBook('R001', 'B001', '2024-05-10');

call borrowBook('R005', 'B008', '2024-05-10');