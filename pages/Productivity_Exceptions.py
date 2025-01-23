import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Productivity Exceptions", layout="wide")

# Add custom CSS
st.markdown("""
    <style>
    .main {
        padding: 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    div[data-testid="stMetricValue"] > div {
        font-size: 1.2rem !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📞 Agent Productivity Exceptions")
st.markdown("""
    This dashboard analyzes agent productivity exceptions. Upload your CSV file to get started.
    
    The CSV should contain these columns:
    - `AGENT GROUP`
    - `AGENT`
    - `CALLS count`
    - Various exception columns (e.g., LONG CALLS count, SHORT CALLS count, etc.)
""")

def create_visualizations(df):
    try:
        # Calculate summary metrics
        total_agents = len(df['AGENT'].unique())
        total_calls = df['CALLS count'].sum()
        total_long_calls = df['LONG CALLS count'].sum()
        total_disconnects = df['AGENT DISCONNECTS FIRST count'].sum()
        
        # Create metrics
        st.markdown("### Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Agents", total_agents)
        with col2:
            st.metric("Total Calls", total_calls)
        with col3:
            st.metric("Long Calls", total_long_calls)
        with col4:
            st.metric("Agent Disconnects", total_disconnects)
            
        # Create tabs for different views
        tab1, tab2 = st.tabs(["📊 Charts", "📑 Detailed Data"])
        
        with tab1:
            # Create charts
            col1, col2 = st.columns(2)
            
            with col1:
                # Calls by Agent Group
                group_calls = df.groupby('AGENT GROUP')['CALLS count'].sum().sort_values(ascending=True)
                fig_group = go.Figure(go.Bar(
                    x=group_calls.values,
                    y=group_calls.index,
                    orientation='h'
                ))
                fig_group.update_layout(
                    title='Total Calls by Agent Group',
                    height=400,
                    margin=dict(l=200)
                )
                st.plotly_chart(fig_group, use_container_width=True)
            
            with col2:
                # Exception Types Distribution
                exception_cols = ['LONG CALLS count', 'SHORT CALLS count', 'AGENT DISCONNECTS FIRST count', 
                                'DISCONNECTED FROM HOLD count', 'LONG HOLDS count']
                exceptions = df[exception_cols].sum()
                fig_exceptions = go.Figure(go.Bar(
                    x=exceptions.values,
                    y=[col.replace(' count', '').title() for col in exceptions.index],
                    orientation='h'
                ))
                fig_exceptions.update_layout(
                    title='Exception Types Distribution',
                    height=400,
                    margin=dict(l=200)
                )
                st.plotly_chart(fig_exceptions, use_container_width=True)
            
            # Add Top Agents chart
            st.subheader("Top Agents by Exception Type")
            exception_type = st.selectbox(
                "Select Exception Type",
                ['LONG CALLS count', 'SHORT CALLS count', 'AGENT DISCONNECTS FIRST count', 
                 'DISCONNECTED FROM HOLD count', 'LONG HOLDS count']
            )
            
            top_agents = df.nlargest(10, exception_type)[['AGENT', 'AGENT GROUP', exception_type]]
            fig_top = go.Figure(go.Bar(
                x=top_agents[exception_type],
                y=top_agents['AGENT'] + ' (' + top_agents['AGENT GROUP'] + ')',
                orientation='h'
            ))
            fig_top.update_layout(
                title=f'Top 10 Agents by {exception_type.replace(" count", "")}',
                height=400,
                margin=dict(l=300)
            )
            st.plotly_chart(fig_top, use_container_width=True)
        
        with tab2:
            # Add agent group filter
            groups = sorted(df['AGENT GROUP'].unique())
            selected_groups = st.multiselect(
                "Filter by Agent Group",
                groups,
                default=[]
            )
            
            # Filter data
            if selected_groups:
                display_df = df[df['AGENT GROUP'].isin(selected_groups)]
            else:
                display_df = df
            
            # Display the dataframe
            st.dataframe(
                display_df[[
                    'AGENT GROUP', 'AGENT', 'CALLS count', 'LONG CALLS count',
                    'AGENT DISCONNECTS FIRST count', 'DISCONNECTED FROM HOLD count',
                    'LONG HOLDS count'
                ]],
                hide_index=True,
                height=400
            )
            
            # Add download button
            csv = display_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Filtered Data",
                data=csv,
                file_name="agent_productivity_filtered.csv",
                mime="text/csv"
            )
            
    except Exception as e:
        st.error(f"Error processing the data: {str(e)}")
        st.error("Please make sure your CSV file is in the correct format")

# File uploader
uploaded_file = st.file_uploader("Upload your Agent Productivity CSV file", type=['csv'])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        required_columns = ['AGENT GROUP', 'AGENT', 'CALLS count']
        if all(col in df.columns for col in required_columns):
            create_visualizations(df)
        else:
            st.error(f"The CSV file must contain these columns: {', '.join(required_columns)}")
    except Exception as e:
        st.error(f"Error reading the file: {str(e)}")
else:
    st.info("👆 Please upload a CSV file to begin the analysis.")
