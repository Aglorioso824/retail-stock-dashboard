import streamlit as st
import pandas as pd
import boto3
import re
from datetime import datetime, timezone
from io import BytesIO
import os

from config import IGNORED_STORES, SKU_MAPPING, IGNORED_SKUS, TOTAL_LISTINGS

# ------------------------------------------------------------------------
# 1. S3 setup
# ------------------------------------------------------------------------
BUCKET_NAME = "my-retail-uploads"
s3_client = boto3.client(
    "s3",
    aws_access_key_id=st.secrets["aws"]["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=st.secrets["aws"]["AWS_SECRET_ACCESS_KEY"],
)

def upload_to_s3(buf, fname):
    s3_client.upload_fileobj(buf, BUCKET_NAME, fname)
    st.success(f"Uploaded {fname} to S3")

def get_latest_file_from_s3(bucket_name: str, prefix: str = "weekly-report-") -> str | None:
    paginator = s3_client.get_paginator("list_objects_v2")
    pages = paginator.paginate(Bucket=bucket_name, Prefix=prefix)

    latest_key = None
    latest_time = datetime(1970, 1, 1, tzinfo=timezone.utc)
    pattern = re.compile(rf"^{re.escape(prefix)}\d{{8}}-\d{{6}}.*\.xlsx$")

    for page in pages:
        for obj in page.get("Contents", []):
            key = obj["Key"]; lm = obj["LastModified"]
            if not pattern.match(key): continue
            if lm > latest_time:
                latest_time, latest_key = lm, key

    return latest_key

def download_from_s3(bucket, key):
    buf = BytesIO()
    s3_client.download_fileobj(bucket, key, buf)
    buf.seek(0)
    return buf

# ------------------------------------------------------------------------
# 2. UI styling
# ------------------------------------------------------------------------
st.markdown("""
<style>
[data-testid="stExpander"] > div:first-child > div > button {
  background-color: #ffffe0 !important;
  text-align: center !important;
  width: 100%;
}
[data-testid="stExpander"] > div:nth-child(2) {
  background-color: #ffffe0 !important;
}
</style>
""", unsafe_allow_html=True)

col1, col2 = st.columns([0.8, 0.2])
with col1:
    st.markdown("<h1 style='text-align: center;'>Welcome, Retail SumUpper</h1>", unsafe_allow_html=True)
with col2:
    st.image("homerbook.png", width=100)

# ------------------------------------------------------------------------
# 3. Last upload date
# ------------------------------------------------------------------------
if os.path.exists("out_of_stock.csv"):
    ts = os.path.getmtime("out_of_stock.csv")
    date = datetime.fromtimestamp(ts).strftime("%d/%m/%Y")
    st.markdown(f"<p style='text-align: center;'>Last Data Upload Date: {date}</p>",
                unsafe_allow_html=True)
else:
    st.markdown("<p style='text-align: center;'>No data uploaded yet.</p>",
                unsafe_allow_html=True)

# ------------------------------------------------------------------------
# Helpers: apply SKU rules, filter stores
# ------------------------------------------------------------------------
def apply_sku_rules(df: pd.DataFrame) -> pd.DataFrame:
    df['SKU'] = df['SKU'].map(lambda s: SKU_MAPPING.get(s, s))
    if IGNORED_SKUS:
        df = df[~df['SKU'].isin(IGNORED_SKUS)]
    return df

def filter_ignored_stores(df: pd.DataFrame) -> pd.DataFrame:
    df['Store'] = df['Store'].astype(str).str.strip().str.upper()
    ignored = [s.strip().upper() for s in IGNORED_STORES]
    return df[~df['Store'].isin(ignored)]

# ------------------------------------------------------------------------
# 4. File upload & process
# ------------------------------------------------------------------------
uploaded_file = st.file_uploader("Upload your weekly Excel file (.xlsx)", type="xlsx")

def process_data(df: pd.DataFrame):
    df = apply_sku_rules(df)
    df = filter_ignored_stores(df)

    required = {'Retailer', 'SKU', 'Store', 'Quantity'}
    if not required.issubset(df.columns):
        st.error("File must have Retailer, SKU, Store, Quantity")
        return None, None, None, None

    retailers = df['Retailer'].unique()[:5]
    df = df[df['Retailer'].isin(retailers)]

    out = (
        df[df['Quantity'] <= 0]
          .groupby(['Retailer', 'SKU'])
          .agg(number_of_stores=('Store','nunique'))
          .reset_index()
          .rename(columns={'number_of_stores':'Number of Stores'})
    )
    inc = (
        df[df['Quantity'] >= 2]
          .groupby(['Retailer', 'SKU'])
          .agg(number_of_stores=('Store','nunique'))
          .reset_index()
          .rename(columns={'number_of_stores':'Number of Stores'})
    )
    crit = (
        df[df['Quantity'] == 1]
          .groupby(['Retailer', 'SKU'])
          .agg(number_of_stores=('Store','nunique'))
          .reset_index()
          .rename(columns={'number_of_stores':'Number of Stores'})
    )
    return out, inc, crit, df

out_of_stock = in_stock = critical_stock = df = None

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, engine="openpyxl")
    except Exception as e:
        st.error(f"Error reading Excel: {e}")
    else:
        uploaded_file.seek(0)
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        fname = f"weekly-report-{ts}.xlsx"
        upload_to_s3(uploaded_file, fname)
        out_of_stock, in_stock, critical_stock, df = process_data(df)
        if out_of_stock is not None:
            out_of_stock.to_csv("out_of_stock.csv", index=False)
            in_stock.to_csv("in_stock.csv", index=False)
            critical_stock.to_csv("critical_stock.csv", index=False)
            df.to_csv("raw_data.csv", index=False)
            st.success("Data uploaded and processed successfully!")
