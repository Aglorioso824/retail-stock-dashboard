import streamlit as st
import pandas as pd
import boto3
from datetime import datetime
from io import BytesIO
import os

# ------------------------------------------------------------------------
# 1. Set up your S3 information
# ------------------------------------------------------------------------
BUCKET_NAME = "my-retail-uploads"

s3_client = boto3.client(
    "s3",
    aws_access_key_id=st.secrets["aws"]["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=st.secrets["aws"]["AWS_SECRET_ACCESS_KEY"]
)

def upload_to_s3(file_buffer, filename):
    s3_client.upload_fileobj(file_buffer, BUCKET_NAME, filename)
    st.success(f"Uploaded {filename} to S3")

def get_latest_file_from_s3(bucket_name):
    resp = s3_client.list_objects_v2(Bucket=bucket_name)
    if "Contents" not in resp:
        return None
    objs = sorted(resp["Contents"], key=lambda x: x["LastModified"], reverse=True)
    return objs[0]["Key"]

def download_from_s3(bucket_name, key):
    buf = BytesIO()
    s3_client.download_fileobj(bucket_name, key, buf)
    buf.seek(0)
    return buf

# ------------------------------------------------------------------------
# 2. UI: Title, Image, and CSS
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
    st.markdown(
        "<h1 style='text-align: center;'>Welcome, Retail SumUpper</h1>",
        unsafe_allow_html=True
    )
with col2:
    st.image("homerbook.png", width=100)

# ------------------------------------------------------------------------
# 3. Last Data Upload Date
# ------------------------------------------------------------------------
if os.path.exists("out_of_stock.csv"):
    ts = os.path.getmtime("out_of_stock.csv")
    date = datetime.fromtimestamp(ts).strftime("%d/%m/%Y")
    st.markdown(
        f"<p style='text-align: center;'>Last Data Upload Date: {date}</p>",
        unsafe_allow_html=True
    )
else:
    st.markdown(
        "<p style='text-align: center;'>No data uploaded yet.</p>",
        unsafe_allow_html=True
    )

# ------------------------------------------------------------------------
# 4. File Uploader & S3 Upload
# ------------------------------------------------------------------------
uploaded_file = st.file_uploader("Upload your weekly Excel file (.xlsx)", type="xlsx")

def process_data(df):
    required = {'Retailer', 'SKU', 'Store', 'Quantity'}
    if not required.issubset(df.columns):
        st.error("The file must have the columns: Retailer, SKU, Store, Quantity")
        return None, None, None, None

    # Filter first 5 retailers
    retailers = df['Retailer'].unique()[:5]
    df = df[df['Retailer'].isin(retailers)]

    # Out-of-stock
    out_of_stock = (
        df[df['Quantity'] <= 0]
          .groupby(['Retailer', 'SKU'])
          .agg(number_of_stores=('Store', 'nunique'))
          .reset_index()
          .rename(columns={'number_of_stores': 'Number of Stores'})
    )
    # In-stock
    in_stock = (
        df[df['Quantity'] >= 2]
          .groupby(['Retailer', 'SKU'])
          .agg(number_of_stores=('Store', 'nunique'))
          .reset_index()
          .rename(columns={'number_of_stores': 'Number of Stores'})
    )
    # Critical (1 unit)
    critical_stock = (
        df[df['Quantity'] == 1]
          .groupby(['Retailer', 'SKU'])
          .agg(number_of_stores=('Store', 'nunique'))
          .reset_index()
          .rename(columns={'number_of_stores': 'Number of Stores'})
    )

    return out_of_stock, in_stock, critical_stock, df

out_of_stock = in_stock = critical_stock = df = None

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file, engine="openpyxl")
    except Exception as e:
        st.error(f"Error reading the Excel file: {e}")
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
    if os.path.exists("out_of_stock.csv"):
        out_of_stock = pd.read_csv("out_of_stock.csv")
    if os.path.exists("in_stock.csv"):
        in_stock = pd.read_csv("in_stock.csv")
    if os.path.exists("critical_stock.csv"):
        critical_stock = pd.read_csv("critical_stock.csv")

