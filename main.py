import streamlit as st
import pandas as pd
import os
from io import BytesIO
import zipfile

st.set_page_config(page_title="Data Sweeper", layout="wide")
st.title("Data Sweeper")
st.write("Transform your files between CSV and Excel formats")

# Helper function to read files with error handling
def read_file(file, ext):
    try:
        if ext == ".csv":
            return pd.read_csv(file)
        elif ext == ".xlsx":
            return pd.read_excel(file)
    except Exception as e:
        st.error(f"Error reading file {file.name}: {e}")
        return None

# Upload files (multiple supported)
uploaded_files = st.file_uploader("Upload Your files (CSV or Excel): ", type=["csv", "xlsx"], accept_multiple_files=True)

# Dictionary to store converted files for bulk download
converted_files = {}

if uploaded_files:
    # Add an enumeration to create unique keys
    for idx, file in enumerate(uploaded_files):
        file_ext = os.path.splitext(file.name)[-1].lower()
        st.header(f"Processing: {file.name}")
        
        # Read file
        df = read_file(file, file_ext)
        if df is None:
            continue
        
        st.write(f"**File Size:** {file.size / 1024:.2f} KB")
        st.write("**Preview (First 5 rows):**")
        st.dataframe(df.head())

        # Data Cleaning Options
        st.subheader("Data Cleaning Options")
        if st.checkbox(f"Clean Data for {file.name}", key=f"clean_{idx}_{file.name}"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("Remove Duplicates", key=f"dup_{idx}_{file.name}"):
                    before = df.shape[0]
                    df = df.drop_duplicates()
                    after = df.shape[0]
                    st.write(f"Removed {before - after} duplicate rows.")
            
            with col2:
                if st.button("Fill Missing Numeric Values", key=f"fill_{idx}_{file.name}"):
                    numeric_cols = df.select_dtypes(include=["number"]).columns
                    if not numeric_cols.empty:
                        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                        st.write("Filled missing numeric values with the column mean.")
                    else:
                        st.write("No numeric columns available to fill missing values.")
            
            with col3:
                if st.button("Remove Rows with Nulls", key=f"null_{idx}_{file.name}"):
                    before = df.shape[0]
                    df = df.dropna()
                    after = df.shape[0]
                    st.write(f"Removed {before - after} rows with null values.")
        
        # Column Selection
        st.subheader("Select Columns to Convert")
        selected_columns = st.multiselect("Choose columns", options=df.columns.tolist(), default=list(df.columns), key=f"cols_{idx}_{file.name}")
        if selected_columns:
            df = df[selected_columns]

        # Data Visualization
        st.subheader("Data Visualization")
        if st.checkbox("Show visualization", key=f"viz_{idx}_{file.name}"):
            numeric_cols = df.select_dtypes(include="number").columns
            if len(numeric_cols) > 0:
                st.bar_chart(df[numeric_cols].head())
            else:
                st.write("No numeric columns available for visualization.")

        # Conversion Options
        st.subheader("Conversion Options")
        conversion_type = st.radio("Convert to:", ["CSV", "Excel"], key=f"conv_{idx}_{file.name}")
        if st.button(f"Convert {file.name}", key=f"convert_{idx}_{file.name}"):
            buffer = BytesIO()
            if conversion_type == "CSV":
                df.to_csv(buffer, index=False)
                new_filename = f"{os.path.splitext(file.name)[0]}_{idx}.csv"
                mime = "text/csv"
            else:
                df.to_excel(buffer, index=False)
                new_filename = f"{os.path.splitext(file.name)[0]}_{idx}.xlsx"
                mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            buffer.seek(0)
            st.download_button(label=f"⬇️ Download {new_filename}", data=buffer, file_name=new_filename, mime=mime, key=f"download_{idx}_{file.name}")
            
            # Save converted file content for bulk download with unique filename
            converted_files[new_filename] = buffer.getvalue()

    # Bulk download all converted files as a ZIP archive (displayed as soon as there are files)
    if converted_files:
        st.subheader("Bulk Download")
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zf:
            for fname, data in converted_files.items():
                zf.writestr(fname, data)
        zip_buffer.seek(0)
        st.download_button("⬇️ Download All Converted Files as ZIP",
                           data=zip_buffer.getvalue(),
                           file_name="converted_files.zip",
                           mime="application/zip",
                           key="bulk_download")
        st.write(f"Total files in ZIP: {len(converted_files)}")
    st.success("All files processed successfully!")
