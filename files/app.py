import streamlit as st
import aiml

# -----------------------------
# 🔧 Normalize user input (NEW)
# -----------------------------
def normalize_input(text):
    text = text.lower().strip()

    # Synonym mapping
    synonyms = {
        "electronic": "electronics",
        "device": "electronics",
        "gadget": "electronics",
        "phone": "electronics",
        "laptop": "electronics",

        "book": "books",
        "novel": "books",
        "comic": "books",

        "clothes": "apparel",
        "shirt": "apparel",
        "tshirt": "apparel",

        "shoe": "footwear",
        "shoes": "footwear",
        "sneaker": "footwear",
        "sneakers": "footwear"
    }

    words = text.split()
    words = [synonyms.get(word, word) for word in words]

    return " ".join(words).upper()


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

# Fix old format messages
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
# INPUT FORM
# -----------------------------
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("Type your message:")
    submitted = st.form_submit_button("Send")

# -----------------------------
# Handle input
# -----------------------------
if submitted and user_input:
    clean_input = normalize_input(user_input)

    # Optional debug (turn on if needed)
    # st.write("DEBUG:", clean_input)

    # Handle empty intent like "I want"
    if clean_input.strip() == "I WANT":
        response = "Please tell me a category 😊 (e.g., electronics, books, apparel, footwear)"
    else:
        response = bot.respond(clean_input)

    # -----------------------------
    # Smart fallback (IMPROVED)
    # -----------------------------
    if response.strip() == "":
        user_lower = user_input.lower()

        if any(word in user_lower for word in ["electronic", "phone", "laptop", "gadget"]):
            response = "Did you mean electronics? Try 'I want electronics' 😊"

        elif any(word in user_lower for word in ["book", "novel", "comic"]):
            response = "Try 'I want books' 📚"

        elif any(word in user_lower for word in ["shoe", "sneaker"]):
            response = "Try 'I want footwear' 👟"

        elif any(word in user_lower for word in ["shirt", "clothes"]):
            response = "Try 'I want apparel' 👕"

        else:
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

    st.rerun()

# -----------------------------
# Clear chat button
# -----------------------------
if st.button("🗑️ Clear Chat"):
    st.session_state.messages = []
    st.rerun()
