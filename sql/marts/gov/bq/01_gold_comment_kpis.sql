CREATE OR REPLACE TABLE gold_comment_kpis AS
SELECT
    COUNT(*) AS comment_count,
    COUNT(DISTINCT docket_id) AS docket_count,
    COUNT(DISTINCT agency) AS agency_count,
    COUNTIF(pii_detected) AS pii_flagged_count,
    ROUND(SAFE_DIVIDE(COUNTIF(pii_detected), COUNT(*)), 4) AS pii_rate,
    MAX(_ingested_at) AS freshness_at
FROM silver_comments;
