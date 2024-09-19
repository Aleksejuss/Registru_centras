import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Set Streamlit page configuration to use wide layout
st.set_page_config(layout="wide")

# Load the data
adresai_apj2 = pd.read_excel('dataset.xlsx')

# Convert 'ja_reg_data' to datetime if it's not already
adresai_apj2['ja_reg_data'] = pd.to_datetime(adresai_apj2['ja_reg_data'])

# Extract the 'year' from 'ja_reg_data' for filtering
adresai_apj2['year'] = adresai_apj2['ja_reg_data'].dt.year

# Streamlit App
st.title("Interactive Company Distribution Dashboard")

# Add slicers (filters) in the sidebar
st.sidebar.header("Filters")

# Date Range Filter for 'ja_reg_data' (Year-based)
with st.sidebar.expander("Select Year(s)", expanded=False):  # Collapsible expander
    years = adresai_apj2['year'].unique()
    selected_years = st.multiselect("Choose Year(s)", options=sorted(years), default=sorted(years))

# Multi-select for 'form_pavadinimas' (Form Type)
with st.sidebar.expander("Select Form Type(s)", expanded=False):
    form_list = adresai_apj2['form_pavadinimas'].unique()
    selected_forms = st.multiselect("Choose Form Type(s)", options=form_list, default=form_list)

# Multi-select for 'apskr_vardas_statiniai' (County)
with st.sidebar.expander("Select County(ies)", expanded=False):
    apskr_list = adresai_apj2['apskr_vardas_statiniai'].unique()
    selected_apskrs = st.multiselect("Choose County(ies)", options=apskr_list, default=apskr_list)

# Multi-select for 'sav_vardas_statiniai' (Municipality)
with st.sidebar.expander("Select Municipality(ies)", expanded=False):
    sav_list = adresai_apj2['sav_vardas_statiniai'].unique()
    selected_savs = st.multiselect("Choose Municipality(ies)", options=sav_list, default=sav_list)

# Apply filters to the dataset

# Filter based on selected year(s)
filtered_data = adresai_apj2[adresai_apj2['year'].isin(selected_years)]

# Apply 'form_pavadinimas' filter
if selected_forms:
    filtered_data = filtered_data[filtered_data['form_pavadinimas'].isin(selected_forms)]

# Apply 'apskr_vardas_statiniai' filter
if selected_apskrs:
    filtered_data = filtered_data[filtered_data['apskr_vardas_statiniai'].isin(selected_apskrs)]

# Apply 'sav_vardas_statiniai' filter
if selected_savs:
    filtered_data = filtered_data[filtered_data['sav_vardas_statiniai'].isin(selected_savs)]

# Group the filtered data by 'apskr_vardas_statiniai' (County) and 'sav_vardas_statiniai' (Municipality)
grouped_data = filtered_data.groupby(['apskr_vardas_statiniai', 'sav_vardas_statiniai']).size().reset_index(name='Count')

# Calculate the total count (sum of all counts) for the KPI
total_count = grouped_data['Count'].sum()

# Display the KPI as a single metric in a separate section
st.header("Key Performance Indicator (KPI)")
st.metric(label="Total Company Count", value=f"{total_count:,}")

# Group the filtered data by 'apskr_vardas_statiniai' for the county chart
county_counts = filtered_data['apskr_vardas_statiniai'].value_counts()

# Display the table and the county chart side by side
st.header("Company Count by County and Municipality")

# Use columns to arrange the table and the graph side by side
col1, col2 = st.columns([1.5, 3])  # Adjusted to make table slightly bigger and graph smaller

with col1:
    # Display the table in the first column and expand its height
    st.dataframe(grouped_data, height=600)  # Adjust height for better vertical space usage

with col2:
    # Display the bar chart for County Distribution and increase DPI for sharper image
    st.subheader("Company Distribution by County")
    fig, ax = plt.subplots(figsize=(14, 6), dpi=150)  # Increase dpi to make the image sharper
    sns.barplot(x=county_counts.index, y=county_counts.values, palette="Set2", ax=ax)  # Using seaborn for color palette
    ax.set_xlabel("County")
    ax.set_ylabel("Count")
    ax.set_title("Count of Companies by County")
    ax.tick_params(axis='x', rotation=45)  # Rotate x-axis labels for better readability
    st.pyplot(fig)






