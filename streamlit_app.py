# streamlit_app.py
import streamlit as st
import requests
import time
from datetime import datetime
import csv
import os

# ✅ Page setup without menu bar
st.set_page_config(
    page_title="Research Agent",
    layout="centered"
)

# 🤖 Intro
st.markdown("## 🤖 Hello, I’m your Research Agent!")
st.markdown("Ask me any technical topic, and I’ll find research papers for you.")

# Optional typing animation
def type_writer(text, delay=0.03):
    for char in text:
        st.write(char, end='', unsafe_allow_html=True)
        time.sleep(delay)

# 🕘 Initialize session state
if "history" not in st.session_state:
    st.session_state.history = []
if "exit_clicked" not in st.session_state:
    st.session_state.exit_clicked = False

# ⛔ Stop if user already exited
if st.session_state.exit_clicked:
    st.warning("👋 You have exited the Research Agent.")
    st.stop()

# 📝 User input
query = st.text_input("🔍 Enter your topic or question")

if query:
    # Add to session history
    st.session_state.history.append(query)

    # ✅ Save query to TXT
    with open("query_history.txt", "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {query}\n")

    # 🔍 Call the API
    with st.spinner("Research Agent is thinking... 🤖💭"):
        try:
            response = requests.get(f"http://127.0.0.1:5000/search?query={query}")
            data = response.json()
        except Exception as e:
            st.error(f"Error fetching results: {e}")
            data = None

    # 🧾 Display & Save Results
    if isinstance(data, list):
        st.markdown("### 📚 Research Agent’s Findings:")

        # ✅ Append to master CSV
        csv_file = "search_results_log.csv"
        csv_exists = os.path.exists(csv_file)

        with open(csv_file, "a", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            if not csv_exists:
                writer.writerow(["Timestamp", "Query", "Title", "Authors", "Abstract", "Year", "URL"])
            for paper in data:
                writer.writerow([
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    query,
                    paper.get("title", ""),
                    ", ".join(paper.get("authors", [])),
                    (paper.get("abstract", "") or "No abstract").replace("\n", " ")[:500],
                    paper.get("year", ""),
                    paper.get("url", "")
                ])

        # 🧾 Display each paper
        for i, paper in enumerate(data):
            with st.expander(f"📄 {paper['title']}"):
                st.markdown(f"**👨‍🔬 Authors:** {', '.join(paper['authors'])}")
                st.markdown(f"**📅 Year:** {paper['year']}")
                abstract = paper.get('abstract') or "No abstract available."
                if len(abstract) > 500:
                    abstract = abstract[:500] + "..."
                st.markdown(f"**🧠 Abstract:** {abstract}")
                st.markdown(f"[🔗 Read Full Paper]({paper['url']})")
    else:
        st.warning("No results found or something went wrong.")

# 🧠 Sidebar controls
with st.sidebar:
    # 🕘 Show recent session history
    if st.session_state.history:
        st.markdown("### 🕘 Your Recent Searches")
        for past_query in reversed(st.session_state.history[-5:]):
            st.markdown(f"- {past_query}")

    # 📥 Download full CSV
    st.markdown("### 🗂️ Saved Research Log")
    if os.path.exists("search_results_log.csv"):
        with open("search_results_log.csv", "rb") as f:
            st.download_button("⬇️ Download Full CSV", f, file_name="search_results_log.csv")
    else:
        st.info("No saved research data yet.")

    # 🛑 Exit
    st.markdown("### ⚙️ Controls")
    if st.button("🔴 Exit Research Agent"):
        st.session_state.exit_clicked = True
        st.session_state.history = []
        st.rerun()
