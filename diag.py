"""
diagnose_supplier_query.py
--------------------------
Runs step-by-step diagnostics on the supplier query to find
which filter is removing rows.
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
        logging.FileHandler("diagnose_supplier_log.txt", encoding="utf-8"),
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
# Diagnostic queries — step by step
# ─────────────────────────────────────────────────────────────
STEPS = [
    (
        "Step 0 — Baseline (only spec_ref = 2)",
        """
        SELECT COUNT(*) AS cnt
        FROM LGS3.InventoryVoucher v
        INNER JOIN LGS3.InventoryVoucherItem vi ON vi.InventoryVoucherRef = v.InventoryVoucherID
        INNER JOIN LGS3.Part p ON p.PartID = vi.PartRef
        WHERE v.InventoryVoucherSpecificationRef = 2
        """
    ),
    (
        "Step 1 — After Additional1 IS NOT NULL",
        """
        SELECT COUNT(*) AS cnt
        FROM LGS3.InventoryVoucher v
        INNER JOIN LGS3.InventoryVoucherItem vi ON vi.InventoryVoucherRef = v.InventoryVoucherID
        INNER JOIN LGS3.Part p ON p.PartID = vi.PartRef
        WHERE v.InventoryVoucherSpecificationRef = 2
          AND vi.Additional1 IS NOT NULL
        """
    ),
    (
        "Step 2 — After LTRIM(RTRIM(Additional1)) <> ''",
        """
        SELECT COUNT(*) AS cnt
        FROM LGS3.InventoryVoucher v
        INNER JOIN LGS3.InventoryVoucherItem vi ON vi.InventoryVoucherRef = v.InventoryVoucherID
        INNER JOIN LGS3.Part p ON p.PartID = vi.PartRef
        WHERE v.InventoryVoucherSpecificationRef = 2
          AND vi.Additional1 IS NOT NULL
          AND LTRIM(RTRIM(vi.Additional1)) <> ''
        """
    ),
    (
        "Step 3 — After INNER JOIN GNR3.Party",
        """
        SELECT COUNT(*) AS cnt
        FROM LGS3.InventoryVoucher v
        INNER JOIN LGS3.InventoryVoucherItem vi ON vi.InventoryVoucherRef = v.InventoryVoucherID
        INNER JOIN LGS3.Part p ON p.PartID = vi.PartRef
        INNER JOIN GNR3.Party pa ON pa.PartyID = v.CounterpartEntityRef
        WHERE v.InventoryVoucherSpecificationRef = 2
          AND vi.Additional1 IS NOT NULL
          AND LTRIM(RTRIM(vi.Additional1)) <> ''
        """
    ),
    (
        "Step 3b — After LEFT JOIN GNR3.Party (keeps unmatched)",
        """
        SELECT COUNT(*) AS cnt
        FROM LGS3.InventoryVoucher v
        INNER JOIN LGS3.InventoryVoucherItem vi ON vi.InventoryVoucherRef = v.InventoryVoucherID
        INNER JOIN LGS3.Part p ON p.PartID = vi.PartRef
        LEFT JOIN GNR3.Party pa ON pa.PartyID = v.CounterpartEntityRef
        WHERE v.InventoryVoucherSpecificationRef = 2
          AND vi.Additional1 IS NOT NULL
          AND LTRIM(RTRIM(vi.Additional1)) <> ''
        """
    ),
    (
        "Step 4 — Distinct (product_code, Additional1) — no party",
        """
        SELECT COUNT(*) AS cnt
        FROM (
            SELECT DISTINCT
                SUBSTRING(p.Code, 1, LEN(p.Code) - 2) AS product_code,
                vi.Additional1 AS supplier
            FROM LGS3.InventoryVoucher v
            INNER JOIN LGS3.InventoryVoucherItem vi ON vi.InventoryVoucherRef = v.InventoryVoucherID
            INNER JOIN LGS3.Part p ON p.PartID = vi.PartRef
            WHERE v.InventoryVoucherSpecificationRef = 2
              AND vi.Additional1 IS NOT NULL
              AND LTRIM(RTRIM(vi.Additional1)) <> ''
        ) x
        """
    ),
    (
        "Step 5 — Distinct (product_code, FullName) — with party INNER JOIN",
        """
        SELECT COUNT(*) AS cnt
        FROM (
            SELECT DISTINCT
                SUBSTRING(p.Code, 1, LEN(p.Code) - 2) AS product_code,
                pa.FullName AS supplier
            FROM LGS3.InventoryVoucher v
            INNER JOIN LGS3.InventoryVoucherItem vi ON vi.InventoryVoucherRef = v.InventoryVoucherID
            INNER JOIN LGS3.Part p ON p.PartID = vi.PartRef
            INNER JOIN GNR3.Party pa ON pa.PartyID = v.CounterpartEntityRef
            WHERE v.InventoryVoucherSpecificationRef = 2
              AND vi.Additional1 IS NOT NULL
              AND LTRIM(RTRIM(vi.Additional1)) <> ''
        ) x
        """
    ),
    (
        "Step 5b — Distinct (product_code, FullName) — with party LEFT JOIN",
        """
        SELECT COUNT(*) AS cnt
        FROM (
            SELECT DISTINCT
                SUBSTRING(p.Code, 1, LEN(p.Code) - 2) AS product_code,
                pa.FullName AS supplier
            FROM LGS3.InventoryVoucher v
            INNER JOIN LGS3.InventoryVoucherItem vi ON vi.InventoryVoucherRef = v.InventoryVoucherID
            INNER JOIN LGS3.Part p ON p.PartID = vi.PartRef
            LEFT JOIN GNR3.Party pa ON pa.PartyID = v.CounterpartEntityRef
            WHERE v.InventoryVoucherSpecificationRef = 2
              AND vi.Additional1 IS NOT NULL
              AND LTRIM(RTRIM(vi.Additional1)) <> ''
        ) x
        """
    ),
    (
        "Step 6 — How many vouchers have NULL/no matching party?",
        """
        SELECT COUNT(*) AS cnt
        FROM LGS3.InventoryVoucher v
        INNER JOIN LGS3.InventoryVoucherItem vi ON vi.InventoryVoucherRef = v.InventoryVoucherID
        INNER JOIN LGS3.Part p ON p.PartID = vi.PartRef
        LEFT JOIN GNR3.Party pa ON pa.PartyID = v.CounterpartEntityRef
        WHERE v.InventoryVoucherSpecificationRef = 2
          AND pa.PartyID IS NULL
        """
    ),
    (
        "Step 6b — How many have Additional1 NULL or empty?",
        """
        SELECT 
            SUM(CASE WHEN vi.Additional1 IS NULL THEN 1 ELSE 0 END) AS null_additional1,
            SUM(CASE WHEN LTRIM(RTRIM(vi.Additional1)) = '' THEN 1 ELSE 0 END) AS empty_additional1,
            COUNT(*) AS total
        FROM LGS3.InventoryVoucher v
        INNER JOIN LGS3.InventoryVoucherItem vi ON vi.InventoryVoucherRef = v.InventoryVoucherID
        INNER JOIN LGS3.Part p ON p.PartID = vi.PartRef
        WHERE v.InventoryVoucherSpecificationRef = 2
        """
    ),
]


def run_diagnostics() -> None:
    started = datetime.now()
    logging.info("=" * 80)
    logging.info("▶️  diagnose_supplier_query.py")
    logging.info(f"   Started: {started:%Y-%m-%d %H:%M:%S}")
    logging.info("=" * 80)

    results = []
    with SQLSERVER_ENGINE.connect() as conn:
        for label, sql in STEPS:
            logging.info(f"🔍 Running: {label}")
            try:
                with conn.begin():
                    row = conn.execute(text(sql)).fetchone()
                    cnt = row[0] if row else None

                # Some queries return multiple columns
                if len(row) > 1:
                    values = dict(zip(row._fields, row))
                    results.append((label, values))
                    logging.info(f"   → {values}")
                else:
                    results.append((label, cnt))
                    logging.info(f"   → {cnt:,}")
            except Exception as e:
                logging.error(f"   ❌ Failed: {e}")
                results.append((label, f"ERROR: {e}"))

    # ─────────────────────────────────────────────
    # Summary
    # ─────────────────────────────────────────────
    print("\n" + "=" * 100)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 100)
    for label, value in results:
        if isinstance(value, dict):
            print(f"\n{label}")
            for k, v in value.items():
                print(f"    {k:25} : {v:,}" if isinstance(v, int) else f"    {k:25} : {v}")
        else:
            print(f"{label:70} → {value}")
    print("=" * 100)

    # ─────────────────────────────────────────────
    # Analysis
    # ─────────────────────────────────────────────
    print("\n📊 ANALYSIS")
    print("-" * 100)

    # Extract clean numbers
    def get_count(label_substring):
        for lbl, val in results:
            if label_substring in lbl and isinstance(val, int):
                return val
        return None

    baseline = get_count("Step 0")
    after_additional1 = get_count("Step 1")
    after_trim = get_count("Step 2")
    after_inner_party = get_count("Step 3 —")
    after_left_party = get_count("Step 3b")
    distinct_no_party = get_count("Step 4")
    distinct_inner = get_count("Step 5 —")
    distinct_left = get_count("Step 5b")

    if baseline:
        print(f"Baseline (spec_ref=2)               : {baseline:,}")
    if after_additional1:
        print(f"After Additional1 IS NOT NULL       : {after_additional1:,}   (lost {baseline - after_additional1:,})" if baseline else "")
    if after_trim:
        print(f"After trim(Additional1) <> ''       : {after_trim:,}   (lost {after_additional1 - after_trim:,})" if after_additional1 else "")
    if after_inner_party:
        print(f"After INNER JOIN GNR3.Party         : {after_inner_party:,}   (lost {after_trim - after_inner_party:,})" if after_trim else "")
    if after_left_party:
        print(f"After LEFT JOIN GNR3.Party          : {after_left_party:,}")
    if distinct_no_party:
        print(f"Distinct (product, Additional1)     : {distinct_no_party:,}")
    if distinct_inner:
        print(f"Distinct (product, FullName) [INNER]: {distinct_inner:,}")
    if distinct_left:
        print(f"Distinct (product, FullName) [LEFT] : {distinct_left:,}")

    print("\n💡 Interpretation:")
    if baseline and after_inner_party and after_left_party:
        lost_from_inner = after_trim - after_inner_party if after_trim else None
        lost_from_left = after_trim - after_left_party if after_trim else None
        if lost_from_inner and lost_from_inner > 0:
            print(f"   ❗ INNER JOIN GNR3.Party is dropping {lost_from_inner:,} rows.")
            print(f"   ❗ Using LEFT JOIN would preserve those rows.")
        if lost_from_left == 0:
            print(f"   ✅ LEFT JOIN preserves all rows.")
        print(f"   ❗ If your target was 25,197 and you're getting 8,403, the difference is {25197 - 8403:,}.")

    elapsed = (datetime.now() - started).total_seconds()
    logging.info("=" * 80)
    logging.info(f"✅ Completed in {elapsed:.2f}s")
    logging.info("=" * 80)


if __name__ == "__main__":
    run_diagnostics()