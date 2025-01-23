import streamlit as st

st.set_page_config(
    page_title="Agent Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Agent Analytics Dashboard")
st.markdown("""
Welcome to the Agent Analytics Dashboard! This application provides comprehensive analytics for your contact center operations.

### Available Reports

1. **⏱️ Not Ready Time Analysis**
   - Track agent not ready time
   - View daily trends and patterns
   - Analyze individual agent performance

2. **📞 Agent Productivity Exceptions**
   - Monitor call handling exceptions
   - Analyze performance by agent group
   - Track various exception types

### How to Use

1. Select a report from the sidebar on the left
2. Upload the corresponding CSV file
3. Explore the interactive visualizations and data

### Need Help?

Each report page includes specific instructions about the required CSV format and available features.
""")

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
    </style>
""", unsafe_allow_html=True)
