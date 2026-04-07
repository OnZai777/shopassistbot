import streamlit as st
import aiml
import pandas as pd

# -----------------------------
# 🔧 Normalize user input
# -----------------------------
def normalize_input(text):
    # We remove .upper() here to let the AIML kernel handle case-insensitivity 
    # and focus only on synonym replacement.
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
    return " ".join(words)


# -----------------------------
# Load AIML bot
# -----------------------------
@st.cache_resource
def load_bot():
    kernel = aiml.Kernel()
    # Ensure the filename matches exactly
    kernel.learn("shopassistbot.aiml")
    return kernel

bot = load_bot()


# -----------------------------
# Load Dataset
# -----------------------------
@st.cache_data
def load_data():
    # Make sure this path exists in your directory
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
        return "⚠️ Please enter a valid numerical budget (e.g., 500)."

    # Filter data based on category (case-insensitive) and price
    filtered = data[
        (data["Category"].str.upper() == category.upper()) &
        (data["Price"] <= budget)
    ]

    if filtered.empty:
        return f"😅 No products found in {category} within RM{budget}."

    # Sort by popularity and get top 3
    filtered = filtered.sort_values(by="Popularity Index", ascending=False)
    top = filtered.head(3)

    result = f"✨ Top recommendations for {category}:\n\n"
    for _, row in top.iterrows():
        result += f"👉 {row['Product Name']} (RM{row['Price']}) ⭐{row['Popularity Index']}\n"

    return result


# -----------------------------
# UI Setup
# -----------------------------
st.set_page_config(page_title="Smart Shopping Assistant", page_icon="🛍️")
st.title("🛍️ Smart Shopping Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input
user_input = st.chat_input("Type your message (e.g., 'I want electronics' or 'Show categories')")

# -----------------------------
# Handle Input
# -----------------------------
if user_input:
    # 1. Normalize for synonyms
    clean_input = normalize_input(user_input)

    # 2. Get response from AIML
    response = bot.respond(clean_input)

    # 3. Check if input is a budget (digit) and we have a category stored
    if user_input.strip().isdigit():
        current_category = bot.getPredicate("category")
        if current_category:
            response = get_recommendation(current_category, user_input.strip())
        else:
            response = "What category are you interested in first? (Electronics, Books, etc.)"

    # 4. Fallback if AIML doesn't match anything
    if not response or response.strip() == "":
        response = "😅 Try saying 'I want electronics' or 'Show categories' to get started!"

    # Save and Refresh
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()

# Sidebar controls
with st.sidebar:
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()
