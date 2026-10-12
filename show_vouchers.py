"""
show_vouchers.py
----------------
Shows all vouchers (spec 68) for a specific product code
from both directions:
  - INCOMING: src in (6,2)       → dst in (17,5,13,18,16,3,10,15)
  - OUTGOING: src in (17,5,13,18,16,3,10,15) → dst in (6,2,5,12)
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
        logging.FileHandler("show_vouchers_log.txt", encoding="utf-8"),
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
PRODUCT_CODE = "2329726901"   # <-- change to whatever you want
TOP_N        = 500
SPEC_REF     = 17

# ─────────────────────────────────────────────────────────────
# Query 1 — INCOMING (goods arriving at destination stores)
# ─────────────────────────────────────────────────────────────
INCOMING_QUERY = text(f"""
    SELECT TOP {TOP_N}
        'INCOMING'              AS Direction,
        v.InventoryVoucherID,
        v.Number                AS VoucherNo,
        v.Date                  AS VoucherDate,
        src.StoreID             AS SourceStoreID,
        src.Name                AS SourceStore,
        dst.StoreID             AS DestStoreID,
        dst.Name                AS DestStore,
        p.Code                  AS PartCode,
        p.Name                  AS PartName,
        vi.MajorUnitQuantity    AS Qty
    FROM     LGS3.InventoryVoucher       AS v
    INNER JOIN LGS3.InventoryVoucherItem AS vi  ON vi.InventoryVoucherRef = v.InventoryVoucherID
    INNER JOIN LGS3.Part                 AS p   ON p.PartID               = vi.PartRef
    INNER JOIN LGS3.Store                AS src ON src.StoreID            = vi.StoreRef
    LEFT  JOIN LGS3.Store                AS dst ON dst.StoreID            = v.CounterpartStoreRef
    WHERE   v.InventoryVoucherSpecificationRef = {SPEC_REF}
      AND   src.StoreID IN (6, 2)
      AND   dst.StoreID IN (17, 5, 13, 18, 16, 3, 10, 15)
      AND   p.Code LIKE '{PRODUCT_CODE}%'
    ORDER BY v.InventoryVoucherID DESC, vi.RowNumber
""")

# ─────────────────────────────────────────────────────────────
# Query 2 — OUTGOING (goods leaving source stores)
# ─────────────────────────────────────────────────────────────
OUTGOING_QUERY = text(f"""
    SELECT TOP {TOP_N}
        'OUTGOING'              AS Direction,
        v.InventoryVoucherID,
        v.Number                AS VoucherNo,
        v.Date                  AS VoucherDate,
        src.StoreID             AS SourceStoreID,
        src.Name                AS SourceStore,
        dst.StoreID             AS DestStoreID,
        dst.Name                AS DestStore,
        p.Code                  AS PartCode,
        p.Name                  AS PartName,
        vi.MajorUnitQuantity    AS Qty
    FROM     LGS3.InventoryVoucher       AS v
    INNER JOIN LGS3.InventoryVoucherItem AS vi  ON vi.InventoryVoucherRef = v.InventoryVoucherID
    INNER JOIN LGS3.Part                 AS p   ON p.PartID               = vi.PartRef
    INNER JOIN LGS3.Store                AS src ON src.StoreID            = vi.StoreRef
    LEFT  JOIN LGS3.Store                AS dst ON dst.StoreID            = v.CounterpartStoreRef
    WHERE   v.InventoryVoucherSpecificationRef = {SPEC_REF}
      AND   src.StoreID IN (17, 5, 13, 18, 16, 3, 10, 15)
      AND   dst.StoreID IN (6, 2, 5, 12)
      AND   p.Code LIKE '{PRODUCT_CODE}%'
    ORDER BY v.InventoryVoucherID DESC, vi.RowNumber
""")


def fetch(query: text, label: str) -> pd.DataFrame:
    logging.info(f"Running {label} query...")
    start = datetime.now()
    with ENGINE.connect() as conn:
        df = pd.read_sql(query, conn)
    elapsed = (datetime.now() - start).total_seconds()
    logging.info(f"  → {len(df)} rows in {elapsed:.2f}s")
    return df


def main():
    logging.info("=" * 70)
    logging.info(f"Product code: {PRODUCT_CODE}")
    logging.info("=" * 70)

    incoming = fetch(INCOMING_QUERY, "INCOMING")
    outgoing = fetch(OUTGOING_QUERY, "OUTGOING")

    # ─────────────────────────────────────────────
    # Combine
    # ─────────────────────────────────────────────
    combined = pd.concat([incoming, outgoing], ignore_index=True)

    if combined.empty:
        print(f"\n⚠️  No vouchers found for product code {PRODUCT_CODE}.\n")
        return

    # Sort by direction then by voucher date
    combined = combined.sort_values(
        by=["Direction", "VoucherDate", "InventoryVoucherID"],
        ascending=[True, False, False],
    ).reset_index(drop=True)

    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 300)
    pd.set_option("display.max_colwidth", 40)

    print("\n" + "=" * 130)
    print(f"ALL VOUCHERS — Product Code: {PRODUCT_CODE}")
    print(f"Total rows: {len(combined)}  (INCOMING: {len(incoming)}, OUTGOING: {len(outgoing)})")
    print("=" * 130)

    print("\n── INCOMING (goods arriving at destination stores) ──\n")
    if incoming.empty:
        print("  (none)")
    else:
        print(incoming.to_string(index=False))

    print("\n── OUTGOING (goods leaving source stores) ──\n")
    if outgoing.empty:
        print("  (none)")
    else:
        print(outgoing.to_string(index=False))

    # ─────────────────────────────────────────────
    # Summary by store
    # ─────────────────────────────────────────────
    print("\n" + "=" * 130)
    print("SUMMARY BY STORE")
    print("=" * 130)

    # Incoming per destination store
    inc_summary = (
        incoming.groupby(["DestStoreID", "DestStore"], dropna=False)["Qty"]
        .sum()
        .reset_index()
        .rename(columns={"Qty": "IncomingQty"})
    )
    # Outgoing per source store
    out_summary = (
        outgoing.groupby(["SourceStoreID", "SourceStore"], dropna=False)["Qty"]
        .sum()
        .reset_index()
        .rename(columns={"Qty": "OutgoingQty"})
    )

    print("\nINCOMING by destination store:")
    print(inc_summary.to_string(index=False))

    print("\nOUTGOING by source store:")
    print(out_summary.to_string(index=False))

    # ─────────────────────────────────────────────
    # Save to CSV
    # ─────────────────────────────────────────────
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = f"vouchers_{PRODUCT_CODE}_{stamp}.csv"
    combined.to_csv(csv_path, index=False, encoding="utf-8-sig")
    logging.info(f"Saved {csv_path}")


if __name__ == "__main__":
    main()