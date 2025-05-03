import streamlit as st
import pandas as pd
import random

@st.cache_data
def load_vocab():
    try:
        df = pd.read_csv("data/vocab.csv")
        df = df.dropna(subset=["Word", "Definition"])
        return df
    except Exception as e:
        st.error(f"Error loading vocab: {e}")
        return pd.DataFrame(columns=["Word", "Definition"])

def show_vocab_quiz():
    vocab_df = load_vocab()

    st.subheader("🧠 Vocabulary Quiz")

    if vocab_df.empty:
        st.warning("No vocab words found. Please check your 'data/vocab.csv' file.")
        return

    num_questions = st.slider("How many quiz questions?", 1, min(10, len(vocab_df)), 5)
    quiz_words = vocab_df.sample(num_questions).reset_index(drop=True)
    score = 0

    with st.form("vocab_quiz_form"):
        st.write("### Match the definitions:")
        answers = []
        for i, row in quiz_words.iterrows():
            user_answer = st.text_input(f"**{i+1}. {row['Definition']}**", key=f"quiz_{i}")
            answers.append((row["Word"].strip().lower(), user_answer.strip().lower()))
        
        submitted = st.form_submit_button("Submit Quiz")
        
        if submitted:
            for idx, (correct, user) in enumerate(answers):
                if correct == user:
                    score += 1
            st.success(f"✅ You got {score} out of {num_questions} correct!")
