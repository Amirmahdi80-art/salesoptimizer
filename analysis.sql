-- run this in powershell: & "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" --default-character-set=utf8mb4 -u root -p salesoptimizer -e "source C:/projects/project-1.0.0/salesop/analysis.sql"

DROP TABLE IF EXISTS salesoptimizer.analysis_grade_one;

CREATE TABLE salesoptimizer.analysis_grade_one AS
WITH product_signals AS (
    SELECT
        p.product_code,
        p.category_code,
        p.total_inventory,
        p.first_show_date,
        p.age_in_months,
        p.age_in_days,
        p.discount_percentage,
        p.total_sold,
        p.total_sold_12_months,

        (p.total_inventory - p.total_sold) AS remaining_inventory,
        GREATEST(6 - p.age_in_months, 0) AS remaining_months,

        CASE
            WHEN p.age_in_months >= 12 THEN
                p.first_month_per + p.second_month_per + p.third_month_per + p.forth_month_per +
                p.fifth_month_per + p.sixth_month_per + p.seventh_month_per + p.eighth_month_per +
                p.ninth_month_per + p.tenth_month_per + p.eleventh_month_per + p.twelveth_month_per
            WHEN p.age_in_months = 11 THEN
                p.first_month_per + p.second_month_per + p.third_month_per + p.forth_month_per +
                p.fifth_month_per + p.sixth_month_per + p.seventh_month_per + p.eighth_month_per +
                p.ninth_month_per + p.tenth_month_per + p.eleventh_month_per
            WHEN p.age_in_months = 10 THEN
                p.first_month_per + p.second_month_per + p.third_month_per + p.forth_month_per +
                p.fifth_month_per + p.sixth_month_per + p.seventh_month_per + p.eighth_month_per +
                p.ninth_month_per + p.tenth_month_per
            WHEN p.age_in_months = 9 THEN
                p.first_month_per + p.second_month_per + p.third_month_per + p.forth_month_per +
                p.fifth_month_per + p.sixth_month_per + p.seventh_month_per + p.eighth_month_per +
                p.ninth_month_per
            WHEN p.age_in_months = 8 THEN
                p.first_month_per + p.second_month_per + p.third_month_per + p.forth_month_per +
                p.fifth_month_per + p.sixth_month_per + p.seventh_month_per + p.eighth_month_per
            WHEN p.age_in_months = 7 THEN
                p.first_month_per + p.second_month_per + p.third_month_per + p.forth_month_per +
                p.fifth_month_per + p.sixth_month_per + p.seventh_month_per
            WHEN p.age_in_months = 6 THEN
                p.first_month_per + p.second_month_per + p.third_month_per + p.forth_month_per +
                p.fifth_month_per + p.sixth_month_per
            WHEN p.age_in_months = 5 THEN
                p.first_month_per + p.second_month_per + p.third_month_per + p.forth_month_per +
                p.fifth_month_per
            WHEN p.age_in_months = 4 THEN
                p.first_month_per + p.second_month_per + p.third_month_per + p.forth_month_per
            WHEN p.age_in_months = 3 THEN
                p.first_month_per + p.second_month_per + p.third_month_per
            WHEN p.age_in_months = 2 THEN
                p.first_month_per + p.second_month_per
            WHEN p.age_in_months = 1 THEN
                p.first_month_per
            ELSE 0
        END AS cumulative_sell_through,

        CASE
            WHEN p.age_in_months >= 12 THEN p.total_sold_12_months
            WHEN p.age_in_months = 11 THEN
                p.first_month_qty + p.second_month_qty + p.third_month_qty + p.forth_month_qty +
                p.fifth_month_qty + p.sixth_month_qty + p.seventh_month_qty + p.eighth_month_qty +
                p.ninth_month_qty + p.tenth_month_qty + p.eleventh_month_qty
            WHEN p.age_in_months = 10 THEN
                p.first_month_qty + p.second_month_qty + p.third_month_qty + p.forth_month_qty +
                p.fifth_month_qty + p.sixth_month_qty + p.seventh_month_qty + p.eighth_month_qty +
                p.ninth_month_qty + p.tenth_month_qty
            WHEN p.age_in_months = 9 THEN
                p.first_month_qty + p.second_month_qty + p.third_month_qty + p.forth_month_qty +
                p.fifth_month_qty + p.sixth_month_qty + p.seventh_month_qty + p.eighth_month_qty +
                p.ninth_month_qty
            WHEN p.age_in_months = 8 THEN
                p.first_month_qty + p.second_month_qty + p.third_month_qty + p.forth_month_qty +
                p.fifth_month_qty + p.sixth_month_qty + p.seventh_month_qty + p.eighth_month_qty
            WHEN p.age_in_months = 7 THEN
                p.first_month_qty + p.second_month_qty + p.third_month_qty + p.forth_month_qty +
                p.fifth_month_qty + p.sixth_month_qty + p.seventh_month_qty
            WHEN p.age_in_months = 6 THEN
                p.first_month_qty + p.second_month_qty + p.third_month_qty + p.forth_month_qty +
                p.fifth_month_qty + p.sixth_month_qty
            WHEN p.age_in_months = 5 THEN
                p.first_month_qty + p.second_month_qty + p.third_month_qty + p.forth_month_qty +
                p.fifth_month_qty
            WHEN p.age_in_months = 4 THEN
                p.first_month_qty + p.second_month_qty + p.third_month_qty + p.forth_month_qty
            WHEN p.age_in_months = 3 THEN
                p.first_month_qty + p.second_month_qty + p.third_month_qty
            WHEN p.age_in_months = 2 THEN
                p.first_month_qty + p.second_month_qty
            WHEN p.age_in_months = 1 THEN
                p.first_month_qty
            ELSE 0
        END AS cumulative_qty,

        CASE
            WHEN p.age_in_months >= 12 THEN p.twelveth_month_qty
            WHEN p.age_in_months = 11 THEN p.eleventh_month_qty
            WHEN p.age_in_months = 10 THEN p.tenth_month_qty
            WHEN p.age_in_months = 9 THEN p.ninth_month_qty
            WHEN p.age_in_months = 8 THEN p.eighth_month_qty
            WHEN p.age_in_months = 7 THEN p.seventh_month_qty
            WHEN p.age_in_months = 6 THEN p.sixth_month_qty
            WHEN p.age_in_months = 5 THEN p.fifth_month_qty
            WHEN p.age_in_months = 4 THEN p.forth_month_qty
            WHEN p.age_in_months = 3 THEN p.third_month_qty
            WHEN p.age_in_months = 2 THEN p.second_month_qty
            WHEN p.age_in_months = 1 THEN p.first_month_qty
            ELSE 0
        END AS current_velocity,

        CASE
            WHEN p.age_in_months >= 12 THEN p.eleventh_month_qty
            WHEN p.age_in_months = 11 THEN p.tenth_month_qty
            WHEN p.age_in_months = 10 THEN p.ninth_month_qty
            WHEN p.age_in_months = 9 THEN p.eighth_month_qty
            WHEN p.age_in_months = 8 THEN p.seventh_month_qty
            WHEN p.age_in_months = 7 THEN p.sixth_month_qty
            WHEN p.age_in_months = 6 THEN p.fifth_month_qty
            WHEN p.age_in_months = 5 THEN p.forth_month_qty
            WHEN p.age_in_months = 4 THEN p.third_month_qty
            WHEN p.age_in_months = 3 THEN p.second_month_qty
            WHEN p.age_in_months = 2 THEN p.first_month_qty
            ELSE 0
        END AS prior_velocity

    FROM salesoptimizer.twelve_month_analysis p
),

