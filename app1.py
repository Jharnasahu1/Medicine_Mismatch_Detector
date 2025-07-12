# app1.py

import streamlit as st
import pandas as pd
import plotly.express as px
from rapidfuzz import fuzz
from datetime import datetime

# --- Streamlit Page Settings ---
st.set_page_config(page_title="Medicine Mismatch Detector", layout="wide")

# --- Sidebar ---
with st.sidebar:
    st.title("🧪 MM Detector")
    st.markdown("Upload a **CSV file** to detect mismatches in medicine compositions.")
    st.markdown("---")
    st.markdown("Developed using Streamlit, Plotly, and RapidFuzz.")

# --- Header ---
st.markdown("<h1 style='color:#4CAF50;'>💊 Medicine Mismatch Detector</h1>", unsafe_allow_html=True)

# --- File Upload ---
uploaded_file = st.file_uploader("📤 Upload CSV file with medicine data", type="csv")

# --- Session Storage for History ---
if "upload_history" not in st.session_state:
    st.session_state.upload_history = []

# --- Main Logic ---
if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Clean & normalize column names
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

    # Optional debug: show final columns
    st.write("🧾 Final Columns:", df.columns.tolist())

    df.fillna("Unknown", inplace=True)

    # Save upload history
    upload_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    st.session_state.upload_history.append({
        "file_name": uploaded_file.name,
        "time": upload_time,
        "rows": df.shape[0]
    })

    # Show Upload History
    with st.expander("🕓 Upload History"):
        for item in st.session_state.upload_history:
            st.markdown(f"- **{item['file_name']}** at {item['time']} | Rows: {item['rows']}")

    # Show preview
    st.subheader("📄 Uploaded Data Preview")
    st.dataframe(df.head(10), use_container_width=True)

    # === Check Required Columns ===
    required_cols = ["name", "short_composition1", "short_composition2"]
    if all(col in df.columns for col in required_cols):

        # Create full_composition column
        df["full_composition"] = (
            df["short_composition1"].str.lower().str.strip() + " | " +
            df["short_composition2"].str.lower().str.strip()
        )

        # === Mismatch Detection using Fuzzy Logic ===
        similarity_scores = []
        mismatch_flags = []

        for idx, row in df.iterrows():
            current_name = row["name"].strip().lower()
            current_comp = row["full_composition"]

            # Get all records with same name
            same_name_df = df[df["name"].str.strip().str.lower() == current_name]
            other_comps = [c for c in same_name_df["full_composition"] if c != current_comp]

            # Calculate max similarity
            if other_comps:
                max_score = max(fuzz.ratio(current_comp, oc) for oc in other_comps)
            else:
                max_score = 100

            similarity_scores.append(max_score)
            mismatch_flags.append(1 if max_score < 85 else 0)

        # Add results to dataframe
        df["Similarity (%)"] = similarity_scores
        df["Mismatch_Flag"] = mismatch_flags
        df["Status"] = df["Mismatch_Flag"].apply(lambda x: "❌ Mismatched" if x else "✅ Matched")

        # === Summary & Charts ===
        st.subheader("📊 Mismatch Summary")

        summary = df["Status"].value_counts().reset_index()
        summary.columns = ["Status", "Count"]

        fig = px.bar(summary, x="Status", y="Count", color="Status", text="Count", width=700)
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig)

        col1, col2 = st.columns(2)
        col1.metric("✅ Matched", (df["Mismatch_Flag"] == 0).sum())
        col2.metric("❌ Mismatched", (df["Mismatch_Flag"] == 1).sum())

        # === Tabs for Table View ===
        st.subheader("📋 Detailed Table View")
        tab1, tab2 = st.tabs(["✅ Matched Medicines", "❌ Mismatched Medicines"])

        with tab1:
            st.dataframe(df[df["Mismatch_Flag"] == 0], use_container_width=True)
        with tab2:
            st.dataframe(df[df["Mismatch_Flag"] == 1], use_container_width=True)

        # === Download CSV Button ===
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Mismatch Report", data=csv, file_name="MM_Report.csv", mime="text/csv")

    else:
        st.error("❗ Required columns 'name', 'short_composition1', and 'short_composition2' not found in the uploaded file.")
else:
    st.info("📌 Please upload a CSV file to begin.")
