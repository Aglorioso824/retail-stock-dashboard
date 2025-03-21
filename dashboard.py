import os
import streamlit as st
import pandas as pd
from datetime import datetime

# IMPORTANT NOTE:
# 1. Save your new Homer image file (e.g., "homer_image.png") in the same folder as this dashboard.py,
#    or in a subfolder like "images/homer_image.png".
# 2. Update the file path in st.image(...) below to match where you actually placed the file.

# Inject CSS to style the expander widget (center header and light yellow background)
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

# Create two columns: one for the title (centered within its column) and one for the image on the right
col1, col2 = st.columns([0.8, 0.2])

with col1:
    # Centered main title in the first column
    st.markdown("<h1 style='text-align: center;'>Welcome, Retail SumUpper</h1>", unsafe_allow_html=True)

with col2:
    # Display the Homer image on the right (adjust width as desired)
    st.image("homer_image.png", width=100)

# Center the Last Data Upload Date below the title row
if os.path.exists("out_of_stock.csv"):
    last_upload_timestamp = os.path.getmtime("out_of_stock.csv")
    last_upload_date = datetime.fromtimestamp(last_upload_timestamp).strftime("%d/%m/%Y")
    st.markdown(f"<p style='text-align: center;'>Last Data Upload Date: {last_upload_date}</p>", unsafe_allow_html=True)
else:
    st.markdown("<p style='text-align: center;'>No data uploaded yet.</p>", unsafe_allow_html=True)

# File uploader for Excel file
uploaded_file = st.file_uploader("Upload your weekly Excel file (.xlsx)", type="xlsx")

def process_data(df):
    # Check if the required columns are present
    required_columns = {'Retailer', 'SKU', 'Store', 'Quantity'}
    if not required_columns.issubset(df.columns):
        st.error("The file must have the columns: Retailer, SKU, Store, Quantity")
        return None, None, None, None
    
    # Use only the first 5 retailers
    selected_retailers = df['Retailer'].unique()[:5]
    df = df[df['Retailer'].isin(selected_retailers)]
    
    # Out of Stock: stores with 0 units or less (grouped by Retailer and SKU)
    out_of_stock = df[df['Quantity'] <= 0].groupby(['Retailer', 'SKU']).agg(
        number_of_stores=('Store', 'nunique')
    ).reset_index()
    
    # In Stock: stores with 2 or more units (grouped by Retailer and SKU)
    in_stock = df[df['Quantity'] >= 2].groupby(['Retailer', 'SKU']).agg(
        number_of_stores=('Store', 'nunique')
    ).reset_index()
    
    # Critical Stock: stores with exactly 1 unit (grouped by Retailer and SKU)
    critical_stock = df[df['Quantity'] == 1].groupby(['Retailer', 'SKU']).agg(
        number_of_stores=('Store', 'nunique')
    ).reset_index()
    
    return out_of_stock, in_stock, critical_stock, df

# Initialize variables
out_of_stock = None
in_stock = None
critical_stock = None
df = None

# Process uploaded file if available
if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Error reading the Excel file: {e}")
    else:
        out_of_stock, in_stock, critical_stock, df = process_data(df)
        if out_of_stock is not None:
            # Save processed data for persistence
            out_of_stock.to_csv("out_of_stock.csv", index=False)
            in_stock.to_csv("in_stock.csv", index=False)
            critical_stock.to_csv("critical_stock.csv", index=False)
            df.to_csv("raw_data.csv", index=False)
            st.success("Data uploaded and processed successfully!")
else:
    # If no new file is uploaded, try to load existing saved data
    if os.path.exists("raw_data.csv"):
        df = pd.read_csv("raw_data.csv")
    if os.path.exists("out_of_stock.csv"):
        out_of_stock = pd.read_csv("out_of_stock.csv")
    if os.path.exists("in_stock.csv"):
        in_stock = pd.read_csv("in_stock.csv")
    if os.path.exists("critical_stock.csv"):
        critical_stock = pd.read_csv("critical_stock.csv")

# Additional Dashboards (if raw data is available)
if df is not None:
    # Dashboard 1: Total Out of Stock by Retailer (using 🚫 emoji)
    if out_of_stock is not None:
        total_out_of_stock_by_retailer = out_of_stock.groupby('Retailer')['number_of_stores'].sum().reset_index()
    else:
        total_out_of_stock_by_retailer = df[df['Quantity'] <= 0].groupby('Retailer').agg(
            total_out_of_stock=('Store', 'nunique')
        ).reset_index()
    
    st.markdown("<h3 style='text-align: center;'>Total Out of Stock by Retailer 🚫</h3>", unsafe_allow_html=True)
    st.dataframe(total_out_of_stock_by_retailer)
    
    # Create separate expandable widgets for each retailer with out-of-stock stores details
    out_of_stock_details = df[df['Quantity'] <= 0][['Retailer', 'Store', 'SKU']].drop_duplicates().reset_index(drop=True)
    for retailer in out_of_stock_details['Retailer'].unique():
        retailer_details = out_of_stock_details[out_of_stock_details['Retailer'] == retailer]
        with st.expander(f"View {retailer} Out-of-Stock Stores"):
            st.markdown(f"<h3 style='text-align: center;'>{retailer} Out-of-Stock Stores</h3>", unsafe_allow_html=True)
            st.dataframe(retailer_details)
    
    # Dashboard 2: Average Units of Stock per Store
    avg_stock_retailer = df.groupby('Retailer').agg(avg_stock=('Quantity','mean')).reset_index()
    avg_stock_by_sku = df.groupby(['Retailer','SKU']).agg(avg_stock=('Quantity','mean')).reset_index()
    
    st.markdown("<h3 style='text-align: center;'>Average Units of Stock per Store</h3>", unsafe_allow_html=True)
    avg_option = st.radio("Choose display option for average stock:", ("Overall per Retailer", "Breakdown by SKU"))
    if avg_option == "Overall per Retailer":
        st.dataframe(avg_stock_retailer)
    else:
        st.dataframe(avg_stock_by_sku)

# Display Main Dashboards in the desired order:
# 1. Out of Stock
if out_of_stock is not None:
    st.markdown("<h3 style='text-align: center;'>Out of Stock (0 units or less) ❌</h3>", unsafe_allow_html=True)
    st.dataframe(out_of_stock)
    
# 2. Critical Stock (placed below Out of Stock)
if critical_stock is not None:
    st.markdown("<h3 style='text-align: center;'>Critical Stock Levels (1 unit) ⚠️</h3>", unsafe_allow_html=True)
    st.dataframe(critical_stock)
    
# 3. In Stock
if in_stock is not None:
    st.markdown("<h3 style='text-align: center;'>In Stock (2 or more units) ✅</h3>", unsafe_allow_html=True)
    st.dataframe(in_stock)