benchmark_signals AS (
    SELECT
        b.category_code,
        b.avg_first_month_per,
        b.avg_second_month_per,
        b.avg_third_month_per,
        b.avg_forth_month_per,
        b.avg_fifth_month_per,
        b.avg_sixth_month_per,
        b.avg_seventh_month_per,
        b.avg_eighth_month_per,
        b.avg_ninth_month_per,
        b.avg_tenth_month_per,
        b.avg_eleventh_month_per,
        b.avg_twelveth_month_per,
        b.avg_first_month_qty,
        b.avg_second_month_qty,
        b.avg_third_month_qty,
        b.avg_forth_month_qty,
        b.avg_fifth_month_qty,
        b.avg_sixth_month_qty,
        b.avg_seventh_month_qty,
        b.avg_eighth_month_qty,
        b.avg_ninth_month_qty,
        b.avg_tenth_month_qty,
        b.avg_eleventh_month_qty,
        b.avg_twelveth_month_qty,
        b.avg_discount_percentage
    FROM salesoptimizer.category_contr_avgs b
),

combined AS (
    SELECT
        ps.*,
        bs.avg_discount_percentage,

        CASE
            WHEN ps.age_in_months >= 12 THEN
                bs.avg_first_month_per + bs.avg_second_month_per + bs.avg_third_month_per + bs.avg_forth_month_per +
                bs.avg_fifth_month_per + bs.avg_sixth_month_per + bs.avg_seventh_month_per + bs.avg_eighth_month_per +
                bs.avg_ninth_month_per + bs.avg_tenth_month_per + bs.avg_eleventh_month_per + bs.avg_twelveth_month_per
            WHEN ps.age_in_months = 11 THEN
                bs.avg_first_month_per + bs.avg_second_month_per + bs.avg_third_month_per + bs.avg_forth_month_per +
                bs.avg_fifth_month_per + bs.avg_sixth_month_per + bs.avg_seventh_month_per + bs.avg_eighth_month_per +
                bs.avg_ninth_month_per + bs.avg_tenth_month_per + bs.avg_eleventh_month_per
            WHEN ps.age_in_months = 10 THEN
                bs.avg_first_month_per + bs.avg_second_month_per + bs.avg_third_month_per + bs.avg_forth_month_per +
                bs.avg_fifth_month_per + bs.avg_sixth_month_per + bs.avg_seventh_month_per + bs.avg_eighth_month_per +
                bs.avg_ninth_month_per + bs.avg_tenth_month_per
            WHEN ps.age_in_months = 9 THEN
                bs.avg_first_month_per + bs.avg_second_month_per + bs.avg_third_month_per + bs.avg_forth_month_per +
                bs.avg_fifth_month_per + bs.avg_sixth_month_per + bs.avg_seventh_month_per + bs.avg_eighth_month_per +
                bs.avg_ninth_month_per
            WHEN ps.age_in_months = 8 THEN
                bs.avg_first_month_per + bs.avg_second_month_per + bs.avg_third_month_per + bs.avg_forth_month_per +
                bs.avg_fifth_month_per + bs.avg_sixth_month_per + bs.avg_seventh_month_per + bs.avg_eighth_month_per
            WHEN ps.age_in_months = 7 THEN
                bs.avg_first_month_per + bs.avg_second_month_per + bs.avg_third_month_per + bs.avg_forth_month_per +
                bs.avg_fifth_month_per + bs.avg_sixth_month_per + bs.avg_seventh_month_per
            WHEN ps.age_in_months = 6 THEN
                bs.avg_first_month_per + bs.avg_second_month_per + bs.avg_third_month_per + bs.avg_forth_month_per +
                bs.avg_fifth_month_per + bs.avg_sixth_month_per
            WHEN ps.age_in_months = 5 THEN
                bs.avg_first_month_per + bs.avg_second_month_per + bs.avg_third_month_per + bs.avg_forth_month_per +
                bs.avg_fifth_month_per
            WHEN ps.age_in_months = 4 THEN
                bs.avg_first_month_per + bs.avg_second_month_per + bs.avg_third_month_per + bs.avg_forth_month_per
            WHEN ps.age_in_months = 3 THEN
                bs.avg_first_month_per + bs.avg_second_month_per + bs.avg_third_month_per
            WHEN ps.age_in_months = 2 THEN
                bs.avg_first_month_per + bs.avg_second_month_per
            WHEN ps.age_in_months = 1 THEN
                bs.avg_first_month_per
            ELSE 0
        END AS benchmark_cumulative_sell_through,

        CASE
            WHEN ps.age_in_months >= 12 THEN
                bs.avg_first_month_qty + bs.avg_second_month_qty + bs.avg_third_month_qty + bs.avg_forth_month_qty +
                bs.avg_fifth_month_qty + bs.avg_sixth_month_qty + bs.avg_seventh_month_qty + bs.avg_eighth_month_qty +
                bs.avg_ninth_month_qty + bs.avg_tenth_month_qty + bs.avg_eleventh_month_qty + bs.avg_twelveth_month_qty
            WHEN ps.age_in_months = 11 THEN
                bs.avg_first_month_qty + bs.avg_second_month_qty + bs.avg_third_month_qty + bs.avg_forth_month_qty +
                bs.avg_fifth_month_qty + bs.avg_sixth_month_qty + bs.avg_seventh_month_qty + bs.avg_eighth_month_qty +
                bs.avg_ninth_month_qty + bs.avg_tenth_month_qty + bs.avg_eleventh_month_qty
            WHEN ps.age_in_months = 10 THEN
                bs.avg_first_month_qty + bs.avg_second_month_qty + bs.avg_third_month_qty + bs.avg_forth_month_qty +
                bs.avg_fifth_month_qty + bs.avg_sixth_month_qty + bs.avg_seventh_month_qty + bs.avg_eighth_month_qty +
                bs.avg_ninth_month_qty + bs.avg_tenth_month_qty
            WHEN ps.age_in_months = 9 THEN
                bs.avg_first_month_qty + bs.avg_second_month_qty + bs.avg_third_month_qty + bs.avg_forth_month_qty +
                bs.avg_fifth_month_qty + bs.avg_sixth_month_qty + bs.avg_seventh_month_qty + bs.avg_eighth_month_qty +
                bs.avg_ninth_month_qty
            WHEN ps.age_in_months = 8 THEN
                bs.avg_first_month_qty + bs.avg_second_month_qty + bs.avg_third_month_qty + bs.avg_forth_month_qty +
                bs.avg_fifth_month_qty + bs.avg_sixth_month_qty + bs.avg_seventh_month_qty + bs.avg_eighth_month_qty
            WHEN ps.age_in_months = 7 THEN
                bs.avg_first_month_qty + bs.avg_second_month_qty + bs.avg_third_month_qty + bs.avg_forth_month_qty +
                bs.avg_fifth_month_qty + bs.avg_sixth_month_qty + bs.avg_seventh_month_qty
            WHEN ps.age_in_months = 6 THEN
                bs.avg_first_month_qty + bs.avg_second_month_qty + bs.avg_third_month_qty + bs.avg_forth_month_qty +
                bs.avg_fifth_month_qty + bs.avg_sixth_month_qty
            WHEN ps.age_in_months = 5 THEN
                bs.avg_first_month_qty + bs.avg_second_month_qty + bs.avg_third_month_qty + bs.avg_forth_month_qty +
                bs.avg_fifth_month_qty
            WHEN ps.age_in_months = 4 THEN
                bs.avg_first_month_qty + bs.avg_second_month_qty + bs.avg_third_month_qty + bs.avg_forth_month_qty
            WHEN ps.age_in_months = 3 THEN
                bs.avg_first_month_qty + bs.avg_second_month_qty + bs.avg_third_month_qty
            WHEN ps.age_in_months = 2 THEN
                bs.avg_first_month_qty + bs.avg_second_month_qty
            WHEN ps.age_in_months = 1 THEN
                bs.avg_first_month_qty
            ELSE 0
        END AS benchmark_cumulative_qty,

        CASE
            WHEN ps.age_in_months >= 12 THEN bs.avg_twelveth_month_qty
            WHEN ps.age_in_months = 11 THEN bs.avg_eleventh_month_qty
            WHEN ps.age_in_months = 10 THEN bs.avg_tenth_month_qty
            WHEN ps.age_in_months = 9 THEN bs.avg_ninth_month_qty
            WHEN ps.age_in_months = 8 THEN bs.avg_eighth_month_qty
            WHEN ps.age_in_months = 7 THEN bs.avg_seventh_month_qty
            WHEN ps.age_in_months = 6 THEN bs.avg_sixth_month_qty
            WHEN ps.age_in_months = 5 THEN bs.avg_fifth_month_qty
            WHEN ps.age_in_months = 4 THEN bs.avg_forth_month_qty
            WHEN ps.age_in_months = 3 THEN bs.avg_third_month_qty
            WHEN ps.age_in_months = 2 THEN bs.avg_second_month_qty
            WHEN ps.age_in_months = 1 THEN bs.avg_first_month_qty
            ELSE 0
        END AS benchmark_current_month_qty

    FROM product_signals ps
    LEFT JOIN benchmark_signals bs
        ON ps.category_code = bs.category_code
),

