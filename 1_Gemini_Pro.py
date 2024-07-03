from PIL import Image
import google.generativeai as genai
import streamlit as st
import time
import random
from dotenv import load_dotenv
from utils import SAFETY_SETTTINGS

load_dotenv()

st.set_page_config(
    page_title="The Answer Genie",
    page_icon="🗣️",
    menu_items={
        'About': "# Made by Prathamesh Khade"
    }
)

# Sidebar for the Gemini logo and clear chat button
st.sidebar.image("Google-Gemini-AI-Logo.png", caption='Gemini AI', use_column_width=True)
st.sidebar.title("Options")
if st.sidebar.button("Clear Chat Window", use_container_width=True, type="primary"):
    st.session_state.history = []
    st.experimental_rerun()

st.title('The Answer Genie')

# API Key input section
if "app_key" not in st.session_state:
    st.markdown(
        "To use this app, you need a Gemini API key. If you don't have one, you can create it "
        "[here](https://aistudio.google.com/app/apikey)."
    )
    app_key = st.text_input("Enter your Gemini App Key below", type='password', key='api_key_input')
    if app_key:
        st.session_state.app_key = app_key

if "history" not in st.session_state:
    st.session_state.history = []

try:
    genai.configure(api_key=st.session_state.app_key)
except AttributeError as e:
    st.warning("Please Put Your Gemini App Key First.")

model = genai.GenerativeModel('gemini-pro')
chat = model.start_chat(history=st.session_state.history)

def delete_message(idx):
    del st.session_state.history[idx]
    st.experimental_rerun()

for idx, message in enumerate(chat.history):
    role = "assistant" if message.role == "model" else message.role
    with st.chat_message(role):
        st.markdown(message.parts[0].text)
        if st.button("Delete", key=f"delete_{idx}"):
            delete_message(idx)

if "app_key" in st.session_state:
    if prompt := st.chat_input("Ask a question here"):
        prompt = prompt.replace('\n', '  \n')
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Thinking...")
            try:
                full_response = ""
                for chunk in chat.send_message(prompt, stream=True, safety_settings=SAFETY_SETTTINGS):
                    word_count = 0
                    random_int = random.randint(5, 10)
                    for word in chunk.text:
                        full_response += word
                        word_count += 1
                        if word_count == random_int:
                            time.sleep(0.05)
                            message_placeholder.markdown(full_response + "_")
                            word_count = 0
                            random_int = random.randint(5, 10)
                message_placeholder.markdown(full_response)
            except genai.types.generation_types.BlockedPromptException as e:
                st.exception(e)
            except Exception as e:
                st.exception(e)
            st.session_state.history = chat.history
