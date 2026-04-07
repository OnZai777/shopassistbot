import streamlit as st
import aiml
import pandas as pd
import os

# --- DEBUGGING: Check if file exists ---
aiml_file = "shopassistbot.aiml"
if not os.path.exists(aiml_file):
    st.error(f"🚨 CRITICAL ERROR: '{aiml_file}' not found in the current folder!")

# -----------------------------
# 🤖 Load AIML bot
# -----------------------------
@st.cache_resource
def load_bot():
    kernel = aiml.Kernel()
    # Forces the kernel to learn the file
    kernel.learn(aiml_file)
    return kernel

bot = load_bot()

# -----------------------------
# 📊 Load Dataset
# -----------------------------
@st.cache_data
def load_data():
    try:
        # Note: Ensure the 'files' folder exists!
        df = pd.read_csv("files/diversified_ecommerce_dataset.csv")
        return df
    except Exception:
        return pd.DataFrame(columns=["Product Name", "Category", "Price", "Popularity Index"])

data = load_data()

# -----------------------------
# 💡 Recommendation Logic
# -----------------------------
def get_recommendation(category, budget):
    try:
        budget_val = float(budget)
        filtered = data[
            (data["Category"].str.upper() == category.upper()) & 
            (data["Price"] <= budget_val)
        ]
        if filtered.empty:
            return f"😅 No products found in {category} under RM{budget_val}."
        
        top = filtered.sort_values(by="Popularity Index", ascending=False).head(3)
        result = f"✨ Top {category} recommendations:\n\n"
        for _, row in top.iterrows():
            result += f"👉 {row['Product Name']} (RM{row['Price']}) ⭐{row['Popularity Index']}\n"
        return result
    except:
        return "⚠️ Please enter a number for the budget."

# -----------------------------
# 🖥️ UI
# -----------------------------
st.title("🛍️ Smart Shopping Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_input = st.chat_input("Type 'Hello'...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # 1. Get AIML response
    # We strip and upper the input for the most reliable pattern matching
    response = bot.respond(user_input.upper())

    # 2. Check if input is a budget
    if user_input.strip().isdigit():
        cat = bot.getPredicate("category")
        if cat:
            response = get_recommendation(cat, user_input.strip())

    # 3. Final Fallback
    if not response or response.strip() == "":
        response = "😅 I'm still learning! Try 'HELLO' or 'I WANT ELECTRONICS'."

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()
