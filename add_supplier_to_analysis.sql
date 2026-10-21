ALTER TABLE salesoptimizer.analysis_grade_one
    ADD COLUMN supplier VARCHAR(225) NULL AFTER all_time_sold;
    
UPDATE salesoptimizer.analysis_grade_one AS a
LEFT JOIN (
    SELECT 
        product_code,
        MIN(id) AS first_supplier_id
    FROM salesoptimizer.product_supplier
    GROUP BY product_code
) AS ps_pick ON ps_pick.product_code = a.product_code
LEFT JOIN salesoptimizer.product_supplier AS ps 
    ON ps.id = ps_pick.first_supplier_id
SET a.supplier = ps.supplier;