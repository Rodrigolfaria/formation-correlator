import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Formation Correlator Pro", layout="wide")

st.title("🛢️ Formation Name Correlator")
st.write("Upload your data file and your reference library separately.")

# Sidebar for the Reference File (The "Library")
st.sidebar.header("Settings")
ref_file = st.sidebar.file_uploader("1. Upload Reference Library", type="xlsx")

# Main area for the Data File
data_file = st.file_uploader("2. Upload Data File to Process", type="xlsx")

if ref_file and data_file:
    # Read the Library
    df_ref = pd.read_excel(ref_file)

    # Let the user pick the columns from the reference file
    st.sidebar.subheader("Library Columns")
    col_lib_full = st.sidebar.selectbox(
        "Full Name Column (Library)", df_ref.columns)
    col_lib_code = st.sidebar.selectbox(
        "Abbreviation Column (Library)", df_ref.columns)

    # Create the mapping
    mapping = dict(zip(
        df_ref[col_lib_full].astype(str).str.strip(),
        df_ref[col_lib_code].astype(str).str.strip()
    ))

    # Read the Data File
    df_data = pd.read_excel(data_file)

    st.subheader("Data Preview")
    st.dataframe(df_data.head(5))

    # Let the user pick the target column in the data file
    col_target = st.selectbox("Column to match in Data File:", df_data.columns)
    col_result = st.selectbox(
        "Column to populate (Short Name):", df_data.columns)

    if st.button("Run Correlation"):
        def match_row(row):
            val = str(row[col_target]).strip()
            # If match found in library, return it; otherwise keep original
            return mapping.get(val, row[col_result])

        df_data[col_result] = df_data.apply(match_row, axis=1)

        st.success("Correlation Complete!")
        st.dataframe(df_data.head(15))

        # Export
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_data.to_excel(writer, index=False)

        st.download_button(
            label="📥 Download Result",
            data=output.getvalue(),
            file_name="processed_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.info(
        "Please upload both the Reference Library (Sidebar) and the Data File to begin.")
