"""
populate_product_supplier.py
----------------------------
Reads distinct (product_code, supplier) pairs from SQL Server
and upserts them into MySQL salesoptimizer.product_supplier.
"""

import logging
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
        logging.FileHandler("product_supplier_log.txt", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

# ─────────────────────────────────────────────────────────────
# SQL Server engine (source)
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

# ─────────────────────────────────────────────────────────────
# MySQL engine (destination)
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
# Query — distinct (product_code, supplier)
# ─────────────────────────────────────────────────────────────
QUERY = text("""
    SELECT DISTINCT
        SUBSTRING(p.Code, 1, LEN(p.Code) - 2) AS product_code,
        pa.FullName                        AS supplier
    FROM     LGS3.InventoryVoucher       AS v
    INNER JOIN LGS3.InventoryVoucherItem AS vi  ON vi.InventoryVoucherRef = v.InventoryVoucherID
    INNER JOIN LGS3.Part                 AS p   ON p.PartID               = vi.PartRef
    INNER JOIN GNR3.Party                AS pa  ON pa.PartyID             = v.CounterpartEntityRef
    WHERE   v.InventoryVoucherSpecificationRef = 2
""")


def extract() -> pd.DataFrame:
    """Fetch distinct (product_code, supplier) pairs from SQL Server."""
    logging.info("📥 Reading from SQL Server...")
    with SQLSERVER_ENGINE.connect() as conn:
        df = pd.read_sql(QUERY, conn)

    logging.info(f"✅ Fetched {len(df):,} rows")
    logging.info(f"   Columns: {list(df.columns)}")

    # Normalize column names to match MySQL table
    df = df.rename(columns={
        "product_code": "product_code",
        "supplier":     "supplier",
    })

    # Coerce types
    df["product_code"] = df["product_code"].astype(str).str.strip()
    df["supplier"]     = df["supplier"].astype(str).str.strip()

    # Drop empty rows
    before = len(df)
    df = df[(df["product_code"] != "") & (df["supplier"] != "")]
    after = len(df)
    if before != after:
        logging.warning(f"⚠️  Dropped {before - after} empty rows")

    # Drop duplicates (already DISTINCT in SQL, but defensive)
    df = df.drop_duplicates(subset=["product_code", "supplier"])

    logging.info(f"📊 Final distinct pairs: {len(df):,}")
    logging.info(f"   Unique products : {df['product_code'].nunique():,}")
    logging.info(f"   Unique suppliers: {df['supplier'].nunique():,}")

    return df


def load(df: pd.DataFrame) -> None:
    """Upsert into MySQL."""
    if df.empty:
        logging.warning("⚠️  No rows to load.")
        return

    logging.info("📤 Writing to MySQL salesoptimizer.product_supplier...")

    insert_sql = text("""
        INSERT INTO salesoptimizer.product_supplier (product_code, supplier)
        VALUES (:product_code, :supplier)
        ON DUPLICATE KEY UPDATE
            supplier = VALUES(supplier)
    """)

    with MYSQL_ENGINE.begin() as conn:
        chunk_size = 500
        total = len(df)
        for start in range(0, total, chunk_size):
            chunk = df.iloc[start:start + chunk_size]
            records = chunk.to_dict(orient="records")
            conn.execute(insert_sql, records)
            logging.info(f"   ↳ Upserted rows {start + 1}–{min(start + chunk_size, total)}")

    logging.info(f"✅ Loaded {len(df):,} rows")


def verify() -> None:
    """Verify the load."""
    logging.info("🔍 Verifying...")
    with MYSQL_ENGINE.connect() as conn:
        count = conn.execute(
            text("SELECT COUNT(*) FROM salesoptimizer.product_supplier")
        ).scalar()

        distinct_products = conn.execute(
            text("SELECT COUNT(DISTINCT product_code) FROM salesoptimizer.product_supplier")
        ).scalar()

        distinct_suppliers = conn.execute(
            text("SELECT COUNT(DISTINCT supplier) FROM salesoptimizer.product_supplier")
        ).scalar()

        sample = pd.read_sql(
            text("""
                SELECT product_code, supplier
                FROM salesoptimizer.product_supplier
                ORDER BY id DESC
                LIMIT 10
            """),
            conn,
        )

    logging.info(f"📊 Total rows         : {count:,}")
    logging.info(f"📊 Distinct products  : {distinct_products:,}")
    logging.info(f"📊 Distinct suppliers : {distinct_suppliers:,}")
    logging.info(f"📋 Latest 10 rows:\n{sample.to_string(index=False)}")


def main():
    started = datetime.now()
    logging.info("=" * 70)
    logging.info("▶️  populate_product_supplier.py")
    logging.info(f"   Started: {started:%Y-%m-%d %H:%M:%S}")
    logging.info("=" * 70)

    try:
        df = extract()
        load(df)
        verify()
    except Exception as e:
        logging.exception(f"❌ Failed: {e}")
        raise

    elapsed = (datetime.now() - started).total_seconds()
    logging.info("=" * 70)
    logging.info(f"✅ Completed in {elapsed:.2f}s")
    logging.info("=" * 70)


if __name__ == "__main__":
    main()