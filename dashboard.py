import streamlit as st
import pandas as pd

st.title("Welcome, Retail SumUpper")

# File uploader for the weekly Excel file
uploaded_file = st.file_uploader("Upload your weekly Excel file (.xlsx)", type="xlsx")

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Error reading the Excel file: {e}")
    
    st.write("### Data Preview")
    st.dataframe(df.head())

    # Ensure the file contains the necessary columns
    required_columns = {'Retailer', 'SKU', 'Store', 'Quantity'}
    if required_columns.issubset(df.columns):
        
        # If you have more than 5 retailers and want to limit to 5,
        # you can filter the dataset. For example, if you want the first 5 unique retailers:
        selected_retailers = df['Retailer'].unique()[:5]
        df = df[df['Retailer'].isin(selected_retailers)]
        
        # Out of Stock: stores with 0 units or less
        out_of_stock = df[df['Quantity'] <= 0].groupby(['Retailer', 'SKU']).agg(
            number_of_stores=('Store', 'nunique')
        ).reset_index()
        
        # In Stock: stores with 2 or more units
        in_stock = df[df['Quantity'] >= 2].groupby(['Retailer', 'SKU']).agg(
            number_of_stores=('Store', 'nunique')
        ).reset_index()
        
        # Critical Stock Levels: stores with exactly 1 unit
        critical_stock = df[df['Quantity'] == 1].groupby(['Retailer', 'SKU']).agg(
            number_of_stores=('Store', 'nunique')
        ).reset_index()
        
        # Display the three tables on the dashboard
        
        st.subheader("Out of Stock (0 units or less)")
        st.dataframe(out_of_stock)
        
        st.subheader("In Stock (2 units or more)")
        st.dataframe(in_stock)
        
        st.subheader("Critical Stock Levels (1 unit)")
        st.dataframe(critical_stock)
        
    else:
        st.error(f"The uploaded file must contain the following columns: {', '.join(required_columns)}")
