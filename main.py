import streamlit as st
import pandas as pd
import os
from io import BytesIO
import zipfile
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Data Sweeper",
    page_icon="🧹",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        margin-top: 1rem;
    }
    .stProgress .st-bo {
        background-color: #ff4b4b;
    }
    .stDataFrame {
        font-size: 0.8rem;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'auto_remove_duplicates' not in st.session_state:
    st.session_state.auto_remove_duplicates = False
if 'auto_fill_nulls' not in st.session_state:
    st.session_state.auto_fill_nulls = False
if 'chart_type' not in st.session_state:
    st.session_state.chart_type = "Bar Chart"
if 'default_cleaning' not in st.session_state:
    st.session_state.default_cleaning = True

# Sidebar
with st.sidebar:
    st.title("⚙️ Settings")
    
    # Data cleaning preferences
    st.subheader("Data Cleaning Preferences")
    st.session_state.default_cleaning = st.checkbox(
        "Enable Data Cleaning by Default",
        value=st.session_state.default_cleaning
    )
    st.session_state.auto_remove_duplicates = st.checkbox(
        "Auto-remove Duplicates",
        value=st.session_state.auto_remove_duplicates
    )
    st.session_state.auto_fill_nulls = st.checkbox(
        "Auto-fill Null Values",
        value=st.session_state.auto_fill_nulls
    )
    
    # Visualization preferences
    st.subheader("Visualization Settings")
    chart_type = st.selectbox(
        "Default Chart Type",
        ["Bar Chart", "Line Chart", "Scatter Plot"],
        key="chart_type_selector"
    )
    
    # Update chart type in session state
    if chart_type != st.session_state.chart_type:
        st.session_state.chart_type = chart_type
    
    # About section
    st.markdown("---")
    st.markdown("### About Data Sweeper")
    st.markdown("""
    Data Sweeper is a powerful tool for:
    - Converting between CSV and Excel formats
    - Cleaning and preprocessing data
    - Visualizing data patterns
    - Batch processing multiple files
    """)

# Main content
st.title("🧹 Data Sweeper")
st.markdown("### Transform and Clean Your Data Files")

@st.cache_data
def read_file(file, ext):
    """Cached function to read files"""
    try:
        if ext == ".csv":
            return pd.read_csv(file, low_memory=False)
        elif ext == ".xlsx":
            return pd.read_excel(file)
    except Exception as e:
        st.error(f"Error reading file {file.name}: {e}")
        return None

@st.cache_data
def clean_data(df, auto_remove_duplicates=False, auto_fill_nulls=False):
    """Cached function for data cleaning operations"""
    df_cleaned = df.copy()
    
    if auto_remove_duplicates:
        before = df_cleaned.shape[0]
        df_cleaned = df_cleaned.drop_duplicates()
        after = df_cleaned.shape[0]
        st.success(f"Removed {before - after} duplicate rows.")
    
    if auto_fill_nulls:
        numeric_cols = df_cleaned.select_dtypes(include=["number"]).columns
        if not numeric_cols.empty:
            df_cleaned[numeric_cols] = df_cleaned[numeric_cols].fillna(df_cleaned[numeric_cols].mean())
            st.success("Filled missing numeric values with column means.")
        else:
            st.warning("No numeric columns available to fill missing values.")
    
    return df_cleaned

@st.cache_data
def convert_file(df, conversion_type):
    """Cached function for file conversion"""
    buffer = BytesIO()
    if conversion_type == "CSV":
        df.to_csv(buffer, index=False)
        mime = "text/csv"
    else:
        df.to_excel(buffer, index=False)
        mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    buffer.seek(0)
    return buffer.getvalue(), mime

# File upload
uploaded_files = st.file_uploader(
    "Upload Your files (CSV or Excel): ",
    type=["csv", "xlsx"],
    accept_multiple_files=True
)

# Dictionary to store converted files for bulk download
converted_files = {}

if uploaded_files:
    # Progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Process each file
    for idx, file in enumerate(uploaded_files):
        # Update progress
        progress = (idx + 1) / len(uploaded_files)
        progress_bar.progress(progress)
        status_text.text(f"Processing file {idx + 1} of {len(uploaded_files)}")
        
        file_ext = os.path.splitext(file.name)[-1].lower()
        
        # Create expander for each file
        with st.expander(f"📄 {file.name}", expanded=True):
            # Read file
            df = read_file(file, file_ext)
            if df is None:
                continue
            
            # Apply auto-cleaning if enabled
            if st.session_state.default_cleaning:
                df = clean_data(df, st.session_state.auto_remove_duplicates, st.session_state.auto_fill_nulls)
            
            # File info
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("File Size", f"{file.size / (1024 * 1024):.2f} MB")
            with col2:
                st.metric("Rows", f"{df.shape[0]:,}")
            with col3:
                st.metric("Columns", f"{df.shape[1]:,}")
            
            # Data preview with optimized display
            st.subheader("📊 Data Preview")
            st.dataframe(df.head(), use_container_width=True)

            # Data Cleaning Options
            st.subheader("🧹 Data Cleaning")
            if not st.session_state.default_cleaning:
                cleaning_enabled = st.checkbox(f"Clean Data for {file.name}", key=f"clean_{idx}_{file.name}")
            else:
                cleaning_enabled = True
            
            if cleaning_enabled:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("Remove Duplicates", key=f"dup_{idx}_{file.name}"):
                        df = clean_data(df, auto_remove_duplicates=True, auto_fill_nulls=False)
                
                with col2:
                    if st.button("Fill Missing Values", key=f"fill_{idx}_{file.name}"):
                        df = clean_data(df, auto_remove_duplicates=False, auto_fill_nulls=True)
                
                with col3:
                    if st.button("Remove Null Rows", key=f"null_{idx}_{file.name}"):
                        before = df.shape[0]
                        df = df.dropna()
                        after = df.shape[0]
                        st.success(f"Removed {before - after} rows with null values.")
            
            # Column Selection
            st.subheader("📑 Column Selection")
            selected_columns = st.multiselect(
                "Choose columns to include",
                options=df.columns.tolist(),
                default=list(df.columns),
                key=f"cols_{idx}_{file.name}"
            )
            if selected_columns:
                df = df[selected_columns]

            # Data Visualization with optimized display
            st.subheader("📈 Data Visualization")
            if st.checkbox("Show visualization", key=f"viz_{idx}_{file.name}"):
                numeric_cols = df.select_dtypes(include="number").columns
                if len(numeric_cols) > 0:
                    if st.session_state.chart_type == "Bar Chart":
                        st.bar_chart(df[numeric_cols].head())
                    elif st.session_state.chart_type == "Line Chart":
                        st.line_chart(df[numeric_cols].head())
                    else:
                        if len(numeric_cols) >= 2:
                            st.scatter_chart(df[numeric_cols].head())
                        else:
                            st.warning("Need at least 2 numeric columns for scatter plot")
                else:
                    st.warning("No numeric columns available for visualization.")

            # Conversion Options
            st.subheader("🔄 Conversion Options")
            conversion_type = st.radio(
                "Convert to:",
                ["CSV", "Excel"],
                key=f"conv_{idx}_{file.name}"
            )
            
            if st.button(f"Convert {file.name}", key=f"convert_{idx}_{file.name}"):
                data, mime = convert_file(df, conversion_type)
                new_filename = f"{os.path.splitext(file.name)[0]}_{idx}.{'csv' if conversion_type == 'CSV' else 'xlsx'}"
                
                # Download button with success message
                if st.download_button(
                    label=f"⬇️ Download {new_filename}",
                    data=data,
                    file_name=new_filename,
                    mime=mime,
                    key=f"download_{idx}_{file.name}"
                ):
                    st.success(f"Successfully converted {file.name}")
                
                # Save for bulk download
                converted_files[new_filename] = data

    # Bulk download section
    if converted_files:
        st.markdown("---")
        st.subheader("📦 Bulk Download")
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for fname, data in converted_files.items():
                zf.writestr(fname, data)
        zip_buffer.seek(0)
        
        if st.download_button(
            "⬇️ Download All Converted Files as ZIP",
            data=zip_buffer.getvalue(),
            file_name=f"converted_files_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
            mime="application/zip",
            key="bulk_download"
        ):
            st.success(f"Successfully downloaded {len(converted_files)} files")
        
        st.info(f"Total files in ZIP: {len(converted_files)}")
    
    # Clear progress bar
    progress_bar.empty()
    status_text.empty()
    st.success("All files processed successfully! 🎉")

# Footer
st.markdown("---")