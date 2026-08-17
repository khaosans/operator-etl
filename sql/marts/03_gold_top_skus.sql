CREATE OR REPLACE TABLE gold_top_skus AS
SELECT
    sku,
    COUNT(*) AS orders,
    ROUND(SUM(amount), 2) AS revenue
FROM silver_orders
GROUP BY sku
ORDER BY revenue DESC
LIMIT 10;
