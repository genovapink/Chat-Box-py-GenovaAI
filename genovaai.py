import time
import os
import joblib
import google.generativeai as genai
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

new_chat_id = f"{time.time()}"

if not os.path.exists("data/"):
    os.mkdir("data/")

try:
    past_chats = joblib.load("data/past_chat_list")
except:
    past_chats = {}

with st.sidebar:
    st.write("# Chat Session")
    if st.session_state.get("chat_id") is None:
        st.session_state.chat_id = st.selectbox(
            label='Pick a chat session',
            options=[new_chat_id] + list(past_chats.keys()),
            format_func=lambda x: past_chats.get(x, 'New Chat'),
        )
    else:
        st.session_state.chat_id = st.selectbox(
            label='Pick a chat session',
            options=[new_chat_id, st.session_state.chat_id] + list(past_chats.keys()),
            index=1,
            format_func=lambda x: past_chats.get(x, 'New Chat' if x != st.session_state.chat_id else st.session_state.chat_title),
        )
    st.session_state.chat_title = f"ChatSession-{st.session_state.chat_id}"

st.write("# Chat With GenovaAI")

try:
    st.session_state.messages = joblib.load(f"data/{st.session_state.chat_id}-st_messages")
    st.session_state.gemini_history = joblib.load(f"data/{st.session_state.chat_id}-gemini_messages")
except:
    st.session_state.messages = []
    st.session_state.gemini_history = []

st.session_state.model = genai.GenerativeModel("gemini-pro")
st.session_state.chat = st.session_state.model.start_chat(history=st.session_state.gemini_history)

# Background Styling
page_bg = f"""
<style>
[data-testid="stAppViewContainer"] {{ s
    background-image: url("https://i.pinimg.com/736x/c5/70/a2/c570a24592c2b77958a7b9d39288e62a.jpg");
    background-size: cover;
    background-repeat: no-repeat;
    background-attachment: fixed;
}}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

for message in st.session_state.messages:
    with st.chat_message(name=message["role"], avatar=message.get("avatar")):
        st.markdown(message["content"])

if prompt := st.chat_input("Your message here..."):
    if st.session_state.chat_id not in past_chats.keys():
        past_chats[st.session_state.chat_id] = st.session_state.chat_title
        joblib.dump(past_chats, "data/past_chat_list")

    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.messages.append(dict(role="user", content=prompt))

    response = st.session_state.chat.send_message(prompt, stream=True)
    with st.chat_message(name="ai", avatar="💟"):
        message_placeholder = st.empty()
        full_response = ''
        for chunk in response:
            for ch in chunk.text.split(' '):
                full_response += ch + ' '
                time.sleep(0.05)
                message_placeholder.write(full_response)
        message_placeholder.write(full_response)

    st.session_state.messages.append(dict(role="ai", content=full_response, avatar="💟"))
    st.session_state.gemini_history = st.session_state.chat.history
    joblib.dump(st.session_state.messages, f'data/{st.session_state.chat_id}-st_messages')
    joblib.dump(st.session_state.gemini_history, f'data/{st.session_state.chat_id}-gemini_messages')

page_bg = f"""s
<style>
[data-testid="stAppViewContainer"] {{
    background-image: url("https://i.pinimg.com/736x/c5/70/a2/c570a24592c2b77958a7b9d39288e62a.jpg");
    background-size: cover;
    background-repeat: no-repeat;
    background-attachment: fixed;
}}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

