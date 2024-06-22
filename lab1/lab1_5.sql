DELIMITER //
DROP PROCEDURE IF EXISTS returnBook;
CREATE PROCEDURE returnBook(
    IN p_reader_ID CHAR(8),
    IN p_book_ID CHAR(8),
    IN p_return_Date DATE
)
BEGIN
    DECLARE errMsg VARCHAR(255);
    DECLARE exitHandler CONDITION FOR SQLSTATE '45000';

    DECLARE hasReservation INT DEFAULT 0;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        GET DIAGNOSTICS CONDITION 1 errMsg = MESSAGE_TEXT;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = errMsg;
    END;


    
    -- 开始事务以确保操作的原子性
    START TRANSACTION;

    IF NOT EXISTS(SELECT 1 FROM borrow WHERE reader_ID = p_reader_ID AND book_ID = p_book_ID AND return_date IS NULL) THEN
        SET errMsg = '读者未借阅此书或已还';
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = errMsg;
    END IF;

    -- 更新Borrow表，添加还书日期
    UPDATE Borrow 
    SET return_date = p_return_Date
    WHERE reader_ID = p_reader_ID AND book_ID = p_book_ID AND return_date IS NULL;

    -- 检查是否有其他读者预约此书
    SELECT COUNT(*) INTO hasReservation 
    FROM Reserve 
    WHERE book_ID = p_book_ID AND take_Date >= p_return_Date;

    -- 根据是否有预约更新Book表的bstatus
    IF hasReservation > 0 THEN
        UPDATE Book 
        SET bstatus = 2 -- 有其他预约
        WHERE BID = p_book_ID;
    ELSE
        UPDATE Book 
        SET bstatus = 0 -- 没有其他预约
        WHERE BID = p_book_ID;
    END IF;

    -- 提交事务
    COMMIT;

    SELECT '还书成功' AS messege;
END; //
DELIMITER ;

call returnBook('R001', 'B008', '2024-05-10');

call returnBook('R001', 'B001', '2024-05-10');
SELECT * FROM borrow WHERE book_ID = 'B001';
SELECT * FROM book WHERE BID = 'B001';