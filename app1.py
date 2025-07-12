# app1.py

import streamlit as st
import pandas as pd
import plotly.express as px
from rapidfuzz import fuzz
from datetime import datetime

st.set_page_config(page_title="Medicine Mismatch Detector", layout="wide")

# Sidebar
with st.sidebar:
    st.title("🧪 MM Detector")
    st.markdown("Upload the **A_Z_medicines_dataset_of_India.csv** to detect mismatches.")
    st.markdown("---")
    st.markdown("Developed with ❤️ using Streamlit, Plotly, and RapidFuzz.")

st.markdown("<h1 style='color:#4CAF50;'>💊 Medicine Mismatch Detector</h1>", unsafe_allow_html=True)

# Upload CSV
uploaded_file = st.file_uploader("📤 Upload A_Z_medicines_dataset_of_India.csv", type="csv")

if "upload_history" not in st.session_state:
    st.session_state.upload_history = []

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Normalize column names
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
    df.fillna("Unknown", inplace=True)

    # Show columns to confirm
    st.write("🧾 Columns in file:", df.columns.tolist())

    # Save upload history
    st.session_state.upload_history.append({
        "file_name": uploaded_file.name,
        "time": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        "rows": df.shape[0]
    })

    # Show history
    with st.expander("🕓 Upload History"):
        for item in st.session_state.upload_history:
            st.markdown(f"- **{item['file_name']}** at {item['time']} | Rows: {item['rows']}")

    # Preview
    st.subheader("📄 Data Preview")
    st.dataframe(df.head(10), use_container_width=True)

    # Force create full_composition
    df["full_composition"] = (
        df["short_composition1"].str.lower().str.strip() + " | " +
        df["short_composition2"].str.lower().str.strip()
    )

    # Run fuzzy mismatch detection
    similarity_scores = []
    mismatch_flags = []

    for idx, row in df.iterrows():
        current_name = row["name"].strip().lower()
        current_comp = row["full_composition"]

        same_name_df = df[df["name"].str.strip().str.lower() == current_name]
        other_comps = [c for c in same_name_df["full_composition"] if c != current_comp]

        if other_comps:
            max_score = max(fuzz.ratio(current_comp, oc) for oc in other_comps)
        else:
            max_score = 100

        similarity_scores.append(max_score)
        mismatch_flags.append(1 if max_score < 85 else 0)

    df["Similarity (%)"] = similarity_scores
    df["Mismatch_Flag"] = mismatch_flags
    df["Status"] = df["Mismatch_Flag"].apply(lambda x: "❌ Mismatched" if x else "✅ Matched")

    # Show summary chart
    st.subheader("📊 Mismatch Summary")

    summary = df["Status"].value_counts().reset_index()
    summary.columns = ["Status", "Count"]

    fig = px.bar(summary, x="Status", y="Count", color="Status", text="Count", width=700)
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig)

    col1, col2 = st.columns(2)
    col1.metric("✅ Matched", (df["Mismatch_Flag"] == 0).sum())
    col2.metric("❌ Mismatched", (df["Mismatch_Flag"] == 1).sum())

    # Show tables
    st.subheader("📋 Detailed Table View")
    tab1, tab2 = st.tabs(["✅ Matched", "❌ Mismatched"])

    with tab1:
        st.dataframe(df[df["Mismatch_Flag"] == 0], use_container_width=True)
    with tab2:
        st.dataframe(df[df["Mismatch_Flag"] == 1], use_container_width=True)

    # Download report
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Mismatch Report", data=csv, file_name="MM_Report.csv", mime="text/csv")

else:
    st.info("📌 Please upload the CSV file to start analysis.")
