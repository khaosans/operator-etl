CREATE OR REPLACE TABLE gold_comment_kpis AS
SELECT
    COUNT(*) AS comment_count,
    COUNT(DISTINCT docket_id) AS docket_count,
    COUNT(DISTINCT agency) AS agency_count,
    SUM(CASE WHEN pii_detected THEN 1 ELSE 0 END) AS pii_flagged_count,
    ROUND(SUM(CASE WHEN pii_detected THEN 1 ELSE 0 END) * 1.0 / NULLIF(COUNT(*), 0), 4) AS pii_rate,
    MAX(_ingested_at) AS freshness_at
FROM silver_comments;
