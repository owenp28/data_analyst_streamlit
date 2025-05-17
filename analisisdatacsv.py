import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Load dataset
@st.cache_data
def load_data():
    script_dir = os.getcwd()  
    # Construct the full path to the CSV file
    file_path = os.path.join(script_dir, 'PRSA_Data_Wanliu_20130301-20170228.csv')
    # Use the full path when reading the file
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError:
        st.error(f"File not found: {file_path}. Please ensure the file exists in the specified directory.")
        return pd.DataFrame()  # Return an empty DataFrame if the file is not found

# Call the function to load the data
data = load_data()

# Tambahkan kolom Date jika tidak ada
if 'Date' not in data.columns:
    data['Date'] = pd.date_range(start='2013-03-01', periods=len(data), freq='h')

# Konversi kolom datetime dengan format yang ditentukan
date_columns = ['Date']  
for col in date_columns:
    data[col] = pd.to_datetime(data[col], format='%Y-%m-%d %H:%M:%S')

# Sidebar Navigation
with st.sidebar:
    selected = option_menu(
        'Fitur Analysis',
        ['Gathering Data', 'Assessing Data', 'Cleaning Data', 
         'Exploratory Data Analysis (EDA)', 'Visualization & Explanatory Analysis'],
        default_index=0
    )

# Title and Description
st.title("Data Analysis App")
st.markdown("""
    ### Features:
    - **Gathering Data**: View dataset.
    - **Assessing Data**: Summary statistics and missing values.
    - **Cleaning Data**: Handle missing values.
    - **Exploratory Data Analysis (EDA)**: Visualize and explore relationships.
    - **Visualization & Explanatory Analysis**: Interactive charts.
""")

# Main application logic
if data is not None:
    # Gathering Data
    if selected == 'Gathering Data':
        st.subheader("1. Gathering Data")
        st.write("Sample Data:")
        st.dataframe(data.head())

    # Assessing Data
    elif selected == 'Assessing Data':
        st.subheader("2. Assessing Data")
        st.write("Summary Statistics:")
        st.write(data.describe())
        st.write("Missing Values:")
        st.write(data.isnull().sum())

    # Cleaning Data
    elif selected == 'Cleaning Data':
        st.subheader("3. Cleaning Data")
        missing_values_handling = st.radio(
            "Choose how to handle missing values:",
            ("Drop rows with missing values", "Fill missing values with mean")
        )
        if missing_values_handling == "Drop rows with missing values":
            data_cleaned = data.dropna()
        else:
            data_cleaned = data.fillna(data.mean(numeric_only=True))
        st.write("Cleaned Data Sample:")
        st.dataframe(data_cleaned.head())

    # Exploratory Data Analysis (EDA)
    elif selected == 'Exploratory Data Analysis (EDA)':
        st.subheader("4. Exploratory Data Analysis (EDA)")
        numerical_columns = data.select_dtypes(include=np.number).columns.tolist()
        selected_column = st.selectbox("Select a numerical column:", numerical_columns)
        if selected_column:
            st.write(f"Distribution of {selected_column}:")
            fig, ax = plt.subplots()
            sns.histplot(data[selected_column], kde=True, ax=ax)
            st.pyplot(fig)

    # Visualization & Explanatory Analysis
    elif selected == 'Visualization & Explanatory Analysis':
        st.subheader("5. Visualization & Explanatory Analysis")

        # Pastikan ada data
        if data.empty:
            st.error("Dataset is empty or not loaded properly.")
        else:
            # Konversi kolom datetime jika memungkinkan
            for col in data.columns:
                try:
                    data[col] = pd.to_datetime(data[col])
                except ValueError:
                    pass

            # Filter by date if datetime columns exist
            datetime_columns = data.select_dtypes(include=['datetime']).columns.tolist()
            if datetime_columns:
                date_column = st.selectbox("Pilih Kolom Tanggal:", datetime_columns)
                start_date = pd.to_datetime(st.date_input("Start date", value=data[date_column].min().date()))
                end_date = pd.to_datetime(st.date_input("End date", value=data[date_column].max().date()))
                filtered_data = data[(data[date_column] >= start_date) & (data[date_column] <= end_date)]
            else:
                st.warning("Tidak ada kolom tanggal dalam dataset.")
                filtered_data = data
            if 'PM2.5' in data.columns:
                monthly_pm25 = data.groupby('Month')['PM2.5'].mean()
            else:
                st.warning("Column 'PM2.5' is missing in the dataset.")
                monthly_pm25 = pd.Series(dtype=float)
            # Visualisasi untuk Pertanyaan 1: How does PM2.5 concentration vary by month?
            st.subheader("How does PM2.5 concentration vary by month?")
            data['Month'] = data['Date'].dt.month
            monthly_pm25 = data.groupby('Month')['PM2.5'].mean()
            fig, ax = plt.subplots()
            monthly_pm25.plot(kind='bar', ax=ax)
            available_pollutants = [col for col in pollutants if col in data.columns]
            if len(available_pollutants) < 2:
                st.warning("Not enough pollutant columns available for correlation analysis.")
                correlation_matrix = pd.DataFrame()
            else:
                correlation_matrix = data[available_pollutants].corr()
            ax.set_ylabel('Average PM2.5 Concentration')
            ax.set_title('Average PM2.5 Concentration by Month')
            st.pyplot(fig)

            # Visualisasi untuk Pertanyaan 2: What is the correlation between PM2.5 and other pollutants?
            st.subheader("What is the correlation between PM2.5 and other pollutants?")
            pollutants = ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']
            correlation_matrix = data[pollutants].corr()
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", ax=ax)
            st.pyplot(fig)