else:
    if os.path.exists("raw_data.csv"):
        df = pd.read_csv("raw_data.csv")
        out_of_stock, in_stock, critical_stock, df = process_data(df)

# ------------------------------------------------------------------------
# 5. Load Latest from S3 AND re-process dashboards
# ------------------------------------------------------------------------
if st.button("Load Latest Report from S3"):
    latest_key = get_latest_file_from_s3(BUCKET_NAME)
    if not latest_key:
        st.warning("No files found in S3!")
    else:
        buf = download_from_s3(BUCKET_NAME, latest_key)
        st.write(f"✅ Loaded `{latest_key}` from S3")
        try:
            new_df = pd.read_excel(buf, engine="openpyxl")
            new_df = apply_sku_rules(new_df)
            new_df = filter_ignored_stores(new_df)
            out_of_stock, in_stock, critical_stock, df = process_data(new_df)
            out_of_stock.to_csv("out_of_stock.csv", index=False)
            in_stock.to_csv("in_stock.csv", index=False)
            critical_stock.to_csv("critical_stock.csv", index=False)
            df.to_csv("raw_data.csv", index=False)
            st.success("Dashboard refreshed with latest S3 report!")
        except Exception as e:
            st.error(f"Error processing latest S3 report: {e}")

# ------------------------------------------------------------------------
# 6. Dashboards
# ------------------------------------------------------------------------
from config import TOTAL_LISTINGS
import pandas as pd

if df is not None:
    # 1) Out-of-stock summary
    summary = (
        out_of_stock
            .groupby('Retailer')["Number of Stores"]
            .sum()
            .reset_index(name='Number of Situations')
    )

    # 2) Warn about any retailers missing from your TOTAL_LISTINGS dict
    missing = set(summary['Retailer']) - set(TOTAL_LISTINGS.keys())
    if missing:
        st.warning(f"Missing total‐listing counts for: {', '.join(missing)}")

    # 3) Build a DataFrame of full listing counts from config
    total_listings = (
        pd.DataFrame.from_dict(TOTAL_LISTINGS, orient='index', columns=['Total Listings'])
            .reset_index()
            .rename(columns={'index': 'Retailer'})
    )

    # 4) Merge with summary and calculate percentage rate
    summary_rate = (
        summary
            .merge(total_listings, on='Retailer', how='left')
            .assign(**{
                'Out of Stock Rate (%)':
                    lambda d: (d['Number of Situations'] / d['Total Listings'] * 100).round(1)
            })
    )

    # 5) Display the new rate table
    st.markdown(
        "<h3 style='text-align: center;'>Out of Stock Situation Rate 📊</h3>",
        unsafe_allow_html=True
    )
    st.dataframe(summary_rate)

    # Detailed per-store views
    details = df[df['Quantity'] <= 0][['Retailer', 'Store', 'SKU']]
    for r in details['Retailer'].unique():
        with st.expander(f"View {r} Out-of-Stock Stores"):
            st.dataframe(details[details['Retailer'] == r])

    # --- Centered “What is a Situation? 🤓” expander just above the Average section ---
    cols = st.columns([1, 1, 1])
    with cols[1]:
        with st.expander("What is a Situation? 🤓"):
            st.write(
                "An Out of Stock Situation is when any SKU is out of stock. "
                "It does not refer to the number of stores. For example, there could "
                "be 1× out of stock store, with 2× out of stock situations in it "
                "(e.g., POS Lite and Air)."
            )

    # Average stock tables
    st.markdown("<h3 style='text-align: center;'>Average Units of Stock per Store</h3>",
                unsafe_allow_html=True)
    avg_sku = (
        df.groupby(['Retailer', 'SKU'])
            .agg(avg_stock=('Quantity','mean'))
            .reset_index()
    )
    sum_avg = (
        avg_sku.groupby('Retailer')['avg_stock']
               .sum()
               .reset_index(name='sum_of_avg_stock')
    )
    avg_sku['avg_stock'] = avg_sku['avg_stock'].round(1)
    sum_avg['sum_of_avg_stock'] = sum_avg['sum_of_avg_stock'].round(1)

    choice = st.radio("Display:", ("Overall per Retailer", "Breakdown by SKU"))
    if choice == "Overall per Retailer":
        st.dataframe(sum_avg)
    else:
        st.dataframe(avg_sku)

    # Final breakdowns
    st.markdown("<h3 style='text-align: center;'>Out of Stock (0 units or less) ❌</h3>",
                unsafe_allow_html=True)
    st.dataframe(out_of_stock)
    st.markdown("<h3 style='text-align: center;'>Critical Stock Levels (1 unit) ⚠️</h3>",
                unsafe_allow_html=True)
    st.dataframe(critical_stock)
    st.markdown("<h3 style='text-align: center;'>In Stock (2 or more units) ✅</h3>",
                unsafe_allow_html=True)
    st.dataframe(in_stock)
