import sys
import streamlit as st

sys.path.insert(0, "src")
from chat import answer

st.set_page_config(page_title="Buna Assistant", page_icon="☕")
st.title("☕ Buna Assistant")
st.caption("Ask about Ethiopian coffee. Answers come only from the documents, with sources.")

TOPICS = ["All", "varieties", "growing", "disease", "harvest",
          "processing", "storage", "quality", "brewing"]
topic = st.selectbox("Topic", TOPICS)

question = st.text_input("Your question", placeholder="What are the diseases of coffee?")

if st.button("Ask") and question.strip():
    theme = None if topic == "All" else topic
    with st.spinner("Searching the documents..."):
        text, results = answer(question.strip(), theme=theme)

    st.subheader("Answer")
    st.write(text)

    st.subheader("Sources")
    if not results:
        st.write("No sources found.")
    for i, r in enumerate(results, start=1):
        with st.expander(f"[{i}] {r['source']} (page {r['page']}) - score {r['score']:.2f}"):
            st.write(r["text"])

st.divider()
st.caption("Data: Wikipedia (CC BY-SA 4.0) and starter notes written for testing. "
           "For pesticide advice, follow the product label and ask a local extension officer.")