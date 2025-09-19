import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Feedback  Collector", page_icon="📝", layout="centered")

st.title("📝Feedback Collector")
st.write("Please fill out this form to share your feedback.")

with st.form("feedback_form", clear_on_submit=True):
    name = st.text_input("Your Name")
    email = st.text_input("Email Address")
    rating = st.slider("Rate your experience (1 = Poor, 5 = Excellent)", 1, 5, 3)
    feedback = st.text_area("Your Feedback")
    submitted = st.form_submit_button("Submit Feedback")

    if submitted:
        new_entry = {
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Name": name,
            "Email": email,
            "Rating": rating,
            "Feedback": feedback,
        }

        try:
            df = pd.read_csv("feedback.csv")
            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
        except FileNotFoundError:
            df = pd.DataFrame([new_entry])

        st.success("✅ Thank you! Your feedback has been recorded.")


