import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit.components.v1 as components

# Rename main page to match the content
st.set_page_config(
    page_title="Not Ready Time Analysis",
    page_icon="⏱️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# Hide the default menu button and Streamlit footer
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
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

# Add custom JavaScript to rename the sidebar item
components.html(
    """
    <script>
        window.parent.document.querySelector("span.st-emotion-cache-16idsys").innerText = "Not Ready Time Analysis";
    </script>
    """,
    height=0,
)

# Rename the page in the sidebar
st.sidebar.header("Not Ready Time Analysis")

st.title("⏱️ Not Ready Time Analysis")
st.markdown("""
    This dashboard analyzes agent not ready time data. Upload your CSV file to get started.
    
    The CSV should contain these columns:
    - `AGENT NAME`
    - `NOT READY TIME` (in HH:MM:SS format)
    - `DATE`
""")

def time_to_seconds(time_str):
    try:
        h, m, s = map(int, time_str.split(':'))
        return h * 3600 + m * 60 + s
    except:
        return 0

def create_visualizations(df):
    try:
        # Convert NOT READY TIME to seconds
        df['NOT READY SECONDS'] = df['NOT READY TIME'].apply(time_to_seconds)
        
        # Convert DATE to datetime
        df['DATE'] = pd.to_datetime(df['DATE'])
        
        # Calculate total not ready time per agent
        agent_total = df.groupby('AGENT NAME')['NOT READY SECONDS'].sum().sort_values(ascending=False)
        
        # Create metrics
        st.markdown("### Metrics")
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1.2])
        
        with col2:
            st.metric("👥 Total Agents", len(agent_total))
        with col4:
            st.metric("⏱️ Total Not Ready Hours", f"{(df['NOT READY SECONDS'].sum() / 3600):.2f}")
        with col3:
            st.metric("⌛ Avg Minutes per Agent", f"{(df['NOT READY SECONDS'].mean() / 60):.2f}")
        with col1:
            start_date = df['DATE'].min().strftime('%m/%d')
            end_date = df['DATE'].max().strftime('%m/%d/%y')
            st.metric("Date Range", f"{start_date} → {end_date}")
        
        # Create tabs for different views
        tab1, tab2 = st.tabs(["📊 Charts", "📑 Detailed Data"])
        
        with tab1:
            # Create a subplot with two charts
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('Total Not Ready Time by Agent', 'Daily Not Ready Time Trend'),
                vertical_spacing=0.3,
                specs=[[{"type": "bar"}], [{"type": "scatter"}]]
            )
            
            # Add bar chart for total not ready time per agent
            fig.add_trace(
                go.Bar(
                    x=agent_total.index,
                    y=agent_total.values / 3600,  # Convert to hours
                    name='Total Not Ready Time',
                    marker_color='rgb(55, 83, 109)'
                ),
                row=1, col=1
            )
            
            # Calculate daily average not ready time
            daily_avg = df.groupby('DATE')['NOT READY SECONDS'].mean().reset_index()
            
            # Add line chart for daily trend
            fig.add_trace(
                go.Scatter(
                    x=daily_avg['DATE'],
                    y=daily_avg['NOT READY SECONDS'] / 60,  # Convert to minutes
                    mode='lines+markers',
                    name='Average Not Ready Time',
                    line=dict(color='rgb(26, 118, 255)')
                ),
                row=2, col=1
            )
            
            # Update layout
            fig.update_layout(
                height=800,
                showlegend=False,
                title_text='Not Ready Time Analysis',
                title_x=0.5
            )
            
            # Update y-axes labels
            fig.update_yaxes(title_text="Hours", row=1, col=1)
            fig.update_yaxes(title_text="Minutes", row=2, col=1)
            
            # Update x-axes labels
            fig.update_xaxes(title_text="Agent Name", row=1, col=1, tickangle=45)
            fig.update_xaxes(title_text="Date", row=2, col=1)
            
            # Display the figure in Streamlit
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            # Add date filter for detailed view
            st.subheader("📅 Daily Not Ready Time Details")
            date_range = st.date_input(
                "Select Date Range",
                [df['DATE'].min(), df['DATE'].max()],
                min_value=df['DATE'].min().date(),
                max_value=df['DATE'].max().date()
            )
            
            if len(date_range) == 2:
                mask = (df['DATE'].dt.date >= date_range[0]) & (df['DATE'].dt.date <= date_range[1])
                filtered_df = df[mask]
                
                # Calculate daily statistics
                daily_stats = filtered_df.groupby(['DATE', 'AGENT NAME'])['NOT READY SECONDS'].sum().reset_index()
                daily_stats['NOT READY HOURS'] = daily_stats['NOT READY SECONDS'] / 3600
                
                # Display the dataframe
                st.dataframe(
                    daily_stats.style.format({
                        'DATE': lambda x: x.strftime('%Y-%m-%d'),
                        'NOT READY HOURS': '{:.2f}'
                    }),
                    hide_index=True,
                    height=400
                )
                
                # Add download button for filtered data
                csv = daily_stats.to_csv(index=False)
                st.download_button(
                    label="📥 Download Filtered Data",
                    data=csv,
                    file_name="not_ready_time_filtered.csv",
                    mime="text/csv"
                )

    except Exception as e:
        st.error(f"Error processing the data: {str(e)}")
        st.error("Please make sure your CSV file is in the correct format")

# File uploader
uploaded_file = st.file_uploader("Upload your Not Ready Time CSV file", type=['csv'])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        required_columns = ['AGENT NAME', 'NOT READY TIME', 'DATE']
        if all(col in df.columns for col in required_columns):
            create_visualizations(df)
        else:
            st.error(f"The CSV file must contain these columns: {', '.join(required_columns)}")
    except Exception as e:
        st.error(f"Error reading the file: {str(e)}")
else:
    st.info("👆 Please upload a CSV file to begin the analysis.")
