"""
create_product_all_time_sold.py
-------------------------------
Drops and recreates salesoptimizer.product_all_time_sold
from invoiceitems_parent data.

Equivalent SQL:
    DROP TABLE IF EXISTS salesoptimizer.product_all_time_sold;
    CREATE TABLE salesoptimizer.product_all_time_sold AS
    SELECT 
        MAX(ParentCode) AS product_code,
        SUM(MajorUnitQuantity) AS all_time_sold
    FROM salesoptimizer.invoiceitems_parent
    GROUP BY ParentCode;
"""

import logging
from datetime import datetime

from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

# ─────────────────────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("product_all_time_sold_log.txt", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

# ─────────────────────────────────────────────────────────────
# MySQL engine
# ─────────────────────────────────────────────────────────────
MYSQL_ENGINE = create_engine(
    URL.create(
        "mysql+pymysql",
        username="root",
        password="Amir@13511348",
        host="localhost",
        port=3306,
        database="salesoptimizer",
        query={"charset": "utf8mb4"},
    ),
    future=True,
)

# ─────────────────────────────────────────────────────────────
# SQL Statements
# ─────────────────────────────────────────────────────────────
DROP_SQL = text("""
    DROP TABLE IF EXISTS salesoptimizer.product_all_time_sold
""")

CREATE_SQL = text("""
    CREATE TABLE salesoptimizer.product_all_time_sold AS
    SELECT 
        MAX(ParentCode) AS product_code,
        SUM(MajorUnitQuantity) AS all_time_sold
    FROM salesoptimizer.invoiceitems_parent
    GROUP BY ParentCode
""")

VERIFY_SQL = text("""
    SELECT 
        COUNT(*) AS total_products,
        SUM(all_time_sold) AS grand_total_sold,
        MIN(all_time_sold) AS min_sold,
        MAX(all_time_sold) AS max_sold,
        AVG(all_time_sold) AS avg_sold
    FROM salesoptimizer.product_all_time_sold
""")

SAMPLE_SQL = text("""
    SELECT product_code, all_time_sold
    FROM salesoptimizer.product_all_time_sold
    ORDER BY all_time_sold DESC
    LIMIT 10
""")


# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────
def main():
    started = datetime.now()
    logging.info("=" * 70)
    logging.info("▶️  create_product_all_time_sold.py")
    logging.info(f"   Started: {started:%Y-%m-%d %H:%M:%S}")
    logging.info("=" * 70)

    try:
        with MYSQL_ENGINE.begin() as conn:
            # 1. Drop table if exists
            logging.info("🗑️  DROP TABLE IF EXISTS product_all_time_sold")
            conn.execute(DROP_SQL)

            # 2. Create table
            logging.info("🏗️  CREATE TABLE product_all_time_sold AS SELECT ...")
            conn.execute(CREATE_SQL)

        # 3. Verify
        logging.info("🔍 Verifying...")
        with MYSQL_ENGINE.connect() as conn:
            stats = conn.execute(VERIFY_SQL).fetchone()
            logging.info(f"📊 Total products : {stats[0]:,}")
            logging.info(f"📊 Grand total sold: {stats[1]:,}")
            logging.info(f"📊 Min sold       : {stats[2]}")
            logging.info(f"📊 Max sold       : {stats[3]}")
            logging.info(f"📊 Avg sold       : {stats[4]:.2f}")

            sample = conn.execute(SAMPLE_SQL).fetchall()
            logging.info(f"📋 Top 10 products by all_time_sold:")
            for row in sample:
                logging.info(f"   {row[0]}  →  {row[1]}")

    except Exception as e:
        logging.exception(f"❌ Failed: {e}")
        raise

    elapsed = (datetime.now() - started).total_seconds()
    logging.info("=" * 70)
    logging.info(f"✅ Completed in {elapsed:.2f}s")
    logging.info("=" * 70)


if __name__ == "__main__":
    main()