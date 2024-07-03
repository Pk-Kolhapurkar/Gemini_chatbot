from PIL import Image
import google.generativeai as genai
import streamlit as st
import time
import random
from dotenv import load_dotenv

load_dotenv()

# Sets the avatar for user as well as the bot
image_path = "Google-Gemini-AI-Logo.png"

st.set_page_config(
    page_title="Chat with image",
    page_icon="🗣️",
    menu_items={
        'About': "# Made by Prathamesh Khade"
    }
)

# Sidebar for the Gemini logo and clear chat button
st.sidebar.image(image_path, caption='Gemini AI', use_column_width=True)
st.sidebar.title("Options")
if st.sidebar.button("Clear Chat Window", use_container_width=True, type="primary"):
    clear_chat_window()

st.title('Upload Image And Chat with Image')

if "app_key" not in st.session_state:
    st.markdown(
        "To use this app, you need a Gemini API key. If you don't have one, you can create it "
        "[here](https://aistudio.google.com/app/apikey)."
    )
    app_key = st.text_input("Enter your Gemini App Key below", type='password', key='api_key_input')
    if app_key:
        st.session_state.app_key = app_key

try:
    genai.configure(api_key=st.session_state.app_key)
    model = genai.GenerativeModel('gemini-pro-vision')
except AttributeError as e:
    st.warning("Please Put Your Gemini App Key First.")

def show_message(prompt, image, loading_str, idx):
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown(loading_str)
        full_response = ""
        try:
            for chunk in model.generate_content([prompt, image], stream=True):                   
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
        except genai.types.generation_types.BlockedPromptException as e:
            st.exception(e)
        except Exception as e:
            st.exception(e)
        message_placeholder.markdown(full_response)
        st.session_state.history_pic[idx] = {"role": "assistant", "text": full_response}

        # Add delete button immediately after the response
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Delete", key=f"delete_{idx}"):
                delete_message(idx)
                st.experimental_rerun()

def clear_chat_window():
    st.session_state.history = []
    st.session_state.history_pic = []
    st.experimental_rerun()

def clear_state():
    st.session_state.history_pic = []

if "history_pic" not in st.session_state:
    st.session_state.history_pic = []

image = None
if "app_key" in st.session_state:
    uploaded_file = st.file_uploader("Choose a pic...", type=["jpg", "png", "jpeg", "gif"], label_visibility='collapsed', key='file_uploader', on_change=clear_state)
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        width, height = image.size
        resized_img = image.resize((128, int(height / (width / 128))), Image.LANCZOS)
        st.image(image)

def delete_message(idx):
    del st.session_state.history_pic[idx]

if len(st.session_state.history_pic) > 0:
    for idx, item in enumerate(st.session_state.history_pic):
        with st.chat_message(item["role"]):
            st.markdown(item["text"])
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("Delete", key=f"delete_{idx}_history"):
                    delete_message(idx)
                    st.experimental_rerun()

if "app_key" in st.session_state:
    if prompt := st.chat_input("Describe this picture", key='prompt_input'):
        if image is None:
            st.warning("Please upload an image first", icon="⚠️")
        else:
            prompt = prompt.replace('\n', '  \n')
            with st.chat_message("user"):
                st.markdown(prompt)
                st.session_state.history_pic.append({"role": "user", "text": prompt})
                idx = len(st.session_state.history_pic) - 1

            show_message(prompt, resized_img, "Thinking...", idx)
