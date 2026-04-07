import streamlit as st
import aiml

# -----------------------------
# Load AIML bot (cached)
# -----------------------------
@st.cache_resource
def load_bot():
    kernel = aiml.Kernel()
    kernel.learn("shopassistbot.aiml")  # make sure file path is correct
    return kernel

bot = load_bot()

# -----------------------------
# UI Title
# -----------------------------
st.title("🛍️ Smart Shopping Assistant")

# -----------------------------
# Session state for chat history
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
else:
    # Clear old incompatible messages
    if len(st.session_state.messages) > 0 and isinstance(st.session_state.messages[0], str):
        st.session_state.messages = []

# -----------------------------
# Display chat history
# -----------------------------
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"👤 **You:** {msg['content']}")
    else:
        st.markdown(f"🤖 **Bot:** {msg['content']}")

# -----------------------------
# User input
# -----------------------------
user_input = st.text_input("Type your message:")

# -----------------------------
# Handle input (NO BUTTON needed)
# -----------------------------
if user_input:
    # Convert to uppercase (IMPORTANT for AIML)
    response = bot.respond(user_input.upper())

    # Fallback if no response
    if response.strip() == "":
        response = "😅 Sorry, I didn't understand that. Try something like 'I want electronics'."

    # Save messages
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.messages.append({"role": "bot", "content": response})

    # Rerun to refresh UI
    st.rerun()
