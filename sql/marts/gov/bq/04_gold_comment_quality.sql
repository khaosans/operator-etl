CREATE OR REPLACE TABLE gold_comment_quality AS
SELECT
    (SELECT COUNT(*) FROM bronze_raw) AS bronze_rows,
    (SELECT COUNT(*) FROM silver_comments) AS silver_rows,
    (SELECT COUNT(*) FROM quarantine_comments) AS quarantined_rows,
    (SELECT MAX(_ingested_at) FROM bronze_raw) AS last_ingest_at,
    ROUND(
        SAFE_DIVIDE(
            (SELECT COUNT(*) FROM quarantine_comments),
            NULLIF((SELECT COUNT(*) FROM bronze_raw), 0)
        ),
        4
    ) AS quarantine_rate;
