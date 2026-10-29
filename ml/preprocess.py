"""
ShopSense - Preprocessing and RFM Feature Engineering
Processes UCI Online Retail Dataset, tracking row exclusions at every step.
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import timedelta
import hashlib

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_RAW = BASE_DIR / "data" / "raw" / "Online Retail.xlsx"
DATA_PROCESSED_DIR = BASE_DIR / "data" / "processed"

def aggregate_rfm(transactions, reference_date):
    """One row per customer; frequency counts invoices, never line items."""
    result = transactions.groupby("CustomerID").agg(
        Recency=("InvoiceDate", lambda dates: (reference_date - dates.max()).days),
        Frequency=("InvoiceNo", "nunique"),
        Monetary=("Revenue", "sum"),
    ).reset_index()
    result["Monetary"] = result["Monetary"].round(2)
    return result

def run_preprocessing():
    DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    print("Step 1: Loading raw dataset from Excel (this may take 20-30s)...")
    df_raw = pd.read_excel(DATA_RAW)
    total_raw_rows = len(df_raw)
    print(f"Raw records loaded: {total_raw_rows:,}")

    # Track exclusions
    audit = {
        "raw_rows": int(total_raw_rows),
        "steps": []
    }
    audit["source"] = "https://archive.ics.uci.edu/dataset/352/online+retail"
    audit["source_sha256"] = hashlib.sha256(DATA_RAW.read_bytes()).hexdigest()

    # Step 1: Missing CustomerID
    missing_cust_mask = df_raw["CustomerID"].isna()
    missing_cust_count = int(missing_cust_mask.sum())
    df_step1 = df_raw[~missing_cust_mask].copy()
    df_step1["CustomerID"] = df_step1["CustomerID"].astype(int)
    audit["steps"].append({
        "step": 1,
        "name": "Missing CustomerID removal",
        "excluded": missing_cust_count,
        "remaining": int(len(df_step1)),
        "description": "Records without an identified customer cannot be attributed to a customer profile."
    })
    print(f"Removed {missing_cust_count:,} records with missing CustomerID -> {len(df_step1):,} remaining")

    # Step 2: Cancelled Invoices (InvoiceNo starts with 'C' or 'c')
    df_step1["InvoiceNo_str"] = df_step1["InvoiceNo"].astype(str)
    cancelled_mask = df_step1["InvoiceNo_str"].str.upper().str.startswith("C")
    cancelled_count = int(cancelled_mask.sum())
    df_step2 = df_step1[~cancelled_mask].copy()
    audit["steps"].append({
        "step": 2,
        "name": "Cancelled transactions removal",
        "excluded": cancelled_count,
        "remaining": int(len(df_step2)),
        "description": "Cancelled orders (invoices prefixed with 'C') represent reversals and returns."
    })
    print(f"Removed {cancelled_count:,} cancelled invoices -> {len(df_step2):,} remaining")

    # Step 3: Invalid sales (Quantity <= 0 or UnitPrice <= 0)
    invalid_sales_mask = (df_step2["Quantity"] <= 0) | (df_step2["UnitPrice"] <= 0)
    invalid_sales_count = int(invalid_sales_mask.sum())
    df_step3 = df_step2[~invalid_sales_mask].copy()
    audit["steps"].append({
        "step": 3,
        "name": "Non-positive Quantity or UnitPrice removal",
        "excluded": invalid_sales_count,
        "remaining": int(len(df_step3)),
        "description": "Non-positive price or quantity is excluded; the reason for these entries is not inferred."
    })
    print(f"Removed {invalid_sales_count:,} records with non-positive values -> {len(df_step3):,} remaining")

    # Step 4: Exact duplicates
    duplicate_mask = df_step3.duplicated(subset=list(df_raw.columns))
    duplicate_count = int(duplicate_mask.sum())
    df_clean = df_step3[~duplicate_mask].copy()
    audit["steps"].append({
        "step": 4,
        "name": "Exact duplicate records removal",
        "excluded": duplicate_count,
        "remaining": int(len(df_clean)),
        "description": "Identical rows across all original columns are removed; their origin is unknown."
    })
    print(f"Removed {duplicate_count:,} exact duplicate rows -> {len(df_clean):,} remaining")

    # Step 5: Revenue calculation
    df_clean["InvoiceDate"] = pd.to_datetime(df_clean["InvoiceDate"])
    df_clean["Revenue"] = (df_clean["Quantity"] * df_clean["UnitPrice"]).round(2)
    df_clean["StockCode"] = df_clean["StockCode"].astype(str)
    df_clean["Description"] = df_clean["Description"].fillna("").astype(str)
    df_clean["Country"] = df_clean["Country"].astype(str)

    total_excluded = total_raw_rows - len(df_clean)
    retention_rate = (len(df_clean) / total_raw_rows) * 100
    audit["total_clean_rows"] = int(len(df_clean))
    audit["total_excluded_rows"] = int(total_excluded)
    audit["retention_rate_pct"] = round(retention_rate, 2)
    audit["min_date"] = str(df_clean["InvoiceDate"].min())
    audit["max_date"] = str(df_clean["InvoiceDate"].max())
    audit["total_revenue_gbp"] = round(float(df_clean["Revenue"].sum()), 2)
    audit["total_orders"] = int(df_clean["InvoiceNo"].nunique())

    # Step 6: Customer-level RFM aggregation
    # Reference Date: exactly 1 day after the latest transaction date in the dataset
    max_date = df_clean["InvoiceDate"].max()
    reference_date = max_date + timedelta(days=1)
    audit["reference_date"] = str(reference_date)

    print(f"Latest transaction date: {max_date}")
    print(f"Fixed reference date for Recency: {reference_date}")

    rfm_df = aggregate_rfm(df_clean, reference_date)

    # Round Monetary to 2 decimal places
    rfm_df["Monetary"] = rfm_df["Monetary"].round(2)
    audit["unique_customers"] = int(len(rfm_df))

    print(f"Aggregated {len(rfm_df):,} unique customers.")
    print("RFM Summary Statistics:")
    print(rfm_df[["Recency", "Frequency", "Monetary"]].describe().T[["mean", "std", "50%", "min", "max"]])

    # Save outputs
    # 1. Cleaned transactions sample/feather/parquet for rapid access
    df_clean.to_parquet(DATA_PROCESSED_DIR / "cleaned_transactions.parquet", index=False)
    # 2. RFM Raw CSV
    rfm_df.to_csv(DATA_PROCESSED_DIR / "rfm_raw.csv", index=False)
    # 3. Preprocessing audit JSON
    with open(DATA_PROCESSED_DIR / "preprocessing_audit.json", "w") as f:
        json.dump(audit, f, indent=2)

    print(f"[SUCCESS] Saved clean dataset and RFM features to {DATA_PROCESSED_DIR}")
    return audit, rfm_df

if __name__ == "__main__":
    run_preprocessing()