# ------------------------------------------------------------------------
# 5. Load Latest from S3 (Debugging)
# ------------------------------------------------------------------------
if st.button("Load Latest Report from S3"):
    key = get_latest_file_from_s3(BUCKET_NAME)
    if key:
        st.write(f"Loading latest file from S3: {key}")
        buf = download_from_s3(BUCKET_NAME, key)
        content = buf.getvalue()
        st.write("File size (bytes):", len(content))

        # Optional: save temp file for inspection
        with open("temp_download.xlsx", "wb") as f:
            f.write(content)
        st.write("Saved temp_download.xlsx for inspection.")

        try:
            new_df = pd.read_excel(buf, engine="openpyxl")
            st.dataframe(new_df.head())
        except Exception as e:
            st.error(f"Error reading Excel file: {e}")
            st.write("First 500 bytes:", content[:500])
    else:
        st.warning("No files found in S3!")

# ------------------------------------------------------------------------
# 6. Dashboards (Local Data + Rounded Averages)
# ------------------------------------------------------------------------
if df is not None:
    # Out-of-Stock Summary by Retailer
    if out_of_stock is not None:
        out_of_stock_by_retailer = (
            out_of_stock.groupby('Retailer')['Number of Stores']
            .sum()
            .reset_index(name='Number of Situations')
        )
    else:
        out_of_stock_by_retailer = (
            df[df['Quantity'] <= 0]
              .groupby('Retailer')
              .agg(total_out_of_stock=('Store', 'nunique'))
              .reset_index()
        )
        out_of_stock_by_retailer = out_of_stock_by_retailer.rename(
            columns={'total_out_of_stock': 'Number of Situations'}
        )

    st.markdown("<h3 style='text-align: center;'>Out of Stock Situations (by Retailer)</h3>",
                unsafe_allow_html=True)
    st.dataframe(out_of_stock_by_retailer)

    # Detailed Out-of-Stock
    details = (
        df[df['Quantity'] <= 0][['Retailer', 'Store', 'SKU']]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    for r in details['Retailer'].unique():
        with st.expander(f"View {r} Out-of-Stock Stores"):
            st.dataframe(details[details['Retailer'] == r])

    # Average Units per SKU & Sum-of-Averages
    avg_stock_by_sku = (
        df.groupby(['Retailer', 'SKU'])
          .agg(avg_stock=('Quantity', 'mean'))
          .reset_index()
    )
    sum_of_avg = (
        avg_stock_by_sku.groupby('Retailer')['avg_stock']
        .sum()
        .reset_index(name='sum_of_avg_stock')
    )

    # Round to 1 decimal
    avg_stock_by_sku['avg_stock'] = avg_stock_by_sku['avg_stock'].round(1)
    sum_of_avg['sum_of_avg_stock'] = sum_of_avg['sum_of_avg_stock'].round(1)

    st.markdown("<h3 style='text-align: center;'>Average Units of Stock per Store</h3>",
                unsafe_allow_html=True)
    choice = st.radio("Choose display option for average stock:",
                      ("Overall per Retailer", "Breakdown by SKU"))
    if choice == "Overall per Retailer":
        st.dataframe(sum_of_avg)
    else:
        st.dataframe(avg_stock_by_sku)

    # Other Dashboards
    if out_of_stock is not None:
        st.markdown("<h3 style='text-align: center;'>Out of Stock (0 units or less) ❌</h3>",
                    unsafe_allow_html=True)
        st.dataframe(out_of_stock)
    if critical_stock is not None:
        st.markdown("<h3 style='text-align: center;'>Critical Stock Levels (1 unit) ⚠️</h3>",
                    unsafe_allow_html=True)
        st.dataframe(critical_stock)
    if in_stock is not None:
        st.markdown("<h3 style='text-align: center;'>In Stock (2 or more units) ✅</h3>",
                    unsafe_allow_html=True)
        st.dataframe(in_stock)
