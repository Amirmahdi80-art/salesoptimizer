"""
preview_query.py
----------------
Runs the DISTINCT query on SQL Server and prints the first 10 rows.
Uses the same SQLAlchemy engine setup as your other scripts.
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
        logging.FileHandler("preview_query_log.txt", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

# ─────────────────────────────────────────────────────────────
# SQL Server engine
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
# Query — TOP 10 (SQL Server syntax)
# ─────────────────────────────────────────────────────────────
QUERY = text("""
    SELECT DISTINCT TOP 10
        pa.PartyID,
        pa.FullName,
        s.StoreID,
        s.Name,
        v.InventoryVoucherID,
        v.Number,
        v.Date,
        p.PartID,
        p.Code,
        p.Name AS Expr1,
        p.TechnicalSpecification,
        vi.Additional1 AS tamin,
        vi.MajorUnitQuantity,
        it.Price,
        pri.Fee
    FROM     LGS3.InventoryVoucher       AS v
    INNER JOIN LGS3.InventoryVoucherItem AS vi  ON vi.InventoryVoucherRef = v.InventoryVoucherID
    INNER JOIN LGS3.Part                 AS p   ON p.PartID               = vi.PartRef
    INNER JOIN LGS3.Store                AS s   ON s.StoreID              = vi.StoreRef
    INNER JOIN GNR3.Party                AS pa  ON pa.PartyID             = v.CounterpartEntityRef
    LEFT  OUTER JOIN LGS3.ItemPrice      AS it  ON it.VoucherItemRef      = vi.InventoryVoucherItemID
    LEFT  OUTER JOIN SLS3.Product        AS po  ON po.PartRef             = p.PartID
    LEFT  OUTER JOIN RMS3.PriceListRetailProduct AS pri ON pri.ProductRef = po.ProductID
    WHERE   v.InventoryVoucherSpecificationRef = 2
    AND p.Code = 954445690139
""")


def main():
    started = datetime.now()
    logging.info("=" * 80)
    logging.info("▶️  preview_query.py")
    logging.info(f"   Started: {started:%Y-%m-%d %H:%M:%S}")
    logging.info("=" * 80)

    try:
        logging.info("📥 Running query on SQL Server...")
        with SQLSERVER_ENGINE.connect() as conn:
            df = pd.read_sql(QUERY, conn)

        logging.info(f"✅ Fetched {len(df)} rows")
        logging.info(f"   Columns: {list(df.columns)}")

        # ─────────────────────────────────────────────
        # Display
        # ─────────────────────────────────────────────
        pd.set_option("display.max_columns", None)
        pd.set_option("display.width", 300)
        pd.set_option("display.max_colwidth", 40)

        print("\n" + "=" * 120)
        print(f"PREVIEW — first {len(df)} rows (spec_ref = 2)")
        print("=" * 120)
        print(df.to_string(index=False))
        print("=" * 120)

        # ─────────────────────────────────────────────
        # Row-by-row dump (easier to read for wide tables)
        # ─────────────────────────────────────────────
        print("\n─── Row-by-row detail ───\n")
        for i, row in enumerate(df.to_dict(orient="records"), start=1):
            print(f"─── Row {i} ───")
            for key, value in row.items():
                print(f"  {key:25} : {value}")
            print()

        # ─────────────────────────────────────────────
        # Save to CSV (optional)
        # ─────────────────────────────────────────────
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_path = f"preview_spec2_{stamp}.csv"
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        logging.info(f"💾 Saved preview to {csv_path}")

    except Exception as e:
        logging.exception(f"❌ Failed: {e}")
        raise

    elapsed = (datetime.now() - started).total_seconds()
    logging.info("=" * 80)
    logging.info(f"✅ Completed in {elapsed:.2f}s")
    logging.info("=" * 80)


if __name__ == "__main__":
    main()