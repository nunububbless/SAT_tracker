import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from vocab_quiz import show_vocab_quiz

# --- Load or Initialize Data ---
def load_data():
    try:
        df = pd.read_csv("scores.csv")
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date"])
        return df
    except:
        return pd.DataFrame(columns=["Date", "Section", "Score", "MissedTopics"])

df = load_data()

# --- Sidebar: Score Entry Form ---
st.sidebar.header("➕ Add a New Score")
with st.sidebar.form("entry_form"):
    section = st.selectbox("Section", ["Math", "Reading"])
    score = st.number_input("Score", min_value=0, max_value=800, step=10)
    date = st.date_input("Test Date", value=datetime.today())
    missed = st.text_input("Missed Topics (comma-separated)")
    submitted = st.form_submit_button("Save Score")
    if submitted:
        date = pd.to_datetime(date)
        new_row = pd.DataFrame([[date, section, score, missed]], columns=df.columns)
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv("scores.csv", index=False)
        st.sidebar.success("✅ Score saved!")

tab = st.selectbox("Choose a Tab", ["Score Tracking", "Vocabulary Quiz"])

if tab == "Score Tracking":
    # --- Score Trends ---
    st.subheader("📈 Score Trend Graphs")
    col1, col2 = st.columns(2)

    # Filter data by section (Math/Reading)
    math_df = df[df["Section"] == "Math"].sort_values("Date")
    read_df = df[df["Section"] == "Reading"].sort_values("Date")

    with col1:
        if not math_df.empty:
            st.markdown("**Math**")
            st.line_chart(math_df.set_index("Date")[["Score"]])

    with col2:
        if not read_df.empty:
            st.markdown("**Reading**")
            st.line_chart(read_df.set_index("Date")[["Score"]])

    # --- Manual Prediction (Linear Regression Model) ---
    st.subheader("🔮 Predicted Scores (1 week from last test)")

    def predict_next_score(section_df):
        if len(section_df) < 2:
            return "Not enough data"
        section_df = section_df.sort_values("Date")
        section_df["Days"] = (section_df["Date"] - section_df["Date"].min()).dt.days
        X = section_df["Days"].values.reshape(-1, 1)
        y = section_df["Score"].values
        model = LinearRegression()
        model.fit(X, y)
        next_day = section_df["Days"].max() + 7
        predicted = model.predict([[next_day]])
        return round(predicted[0])

    # --- Calculate R² for the Model ---
    def calculate_r2(section_df):
        if len(section_df) < 2:
            return None  # Not enough data to calculate R²
        section_df = section_df.sort_values("Date")
        section_df["Days"] = (section_df["Date"] - section_df["Date"].min()).dt.days
        X = section_df["Days"].values.reshape(-1, 1)
        y = section_df["Score"].values
        model = LinearRegression()
        model.fit(X, y)
        predictions = model.predict(X)
        return r2_score(y, predictions)

    # Predictions for Math and Reading
    math_pred = predict_next_score(math_df)
    read_pred = predict_next_score(read_df)

    # R² calculation
    math_r2 = calculate_r2(math_df)
    read_r2 = calculate_r2(read_df)

    # Display results
    st.write(f"📐 **Math Prediction**: {math_pred} (R²: {round(math_r2, 2) if math_r2 is not None else 'N/A'})")
    st.write(f"📘 **Reading Prediction**: {read_pred} (R²: {round(read_r2, 2) if read_r2 is not None else 'N/A'})")

elif tab == "Vocabulary Quiz":
    # Show the vocabulary quiz in this tab
    show_vocab_quiz()