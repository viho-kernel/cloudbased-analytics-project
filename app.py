from cmath import nan
from datetime import date
import streamlit as st
from helper import data, seconddata, match_elements, describe, outliers, drop_items, download_data, filter_data, num_filter_data, rename_columns, clear_image_cache, handling_missing_values, data_wrangling
import io
import boto3
import os
import docx2txt
from PIL import Image
import pytesseract
import fitz
import streamlit as st
import pandas as pd
import numpy as np
import csv
import plotly.express as px
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Data Analysis Web App",
    page_icon="🧙‍♂️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/everydaycodings/Data-Analysis-Web-App',
        'Report a bug': "https://github.com/everydaycodings/Data-Analysis-Web-App/issues/new",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)

import pandas as pd
import numpy as np

uploaded_file = st.file_uploader("Upload file", type=["pdf", "docx", "xlsx", "csv", "jpeg", "jpg", "png"])

def read_file(uploaded_file):
    file_type = uploaded_file.name.split(".")[-1].lower()
    if file_type == "csv":
        return pd.read_csv(uploaded_file)
    elif file_type == "xlsx":
        return pd.read_excel(uploaded_file)
    elif file_type == "docx":
        return docx2txt.process(uploaded_file)
    elif file_type == "pdf":
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    elif file_type in ["jpeg", "jpg", "png"]:
        image = Image.open(uploaded_file)
        text = pytesseract.image_to_string(image)
        return text
    else:
        return "Unsupported file format"

if uploaded_file is not None:
    result = read_file(uploaded_file)

    if isinstance(result, pd.DataFrame):
        st.write("### DataFrame Preview")
        st.dataframe(result)
    else:
        st.write("### Extracted Text")
        st.text(result)

def upload_to_s3(file_obj, file_name):
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name='eu-north-1'  # use your AWS region
    )
    BUCKET_NAME = "cloudanalytics-data-files"  # Replace with your real bucket name
    file_obj.seek(0)
    s3.upload_fileobj(file_obj, BUCKET_NAME, file_name)
    return f"https://{BUCKET_NAME}.s3.amazonaws.com/{file_name}"

def send_sns_notification(file_name, s3_url):
    sns = boto3.client(
        'sns',
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name='us-east-1'
    )

    topic_arn = "arn:aws:sns:us-east-1:463470942394:cloudanalytics-file-upload-alert"  # change this!

    message = f"📁 New File Uploaded: {file_name}\n🔗 S3 URL: {s3_url}"

    response = sns.publish(
        TopicArn=topic_arn,
        Message=message,
        Subject="📊 New Cloud Analytics Upload"
    )
    return response


st.sidebar.title("Data Analysis Web App")
file_format_type = ["csv", "txt", "xls", "xlsx", "ods", "odt"]
functions = ["Overview", "Outliers", "Drop Columns", "Drop Categorical Rows", "Drop Numeric Rows", "Rename Columns", "Display Plot", "Handling Missing Data", "Data Wrangling"]
excel_type =["vnd.ms-excel","vnd.openxmlformats-officedocument.spreadsheetml.sheet", "vnd.oasis.opendocument.spreadsheet", "vnd.oasis.opendocument.text"]

st.sidebar.metric("📤 Total Uploads", 12)  # Replace with dynamic count from S3/DynamoDB if available

