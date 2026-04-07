import streamlit as st
import aiml
import pandas as pd
import os

# -----------------------------
# Load AIML bot
# -----------------------------
@st.cache_resource
def load_bot():
    kernel = aiml.Kernel()
    # Check if file exists to avoid silent errors
    if os.path.exists("shopassistbot.aiml"):
        kernel.learn("shopassistbot.aiml")
    else:
        st.error("Error: 'shopassistbot.aiml' not found in the directory!")
    return kernel

bot = load_bot()

# -----------------------------
# Load Dataset
# -----------------------------
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("files/diversified_ecommerce_dataset.csv")
        return df
    except Exception as e:
        st.error(f"Could not load CSV: {e}")
        return pd.DataFrame()

data = load_data()

# -----------------------------
# Recommendation Function
# -----------------------------
def get_recommendation(category, budget):
    try:
        budget_val = float(budget)
    except:
        return "⚠️ Please enter a numerical budget."

    # Filter by category and price
    filtered = data[
        (data["Category"].str.upper() == category.upper()) &
        (data["Price"] <= budget_val)
    ]

    if filtered.empty:
        return f"😅 No products found in {category} under RM{budget}."

    # Sort by popularity and get top 3
    top = filtered.sort_values(by="Popularity Index", ascending=False).head(3)

    result = f"✨ Top recommendations for {category}:\n\n"
    for _, row in top.iterrows():
        result += f"👉 {row['Product Name']} (RM{row['Price']}) ⭐{row['Popularity Index']}\n"
    return result

# -----------------------------
# UI
# -----------------------------
st.title("🛍️ Smart Shopping Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Input
user_input = st.chat_input("Say 'Hello' or 'I want electronics'")

if user_input:
    # 1. Store user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # 2. Get AIML response (AIML is case-insensitive by default)
    response = bot.respond(user_input)

    # 3. Logic for Recommendation Engine
    # If the input is just a number, we treat it as a budget request
    if user_input.strip().isdigit():
        stored_cat = bot.getPredicate("category")
        if stored_cat:
            response = get_recommendation(stored_cat, user_input.strip())
        else:
            response = "I need to know what you are looking for first! Try 'I want electronics'."

    # 4. Fallback if AIML returned nothing
    if not response or response.strip() == "":
        response = "😅 Try saying 'Hello', 'Show categories', or 'I want electronics'."

    # 5. Store and display bot message
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()
