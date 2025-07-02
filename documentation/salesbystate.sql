SELECT
    FORMAT(s.[Invoice Date Key], 'yyyy-MM') AS [Month],
    SUM(s.[Total Excluding Tax]) AS [Total Sales]
FROM Fact.Sale s
    JOIN Dimension.City c ON s.[City Key] = c.[City Key]
WHERE 
    c.[State Province] = 'California'
    AND s.[Invoice Date Key] >= DATEADD(YEAR, -3, CAST(GETDATE() AS DATE))
GROUP BY FORMAT(s.[Invoice Date Key], 'yyyy-MM')
ORDER BY [Month];