import streamlit as st
import aiml
import os

# Initialize kernel
@st.cache_resource
def load_bot():
    kernel = aiml.Kernel()
    kernel.learn("shopassistbot.aiml")
    return kernel

bot = load_bot()

st.title("🛍️ Smart Shopping Assistant")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display messages
for msg in st.session_state.messages:
    st.write(msg)

# User input
user_input = st.text_input("You:", "")

if st.button("Send"):
    if user_input:
        response = bot.respond(user_input)

        st.session_state.messages.append(f"👤: {user_input}")
        st.session_state.messages.append(f"🤖: {response}")
