USE flask_app;

DELIMITER //
-- DROP TRIGGER IF EXISTS Reserve_Insert_Trigger;
CREATE TRIGGER Reserve_Insert_Trigger
AFTER INSERT ON Reserve
FOR EACH ROW
BEGIN
    UPDATE Book
    SET reserve_num = reserve_num + 1
    WHERE BID = NEW.book_ID;
END; //
DELIMITER ;

DELIMITER //
-- DROP TRIGGER IF EXISTS Reserve_Delete_Trigger;
CREATE TRIGGER Reserve_Delete_Trigger
AFTER DELETE ON Reserve
FOR EACH ROW
BEGIN
    UPDATE Book
    SET reserve_num = reserve_num - 1
    WHERE BID = OLD.book_ID;
END; //
DELIMITER ;

DELIMITER //
-- DROP TRIGGER IF EXISTS Borrow_Insert_Trigger;
CREATE TRIGGER Borrow_Insert_Trigger
AFTER INSERT ON Borrow_record
FOR EACH ROW
BEGIN
    UPDATE Book
    SET borrow_num = borrow_num + 1
    WHERE BID = NEW.book_ID;
END; //
DELIMITER ;

DELIMITER //
-- DROP TRIGGER IF EXISTS Borrow_Delete_Trigger;
CREATE TRIGGER Borrow_Delete_Trigger
AFTER DELETE ON Borrow_record
FOR EACH ROW
BEGIN
    UPDATE Book
    SET borrow_num = borrow_num - 1
    WHERE BID = OLD.book_ID;
END; //
DELIMITER ;

DELIMITER //
-- DROP TRIGGER IF EXISTS Rate_Insert_Trigger;
CREATE TRIGGER Rate_Insert_Trigger
AFTER INSERT ON Rate
FOR EACH ROW
BEGIN
    UPDATE Book
    SET rating = (rating * rating_num + NEW.score) / (rating_num + 1),
        rating_num = rating_num + 1
    WHERE BID = NEW.book_ID;
END; //
DELIMITER ;

DELIMITER //
-- DROP TRIGGER IF EXISTS Rate_Delete_Trigger;
CREATE TRIGGER Rate_Delete_Trigger
AFTER DELETE ON Rate
FOR EACH ROW
BEGIN
    UPDATE Book
    SET rating = (rating * rating_num - OLD.score) / (rating_num - 1),
        rating_num = rating_num - 1
    WHERE BID = OLD.book_ID;
END; //
DELIMITER ;

DELIMITER //
-- DROP TRIGGER IF EXISTS Rate_Update_Trigger;
CREATE TRIGGER Rate_Update_Trigger
AFTER UPDATE ON Rate
FOR EACH ROW
BEGIN
    UPDATE Book
    SET rating = (rating * rating_num - OLD.score + NEW.score) / rating_num
    WHERE BID = NEW.book_ID;
END; //
DELIMITER ;

DELIMITER //
-- DROP PROCEDURE IF EXISTS ADD_RATE;
CREATE PROCEDURE ADD_RATE(IN book_id INT, IN score INT)
BEGIN
    INSERT INTO Rate(book_ID, user_ID, score)
    VALUES (book_id, user_id, score);
END; //
DELIMITER ;

DELIMITER //
-- DROP PROCEDURE IF EXISTS Most_Popular_Book;
CREATE PROCEDURE Most_Popular_Book(OUT book_name VARCHAR(100), OUT rating FLOAT)
BEGIN
    SELECT bname, rating INTO book_name, rating
    FROM Book
    ORDER BY rating DESC
    LIMIT 1;
END; //
DELIMITER ;