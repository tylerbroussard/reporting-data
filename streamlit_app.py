import streamlit as st

st.set_page_config(
    page_title="Agent Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Agent Analytics Dashboard")

# Add custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    h1 {
        margin-bottom: 2rem;
    }
    h3 {
        margin-top: 2rem;
    }
    .highlight {
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Welcome message
st.markdown("""
Welcome to the Five9 Agent Analytics Dashboard! This application helps you analyze agent performance data.
""")

# Report descriptions in highlighted boxes
st.markdown("""
<div class="highlight">
<h3>⏱️ Not Ready Time Analysis</h3>
<ul>
<li>Track agent not ready time</li>
<li>View daily trends and patterns</li>
<li>Analyze individual agent performance</li>
</ul>
</div>

<div class="highlight">
<h3>📞 Agent Productivity Exceptions</h3>
<ul>
<li>Monitor call handling exceptions</li>
<li>Analyze performance by agent group</li>
<li>Track various exception types</li>
</ul>
</div>
""", unsafe_allow_html=True)

# Instructions
st.markdown("""
### Getting Started

1. Select a report from the sidebar on the left
2. Upload the corresponding CSV file
3. Explore the interactive visualizations and data

Each report page includes specific instructions about the required CSV format and available features.
""")
