DELIMITER //
DROP PROCEDURE IF EXISTS reserveBook;
CREATE procedure reserveBook(
    IN p_reader_ID CHAR(8),
    IN p_book_ID CHAR(8),
    IN p_take_date DATE
)
BEGIN
    DECLARE errMsg VARCHAR(255);
    DECLARE exitHandler CONDITION FOR SQLSTATE '45000';

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

    IF p_take_date <= current_date() THEN
        SET errMsg = '预约日期不能早于当前日期';
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = errMsg;
    END IF;

    INSERT INTO Reserve (reader_ID, book_ID, reserve_Date, take_Date)
    value (p_reader_ID, p_book_ID, current_date(), p_take_date);

    COMMIT;

    SELECT '预约成功' AS result;
END; //
DELIMITER ;

DELIMITER //
DROP PROCEDURE IF EXISTS CancelReservation;
CREATE PROCEDURE CancelReservation(
    IN p_reader_ID CHAR(8), 
    IN p_book_ID CHAR(8)
)
BEGIN
    DECLARE errMsg VARCHAR(255);
    DECLARE exitHandler CONDITION FOR SQLSTATE '45000';
    -- 声明变量
    DECLARE isLastReservation INT DEFAULT 0;
    DECLARE bookStatus INT;

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

    IF NOT EXISTS(SELECT 1 FROM Reserve WHERE book_ID = p_book_ID AND reader_ID = p_reader_ID) THEN
        SET errMsg = '该读者没有预约该图书';
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = errMsg;
    END IF;

    -- 检查是否是最后一条预约记录
    SELECT COUNT(*) INTO isLastReservation
    FROM Reserve
    WHERE book_ID = p_book_ID AND reader_ID <> p_reader_ID;

    -- 获取图书当前状态
    SELECT bstatus INTO bookStatus
    FROM Book
    WHERE BID = p_book_ID;

    -- 如果是最后一条预约记录且图书状态为2（已被预约）
    IF isLastReservation = 0 AND bookStatus = 2 THEN
        -- 更新图书状态为可借
        UPDATE Book
        SET bstatus = 0
        WHERE BID = p_book_ID;
    END IF;

	-- 由 Trigger 减少图书的预约次数

    -- 删除该读者的预约记录（逻辑删除，实际项目中可能需要一个标志位来标记删除）
    DELETE FROM Reserve
    WHERE book_ID = p_book_ID AND reader_ID = p_reader_ID;

    COMMIT;
    
    -- 可选：返回操作结果或状态信息
    SELECT CONCAT(p_reader_ID, '对图书 ', p_book_ID, '的预约取消') AS message;
END; //
DELIMITER ;

DELIMITER //
CREATE TRIGGER Reserve_Insert_Trigger
AFTER INSERT ON Reserve
FOR EACH ROW
BEGIN
    UPDATE Book
    SET bstatus = 2, reserve_Times = reserve_Times + 1
    WHERE BID = NEW.book_ID;
END; //
DELIMITER ;

DELIMITER //
CREATE TRIGGER Reserve_Delete_Trigger
AFTER DELETE ON Reserve
FOR EACH ROW
BEGIN
    UPDATE Book
    SET reserve_Times = reserve_Times - 1
    WHERE BID = OLD.book_ID;
END; //
DELIMITER ;

DELIMITER //
CREATE TRIGGER Borrow_Insert_Trigger
AFTER INSERT ON Borrow
FOR EACH ROW
BEGIN
    UPDATE Book
    SET reserve_Times = reserve_Times - 1
    WHERE BID = NEW.book_ID AND bstatus = 2;
END; //
DELIMITER ;

call reserveBook('R001', 'B012', '2024-12-12');
SELECT * FROM book WHERE BID = 'B012';
SELECT * FROM reserve WHERE reader_ID = 'R001' AND book_ID = 'B012';

call cancelReservation('R001', 'B012');
SELECT * FROM book WHERE BID = 'B012';
SELECT * FROM reserve WHERE reader_ID = 'R001' AND book_ID = 'B012';

