import streamlit as st
import aiml
import pandas as pd
import os

# --- PATH SETUP ---
base_path = os.path.dirname(os.path.abspath(__file__))
aiml_path = os.path.join(base_path, "shopassistbot.aiml")
csv_path = os.path.join(base_path, "files", "diversified_ecommerce_dataset.csv")

# -----------------------------
# 🤖 Load AIML bot
# -----------------------------
def init_bot():
    kernel = aiml.Kernel()
    if os.path.exists(aiml_path):
        # We use learn() directly to ensure it reads the latest file
        kernel.learn(aiml_path)
        return kernel
    else:
        st.error(f"Missing file at: {aiml_path}")
        return None

if "bot" not in st.session_state:
    st.session_state.bot = init_bot()

# -----------------------------
# 📊 Load Dataset
# -----------------------------
@st.cache_data
def load_data():
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    return pd.DataFrame()

df = load_data()

# 💡 Recommendation Logic
def get_recommendation(category, budget):
    try:
        budget_val = float(budget)
        filtered = df[(df["Category"].str.upper() == category.upper()) & (df["Price"] <= budget_val)]
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

# Sidebar Debugging
with st.sidebar:
    if st.button("🔄 Force Reload AIML"):
        st.session_state.bot = init_bot()
        st.success("Bot reloaded!")
    if os.path.exists(aiml_path):
        st.write("✅ AIML file detected.")
    else:
        st.write("❌ AIML file NOT found.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_input = st.chat_input("Type 'HELLO'")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Send to AIML (using .upper() to guarantee match)
    response = ""
    if st.session_state.bot:
        response = st.session_state.bot.respond(user_input.upper())

    # Budget logic: If input is a number
    if user_input.strip().isdigit():
        cat = st.session_state.bot.getPredicate("category")
        if cat:
            response = get_recommendation(cat, user_input.strip())
        else:
            response = "I don't know what you're looking for! Say 'I want electronics' first."

    # Final Fallback
    if not response or response.strip() == "":
        response = "😅 My brain is empty! Make sure the AIML file has a pattern for this."

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()
