-- Customer 360 business questions for MySQL 8.0+
USE customer360_db;

-- 1. Which states generate the most merchandise revenue?
SELECT
    c.state,
    COUNT(DISTINCT o.order_id) AS orders,
    COUNT(DISTINCT o.customer_id) AS customers,
    ROUND(SUM(o.revenue), 2) AS revenue
FROM fact_orders AS o
JOIN dim_customer AS c ON c.customer_id = o.customer_id
WHERE o.order_status NOT IN ('canceled', 'unavailable')
GROUP BY c.state
ORDER BY revenue DESC;

-- 2. Which cities generate the most revenue?
SELECT
    c.city,
    c.state,
    COUNT(DISTINCT o.customer_id) AS customers,
    ROUND(SUM(o.revenue), 2) AS revenue
FROM fact_orders AS o
JOIN dim_customer AS c ON c.customer_id = o.customer_id
WHERE o.order_status NOT IN ('canceled', 'unavailable')
GROUP BY c.city, c.state
ORDER BY revenue DESC
LIMIT 20;

-- 3. Which categories have the highest repeat-customer rate?
-- A minimum customer threshold prevents tiny categories from ranking first by chance.
WITH category_customer_orders AS (
    SELECT
        COALESCE(p.category_name_english, 'unknown') AS category,
        o.customer_id,
        COUNT(DISTINCT o.order_id) AS order_count
    FROM fact_orders AS o
    JOIN dim_product AS p ON p.product_id = o.product_id
    WHERE o.order_status NOT IN ('canceled', 'unavailable')
    GROUP BY COALESCE(p.category_name_english, 'unknown'), o.customer_id
)
SELECT
    category,
    COUNT(*) AS customers,
    SUM(order_count > 1) AS repeat_customers,
    ROUND(100.0 * SUM(order_count > 1) / NULLIF(COUNT(*), 0), 2) AS repeat_rate_pct
FROM category_customer_orders
GROUP BY category
HAVING COUNT(*) >= 30
ORDER BY repeat_rate_pct DESC, customers DESC;

-- 4. What is the monthly revenue and customer trend?
SELECT
    d.calendar_year,
    d.month_number,
    d.month_name,
    COUNT(DISTINCT o.order_id) AS orders,
    COUNT(DISTINCT o.customer_id) AS active_customers,
    ROUND(SUM(o.revenue), 2) AS revenue
FROM fact_orders AS o
JOIN dim_date AS d ON d.date_key = o.purchase_date_key
WHERE o.order_status NOT IN ('canceled', 'unavailable')
GROUP BY d.calendar_year, d.month_number, d.month_name
ORDER BY d.calendar_year, d.month_number;

-- 5. Which payment methods account for the most collected value?
SELECT
    payment_type,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(SUM(payment_value), 2) AS payment_value
FROM fact_payments
GROUP BY payment_type
ORDER BY payment_value DESC;

-- 6. Which mapped web visitors browsed but did not purchase in clickstream data?
SELECT
    customer_id,
    COUNT(DISTINCT user_session) AS sessions,
    SUM(event_type = 'view') AS views,
    SUM(event_type = 'cart') AS cart_additions
FROM fact_web_activity
GROUP BY customer_id
HAVING SUM(event_type = 'purchase') = 0
ORDER BY views DESC
LIMIT 50;

-- 7. Which campaigns have the best funnel and return on investment?
SELECT
    f.campaign_id,
    d.campaign_type,
    SUM(f.email_sent) AS sent,
    ROUND(100.0 * SUM(f.opened) / NULLIF(SUM(f.email_sent), 0), 2) AS open_rate_pct,
    ROUND(100.0 * SUM(f.clicked) / NULLIF(SUM(f.email_sent), 0), 2) AS ctr_pct,
    ROUND(100.0 * SUM(f.converted) / NULLIF(SUM(f.clicked), 0), 2) AS click_conversion_pct,
    ROUND(SUM(f.revenue_generated), 2) AS revenue,
    ROUND(d.campaign_cost, 2) AS cost,
    ROUND((SUM(f.revenue_generated) - d.campaign_cost) / NULLIF(d.campaign_cost, 0), 2) AS roi
FROM fact_campaign AS f
JOIN dim_campaign AS d ON d.campaign_id = f.campaign_id
GROUP BY f.campaign_id, d.campaign_type, d.campaign_cost
ORDER BY roi DESC;

-- 8. What is the Olist customer-rating distribution?
SELECT rating, COUNT(*) AS reviews
FROM fact_customer_reviews
GROUP BY rating
ORDER BY rating;

-- 9. Which external product categories show weak sentiment?
SELECT
    category_name,
    COUNT(*) AS reviews,
    ROUND(AVG(rating), 2) AS avg_rating,
    ROUND(AVG(sentiment_score), 3) AS avg_sentiment_score
FROM fact_product_reviews
GROUP BY category_name
HAVING COUNT(*) >= 20
ORDER BY avg_sentiment_score ASC, reviews DESC;

-- 10. Who are the most loyal repeat customers?
SELECT
    o.customer_id,
    COUNT(DISTINCT o.order_id) AS orders,
    ROUND(SUM(o.revenue), 2) AS revenue,
    MAX(o.purchase_date) AS last_purchase_date
FROM fact_orders AS o
WHERE o.order_status NOT IN ('canceled', 'unavailable')
GROUP BY o.customer_id
HAVING COUNT(DISTINCT o.order_id) > 1
ORDER BY orders DESC, revenue DESC
LIMIT 50;
