import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="Agent Occupancy Analysis",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Agent Occupancy Analysis")
st.markdown("""
    This dashboard analyzes agent occupancy and utilization metrics. Upload your CSV file to get started.
    
    The CSV should contain these columns:
    - `AGENT`, `AGENT FIRST NAME`, `AGENT LAST NAME`
    - Time metrics (LOGIN TIME, NOT READY TIME, WAIT TIME, etc.)
    - Occupancy and utilization percentages
""")

def time_to_seconds(time_str):
    if pd.isna(time_str) or time_str == '':
        return 0
    try:
        h, m, s = map(int, time_str.split(':'))
        return h * 3600 + m * 60 + s
    except:
        return 0

def format_time(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{hours:02d}:{minutes:02d}"

def create_visualizations(df):
    try:
        # Convert time columns to seconds
        time_columns = ['LOGIN TIME', 'NOT READY TIME', 'WAIT TIME', 'RINGING TIME', 
                       'ON CALL TIME', 'ON VOICEMAIL TIME', 'ON ACW TIME', 
                       'AVAILABLE TIME (LOGIN LESS NOT READY)']
        
        for col in time_columns:
            if col in df.columns:
                df[f'{col}_SECONDS'] = df[col].apply(time_to_seconds)

        # Calculate metrics
        total_agents = len(df)
        avg_login_time = df['LOGIN TIME_SECONDS'].mean()
        avg_occupancy = df['LOGIN TIME_SECONDS'].sum() / total_agents

        # Create metrics section
        st.markdown("### Key Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Agents", total_agents)
        with col2:
            st.metric("Avg Login Time", format_time(int(avg_login_time)))
        with col3:
            st.metric("Avg Occupancy", f"{(avg_occupancy/3600):.2f} hrs")
        with col4:
            date = pd.to_datetime(df['DATE'].iloc[0]).strftime('%m/%d/%Y')
            st.metric("Date", date)

        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["📊 Time Distribution", "🎯 Occupancy Analysis", "📑 Detailed Data"])
        
        with tab1:
            # Time distribution chart
            time_metrics = {
                'Not Ready': df['NOT READY TIME_SECONDS'].sum(),
                'Wait': df['WAIT TIME_SECONDS'].sum(),
                'On Call': df['ON CALL TIME_SECONDS'].sum(),
                'ACW': df['ON ACW TIME_SECONDS'].sum(),
                'Available': df['AVAILABLE TIME (LOGIN LESS NOT READY)_SECONDS'].sum()
            }
            
            fig_time = go.Figure(data=[
                go.Pie(
                    labels=list(time_metrics.keys()),
                    values=list(time_metrics.values()),
                    hole=0.4
                )
            ])
            fig_time.update_layout(
                title="Time Distribution Across All Agents",
                height=500
            )
            st.plotly_chart(fig_time, use_container_width=True)

        with tab2:
            # Create occupancy analysis
            df['Full Name'] = df['AGENT FIRST NAME'] + ' ' + df['AGENT LAST NAME'].fillna('')
            df['Occupancy %'] = (df['ON CALL TIME_SECONDS'] + df['ON ACW TIME_SECONDS']) / df['LOGIN TIME_SECONDS'] * 100
            
            # Sort by occupancy
            df_sorted = df.sort_values('Occupancy %', ascending=True)
            
            fig_occupancy = go.Figure()
            fig_occupancy.add_trace(
                go.Bar(
                    x=df_sorted['Occupancy %'],
                    y=df_sorted['Full Name'],
                    orientation='h'
                )
            )
            
            fig_occupancy.update_layout(
                title="Agent Occupancy Rates",
                xaxis_title="Occupancy %",
                yaxis_title="Agent Name",
                height=max(500, len(df) * 20),
                showlegend=False
            )
            st.plotly_chart(fig_occupancy, use_container_width=True)

            # Time breakdown by agent
            selected_agents = st.multiselect(
                "Select Agents for Time Breakdown",
                options=sorted(df['Full Name'].unique()),
                default=sorted(df['Full Name'].unique())[:5]
            )

            if selected_agents:
                df_selected = df[df['Full Name'].isin(selected_agents)]
                
                fig_breakdown = go.Figure()
                
                # Add traces for each time metric
                metrics = [
                    ('Not Ready', 'NOT READY TIME_SECONDS'),
                    ('Wait', 'WAIT TIME_SECONDS'),
                    ('On Call', 'ON CALL TIME_SECONDS'),
                    ('ACW', 'ON ACW TIME_SECONDS')
                ]
                
                for label, column in metrics:
                    fig_breakdown.add_trace(
                        go.Bar(
                            name=label,
                            x=df_selected[column] / 3600,  # Convert to hours
                            y=df_selected['Full Name'],
                            orientation='h'
                        )
                    )
                
                fig_breakdown.update_layout(
                    barmode='stack',
                    title="Time Breakdown by Agent",
                    xaxis_title="Hours",
                    height=max(400, len(selected_agents) * 30),
                    legend_title="Time Type",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig_breakdown, use_container_width=True)

        with tab3:
            # Detailed data view
            st.subheader("Agent Details")
            
            # Format time columns for display
            display_df = df.copy()
            for col in time_columns:
                if col in display_df.columns:
                    display_df[col] = display_df[f'{col}_SECONDS'].apply(format_time)
            
            # Select columns for display
            display_columns = ['Full Name', 'LOGIN TIME', 'NOT READY TIME', 'WAIT TIME', 
                             'ON CALL TIME', 'ON ACW TIME', 'Occupancy %']
            
            st.dataframe(
                display_df[display_columns].sort_values('Occupancy %', ascending=False),
                hide_index=True,
                height=400
            )
            
            # Add download button
            csv = display_df[display_columns].to_csv(index=False)
            st.download_button(
                label="📥 Download Data",
                data=csv,
                file_name="agent_occupancy_data.csv",
                mime="text/csv"
            )

    except Exception as e:
        st.error(f"Error processing the data: {str(e)}")
        st.error("Please make sure your CSV file is in the correct format")

# File uploader
uploaded_file = st.file_uploader("Upload your Agent Occupancy CSV file", type=['csv'])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        required_columns = ['AGENT', 'LOGIN TIME', 'NOT READY TIME']
        if all(col in df.columns for col in required_columns):
            create_visualizations(df)
        else:
            st.error(f"The CSV file must contain these columns: {', '.join(required_columns)}")
    except Exception as e:
        st.error(f"Error reading the file: {str(e)}")
else:
    st.info("👆 Please upload a CSV file to begin the analysis.")
