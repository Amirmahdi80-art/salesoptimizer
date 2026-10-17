"""
populate_product_voucher_fast.py
--------------------------------
Streams data from SQL Server → CSV → MySQL using LOAD DATA.
Handles 1M+ rows in 2–3 minutes.
"""

import logging
import os
from datetime import datetime

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

# ─────────────────────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("product_voucher_fast_log.txt", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

# ─────────────────────────────────────────────────────────────
# Engines
# ─────────────────────────────────────────────────────────────
SQLSERVER_ENGINE = create_engine(
    URL.create(
        "mssql+pyodbc",
        username="reports",
        password="123456789",
        host="172.16.30.20",
        database="Webpoosh_Sg3",
        query={
            "driver": "ODBC Driver 17 for SQL Server",
            "TrustServerCertificate": "yes",
        },
    ),
    fast_executemany=True,
)

MYSQL_ENGINE = create_engine(
    URL.create(
        "mysql+pymysql",              
        username="root",
        password="Amir@13511348",
        host="localhost",
        port=3306,
        database="salesoptimizer",
        query={
            "charset": "utf8mb4",
            "local_infile": "1",      
        },
    ),
    future=True,
)

# ─────────────────────────────────────────────────────────────
# Query
# ─────────────────────────────────────────────────────────────
QUERY = text("""
    SELECT
        'INCOMING'              AS direction,
        v.InventoryVoucherID    AS inventory_voucher_id,
        v.InventoryVoucherSpecificationRef AS spec_ref,
        v.Number                AS voucher_no,
        v.Date                  AS voucher_date,
        src.StoreID             AS source_store_id,
        src.Name                AS source_store,
        dst.StoreID             AS dest_store_id,
        dst.Name                AS dest_store,
        p.Code                  AS part_code,
        p.Name                  AS part_name,
        vi.MajorUnitQuantity    AS qty,
        v.Description           AS voucher_caption
    FROM     LGS3.InventoryVoucher       AS v
    INNER JOIN LGS3.InventoryVoucherItem AS vi  ON vi.InventoryVoucherRef = v.InventoryVoucherID
    INNER JOIN LGS3.Part                 AS p   ON p.PartID               = vi.PartRef
    INNER JOIN LGS3.Store                AS src ON src.StoreID            = vi.StoreRef
    LEFT  JOIN LGS3.Store                AS dst ON dst.StoreID            = v.CounterpartStoreRef
    WHERE   src.StoreID IN (6, 2)
    AND v.DATE >= '2024-01-01'

    UNION ALL

    SELECT
        'OUTGOING',
        v.InventoryVoucherID,
        v.InventoryVoucherSpecificationRef,
        v.Number,
        v.Date,
        src.StoreID,
        src.Name,
        dst.StoreID,
        dst.Name,
        p.Code,
        p.Name,
        vi.MajorUnitQuantity,
        v.Description
    FROM     LGS3.InventoryVoucher       AS v
    INNER JOIN LGS3.InventoryVoucherItem AS vi  ON vi.InventoryVoucherRef = v.InventoryVoucherID
    INNER JOIN LGS3.Part                 AS p   ON p.PartID               = vi.PartRef
    INNER JOIN LGS3.Store                AS src ON src.StoreID            = vi.StoreRef
    LEFT  JOIN LGS3.Store                AS dst ON dst.StoreID            = v.CounterpartStoreRef
    WHERE   src.StoreID IN (17, 5, 13, 18, 16, 3, 10, 15)
    AND v.DATE >= '2024-01-01'

    ORDER BY voucher_date DESC, inventory_voucher_id DESC
""")

# ─────────────────────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────────────────────
CSV_PATH = os.path.abspath("product_voucher.csv")
CHUNK_SIZE = 50_000