uploaded_file = st.sidebar.file_uploader("Upload Your file", type=file_format_type)
if uploaded_file is not None:
    file_bytes = uploaded_file.read()
    file_name = uploaded_file.name
    file_ext = file_name.split(".")[-1].lower()

    s3_url = upload_to_s3(io.BytesIO(file_bytes), file_name)
    send_sns_notification(file_name, s3_url)
    st.success(f" File uploaded to s3 successfully!")
    st.markdown(f"[View File on S3]({s3_url})")

    file_stream = io.BytesIO(file_bytes)


    try:
        if file_ext in ["csv", "txt"]:
            # Try to sniff separator automatically
            try:
                sample = file_bytes[:2048].decode("utf-8", errors="ignore")
                guessed_sep = csv.Sniffer().sniff(sample).delimiter
            except:
                guessed_sep = ","
            sep = st.sidebar.text_input("Enter separator (e.g., ',', '|', '\\t')", value=guessed_sep)
            st.caption("Raw Preview of Uploaded File:")
            st.code(sample)
            file_stream.seek(0)
            data = pd.read_csv(file_stream, sep=sep, engine="python", on_bad_lines="skip")

        elif file_ext in ["xls", "xlsx"]:
            data = pd.read_excel(file_stream)

        else:
            st.error("❌ Unsupported file type for analytics.")
            st.stop()

    except pd.errors.EmptyDataError:
        st.error("❌ Uploaded file is empty.")
        st.stop()
    except pd.errors.ParserError as e:
        st.error(f"❌ Parsing error: {e}")
        st.stop()
    except Exception as e:
        st.error(f"❌ Unexpected error: {e}")
        st.stop()

    describe, shape, columns, num_category, str_category, null_values, dtypes, unique, str_category, column_with_null_values = describe(data)
    multi_function_selector = st.sidebar.multiselect("Enter Name or Select the Column which you Want To Plot: ", functions, default=["Overview"])
    st.subheader("Dataset Preview")
    st.dataframe(data)
    st.text(" ")
    st.text(" ")
    st.text(" ")
    if "Overview" in multi_function_selector:
        st.subheader("Dataset Description")
        st.write(describe)
        st.text(" ")
        st.text(" ")
        st.text(" ")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.text("Basic Information")
            st.write("Dataset Name")
            st.text(uploaded_file.name)
            st.write("Dataset Size(MB)")
            number = round((uploaded_file.size*0.000977)*0.000977,2)
            st.write(number)
            st.write("Dataset Shape")
            st.write(shape)

        with col2:
            st.text("Dataset Columns")
            st.write(columns)

        with col3:
            st.text("Numeric Columns")
            st.dataframe(num_category)

        with col4:
            st.text("String Columns")
            st.dataframe(str_category)

        col5, col6, col7, col8= st.columns(4)
        with col6:
            st.text("Columns Data-Type")
            st.dataframe(dtypes)

        with col7:
            st.text("Counted Unique Values")
            st.write(unique)

        with col5:
            st.write("Counted Null Values")
            st.dataframe(null_values)


    # ====================================> Custom Visual Analytics: Pie + Histogram
    if "Display Plot" in multi_function_selector:
        st.subheader("📊 Visual Analytics")

        if len(str_category) > 0:
            selected_cat_col = st.selectbox("Select a categorical column for Pie Chart", str_category)
            pie_data = data[selected_cat_col].value_counts().reset_index()
            pie_data.columns = [selected_cat_col, "count"]
            st.markdown("#### Pie Chart")
            st.plotly_chart(
                px.pie(pie_data, names=selected_cat_col, values="count", title=f"Pie chart of {selected_cat_col}")
            )

        if len(num_category) > 0:
            selected_num_col = st.selectbox("Select a numeric column for Histogram", num_category)
            st.markdown("#### Histogram")
            st.plotly_chart(
                px.histogram(data, x=selected_num_col, nbins=20, title=f"Histogram of {selected_num_col}")
            )

    # ============================== 📊 Dashboard Visuals Section ==============================
    st.subheader("📈 Visual Dashboard")

    selected_col = st.selectbox("Select a column to visualize", data.columns)

    if selected_col:
        if pd.api.types.is_numeric_dtype(data[selected_col]):
            st.markdown(f"### Histogram of `{selected_col}`")
            st.bar_chart(data[selected_col])

            st.markdown(f"### Boxplot of `{selected_col}`")
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots()
            ax.boxplot(data[selected_col].dropna())
            ax.set_title(f'Boxplot for {selected_col}')
            st.pyplot(fig)

        else:
            st.markdown(f"### Pie Chart of `{selected_col}` values")
            pie_data = data[selected_col].value_counts()
            st.dataframe(pie_data)

            fig, ax = plt.subplots()
            ax.pie(pie_data.values, labels=pie_data.index, autopct="%1.1f%%", startangle=140)
            ax.axis('equal')
            st.pyplot(fig)

    # ==================================================================================================
    if "Outliers" in multi_function_selector:
        outliers_selection = st.multiselect("Enter or select Name of the columns to see Outliers:", num_category)
        outliers = outliers(data, outliers_selection)

        for i in range(len(outliers)):
            st.image(outliers[i])
    # ===================================================================================================
    if "Drop Columns" in multi_function_selector:

        multiselected_drop = st.multiselect("Please Type or select one or Multipe Columns you want to drop: ", data.columns)

        droped = drop_items(data, multiselected_drop)
        st.write(droped)

        drop_export = download_data(droped, label="Droped(edited)")
    # =====================================================================================================================================
    if "Drop Categorical Rows" in multi_function_selector:
        filter_column_selection = st.selectbox("Please Select or Enter a column Name: ", options=data.columns)
        filtered_value_selection = st.multiselect("Enter Name or Select the value which you don't want in your {} column(You can choose multiple values): ".format(filter_column_selection), data[filter_column_selection].unique())

        filtered_data = filter_data(data, filter_column_selection, filtered_value_selection)
        st.write(filtered_data)

        filtered_export = download_data(filtered_data, label="filtered")
    # =============================================================================================================================
    if "Drop Numeric Rows" in multi_function_selector:
        option = st.radio(
            "Which kind of Filteration you want",
            ('Delete data inside the range', 'Delete data outside the range'))
        num_filter_column_selection = st.selectbox("Please Select or Enter a column Name: ", options=num_category)
        selection_range = data[num_filter_column_selection].unique()
        for i in range(0, len(selection_range)) :
            selection_range[i] = selection_range[i]
        selection_range.sort()
        selection_range = [x for x in selection_range if np.isnan(x) == False]
        start_value, end_value = st.select_slider(
            'Select a range of Numbers you want to edit or keep',
            options=selection_range,
            value=(min(selection_range), max(selection_range)))

        if option == "Delete data inside the range":
            st.write('We will be removing all the values between ', int(start_value), 'and', int(end_value))
            num_filtered_data = num_filter_data(data, start_value, end_value, num_filter_column_selection, param=option)
        else:
            st.write('We will be Keeping all the values between', int(start_value), 'and', int(end_value))
            num_filtered_data = num_filter_data(data, start_value, end_value, num_filter_column_selection, param=option)
        st.write(num_filtered_data)
        num_filtered_export = download_data(num_filtered_data, label="num_filtered")
    # =======================================================================================================================================
    if "Rename Columns" in multi_function_selector:
        if 'rename_dict' not in st.session_state:
            st.session_state.rename_dict = {}
        rename_dict = {}
        rename_column_selector = st.selectbox("Please Select or Enter a column Name you want to rename: ", options=data.columns)
        rename_text_data = st.text_input("Enter the New Name for the {} column".format(rename_column_selector), max_chars=50)
        if st.button("Draft Changes", help="when you want to rename multiple columns/single column so first you have to click Save Draft button this updates the data and then press Rename Columns Button."):
            st.session_state.rename_dict[rename_column_selector] = rename_text_data
            st.code(st.session_state.rename_dict)


# Footer Tech Stack Info
st.markdown("""
---
🛠️ Built using **Streamlit**, **AWS S3**, **SNS**, **Pandas**, **Plotly**, **Matplotlib**
""", unsafe_allow_html=True)


if st.button("📥 Download Dashboard Summary"):
    summary_df = pd.DataFrame({"info": ["Feature summary pending..."]})
    buffer = io.BytesIO()
    buffer.write(summary_df.to_csv(index=False).encode('utf-8'))
    buffer.seek(0)
    st.download_button("📥 Download Summary CSV", buffer, file_name="dashboard_summary.csv", mime="text/csv")

