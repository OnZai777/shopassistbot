import streamlit as st
import aiml
import pandas as pd
import os

# -----------------------------
# 🤖 Load AIML bot
# -----------------------------
@st.cache_resource
def load_bot():
    kernel = aiml.Kernel()
    # Check if the file exists to prevent silent crashes
    if os.path.exists("shopassistbot.aiml"):
        kernel.learn("shopassistbot.aiml")
    else:
        st.error("❌ 'shopassistbot.aiml' not found! Please ensure the file is in the same folder.")
    return kernel

bot = load_bot()

# -----------------------------
# 📊 Load Dataset
# -----------------------------
@st.cache_data
def load_data():
    try:
        # Ensure your CSV is in a folder named 'files'
        df = pd.read_csv("files/diversified_ecommerce_dataset.csv")
        return df
    except Exception as e:
        st.error(f"❌ Dataset error: {e}")
        return pd.DataFrame()

data = load_data()

# -----------------------------
# 💡 Recommendation Logic
# -----------------------------
def get_recommendation(category, budget):
    try:
        budget_val = float(budget)
    except:
        return "⚠️ Please enter a valid number for your budget."

    # Filter by category and price limit
    filtered = data[
        (data["Category"].str.upper() == category.upper()) &
        (data["Price"] <= budget_val)
    ]

    if filtered.empty:
        return f"😅 Sorry, I couldn't find any {category} under RM{budget_val}."

    # Sort by Popularity and take top 3
    top = filtered.sort_values(by="Popularity Index", ascending=False).head(3)

    result = f"✨ Here are the top {category} recommendations within your budget:\n\n"
    for _, row in top.iterrows():
        result += f"👉 **{row['Product Name']}** - RM{row['Price']} (Rating: {row['Popularity Index']})\n"
    return result

# -----------------------------
# 🖥️ User Interface
# -----------------------------
st.title("🛍️ Smart Shopping Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# User Chat Input
user_input = st.chat_input("Type 'Hello', 'Show categories', or 'I want electronics'...")

if user_input:
    # 1. Show user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # 2. Process with AIML
    # We send raw input; aiml-python handles case-insensitivity automatically.
    response = bot.respond(user_input)

    # 3. Check for Recommendation Trigger
    # If the user enters a number and we have a category stored in AIML memory
    if user_input.strip().isdigit():
        stored_category = bot.getPredicate("category")
        if stored_category:
            response = get_recommendation(stored_category, user_input.strip())
        else:
            response = "I'm not sure what you're looking for yet. Try saying 'I want electronics' first!"

    # 4. Fallback for empty responses
    if not response or response.strip() == "":
        response = "😅 I'm not sure how to help with that. Try 'Show categories'!"

    # 5. Show bot response
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()
