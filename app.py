import streamlit as st
import pandas as pd
from datetime import datetime
import os


st.set_page_config(page_title="Feedback Collector", page_icon="📝", layout="centered")

DATA_FILE = "category_feedback.csv"
COLUMNS = [
    "Timestamp", "Name", "Email", "Category", "Q1", "Q2", "Q3", "Q4", "Q5", "Suggestions"
]


if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=COLUMNS).to_csv(DATA_FILE, index=False)

def save_feedback(row_dict):
    pd.DataFrame([row_dict]).to_csv(DATA_FILE, mode="a", header=False, index=False)

CATEGORY_QUESTIONS = {
    "🏦 Banking Service": [
        "Which type of banking do you use most?",
        "Have you faced any transaction failures recently?",
        "How secure do you feel about online banking?",
        "How satisfied are you with customer support?",
        "How easy is your bank's app or website to use?",
    ],
    "📱 Mobile Service": [
        "Which mobile operator do you use?",
        "Do you face frequent call drops?",
        "How is your internet speed?",
        "How satisfied are you with customer support?",
        "Are recharge plans affordable?",
    ],
    "🌐 Internet / Wi-Fi": [
        "Which internet provider do you use?",
        "Do you face frequent disconnections?",
        "Is your speed consistent?",
        "Are you satisfied with technical support?",
        "Is your internet plan value for money?",
    ],
    "🛍️ E-Commerce": [
        "Which shopping platform do you use most?",
        "Are you happy with delivery timings?",
        "How satisfied are you with product quality?",
        "How easy is the refund/return process?",
        "Are prices reasonable compared to stores?",
    ],
    "🏥 Healthcare Service": [
        "How easy is it to get appointments?",
        "Are doctors polite and helpful?",
        "Is the waiting time reasonable?",
        "How satisfied are you with medical facilities?",
        "Do you find the cost of treatment fair?",
    ],
    "🏫 Education / College Service": [
        "Are teachers supportive and friendly?",
        "Is study material easy to understand?",
        "How useful are online lectures or portals?",
        "Are you satisfied with campus facilities?",
        "Would you recommend this institute to others?",
    ]
}


def login_page():
    st.title("🔐 Login to Feedback Collector")
    st.write("Enter your name")

    username = st.text_input("Your Name")

    if st.button("Login"):
        if username.strip() == "":
            st.warning("⚠ Please enter your name.")
        else:
            st.session_state["authenticated"] = True
            st.session_state["username"] = username
            st.success(f"Welcome, {username}! 👋")


def feedback_page():
    st.sidebar.success(f"Logged in as: {st.session_state['username']}")
    st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"authenticated": False}))

    tab1, tab2 = st.tabs(["📝 Submit Feedback", "📊 Admin Dashboard"])

    
    with tab1:
        st.title("📝 Feedback Collector")
        st.write("Please provide your feedback")

        name = st.text_input("Your Name *", value=st.session_state["username"])
        email = st.text_input("Email Address *")

        category = st.selectbox("Select Service / Problem Category", list(CATEGORY_QUESTIONS.keys()))

        st.markdown("---")
        st.subheader(f"{category} — Feedback Form")

        questions = CATEGORY_QUESTIONS[category]
        answers = []

        for i, question in enumerate(questions, start=1):
            if i <= 2:
                options = ["Yes", "No", "Maybe"]
                answer = st.radio(f"{i}. {question}", options, horizontal=True)
            else:
                answer = st.slider(f"{i}. {question} (1=Poor, 5=Excellent)", 1, 5, 3)
            answers.append(answer)

        suggestions = st.text_area("💡 Additional Feedback or Suggestions", height=100)

        if st.button("✅ Submit Feedback"):
            if not name.strip() or not email.strip():
                st.warning("⚠ Please fill in your name and email before submitting.")
            else:
                row = {
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Name": name,
                    "Email": email,
                    "Category": category,
                    "Q1": answers[0],
                    "Q2": answers[1],
                    "Q3": answers[2],
                    "Q4": answers[3],
                    "Q5": answers[4],
                    "Suggestions": suggestions
                }
                save_feedback(row)
                st.success("🎉 Thank you! Your feedback has been recorded successfully.")

    
    with tab2:
        st.title("📊 Feedback Responses (Admin Only)")

        admin_pass = st.text_input("Enter Admin Password", type="password")

        if admin_pass == "Gaurav":
            st.success("Welcome Gaurav ✅")

            df = pd.read_csv(DATA_FILE)
            if not df.empty:
                st.write(f"Total Responses: **{len(df)}**")

                selected_category = st.selectbox("Filter by Category", ["All"] + list(CATEGORY_QUESTIONS.keys()))
                if selected_category != "All":
                    df = df[df["Category"] == selected_category]

                st.dataframe(df, use_container_width=True)

                st.download_button(
                    "⬇ Download All Feedback (CSV)",
                    data=df.to_csv(index=False).encode("utf-8"),
                    file_name="feedback_responses.csv",
                    mime="text/csv"
                )

                st.markdown("### 📈 Summary by Category")
                st.bar_chart(df["Category"].value_counts())
            else:
                st.info("No feedback responses yet.")
        elif admin_pass != "":
            st.error("❌ Incorrect password")


def main():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
        st.session_state["username"] = ""

    if st.session_state["authenticated"]:
        feedback_page()
    else:
        login_page()

if __name__ == "__main__":
    main()
