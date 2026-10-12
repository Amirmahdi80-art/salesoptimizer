-- run this in powershell: & "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" --default-character-set=utf8mb4 -u root -p salesoptimizer -e "source C:/projects/project-1.0.0/salesop/all_time_sold.sql"

-- Disable safe update mode
SET SQL_SAFE_UPDATES = 0;

-- Populate all_time_sold
UPDATE salesoptimizer.analysis_grade_one AS a
LEFT JOIN salesoptimizer.product_all_time_sold AS p
    ON a.product_code = p.product_code
SET a.all_time_sold = p.all_time_sold;
