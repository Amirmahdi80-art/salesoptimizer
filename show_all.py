"""
show_all_vouchers.py
--------------------
Shows ALL vouchers for a product code (all spec refs) —
incoming to stores (6,2) and outgoing from the other stores.
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
        logging.FileHandler("show_all_vouchers_log.txt", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

# ─────────────────────────────────────────────────────────────
# SQL Server engine
# ─────────────────────────────────────────────────────────────
ENGINE = create_engine(
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
# Configuration
# ─────────────────────────────────────────────────────────────
PRODUCT_CODE = "9544456901"

# ─────────────────────────────────────────────────────────────
# Query — both directions, ALL spec refs
# ─────────────────────────────────────────────────────────────
QUERY = text(f"""
    SELECT
        'INCOMING'              AS Direction,
        v.InventoryVoucherID,
        v.InventoryVoucherSpecificationRef AS SpecRef,
        v.Number                AS VoucherNo,
        v.Date                  AS VoucherDate,
        src.StoreID             AS SourceStoreID,
        src.Name                AS SourceStore,
        dst.StoreID             AS DestStoreID,
        dst.Name                AS DestStore,
        p.Code                  AS PartCode,
        p.Name                  AS PartName,
        vi.MajorUnitQuantity    AS Qty,
        v.Description           AS VoucherCaption
    FROM     LGS3.InventoryVoucher       AS v
    INNER JOIN LGS3.InventoryVoucherItem AS vi  ON vi.InventoryVoucherRef = v.InventoryVoucherID
    INNER JOIN LGS3.Part                 AS p   ON p.PartID               = vi.PartRef
    INNER JOIN LGS3.Store                AS src ON src.StoreID            = vi.StoreRef
    LEFT  JOIN LGS3.Store                AS dst ON dst.StoreID            = v.CounterpartStoreRef
    WHERE   p.Code LIKE '{PRODUCT_CODE}%'
    AND src.StoreID IN (6, 2)

    UNION ALL

    SELECT
        'OUTGOING'              AS Direction,
        v.InventoryVoucherID,
        v.InventoryVoucherSpecificationRef AS SpecRef,
        v.Number                AS VoucherNo,
        v.Date                  AS VoucherDate,
        src.StoreID             AS SourceStoreID,
        src.Name                AS SourceStore,
        dst.StoreID             AS DestStoreID,
        dst.Name                AS DestStore,
        p.Code                  AS PartCode,
        p.Name                  AS PartName,
        vi.MajorUnitQuantity    AS Qty,
        v.Description           AS VoucherCaption
    FROM     LGS3.InventoryVoucher       AS v
    INNER JOIN LGS3.InventoryVoucherItem AS vi  ON vi.InventoryVoucherRef = v.InventoryVoucherID
    INNER JOIN LGS3.Part                 AS p   ON p.PartID               = vi.PartRef
    INNER JOIN LGS3.Store                AS src ON src.StoreID            = vi.StoreRef
    LEFT  JOIN LGS3.Store                AS dst ON dst.StoreID            = v.CounterpartStoreRef
    WHERE   p.Code LIKE '{PRODUCT_CODE}%'
      AND   src.StoreID IN (17, 5, 13, 18, 16, 3, 10, 15)

    ORDER BY VoucherDate DESC, InventoryVoucherID DESC
""")


def main():
    logging.info("=" * 100)
    logging.info(f"ALL VOUCHERS for product code: {PRODUCT_CODE}")
    logging.info("=" * 100)

    start = datetime.now()
    with ENGINE.connect() as conn:
        df = pd.read_sql(QUERY, conn)
    elapsed = (datetime.now() - start).total_seconds()
    logging.info(f"Fetched {len(df)} rows in {elapsed:.2f}s")

    if df.empty:
        print(f"\n⚠️  No vouchers found for {PRODUCT_CODE}\n")
        return

    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 320)
    pd.set_option("display.max_colwidth", 40)

    # ─────────────────────────────────────────────
    # Group by spec ref to see the composition
    # ─────────────────────────────────────────────
    print("\n── Breakdown by SpecRef and Direction ──\n")
    breakdown = (
        df.groupby(["SpecRef", "Direction"])["Qty"]
        .agg(["count", "sum"])
        .rename(columns={"count": "voucher_rows", "sum": "total_qty"})
        .reset_index()
    )
    print(breakdown.to_string(index=False))

    # ─────────────────────────────────────────────
    # Full table
    # ─────────────────────────────────────────────
    print("\n── All rows ──\n")
    print(df.to_string(index=False))

    # ─────────────────────────────────────────────
    # Save
    # ─────────────────────────────────────────────
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = f"all_vouchers_{PRODUCT_CODE}_{stamp}.csv"
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    logging.info(f"Saved {csv_path}")


if __name__ == "__main__":
    main()