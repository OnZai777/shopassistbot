import streamlit as st
import aiml
import pandas as pd

# -----------------------------
# 🔧 Normalize user input
# -----------------------------
def normalize_input(text):
    text = text.lower().strip()

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

        "shoe": "footwear",
        "shoes": "footwear",
        "sneaker": "footwear"
    }

    words = text.split()
    words = [synonyms.get(word, word) for word in words]

    return " ".join(words).upper()


# -----------------------------
# Load AIML bot
# -----------------------------
@st.cache_resource
def load_bot():
    kernel = aiml.Kernel()
    kernel.learn("shopassistbot.aiml")
    return kernel

bot = load_bot()


# -----------------------------
# Load Dataset
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("files/diversified_ecommerce_dataset.csv")
    return df

data = load_data()


# -----------------------------
# Recommendation Function
# -----------------------------
def get_recommendation(category, budget):
    try:
        budget = float(budget)
    except:
        return "⚠️ Please enter a valid number."

    filtered = data[
        (data["Category"].str.upper() == category) &
        (data["Price"] <= budget)
    ]

    if filtered.empty:
        return "😅 No products found within your budget."

    filtered = filtered.sort_values(by="Popularity Index", ascending=False)

    top = filtered.head(3)

    result = "✨ Top recommendations:\n\n"
    for _, row in top.iterrows():
        result += f"👉 {row['Product Name']} (RM{row['Price']}) ⭐{row['Popularity Index']}\n"

    return result


# -----------------------------
# UI
# -----------------------------
st.title("🛍️ Smart Shopping Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"👤 **You:** {msg['content']}")
    else:
        st.markdown(f"🤖 **Bot:** {msg['content']}")

# Input
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("Type your message:")
    submitted = st.form_submit_button("Send")

# -----------------------------
# Handle Input
# -----------------------------
if submitted and user_input:
    clean_input = normalize_input(user_input)

    # AIML response
    response = bot.respond(clean_input)

    # Check if user gave budget (number)
    if user_input.strip().isdigit():
        category = bot.getPredicate("category")
        budget = user_input.strip()

        if category:
            response = get_recommendation(category, budget)

    # Fallback
    if response.strip() == "":
        response = "😅 Try 'I want electronics' or 'Show categories'."

    # Save messages
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.messages.append({"role": "bot", "content": response})

    st.rerun()

# Clear chat
if st.button("🗑️ Clear Chat"):
    st.session_state.messages = []
    st.rerun()

st.write("DEBUG INPUT:", clean_input)
