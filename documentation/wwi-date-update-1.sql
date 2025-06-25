-- Step 1: Create a staging table with updated values
SELECT
    DATEADD(YEAR, 9, [Date]) AS [Date],
    MIN([Day Number]) AS [Day Number],
    MIN([Day]) AS [Day],
    MIN([Month]) AS [Month],
    MIN([Short Month]) AS [Short Month],
    MIN([Calendar Month Number]) AS [Calendar Month Number],
    MIN([Calendar Month Label]) AS [Calendar Month Label],
    MIN([Calendar Year]) + 9 AS [Calendar Year],
    'CY' + CAST(MIN([Calendar Year]) + 9 AS VARCHAR(4)) AS [Calendar Year Label],
    MIN([Fiscal Month Number]) AS [Fiscal Month Number],
    MIN([Fiscal Month Label]) AS [Fiscal Month Label],
    MIN([Fiscal Year]) + 9 AS [Fiscal Year],
    'FY' + CAST(MIN([Fiscal Year]) + 9 AS VARCHAR(4)) AS [Fiscal Year Label],
    MIN([ISO Week Number]) AS [ISO Week Number],
    MONTH(DATEADD(YEAR, 9, [Date])) AS [Calendar Month],
    DATEPART(QUARTER, DATEADD(YEAR, 9, [Date])) AS [Calendar Quarter],
    CEILING(MIN([Fiscal Month Number]) / 3.0) AS [Fiscal Quarter]
INTO #ShiftedDateDimension
FROM [Dimension].[Date]
GROUP BY DATEADD(YEAR, 9, [Date]);

-- Step 2: Update Dimension.Date to add new columns
ALTER TABLE [Dimension].[Date]
ADD [Calendar Quarter] TINYINT,
    [Fiscal Quarter] TINYINT;

-- Step 3: Insert shifted rows
BEGIN TRANSACTION;
BEGIN TRY
    INSERT INTO [Dimension].[Date]
    (
    [Date],
    [Day Number],
    [Day],
    [Month],
    [Short Month],
    [Calendar Month Number],
    [Calendar Month Label],
    [Calendar Year],
    [Calendar Year Label],
    [Fiscal Month Number],
    [Fiscal Month Label],
    [Fiscal Year],
    [Fiscal Year Label],
    [ISO Week Number],
    [Calendar Quarter],
    [Fiscal Quarter]
    )
SELECT
    [Date],
    [Day Number],
    [Day],
    [Month],
    [Short Month],
    [Calendar Month Number],
    [Calendar Month Label],
    [Calendar Year],
    [Calendar Year Label],
    [Fiscal Month Number],
    [Fiscal Month Label],
    [Fiscal Year],
    [Fiscal Year Label],
    [ISO Week Number],
    [Calendar Quarter],
    [Fiscal Quarter]
FROM #ShiftedDateDimension;

  COMMIT;
  PRINT 'Inserted shifted dates into Dimension.Date.';
END TRY
BEGIN CATCH
  ROLLBACK;
  PRINT 'Error inserting into Dimension.Date: ' + ERROR_MESSAGE();
END CATCH;

-- Clean up temp table
DROP TABLE #ShiftedDateDimension;