CREATE OR REPLACE TABLE gold_comments_by_agency AS
SELECT
    agency,
    COUNT(*) AS comments,
    COUNTIF(pii_detected) AS pii_flagged
FROM silver_comments
GROUP BY agency
ORDER BY comments DESC;
