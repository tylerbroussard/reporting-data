import streamlit as st

st.set_page_config(
    page_title="Agent Analytics",
    page_icon="📊",
    layout="wide"
)

st.title("Agent Analytics")

col1, col2 = st.columns(2)

with col1:
    st.link_button("⏱️ Not Ready Time Analysis", "Not_Ready_Analysis", use_container_width=True)

with col2:
    st.link_button("📞 Agent Productivity Exceptions", "Productivity_Exceptions", use_container_width=True)
