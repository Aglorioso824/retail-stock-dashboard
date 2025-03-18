import os
import streamlit as st
import pandas as pd

# Title of the dashboard
st.title("Welcome, Retail SumUpper")

# Create a file uploader widget to upload an Excel file
uploaded_file = st.file_uploader("Upload your weekly Excel file (.xlsx)", type="xlsx")

# Function to process the uploaded data
def process_data(df):
    # Check that the file has all the columns we need
    required_columns = {'Retailer', 'SKU', 'Store', 'Quantity'}
    if not required_columns.issubset(df.columns):
        st.error("The file must have the columns: Retailer, SKU, Store, Quantity")
        return None, None, None
    
    # Choose only the first 5 retailers
    selected_retailers = df['Retailer'].unique()[:5]
    df = df[df['Retailer'].isin(selected_retailers)]
    
    # Table 1: Out of Stock (0 units or less)
    out_of_stock = df[df['Quantity'] <= 0].groupby(['Retailer', 'SKU']).agg(
        number_of_stores=('Store', 'nunique')
    ).reset_index()
    
    # Table 2: In Stock (2 or more units)
    in_stock = df[df['Quantity'] >= 2].groupby(['Retailer', 'SKU']).agg(
        number_of_stores=('Store', 'nunique')
    ).reset_index()
    
    # Table 3: Critical Stock Levels (exactly 1 unit)
    critical_stock = df[df['Quantity'] == 1].groupby(['Retailer', 'SKU']).agg(
        number_of_stores=('Store', 'nunique')
    ).reset_index()
    
    return out_of_stock, in_stock, critical_stock

# Check if a new file has been uploaded
if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Error reading the Excel file: {e}")
    else:
        # Process the uploaded file to get the three tables
        out_of_stock, in_stock, critical_stock = process_data(df)
        if out_of_stock is not None:
            # Save the processed data to CSV files so it can be loaded later
            out_of_stock.to_csv("out_of_stock.csv", index=False)
            in_stock.to_csv("in_stock.csv", index=False)
            critical_stock.to_csv("critical_stock.csv", index=False)
else:
    # If no new file is uploaded, check if we already saved CSV files before
    if os.path.exists("out_of_stock.csv") and os.path.exists("in_stock.csv") and os.path.exists("critical_stock.csv"):
        out_of_stock = pd.read_csv("out_of_stock.csv")
        in_stock = pd.read_csv("in_stock.csv")
        critical_stock = pd.read_csv("critical_stock.csv")
    else:
        st.info("No data uploaded yet. Please upload a data sheet.")

# Display the tables if they exist
if 'out_of_stock' in locals() and out_of_stock is not None:
    st.subheader("Out of Stock (0 units or less)")
    st.dataframe(out_of_stock)

if 'in_stock' in locals() and in_stock is not None:
    st.subheader("In Stock (2 or more units)")
    st.dataframe(in_stock)

if 'critical_stock' in locals() and critical_stock is not None:
    st.subheader("Critical Stock Levels (1 unit)")
    st.dataframe(critical_stock)
