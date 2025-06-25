DECLARE @schema NVARCHAR(128),
        @table  NVARCHAR(128),
        @column NVARCHAR(128),
        @sql    NVARCHAR(MAX);

DECLARE cur CURSOR LOCAL FAST_FORWARD FOR
SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME
FROM INFORMATION_SCHEMA.COLUMNS
WHERE DATA_TYPE IN ('date','datetime','datetime2','smalldatetime')
    AND TABLE_SCHEMA NOT IN ('Integration', 'sys') -- Integration schema is just a staging area, no need to waste resources
    AND TABLE_NAME <> 'Date' -- Updated BEFORE this script can be run
    AND COLUMN_NAME NOT IN ('Valid To', 'Valid From');
-- This should be irrelevant for the update

OPEN cur;
FETCH NEXT FROM cur INTO @schema, @table, @column;

WHILE @@FETCH_STATUS = 0
BEGIN
    BEGIN TRANSACTION;
    BEGIN TRY
        SET @sql = N'UPDATE [' + @schema + '].[' + @table + '] ' +
                   N'SET [' + @column + '] = DATEADD(year, 9, [' + @column + ']) ' +
                   N'WHERE [' + @column + '] IS NOT NULL;';

        PRINT @sql;  -- Inspect before execution
        EXEC sp_executesql @sql;

        COMMIT TRANSACTION;
        PRINT @schema + '.' + @table + ' updated successfully.';
    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;
        PRINT 'Error updating ' + @schema + '.' + @table + 
              ' (' + @column + '): ' + ERROR_MESSAGE();
    END CATCH;

    FETCH NEXT FROM cur INTO @schema, @table, @column;
END

CLOSE cur;
DEALLOCATE cur;