# ─────────────────────────────────────────────────────────────
# Step 1 — Stream SQL Server → CSV
# ─────────────────────────────────────────────────────────────
def extract_to_csv() -> int:
    logging.info("📥 Streaming SQL Server → CSV...")
    logging.info(f"   Target CSV: {CSV_PATH}")

    total = 0
    chunk_num = 0
    first_chunk = True

    with SQLSERVER_ENGINE.connect() as conn:
        for chunk in pd.read_sql(QUERY, conn, chunksize=CHUNK_SIZE):
            chunk_num += 1
            chunk.to_csv(
                CSV_PATH,
                mode="w" if first_chunk else "a",
                header=first_chunk,
                index=False,
                encoding="utf-8",
                quoting=1,                    # QUOTE_ALL — safe for Persian + commas
                date_format="%Y-%m-%d %H:%M:%S",
                na_rep="",                    # empty string for NULL
                lineterminator="\n", 
            )
            total += len(chunk)
            first_chunk = False
            logging.info(f"   Chunk {chunk_num}: +{len(chunk):,} rows (total: {total:,})")

    logging.info(f"✅ CSV written: {total:,} rows → {CSV_PATH}")
    return total


# ─────────────────────────────────────────────────────────────
# Step 2 — Load CSV → MySQL with LOAD DATA LOCAL INFILE
# ─────────────────────────────────────────────────────────────
def load_csv_to_mysql() -> None:
    logging.info("📤 Loading CSV → MySQL via LOAD DATA LOCAL INFILE...")

    # MySQL wants forward slashes in the path, even on Windows
    csv_path_sql = CSV_PATH.replace("\\", "/")

    # ─────────────────────────────────────────────
    # DDL — run separately (only needed once)
    # ─────────────────────────────────────────────
    create_table_sql = """
        CREATE TABLE IF NOT EXISTS salesoptimizer.product_voucher (
            id                  INT AUTO_INCREMENT PRIMARY KEY,
            direction           VARCHAR(16)     NOT NULL,
            inventory_voucher_id BIGINT         NOT NULL,
            spec_ref            INT             NULL,
            voucher_no          VARCHAR(64)     NULL,
            voucher_date        DATETIME        NULL,
            source_store_id     BIGINT          NULL,
            source_store        VARCHAR(256)    NULL,
            dest_store_id       BIGINT          NULL,
            dest_store          VARCHAR(256)    NULL,
            part_code           VARCHAR(128)    NOT NULL,
            part_name           VARCHAR(512)    NULL,
            qty                 DECIMAL(28,6)   NULL,
            voucher_caption     VARCHAR(1024)   NULL,
            created_at          TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_part_code      (part_code),
            INDEX idx_voucher_id     (inventory_voucher_id),
            INDEX idx_direction      (direction),
            INDEX idx_spec_ref       (spec_ref),
            INDEX idx_source_store   (source_store_id),
            INDEX idx_dest_store     (dest_store_id),
            INDEX idx_voucher_date   (voucher_date),
            INDEX idx_part_direction (part_code, direction)
        )
        ENGINE=InnoDB
        DEFAULT CHARSET=utf8mb4
        COLLATE=utf8mb4_unicode_ci
    """

    # ─────────────────────────────────────────────
    # LOAD DATA — no semicolon at the end
    # ─────────────────────────────────────────────
    load_sql = f"""
        LOAD DATA LOCAL INFILE '{csv_path_sql}'
        INTO TABLE salesoptimizer.product_voucher
        CHARACTER SET utf8mb4
        FIELDS TERMINATED BY ','
               OPTIONALLY ENCLOSED BY '"'
               ESCAPED BY '"'
        LINES TERMINATED BY '\r\n'
        IGNORE 1 LINES
        (direction, inventory_voucher_id, spec_ref, voucher_no,
         voucher_date, source_store_id, source_store,
         dest_store_id, dest_store, part_code, part_name,
         qty, voucher_caption)
        SET
            inventory_voucher_id = CASE WHEN TRIM(inventory_voucher_id) = '' THEN NULL ELSE inventory_voucher_id END,
            spec_ref             = CASE WHEN TRIM(spec_ref)             = '' THEN NULL ELSE spec_ref             END,
            voucher_no           = CASE WHEN TRIM(voucher_no)           = '' THEN NULL ELSE voucher_no           END,
            voucher_date         = CASE WHEN TRIM(voucher_date)         = '' THEN NULL ELSE voucher_date         END,
            source_store_id      = CASE WHEN TRIM(source_store_id)      = '' THEN NULL ELSE source_store_id      END,
            source_store         = CASE WHEN TRIM(source_store)         = '' THEN NULL ELSE source_store         END,
            dest_store_id        = CASE WHEN TRIM(dest_store_id)        = '' THEN NULL ELSE dest_store_id        END,
            dest_store           = CASE WHEN TRIM(dest_store)           = '' THEN NULL ELSE dest_store           END,
            part_name            = CASE WHEN TRIM(part_name)            = '' THEN NULL ELSE part_name            END,
            qty                  = CASE WHEN TRIM(qty)                  = '' THEN NULL ELSE qty                  END,
            voucher_caption      = CASE WHEN TRIM(voucher_caption)      = '' THEN NULL ELSE voucher_caption      END
    """

    with MYSQL_ENGINE.begin() as conn:
        # 1. Ensure table exists (safe to run every time)
        conn.execute(text(create_table_sql))

        # 2. Clear any existing rows
        logging.info("🧹 TRUNCATE product_voucher")
        conn.execute(text("TRUNCATE TABLE salesoptimizer.product_voucher"))

        # 3. LOAD DATA via raw DBAPI connection
        raw_conn = conn.connection
        cursor = raw_conn.cursor()
        try:
            cursor.execute(load_sql)
            logging.info(f"✅ LOAD DATA affected {cursor.rowcount:,} rows")

            # Show any warnings
            cursor.execute("SHOW WARNINGS")
            warnings = cursor.fetchall()
            if warnings:
                logging.warning(f"⚠️  {len(warnings)} warnings:")
                for w in warnings[:20]:
                    logging.warning(f"   {w}")
            else:
                logging.info("✅ No warnings")
        finally:
            cursor.close()

