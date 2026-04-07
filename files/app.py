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
    
    # Get the absolute path of the current directory
    base_path = os.path.dirname(os.path.abspath(__file__))
    aiml_path = os.path.join(base_path, "shopassistbot.aiml")
    
    if os.path.exists(aiml_path):
        kernel.learn(aiml_path)
        st.sidebar.success("✅ shopassistbot.aiml loaded!")
    else:
        st.sidebar.error("❌ shopassistbot.aiml NOT FOUND!")
        
    return kernel

bot = load_bot()

# -----------------------------
# 📊 Load Dataset
# -----------------------------
@st.cache_data
def load_data():
    try:
        # Standardize path for the CSV
        base_path = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(base_path, "files", "diversified_ecommerce_dataset.csv")
        return pd.read_csv(csv_path)
    except:
        return pd.DataFrame()

data = load_data()

# 💡 Recommendation Logic
def get_recommendation(category, budget):
    try:
        budget_val = float(budget)
        filtered = data[(data["Category"].str.upper() == category.upper()) & (data["Price"] <= budget_val)]
        if filtered.empty:
            return f"😅 No {category} found under RM{budget_val}."
        top = filtered.sort_values(by="Popularity Index", ascending=False).head(3)
        res = f"✨ Recommendations for {category}:\n\n"
        for _, row in top.iterrows():
            res += f"👉 {row['Product Name']} (RM{row['Price']}) ⭐{row['Popularity Index']}\n"
        return res
    except:
        return "⚠️ Please enter a number for the budget."

# -----------------------------
# 🖥️ Chat UI
# -----------------------------
st.title("🛍️ Smart Shopping Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_input = st.chat_input("Say 'HELLO' to start")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # AIML lookup (Send as Uppercase to match pattern exactly)
    response = bot.respond(user_input.upper())

    # Budget logic
    if user_input.strip().isdigit():
        cat = bot.getPredicate("category")
        if cat:
            response = get_recommendation(cat, user_input.strip())

    # The Fallback
    if not response or response.strip() == "":
        response = "😅 I didn't find a match in my AIML file. Try 'HELLO'."

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()
