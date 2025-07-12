# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
from rapidfuzz import fuzz
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(page_title="Medicine Mismatch Detector", layout="wide")

# --- Sidebar ---
with st.sidebar:
    st.title("🧪 MM Detector")
    st.markdown("Upload a **CSV** containing medicine data to detect mismatches.")
    st.markdown("---")
    st.markdown("Developed with ❤️ using Streamlit, Plotly, and RapidFuzz.")

# --- Title ---
st.markdown("<h1 style='color:#4CAF50'>💊 Medicine Mismatch Detector</h1>", unsafe_allow_html=True)

# --- Upload File ---
uploaded_file = st.file_uploader("📤 Upload your medicine dataset (CSV format)", type="csv")

if "upload_history" not in st.session_state:
    st.session_state.upload_history = []

if uploaded_file:
    # Read CSV
    df = pd.read_csv(uploaded_file)

    # Clean column names
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
    df.fillna("Unknown", inplace=True)

    # Save file info in session history
    upload_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    st.session_state.upload_history.append({
        "file_name": uploaded_file.name,
        "time": upload_time,
        "rows": df.shape[0]
    })

    # Show upload history
    with st.expander("🕓 Upload History"):
        for item in st.session_state.upload_history:
            st.markdown(f"- **{item['file_name']}** uploaded at {item['time']} | Rows: {item['rows']}")

    # Show preview
    st.subheader("📄 Uploaded Data Preview")
    st.dataframe(df.head(10), use_container_width=True)

    # Check required columns
    required_cols = ["name", "short_composition1", "short_composition2"]
    if all(col in df.columns for col in required_cols):

        # Create full composition column
        df["full_composition"] = df["short_composition1"].str.lower().str.strip() + " | " + df["short_composition2"].str.lower().str.strip()

        # Initialize mismatch flag and similarity score
        mismatch_flags = []
        similarity_scores = []

        for idx, row in df.iterrows():
            current_name = row["name"].strip().lower()
            current_comp = row["full_composition"]

            # Get all same-name entries
            same_name_df = df[df["name"].str.strip().str.lower() == current_name]

            # Compare composition with all same-name entries
            max_score = max(
                fuzz.ratio(current_comp, other_comp)
                for other_comp in same_name_df["full_composition"]
                if other_comp != current_comp
            ) if len(same_name_df) > 1 else 100

            similarity_scores.append(max_score)
            mismatch_flags.append(1 if max_score < 85 else 0)

        df["Similarity (%)"] = similarity_scores
        df["Mismatch_Flag"] = mismatch_flags
        df["Status"] = df["Mismatch_Flag"].apply(lambda x: "❌ Mismatched" if x else "✅ Matched")

        # --- Summary Metrics ---
        st.subheader("📊 Mismatch Summary")

        summary = df["Status"].value_counts().reset_index()
        summary.columns = ["Status", "Count"]

        fig = px.bar(summary, x="Status", y="Count", color="Status", text="Count", width=700)
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig)

        col1, col2 = st.columns(2)
        with col1:
            st.metric("✅ Matched Medicines", (df["Mismatch_Flag"] == 0).sum())
        with col2:
            st.metric("❌ Mismatched Medicines", (df["Mismatch_Flag"] == 1).sum())

        # --- Show Data ---
        st.subheader("🧾 Detailed Table View")
        tab1, tab2 = st.tabs(["✅ Matched", "❌ Mismatched"])
        with tab1:
            st.dataframe(df[df["Mismatch_Flag"] == 0], use_container_width=True)
        with tab2:
            st.dataframe(df[df["Mismatch_Flag"] == 1], use_container_width=True)

        # --- Download CSV ---
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Full Report", data=csv, file_name="MM_Report.csv", mime="text/csv")

    else:
        st.error("❗ Required columns: `name`, `short_composition1`, and `short_composition2` not found.")
else:
    st.info("📌 Please upload a CSV file to begin.")