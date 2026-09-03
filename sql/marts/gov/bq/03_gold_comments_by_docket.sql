CREATE OR REPLACE TABLE gold_comments_by_docket AS
SELECT
    docket_id,
    agency,
    COUNT(*) AS comments,
    COUNTIF(pii_detected) AS pii_flagged
FROM silver_comments
GROUP BY docket_id, agency
ORDER BY comments DESC;
