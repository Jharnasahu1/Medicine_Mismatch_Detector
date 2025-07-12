# app.py
import streamlit as st
import pandas as pd

st.set_page_config(page_title="MM Detector", layout="wide")
st.title("💊 Medicine Mismatch Detector")

# Upload CSV
uploaded_file = st.file_uploader("Upload your medicine dataset (CSV format)", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    
    # Clean columns
    df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]

    # Fill missing values
    df.fillna("Unknown", inplace=True)

    # Display dataset preview
    st.subheader("🔍 Uploaded Data")
    st.dataframe(df.head(10))

    # Select important columns
    if "short_composition1" in df.columns and "short_composition2" in df.columns:
        df["full_composition"] = df["short_composition1"].str.strip() + " | " + df["short_composition2"].str.strip()
    else:
        st.warning("Composition columns not found!")
    
    # Basic mismatch detection (example: duplicate names with different compositions)
    mismatch_flag = df.duplicated(subset=["name", "full_composition"], keep=False) == False
    df["Mismatch_Flag"] = mismatch_flag.astype(int)

    st.subheader("📊 Medicine Mismatch Summary")
    mismatch_count = df["Mismatch_Flag"].value_counts()
    st.bar_chart(mismatch_count)

    st.subheader("✅ Matched Medicines")
    st.dataframe(df[df["Mismatch_Flag"] == 0])

    st.subheader("❌ Mismatched Medicines")
    st.dataframe(df[df["Mismatch_Flag"] == 1])

    # Download option
    st.download_button("Download Mismatch Report", data=df.to_csv(index=False), file_name="MM_Report.csv")
else:
    st.info("Please upload a CSV file to begin.")
