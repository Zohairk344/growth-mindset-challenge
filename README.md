# Data Sweeper

Data Sweeper is a web-based application built with Streamlit that allows users to easily transform and clean their data files between CSV and Excel formats.

## Features

- **Multiple File Support**: Upload and process multiple CSV and Excel files simultaneously
- **File Preview**: View the first 5 rows of each uploaded file
- **Data Cleaning Options**:
  - Remove duplicate rows
  - Fill missing numeric values with column means
  - Remove rows containing null values
- **Column Selection**: Choose specific columns to include in the converted file
- **Data Visualization**: View bar charts of numeric columns
- **Format Conversion**: Convert between CSV and Excel formats
- **Bulk Download**: Download all converted files in a single ZIP archive

## Installation

1. Clone this repository or download the source code
2. Install the required dependencies:
```bash
pip install streamlit pandas openpyxl
```

## Usage

1. Run the application:
```bash
streamlit run main.py
```

2. Open your web browser and navigate to the URL shown in the terminal (typically http://localhost:8501)

3. Use the application:
   - Upload one or more CSV/Excel files using the file uploader
   - For each file:
     - View the file preview
     - Apply data cleaning operations if needed
     - Select columns to include
     - Choose the output format (CSV or Excel)
     - Convert and download individual files
   - Use the bulk download option to get all converted files in a ZIP archive

## Requirements

- Python 3.x
- streamlit
- pandas
- openpyxl

## File Size Limitations

- The application displays file sizes in KB
- Suitable for small to medium-sized data files
- Performance may vary with larger files

## Error Handling

The application includes error handling for:
- File reading errors
- Invalid file formats
- Missing numeric columns for visualization
- Data processing operations

## Contributing

Feel free to fork this repository and submit pull requests for any improvements.

## License

This project is open source and available under the [MIT License](LICENSE).
