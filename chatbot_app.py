import streamlit as st
import google.generativeai as genai
import fitz  # PyMuPDF for PDF reading

# Setup Gemini
genai.configure(api_key=st.secrets["GEMINI_API_KEY"]) # Replace with your actual API key
model = genai.GenerativeModel('gemini-1.5-flash')

# Page setup
st.set_page_config(page_title="Gemini Chatbot", layout="centered")
st.title("🧠 Talk to My Bot")

# 🧹 Clear Chat Button
if st.button("🧹 Clear Chat"):
    st.session_state.chat_history = []
    st.rerun()

# Select character
personality = st.selectbox("Choose a character:", ["Professor", "Career Counselor", "Best Friend", "Lover", "Family"])

# Select language
language = st.selectbox("Choose response language:", ["English", "Hindi"])

# Prompt styles
styles = {
    "Professor": "Answer like a strict, sarcastic college professor. Be direct and mildly rude, but educational: ",
    
    "Career Counselor": "Respond like an experienced, empathetic career counselor. Keep it short, calm, and actionable: ",
    
    "Best Friend": "Respond like a chilled-out best friend. Keep it honest, goofy, supportive, and short: ",
    
    "Lover": "Talk like a loving, emotionally supportive partner. Be warm and caring, but keep the message clear and simple: ",
    
    "Family": "Respond like a caring family member who struggles to express love. Keep it emotionally sincere but concise: "
}

# Add language instruction to prompt
if language == "Hindi":
    for key in styles:
        styles[key] += " Respond in Hindi."

# Session-based memory
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# PDF Upload
uploaded_file = st.file_uploader("📄 Upload a PDF to chat with it", type="pdf")
pdf_text = ""
if uploaded_file:
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        for page in doc:
            pdf_text += page.get_text()

# Show previous chat
for speaker, msg in st.session_state.chat_history:
    if speaker == "You":
        st.markdown(f"🧍 **You:** {msg}")
    else:
        st.markdown(f"🎭 **{speaker}:** {msg}")

# 💾 Download Chat History
if st.session_state.chat_history:
    chat_text = ""
    for speaker, msg in st.session_state.chat_history:
        chat_text += f"{speaker}: {msg}\n\n"

    st.download_button(
        label="💾 Download Chat as .txt",
        data=chat_text,
        file_name="chat_history.txt",
        mime="text/plain"
    )

# Input box at the end of chat
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("Type your message here")
    submit = st.form_submit_button("Send")

if submit and user_input:
    if pdf_text:
        full_prompt = styles[personality] + f"\n\nThis PDF content is relevant:\n{pdf_text}\n\nNow answer this: {user_input}"
    else:
        full_prompt = styles[personality] + user_input

    response = model.generate_content(full_prompt)
    st.session_state.chat_history.append(("You", user_input))
    st.session_state.chat_history.append((personality, response.text))
    st.rerun()