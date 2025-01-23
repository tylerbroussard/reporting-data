import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime

st.set_page_config(
    page_title="Agent Occupancy Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS
st.markdown("""
    <style>
    .main {
        padding: 1rem;
    }
    .metric-row {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .stMetric {
        background-color: white !important;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
    }
    div[data-testid="stMetricValue"] > div {
        font-size: 1.2rem !important;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

st.title("📊 Agent Occupancy Analysis")
st.markdown("""
    This dashboard provides detailed insights into agent occupancy, utilization, and time distribution metrics.
    Upload your CSV file to begin the analysis.
""")

def time_to_seconds(time_str):
    """Convert time string to seconds"""
    if pd.isna(time_str) or time_str == '' or not isinstance(time_str, str):
        return 0
    try:
        h, m, s = map(int, time_str.split(':'))
        return h * 3600 + m * 60 + s
    except Exception as e:
        st.write(f"Error converting time {time_str}: {str(e)}")
        return 0

def format_time(seconds):
    """Format seconds to HH:MM"""
    if not isinstance(seconds, (int, float)) or pd.isna(seconds):
        return "00:00"
    hours = int(seconds) // 3600
    minutes = (int(seconds) % 3600) // 60
    return f"{hours:02d}:{minutes:02d}"

def format_percentage(value):
    """Format value as percentage"""
    if pd.isna(value):
        return "0.0%"
    return f"{float(value):.1f}%"

def process_data(df):
    """Process the data and create visualizations"""
    try:
        # Create a copy to avoid modifying original
        df = df.copy()
        
        # Convert time columns to seconds
        time_columns = ['LOGIN TIME', 'NOT READY TIME', 'WAIT TIME', 'RINGING TIME', 
                       'ON CALL TIME', 'ON VOICEMAIL TIME', 'ON ACW TIME', 
                       'AVAILABLE TIME (LOGIN LESS NOT READY)']
        
        for col in time_columns:
            if col in df.columns:
                df[f'{col}_SECONDS'] = df[col].apply(time_to_seconds)

        # Calculate additional metrics
        df['Full Name'] = df['AGENT FIRST NAME'].fillna('') + ' ' + df['AGENT LAST NAME'].fillna('')
        df['Total Active Time'] = df['ON CALL TIME_SECONDS'] + df['ON ACW TIME_SECONDS']
        
        # Handle division by zero
        df['LOGIN TIME_SECONDS'] = df['LOGIN TIME_SECONDS'].replace(0, 1)  # Avoid division by zero
        df['Occupancy %'] = (df['Total Active Time'] / df['LOGIN TIME_SECONDS'] * 100).clip(0, 100)
        
        not_ready_time = df['NOT READY TIME_SECONDS'].fillna(0)
        login_time = df['LOGIN TIME_SECONDS'].fillna(0)
        df['Utilization %'] = (df['Total Active Time'] / (login_time - not_ready_time).replace(0, 1) * 100).clip(0, 100)
        
        return df
    except Exception as e:
        st.error(f"Error processing data: {str(e)}")
        return None

def show_metrics(df):
    """Display the metrics section"""
    total_agents = len(df)
    avg_login_time = df['LOGIN TIME_SECONDS'].mean()
    avg_occupancy = df['Occupancy %'].mean()
    avg_utilization = df['Utilization %'].mean()
    total_calls_time = df['ON CALL TIME_SECONDS'].sum()
    total_login_time = df['LOGIN TIME_SECONDS'].sum()

    st.markdown("### 📈 Performance Metrics")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("👥 Total Agents", total_agents)
        st.metric("⏰ Avg Login Time", format_time(int(avg_login_time)))
    with col2:
        st.metric("📊 Average Occupancy", format_percentage(avg_occupancy))
        st.metric("🎯 Average Utilization", format_percentage(avg_utilization))
    with col3:
        st.metric("☎️ Total Call Hours", format_time(int(total_calls_time)))
        st.metric("⌛ Total Login Hours", format_time(int(total_login_time)))

def create_visualizations(df):
    """Create and display visualizations"""
    try:
        processed_df = process_data(df)
        if processed_df is None:
            return
            
        show_metrics(processed_df)
        
        # Create tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Time Distribution", "🎯 Agent Performance", "📈 Hourly Trends", "📑 Detailed Data"])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                # Time distribution chart
                time_metrics = {
                    'Not Ready': processed_df['NOT READY TIME_SECONDS'].sum(),
                    'Wait': processed_df['WAIT TIME_SECONDS'].sum(),
                    'On Call': processed_df['ON CALL TIME_SECONDS'].sum(),
                    'ACW': processed_df['ON ACW TIME_SECONDS'].sum()
                }
                
                if all(v == 0 for v in time_metrics.values()):
                    st.warning("No time data available for visualization")
                else:
                    fig_time = go.Figure(data=[
                        go.Pie(
                            labels=list(time_metrics.keys()),
                            values=list(time_metrics.values()),
                            hole=0.4,
                            marker=dict(colors=['rgb(255, 99, 71)', 'rgb(255, 195, 0)', 
                                              'rgb(60, 179, 113)', 'rgb(30, 144, 255)'])
                        )
                    ])
                    fig_time.update_layout(
                        title="Overall Time Distribution",
                        height=400
                    )
                    st.plotly_chart(fig_time, use_container_width=True)
            
            with col2:
                # Top 10 agents by occupancy
                top_agents = processed_df.nlargest(10, 'Occupancy %')
                if len(top_agents) > 0:
                    fig_top = go.Figure(data=[
                        go.Bar(
                            x=top_agents['Occupancy %'],
                            y=top_agents['Full Name'],
                            orientation='h',
                            marker_color='rgb(60, 179, 113)'
                        )
                    ])
                    fig_top.update_layout(
                        title="Top 10 Agents by Occupancy",
                        xaxis_title="Occupancy %",
                        height=400,
                        margin=dict(l=200)
                    )
                    st.plotly_chart(fig_top, use_container_width=True)
                else:
                    st.warning("No agent data available for visualization")

        with tab2:
            try:
                # Time breakdown for all agents
                st.subheader("Agent Time Distribution")
                
                # Sort agents by total time
                processed_df['Total Time'] = processed_df['NOT READY TIME_SECONDS'] + processed_df['WAIT TIME_SECONDS'] + \
                                  processed_df['ON CALL TIME_SECONDS'] + processed_df['ON ACW TIME_SECONDS']
                
                # Add filter for sorting
                sort_by = st.selectbox(
                    "Sort Agents By:",
                    ["Total Time", "Occupancy %", "On Call Time", "Not Ready Time"],
                    index=0
                )
                
                sort_column = {
                    "Total Time": "Total Time",
                    "Occupancy %": "Occupancy %",
                    "On Call Time": "ON CALL TIME_SECONDS",
                    "Not Ready Time": "NOT READY TIME_SECONDS"
                }[sort_by]
                
                df_sorted = processed_df.sort_values(sort_column, ascending=True)
                
                if len(df_sorted) > 0:
                    fig_breakdown = go.Figure()
                    
                    # Add traces for each time metric
                    metrics = [
                        ('Not Ready', 'NOT READY TIME_SECONDS', 'rgb(255, 99, 71)'),
                        ('Wait', 'WAIT TIME_SECONDS', 'rgb(255, 195, 0)'),
                        ('On Call', 'ON CALL TIME_SECONDS', 'rgb(60, 179, 113)'),
                        ('ACW', 'ON ACW TIME_SECONDS', 'rgb(30, 144, 255)')
                    ]
                    
                    for label, column, color in metrics:
                        fig_breakdown.add_trace(
                            go.Bar(
                                name=label,
                                x=df_sorted[column].fillna(0) / 3600,  # Convert to hours and handle NaN
                                y=df_sorted['Full Name'],
                                orientation='h',
                                marker_color=color,
                                hovertemplate="%{y}<br>" +
                                            f"{label}: %{x:.1f} hours<br>" +
                                            "<extra></extra>"
                            )
                        )
                    
                    fig_breakdown.update_layout(
                        barmode='stack',
                        title=f"Time Distribution by Agent (Sorted by {sort_by})",
                        xaxis_title="Hours",
                        yaxis_title="Agent Name",
                        height=max(600, len(processed_df) * 25),
                        legend_title="Time Type",
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                        margin=dict(l=200)
                    )
                    st.plotly_chart(fig_breakdown, use_container_width=True)
                else:
                    st.warning("No agent data available for visualization")
            except Exception as e:
                st.error(f"Error creating agent performance visualization: {str(e)}")

        with tab3:
            try:
                st.subheader("Hourly Performance Trends")
                
                # Convert DATE to datetime and extract hour
                processed_df['Hour'] = pd.to_datetime(processed_df['DATE']).dt.hour
                
                # Calculate hourly metrics
                hourly_metrics = processed_df.groupby('Hour').agg({
                    'ON CALL TIME_SECONDS': 'sum',
                    'Occupancy %': 'mean'
                }).reset_index()
                
                if len(hourly_metrics) > 0:
                    # Create dual-axis chart
                    fig_hourly = make_subplots(specs=[[{"secondary_y": True}]])
                    
                    fig_hourly.add_trace(
                        go.Bar(
                            name="Call Time",
                            x=hourly_metrics['Hour'],
                            y=hourly_metrics['ON CALL TIME_SECONDS'].fillna(0) / 3600,  # Convert to hours
                            marker_color='rgb(60, 179, 113)'
                        ),
                        secondary_y=False
                    )
                    
                    fig_hourly.add_trace(
                        go.Scatter(
                            name="Occupancy",
                            x=hourly_metrics['Hour'],
                            y=hourly_metrics['Occupancy %'].fillna(0),  # Handle NaN values
                            mode='lines+markers',
                            line=dict(color='rgb(255, 99, 71)')
                        ),
                        secondary_y=True
                    )
                    
                    fig_hourly.update_layout(
                        title="Hourly Performance Trends",
                        xaxis_title="Hour of Day",
                        height=400,
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                    )
                    
                    fig_hourly.update_yaxes(title_text="Call Hours", secondary_y=False)
                    fig_hourly.update_yaxes(title_text="Occupancy %", secondary_y=True)
                    
                    st.plotly_chart(fig_hourly, use_container_width=True)
                else:
                    st.warning("No hourly data available for visualization")
            except Exception as e:
                st.error(f"Error creating hourly trends visualization: {str(e)}")

        with tab4:
            try:
                st.subheader("📑 Detailed Data View")
                
                # Prepare data for display
                display_df = processed_df[[
                    'Full Name', 'LOGIN TIME', 'NOT READY TIME', 'WAIT TIME',
                    'ON CALL TIME', 'ON ACW TIME', 'Occupancy %', 'Utilization %'
                ]].copy()
                
                # Format percentages
                display_df['Occupancy %'] = display_df['Occupancy %'].apply(lambda x: f"{x:.1f}%")
                display_df['Utilization %'] = display_df['Utilization %'].apply(lambda x: f"{x:.1f}%")
                
                st.dataframe(
                    display_df,
                    hide_index=True,
                    height=400
                )
                
                # Add download button
                csv = display_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Data",
                    data=csv,
                    file_name="agent_occupancy_data.csv",
                    mime="text/csv"
                )
            except Exception as e:
                st.error(f"Error displaying detailed data: {str(e)}")
    except Exception as e:
        st.error(f"Error creating visualizations: {str(e)}")

# File uploader
uploaded_file = st.file_uploader("Upload your Agent Occupancy CSV file", type=['csv'])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        required_columns = [
            'AGENT', 'AGENT FIRST NAME', 'AGENT LAST NAME', 'DATE',
            'LOGIN TIME', 'NOT READY TIME', 'WAIT TIME', 'ON CALL TIME',
            'ON ACW TIME'
        ]
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.error(f"Missing columns: {', '.join(missing_columns)}")
        else:
            create_visualizations(df)
            
    except Exception as e:
        st.error(f"Error reading the file: {str(e)}")
        st.error("Please make sure your CSV file is in the correct format")
else:
    st.info("Please upload a CSV file to begin the analysis.")
