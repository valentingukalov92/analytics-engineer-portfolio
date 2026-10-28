WITH daily_totals AS (
    SELECT
        DATE_TRUNC('month', day_date) AS month_date,
        SUM(total_contacts)           AS daily_sum
    FROM {{ ref('mart_monetizing_daily') }}
    GROUP BY 1
),

monthly_totals AS (
    SELECT
        month_date,
        SUM(total_contacts) AS monthly_sum
    FROM {{ ref('mart_monetizing_monthly') }}
    GROUP BY 1
)

SELECT
    COALESCE(d.month_date, m.month_date) AS month_date,
    d.daily_sum,
    m.monthly_sum
FROM daily_totals d
FULL OUTER JOIN monthly_totals m USING (month_date)
WHERE d.daily_sum IS DISTINCT FROM m.monthly_sum