metrics AS (
    SELECT
        c.*,

        CASE
            WHEN c.benchmark_cumulative_sell_through > 0
            THEN c.cumulative_sell_through / c.benchmark_cumulative_sell_through
            ELSE NULL
        END AS rstr,

        CASE
            WHEN c.benchmark_cumulative_qty > 0
            THEN c.cumulative_qty / c.benchmark_cumulative_qty
            ELSE NULL
        END AS cdr,

        CASE
            WHEN c.benchmark_current_month_qty > 0
            THEN c.current_velocity / c.benchmark_current_month_qty
            ELSE NULL
        END AS rvr,
        -- This part can be editted
        @@vt@@
        -- End
        (c.discount_percentage - c.avg_discount_percentage) AS dd,

        CASE
            WHEN c.remaining_months > 0
            THEN c.remaining_inventory / c.remaining_months
            ELSE NULL
        END AS required_future_velocity,

        CASE
            WHEN c.remaining_months > 0 AND c.remaining_inventory > 0
            THEN c.current_velocity / (c.remaining_inventory / c.remaining_months)
            ELSE NULL
        END AS velocity_gap,

        CASE
            WHEN c.total_inventory > 0 AND c.total_inventory - c.total_sold <= 0 THEN 1
            ELSE 0
        END AS completed,
        -- This part can be editted
        @@discount_quality@@
        -- End
    FROM combined c
),
-- This part can be editted
@@tag@@
-- End
action_rollup AS (
    SELECT
        a.product_code,
        COUNT(*) AS action_count_total,
        SUM(CASE WHEN a.measurement_status IN ('کامل_شده','داده_ناکافی')
                 THEN 1 ELSE 0 END) AS action_count_measured
    FROM salesoptimizer.actions a
    GROUP BY a.product_code
),