# ─────────────────────────────────────────────────────────────
# Step 3 — Verify
# ─────────────────────────────────────────────────────────────
def verify() -> None:
    logging.info("🔍 Verifying...")
    with MYSQL_ENGINE.connect() as conn:
        count = conn.execute(
            text("SELECT COUNT(*) FROM salesoptimizer.product_voucher")
        ).scalar()

        by_direction = pd.read_sql(
            text("""
                SELECT direction, COUNT(*) AS cnt, SUM(qty) AS total_qty
                FROM salesoptimizer.product_voucher
                GROUP BY direction
            """),
            conn,
        )

        sample = pd.read_sql(
            text("""
                SELECT direction, inventory_voucher_id, spec_ref, voucher_no,
                       voucher_date, source_store, dest_store, part_code, qty
                FROM salesoptimizer.product_voucher
                ORDER BY id DESC
                LIMIT 10
            """),
            conn,
        )

    logging.info(f"📊 Total rows: {count:,}")
    logging.info(f"📊 By direction:\n{by_direction.to_string(index=False)}")
    logging.info(f"📋 Latest 10 rows:\n{sample.to_string(index=False)}")


# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────
def main():
    started = datetime.now()
    logging.info("=" * 70)
    logging.info("▶️  Fast CSV + LOAD DATA pipeline")
    logging.info(f"   Started: {started:%Y-%m-%d %H:%M:%S}")
    logging.info("=" * 70)

    try:
        total = extract_to_csv()
        load_csv_to_mysql()
        verify()

        # Clean up CSV (optional — keep for debugging)
        # os.remove(CSV_PATH)
        # logging.info(f"🧹 Removed {CSV_PATH}")

    except Exception as e:
        logging.exception(f"❌ Failed: {e}")
        raise

    elapsed = (datetime.now() - started).total_seconds()
    logging.info("=" * 70)
    logging.info(f"✅ Completed in {elapsed:.2f}s")
    logging.info("=" * 70)


if __name__ == "__main__":
    main()