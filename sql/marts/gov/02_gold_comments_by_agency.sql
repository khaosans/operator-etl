CREATE OR REPLACE TABLE gold_comments_by_agency AS
SELECT
    agency,
    COUNT(*) AS comments,
    SUM(CASE WHEN pii_detected THEN 1 ELSE 0 END) AS pii_flagged
FROM silver_comments
GROUP BY agency
ORDER BY comments DESC;
