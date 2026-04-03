import streamlit as st
import aiml
import os

# --- STEP 1: INITIALIZE AIML ---
@st.cache_resource
def get_bot():
    kernel = aiml.Kernel()
    # Path to your AIML file
    aiml_path = "shopassistbot.aiml"
    if os.path.exists(aiml_path):
        kernel.learn(aiml_path)
    else:
        st.error(f"Error: {aiml_path} not found!")
    return kernel

bot = get_bot()

# --- STEP 2: STREAMLIT UI ---
st.set_page_config(page_title="AI Shopping Assistant", page_icon="🤖")
st.title("🛒 AI Shopping Assistant")
st.caption("Powered by AIML and Streamlit")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Trigger the 'HELLO' pattern automatically to start the session
    initial_response = bot.respond("HELLO")
    st.session_state.messages.append({"role": "assistant", "content": initial_response})

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("How can I help you?"):
    # Display user message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Get response from AIML
    response = bot.respond(prompt)

    # Display assistant response
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
