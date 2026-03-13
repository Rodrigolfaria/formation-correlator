import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Formation Correlator", layout="centered")

st.title("🛢️ Formation Name Correlator")
st.write("Upload your Excel file to automatically match formation tops with their short names.")

# File Uploader
uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")

if uploaded_file:
    # Read data
    df = pd.read_excel(uploaded_file)

    with st.expander("Preview Original Data"):
        st.dataframe(df.head())

    # Mapping Logic (Same as before)
    try:
        COL_TARGET = 'formation Tops/Reservoir'
        COL_SHORT_RESULT = 'Short Name'
        COL_LIB_CODE = 'Short Name.1'
        COL_LIB_FULL = 'formation Tops/Reservoir.1'

        # Create the library/dictionary
        library = df[[COL_LIB_FULL, COL_LIB_CODE]].dropna(
            subset=[COL_LIB_FULL])
        mapping = dict(zip(
            library[COL_LIB_FULL].astype(str).str.strip(),
            library[COL_LIB_CODE].astype(str).str.strip()
        ))

        # Perform correlation
        if st.button("Run Correlation"):
            def match_row(row):
                target_val = str(row[COL_TARGET]).strip()
                return mapping.get(target_val, row[COL_SHORT_RESULT])

            df[COL_SHORT_RESULT] = df.apply(match_row, axis=1)

            st.success("Correlation Complete!")
            st.dataframe(df[[COL_TARGET, COL_SHORT_RESULT]].head(15))

            # Convert to Excel for download
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)

            st.download_button(
                label="📥 Download Processed File",
                data=output.getvalue(),
                file_name="correlated_formations.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    except Exception as e:
        st.error(
            f"Error: Make sure your columns are named correctly. Details: {e}")
