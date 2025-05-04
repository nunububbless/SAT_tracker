import streamlit as st
import pandas as pd
import random

@st.cache_data
def load_vocab():
    try:
        df = pd.read_csv("vocab.csv")
        df = df.dropna(subset=["Word", "Definition"])
        return df
    except Exception as e:
        st.error(f"Error loading vocab: {e}")
        return pd.DataFrame(columns=["Word", "Definition"])

def generate_quiz(vocab_df, num_questions):
    quiz_words = vocab_df.sample(num_questions).reset_index(drop=True)
    questions = []

    for i, row in quiz_words.iterrows():
        correct_word = row["Word"].strip()
        definition = row["Definition"].strip()

        # Generate 3 incorrect choices
        distractors = vocab_df[vocab_df["Word"] != correct_word]["Word"].sample(3).tolist()
        options = distractors + [correct_word]
        random.shuffle(options)

        questions.append({
            "definition": definition,
            "correct": correct_word,
            "options": options
        })

    return questions

def show_vocab_quiz():
    vocab_df = load_vocab()

    st.subheader("🧠 Vocabulary Quiz")

    if vocab_df.empty:
        st.warning("No vocab words found. Please check your 'vocab.csv' file.")
        return

    if "quiz_data" not in st.session_state:
        num_questions = st.slider("How many quiz questions?", 1, min(10, len(vocab_df)), 5, key="slider")
        st.session_state.quiz_data = generate_quiz(vocab_df, num_questions)
        st.session_state.quiz_submitted = False

    quiz_data = st.session_state.quiz_data

    with st.form("vocab_mcq_form"):
        user_answers = []
        for i, q in enumerate(quiz_data):
            answer = st.radio(
                f"{i+1}. {q['definition']}",
                options=q["options"],
                key=f"mcq_{i}"
            )
            user_answers.append(answer)

        submitted = st.form_submit_button("Submit Quiz")

        if submitted:
            score = 0
            feedback = []
            for i, q in enumerate(quiz_data):
                correct = q["correct"]
                selected = user_answers[i]
                if selected == correct:
                    score += 1
                    feedback.append(f"✅ Question {i+1}: Correct!")
                else:
                    feedback.append(f"❌ Question {i+1}: Incorrect. Correct answer: **{correct}**")

            st.session_state.quiz_submitted = True
            st.session_state.last_score = score
            st.session_state.last_feedback = feedback

    # Show feedback if quiz was submitted
    if st.session_state.get("quiz_submitted", False):
        st.success(f"🎉 You scored {st.session_state.last_score} out of {len(quiz_data)}")
        st.write("### Feedback:")
        for fb in st.session_state.last_feedback:
            st.write(fb)

        # Reset button
        if st.button("🔄 Try Another Quiz"):
            for key in list(st.session_state.keys()):
                if key.startswith("mcq_") or key in ["quiz_data", "quiz_submitted", "last_score", "last_feedback", "slider"]:
                    del st.session_state[key]
            st.rerun()
