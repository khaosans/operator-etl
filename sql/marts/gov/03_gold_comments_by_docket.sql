CREATE OR REPLACE TABLE gold_comments_by_docket AS
SELECT
    docket_id,
    agency,
    COUNT(*) AS comments,
    SUM(CASE WHEN pii_detected THEN 1 ELSE 0 END) AS pii_flagged
FROM silver_comments
GROUP BY docket_id, agency
ORDER BY comments DESC;
