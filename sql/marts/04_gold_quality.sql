CREATE OR REPLACE TABLE gold_quality AS
SELECT
    (SELECT COUNT(*) FROM bronze_raw) AS bronze_rows,
    (SELECT COUNT(*) FROM silver_orders) AS silver_rows,
    (SELECT COUNT(*) FROM quarantine_orders) AS quarantined_rows,
    (SELECT MAX(_ingested_at) FROM bronze_raw) AS last_ingest_at,
    CASE
        WHEN (SELECT COUNT(*) FROM bronze_raw) = 0 THEN 0.0
        ELSE ROUND(
            (SELECT COUNT(*) FROM quarantine_orders) * 1.0
            / (SELECT COUNT(*) FROM bronze_raw),
            4
        )
    END AS quarantine_rate;
