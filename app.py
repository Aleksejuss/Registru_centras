import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from PIL import Image

# Set Streamlit page configuration to use wide layout
st.set_page_config(layout="wide")

# Cache the data loading process
@st.cache_data
def load_data():
    return pd.read_excel('JAR_dataset.xlsx', sheet_name="Sheet1")

# Load the data (cached)
adresai_apj2 = load_data()

# Convert 'ja_reg_data' to datetime if it's not already and extract the year
@st.cache_data
def preprocess_data(data):
    data['ja_reg_data'] = pd.to_datetime(data['ja_reg_data'])
    data['year'] = data['ja_reg_data'].dt.year
    return data

adresai_apj2 = preprocess_data(adresai_apj2)

# Streamlit App
st.markdown("<h1 style='text-align: center; font-weight: bold;'>Juridinių asmenų duomenų vizualizacija</h1>", unsafe_allow_html=True)

# Add the logo to the top-right corner
logo = Image.open("Logotipas.png")
st.sidebar.image(logo, use_column_width=True)

# Add slicers (filters) in the sidebar
st.sidebar.header("Filtrai")

@st.cache_data
def get_unique_values(data):
    years = data['year'].unique()
    form_list = data['form_pavadinimas'].unique()
    apskr_list = data['apskritys_final'].unique()
    sav_list = data['savivaldybes_final'].unique()
    return years, form_list, apskr_list, sav_list

years, form_list, apskr_list, sav_list = get_unique_values(adresai_apj2)

def multiselect_with_all(label, options, default):
    options_with_all = ["All"] + list(options)
    selected = st.multiselect(label, options_with_all, default=["All"])
    if "All" in selected:
        return options  # Return all options if "All" is selected
    else:
        return selected

# Date Range Filter for 'ja_reg_data' (Year-based)
with st.sidebar.expander("Pasirinkite metus", expanded=False):  # Collapsible expander
    selected_years = multiselect_with_all("Choose Year(s)", options=sorted(years), default=sorted(years))

# Multi-select for 'form_pavadinimas' (Form Type)
with st.sidebar.expander("Pasirinkite įmonės formą", expanded=False):
    selected_forms = multiselect_with_all("Choose Form Type(s)", options=form_list, default=form_list)

# Multi-select for 'apskr_vardas_statiniai' (County)
with st.sidebar.expander("Pasirinkite apskritį", expanded=False):
    selected_apskrs = multiselect_with_all("Choose County(ies)", options=apskr_list, default=apskr_list)

# Multi-select for 'sav_vardas_statiniai' (Municipality)
with st.sidebar.expander("Pasirinkite savivaldybę", expanded=False):
    selected_savs = multiselect_with_all("Choose Municipality(ies)", options=sav_list, default=sav_list)

@st.cache_data
def filter_data(data, selected_years, selected_forms, selected_apskrs, selected_savs):
    if len(selected_years) > 0:
        data = data[data['year'].isin(selected_years)]
    if len(selected_forms) > 0:
        data = data[data['form_pavadinimas'].isin(selected_forms)]
    if len(selected_apskrs) > 0:
        data = data[data['apskritys_final'].isin(selected_apskrs)]
    if len(selected_savs) > 0:
        data = data[data['savivaldybes_final'].isin(selected_savs)]
    return data

# Apply filters
filtered_data = filter_data(adresai_apj2, selected_years, selected_forms, selected_apskrs, selected_savs)

# Group the filtered data by 'apskr_vardas_statiniai' (County) and 'sav_vardas_statiniai' (Municipality)
grouped_data = filtered_data.groupby(['apskritys_final', 'savivaldybes_final']).size().reset_index(name='Count')

# Rename the columns for display
grouped_data = grouped_data.rename(columns={
    'apskritys_final': 'Apskritys',
    'savivaldybes_final': 'Savivaldybės',
    'Count': 'Įmonių skaičius'
})

# Calculate the total count (sum of all counts) for the KPI
total_count = grouped_data['Įmonių skaičius'].sum()

# Display the KPI in the center and make it bigger
st.markdown(f"""
    <div style='text-align: center;'>
        <h1 style='color: green; font-size: 48px; font-weight: bold;'>{total_count:,}</h1>
    </div>
""", unsafe_allow_html=True)

# Group the filtered data by 'apskr_vardas_statiniai' for the county chart
county_counts = filtered_data['apskritys_final'].value_counts()

# Display the table and the graphs side by side
col1, col2 = st.columns([1.5, 3])

with col1:
    st.subheader("Apskričių ir savivaldybių lentelė")
    st.dataframe(grouped_data, height=400, width=400)  # Adjust height for better vertical space usage
    
    st.subheader("Apskričių pasiskirstymas")
    fig, ax = plt.subplots(figsize=(4, 2), dpi=350)
    sns.barplot(x=county_counts.index, y=county_counts.values, palette="Set2", ax=ax)
    ax.set_xlabel("Apskritys", fontsize=5, fontweight='bold')
    ax.set_ylabel("Įmonių skaičius", fontsize=5, fontweight='bold')
    ax.tick_params(axis='x', labelsize=5, rotation=45)
    ax.tick_params(axis='y', labelsize=5)
    st.pyplot(fig)

with col2:
    st.subheader("Įmonių pasiskirstymas pagal formą TOP 10")
    form_counts = filtered_data['form_pavadinimas'].value_counts().nlargest(10)
    fig, ax = plt.subplots(figsize=(7, 2), dpi=350)  # Smaller size
    sns.barplot(x=form_counts.values, y=form_counts.index, palette="Set1", ax=ax)
    ax.set_xlabel("Įmonių skaičius", fontsize=5, fontweight='bold')
    ax.set_ylabel("Formos tipas", fontsize=5, fontweight='bold')
    ax.tick_params(axis='y', labelsize=5)
    ax.tick_params(axis='x', labelsize=5)
    st.pyplot(fig)

    st.subheader("Metinė įmonių registracija")
    year_counts = filtered_data['year'].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(9, 2), dpi=350)
    sns.lineplot(x=year_counts.index, y=year_counts.values, ax=ax, marker='o', color='green')
    ax.set_xlabel("Metai", fontsize=5, fontweight='bold')
    ax.set_ylabel("Įmonių skaičius", fontsize=5, fontweight='bold')
    ax.tick_params(axis='x', labelsize=5)
    ax.tick_params(axis='y', labelsize=5)
    st.pyplot(fig)













