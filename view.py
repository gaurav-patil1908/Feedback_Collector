import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Feedback Collector", page_icon="📝", layout="wide")

# -------------------------
# Login Page
# -------------------------
def login_page():
    st.title("🔐 Login to Feedback Collector")
    username = st.text_input("Your Name")

    if st.button("Login"):
        if username.strip() == "":
            st.warning("⚠ Please enter your name.")
        else:
            st.session_state["authenticated"] = True
            st.session_state["username"] = username
            st.success(f"Welcome, {username}! 👋")


# -------------------------
# Feedback Page
# -------------------------
def feedback_page():
    st.sidebar.success(f"Logged in as: {st.session_state['username']}")
    st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"authenticated": False}))

    tab1, tab2 = st.tabs(["📝 Submit Feedback", "📊 Admin Dashboard"])

    # -------------------------
    # Submit Feedback
    # -------------------------
    with tab1:
        st.title("📝 Feedback Form")

        name = st.text_input("Your Name", value=st.session_state["username"])
        email = st.text_input("Email Address")

        # Fetch categories
        categories = requests.get(f"{API_URL}/categories").json()
        category = st.selectbox("Select Category", categories)

        # Fetch questions for selected category
        questions = requests.get(f"{API_URL}/questions/{category}").json()

        st.markdown("---")
        st.subheader(f"{category} — Feedback Form")

        q1 = st.radio(f"1. {questions[0]}", ["Yes", "No", "Maybe"], horizontal=True)
        q2 = st.radio(f"2. {questions[1]}", ["Yes", "No", "Maybe"], horizontal=True)
        q3 = st.slider(f"3. {questions[2]} (1–5)", 1, 5, 3)
        q4 = st.slider(f"4. {questions[3]} (1–5)", 1, 5, 3)
        q5 = st.slider(f"5. {questions[4]} (1–5)", 1, 5, 3)

        suggestions = st.text_area("💡 Additional Feedback or Suggestions", height=100)

        if st.button("Submit Feedback"):
            if not name or not email:
                st.warning("⚠ Please fill in all details.")
            else:
                payload = {
                    "name": name,
                    "email": email,
                    "category": category,
                    "q1": q1,
                    "q2": q2,
                    "q3": q3,
                    "q4": q4,
                    "q5": q5,
                    "suggestions": suggestions
                }

                res = requests.post(f"{API_URL}/submit", json=payload)

                if res.status_code == 200:
                    st.success("🎉 Feedback submitted successfully!")
                else:
                    st.error("Something went wrong!")


    # -------------------------
    # ADMIN DASHBOARD
    # -------------------------
    with tab2:
        st.title("📊 Feedback Responses (Admin)")

        admin_pass = st.text_input("Enter Admin Password", type="password")

        if admin_pass:
            auth = requests.get(f"{API_URL}/admin/all", auth=("admin", admin_pass))

            if auth.status_code == 200:
                df = pd.DataFrame(auth.json())

                # -------------------------
                # FIX → convert column names to lowercase
                # -------------------------
                df.columns = [c.lower() for c in df.columns]

                st.success("Logged in as Admin ✔")

                # Show Table
                st.write(f"Total Responses: **{len(df)}**")
                st.dataframe(df, use_container_width=True)

                # Download CSV
                csv = df.to_csv(index=False).encode()
                st.download_button("⬇ Download CSV", csv, "feedback.csv", "text/csv")

                st.markdown("---")
                st.subheader("📈 Visual Analytics")

                if not df.empty:
                    # -------------------------
                    # 1️⃣ Category Count (Bar Chart)
                    # -------------------------
                    st.markdown("### 🔵 Feedback Count by Category")

                    fig1, ax1 = plt.subplots()
                    df["category"].value_counts().plot(kind="bar", ax=ax1)
                    ax1.set_xlabel("Category")
                    ax1.set_ylabel("Count")
                    ax1.set_title("Feedback per Category")
                    st.pyplot(fig1)

                    # -------------------------
                    # 2️⃣ Average Rating per Category (Line Chart)
                    # -------------------------
                    st.markdown("### 🔴 Average Rating per Category")

                    rating_cols = ["q3", "q4", "q5"]
                    avg_rating = df.groupby("category")[rating_cols].mean()

                    fig2, ax2 = plt.subplots()
                    avg_rating.plot(ax=ax2)
                    ax2.set_title("Average Rating (1–5)")
                    ax2.set_ylabel("Average Score")
                    st.pyplot(fig2)

                    # -------------------------
                    # 3️⃣ Q1 Yes/No/Maybe Distribution (Pie Chart)
                    # -------------------------
                    st.markdown("### 🟢 Q1: Yes/No/Maybe Distribution")

                    fig3, ax3 = plt.subplots()
                    df["q1"].value_counts().plot(kind="pie", autopct="%1.1f%%", ax=ax3)
                    ax3.set_ylabel("")
                    ax3.set_title("Q1 Response Distribution")
                    st.pyplot(fig3)

            else:
                st.error("❌ Incorrect Password")


# -------------------------
# MAIN
# -------------------------
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