last_completed AS (
    SELECT
        a.product_code,
        a.action_type,
        a.action_verdict,
        a.action_lift,
        a.action_margin_impact,
        ROW_NUMBER() OVER (
            PARTITION BY a.product_code
            ORDER BY a.measurement_end_date DESC, a.id DESC
        ) AS rn
    FROM salesoptimizer.actions a
    WHERE a.measurement_status = 'کامل_شده'
),

current_active AS (
    SELECT
        a.product_code,
        a.action_type,
        a.action_start_date,
        a.action_end_date,
        ROW_NUMBER() OVER (
            PARTITION BY a.product_code
            ORDER BY a.action_start_date DESC, a.id DESC
        ) AS rn
    FROM salesoptimizer.actions a
    WHERE a.action_start_date <= CURDATE()
      AND (a.action_end_date IS NULL OR a.action_end_date >= CURDATE())
)
-- this part can be edited
@@action@@
-- End
LEFT JOIN salesoptimizer.product_categories pc ON pc.category_code = t.category_code
LEFT JOIN action_rollup   ar ON ar.product_code = t.product_code
LEFT JOIN last_completed  lc ON lc.product_code = t.product_code AND lc.rn = 1
LEFT JOIN current_active  ca ON ca.product_code = t.product_code AND ca.rn = 1;

-- SELECT
--     product_code,
--     category_code,
--     age_in_months,
--     age_in_days,
--     total_inventory,
--     total_sold_12_months,
--     remaining_inventory,
--     remaining_months,
--     cumulative_sell_through,
--     benchmark_cumulative_sell_through,
--     rstr,
--     cdr,
--     rvr,
--     vt,
--     discount_percentage,
--     avg_discount_percentage,
--     dd,
--     discount_quality,
--     current_velocity,
--     required_future_velocity,
--     velocity_gap,
--     completed,
--     status_tag,
--     action
-- FROM tagged;