import streamlit as st
import aiml
import pandas as pd
import os

# Set up paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AIML_PATH = os.path.join(BASE_DIR, "shopassistbot.aiml")
DATA_PATH = os.path.join(BASE_DIR, "diversified_ecommerce_dataset.csv")

@st.cache_resource
def load_bot():
    kernel = aiml.Kernel()
    if os.path.exists(AIML_PATH):
        kernel.learn(AIML_PATH)
    return kernel

@st.cache_data
def load_data():
    if os.path.exists(DATA_PATH):
        return pd.read_csv(DATA_PATH)
    return pd.DataFrame()

bot = load_bot()
df = load_data()

def get_recommendation(category, budget):
    try:
        budget_val = float(budget)
        # Filter by category and price from your dataset
        results = df[(df['Category'].str.upper() == category.upper()) & (df['Price'] <= budget_val)]
        if results.empty:
            return f"I couldn't find any {category} under RM{budget_val}."
        
        # Sort by popularity index
        top = results.sort_values(by="Popularity Index", ascending=False).head(3)
        msg = f"✨ Top picks for {category}:\n\n"
        for _, row in top.iterrows():
            msg += f"👉 {row['Product Name']} (RM{row['Price']}) ⭐{row['Popularity Index']}\n"
        return msg
    except:
        return "Please enter a valid budget."

st.title("🛍️ ShopAssist AI")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Type 'Hello'"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Logic: Budget vs AIML conversation
    if prompt.strip().isdigit():
        cat = bot.getPredicate("category")
        response = get_recommendation(cat, prompt.strip()) if cat else "What category are you looking for?"
    else:
        response = bot.respond(prompt.upper())

    if not response:
        response = "I'm still learning! Try 'Show categories'."

    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)
