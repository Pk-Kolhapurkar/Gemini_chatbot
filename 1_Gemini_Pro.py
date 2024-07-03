import google.generativeai as genai
import streamlit as st
import time
import random
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Chat with image",
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

st.title('Upload Image and Chat with Image')


# API Key input section
if "app_key" not in st.session_state:
    st.markdown(
        "To use this app, you need a Gemini API key. If you don't have one, you can create it "
        "[here](https://developers.google.com/gemini/get-api-key)."
    )
    app_key = st.text_input("Enter your Gemini App Key below", type='password', key='api_key_input')
    if app_key:
        st.session_state.app_key = app_key

if "history" not in st.session_state:
    st.session_state.history = []

try:
    genai.configure(api_key=st.session_state.app_key)
    model = genai.GenerativeModel('gemini-pro')
    chat = model.start_chat(history=st.session_state.history)
except AttributeError as e:
    st.warning("Please enter your Gemini App Key.")

# Display chat history
for message in st.session_state.history:
    role = "assistant" if message['role'] == "model" else message['role']
    with st.chat_message(role):
        st.markdown(message['text'])

# Handle new prompts
if "app_key" in st.session_state:
    if prompt := st.chat_input("Type your message here"):
        prompt = prompt.replace('\n', '  \n')
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Thinking...")
            try:
                full_response = ""
                for chunk in chat.send_message(prompt, stream=True):
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
                st.session_state.history.append({"role": "assistant", "text": full_response})
            except genai.types.generation_types.BlockedPromptException as e:
                st.exception(e)
            except Exception as e:
                st.exception(e)
