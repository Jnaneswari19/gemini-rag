import streamlit as st
import requests

st.title("Gemini RAG Demo")

# Upload
st.header("Upload Document")
uploaded_file = st.file_uploader("Choose a file", type=["pdf", "txt", "docx"])
if uploaded_file:
    st.write("File uploaded:", uploaded_file.name)

# Ask
st.header("Ask a Question")
question = st.text_input("Enter your question")
if st.button("Ask"):
    st.write("Answer: Demo answer")
    st.write("Source: Example chunk")
    st.write("Tokens used: 30")
