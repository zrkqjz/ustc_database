DELIMITER //
DROP PROCEDURE updateReaderID;
CREATE PROCEDURE updateReaderID(
    IN old_ID VARCHAR(8),
    IN new_ID VARCHAR(8),
    OUT msg VARCHAR(128)
 )
BEGIN
    DECLARE exits INT DEFAULT 0;
    IF EXISTS(SELECT 1 FROM reader WHERE RID = new_ID) THEN
        SET exits = 1;
        SET msg = 'new_ID already exists';
    ELSEIF NOT EXISTS(SELECT 1 FROM reader WHERE RID = old_ID) THEN
        SET exits = 1;
        SET msg = 'old_ID not found';
    END IF;
	
    -- 根据exits的值决定是否抛出异常或执行其他逻辑
    IF exits = 0 THEN
		START TRANSACTION;
			INSERT INTO reader (rid, rname, age, address)
				SELECT new_ID, rname, age, address 
                FROM reader WHERE RID = old_ID;
            UPDATE Borrow SET reader_ID = new_ID WHERE reader_ID = old_ID;
            UPDATE Reserve SET reader_ID = new_ID WHERE reader_ID = old_ID;
			DELETE FROM Reader WHERE RID = old_ID;
        COMMIT;
        SET msg = 'update finished';
    END IF;
END; 
// DELIMITER ;

CALL updateReaderID('R006', 'R999', @outputMessage);
SELECT @outputMessage;
SELECT * from reader;
SELECT * from borrow order by reader_ID;
SELECT * from reserve order by reader_ID;

