import streamlit as st
import google.generativeai as genai
import fitz  # PyMuPDF
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Check if API key is set
if not api_key:
    st.error("❌ API key not found. Please set GEMINI_API_KEY in a .env file.")
    st.stop()

# Configure Gemini
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# Page settings
st.set_page_config(page_title="Gemini Chatbot", layout="centered")
st.title("🧠 Talk to My Bot")

# Clear chat button
if st.button("🧹 Clear Chat"):
    st.session_state.chat_history = []
    st.rerun()

# Character & language selection
personality = st.selectbox("Choose a character:", ["Professor", "Career Counselor", "Best Friend", "Lover", "Family"])
language = st.selectbox("Choose response language:", ["English", "Hindi"])

# Prompt styles
styles = {
    "Professor": "Answer like a strict, sarcastic college professor. Be direct and mildly rude, but educational: ",
    "Career Counselor": "Respond like an experienced, empathetic career counselor. Keep it short, calm, and actionable: ",
    "Best Friend": "Respond like a chilled-out best friend. Keep it honest, goofy, supportive, and short: ",
    "Lover": "Talk like a loving, emotionally supportive partner. Be warm and caring, but keep the message clear and simple: ",
    "Family": "Respond like a caring family member who struggles to express love. Keep it emotionally sincere but concise: "
}

if language == "Hindi":
    for key in styles:
        styles[key] += " Respond in Hindi."

# Session-based memory
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# PDF upload
uploaded_file = st.file_uploader("📄 Upload a PDF to chat with it", type="pdf")
pdf_text = ""
if uploaded_file:
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        for page in doc:
            pdf_text += page.get_text()

    if len(pdf_text) > 8000:
        pdf_text = pdf_text[:8000]
        st.warning("⚠️ PDF content too long. Only the first 8000 characters are used.")

# Display previous chat
for speaker, msg in st.session_state.chat_history:
    st.markdown(f"🧍 **{speaker}**: {msg}" if speaker == "You" else f"🎭 **{speaker}**: {msg}")

# Download chat
if st.session_state.chat_history:
    chat_text = "\n\n".join([f"{s}: {m}" for s, m in st.session_state.chat_history])
    st.download_button("💾 Download Chat as .txt", data=chat_text, file_name="chat_history.txt", mime="text/plain")

# Chat input
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("Type your message here")
    submit = st.form_submit_button("Send")

if submit and user_input.strip():
    base_prompt = styles[personality]
    if pdf_text:
        full_prompt = f"{base_prompt}\n\nThis PDF content is relevant:\n{pdf_text}\n\nNow answer this: {user_input}"
    else:
        full_prompt = base_prompt + user_input

    try:
        response = model.generate_content(full_prompt)
        st.session_state.chat_history.append(("You", user_input))
        st.session_state.chat_history.append((personality, response.text.strip()))
        st.rerun()
    except Exception as e:
        st.error(f"Something went wrong: {e}")
