import streamlit as st
import aiml

# -----------------------------
# Load AIML bot (cached)
# -----------------------------
@st.cache_resource
def load_bot():
    kernel = aiml.Kernel()
    kernel.learn("shopassistbot.aiml")  # make sure path is correct
    return kernel

bot = load_bot()

# -----------------------------
# UI Title
# -----------------------------
st.title("🛍️ Smart Shopping Assistant")

# -----------------------------
# Session state (chat history)
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Clear old string-format messages (important fix)
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
# INPUT FORM (prevents loop ✅)
# -----------------------------
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("Type your message:")
    submitted = st.form_submit_button("Send")

# -----------------------------
# Handle input
# -----------------------------
if submitted and user_input:
    # Convert to uppercase (AIML needs this)
    response = bot.respond(user_input.upper())

    # Fallback if AIML fails
    if response.strip() == "":
        response = "😅 Sorry, I didn't understand that. Try 'Show categories' or 'I want electronics'."

    # Save messages
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })
    st.session_state.messages.append({
        "role": "bot",
        "content": response
    })

    # Refresh UI
    st.rerun()

# -----------------------------
# Optional: Clear chat button
# -----------------------------
if st.button("🗑️ Clear Chat"):
    st.session_state.messages = []
    st.rerun()
