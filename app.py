import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io
from data_processor import DataProcessor
from visualizations import TicketVisualizer

# Set page configuration
st.set_page_config(
    page_title="Ticket Tracking Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = None
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None

def main():
    st.title("📊 Ticket Tracking Dashboard")
    st.markdown("---")
    
    # Sidebar for file upload and filters
    with st.sidebar:
        st.header("📁 Data Upload")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Upload Excel file",
            type=['xlsx', 'xls'],
            help="Upload an Excel file with ticket data"
        )
        
        if uploaded_file is not None:
            try:
                # Process the uploaded file
                with st.spinner("Processing file..."):
                    processor = DataProcessor()
                    data = processor.load_excel_file(uploaded_file)
                    
                    if data is not None:
                        st.session_state.data = data
                        st.session_state.processed_data = processor.process_data(data)
                        st.success("✅ File uploaded and processed successfully!")
                        st.info(f"📈 Total records: {len(data)}")
                    else:
                        st.error("❌ Failed to process the file. Please check the file format.")
                        
            except Exception as e:
                st.error(f"❌ Error processing file: {str(e)}")
                st.info("Please ensure your Excel file has the expected column structure.")
    
    # Main content area
    if st.session_state.data is not None and st.session_state.processed_data is not None:
        display_dashboard()
    else:
        display_welcome_message()

def display_welcome_message():
    """Display welcome message when no data is loaded"""
    st.markdown("""
    <div style="text-align: center; padding: 50px;">
        <h2>Welcome to the Ticket Tracking Dashboard</h2>
        <p style="font-size: 18px; color: #666;">
            Please upload an Excel file using the sidebar to get started.
        </p>
        <p style="font-size: 14px; color: #888;">
            The Excel file should contain ticket data with columns for:
            <br>• Ticket ID, Status, Assigned User, Resolver
            <br>• Created Date, Resolved Date, Company, Branch
            <br>• Priority, Category, Description
        </p>
    </div>
    """, unsafe_allow_html=True)

def display_dashboard():
    """Display the main dashboard with filters and visualizations"""
    data = st.session_state.data
    processed_data = st.session_state.processed_data
    
    # Sidebar filters
    with st.sidebar:
        st.header("🔍 Filters")
        
        # Date range filter
        if 'Created Date' in data.columns:
            min_date = pd.to_datetime(data['Created Date']).min().date()
            max_date = pd.to_datetime(data['Created Date']).max().date()
            
            date_range = st.date_input(
                "Select Date Range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )
        else:
            date_range = None
        
        # Company filter
        if 'Company' in data.columns:
            companies = ['All'] + sorted(data['Company'].dropna().unique().tolist())
            selected_company = st.selectbox("Select Company", companies)
        else:
            selected_company = 'All'
        
        # Branch filter
        if 'Branch' in data.columns:
            branches = ['All'] + sorted(data['Branch'].dropna().unique().tolist())
            selected_branch = st.selectbox("Select Branch", branches)
        else:
            selected_branch = 'All'
        
        # Status filter
        if 'Status' in data.columns:
            statuses = ['All'] + sorted(data['Status'].dropna().unique().tolist())
            selected_status = st.selectbox("Select Status", statuses)
        else:
            selected_status = 'All'
    
    # Apply filters
    filtered_data = apply_filters(data, date_range, selected_company, selected_branch, selected_status)
    
    if filtered_data.empty:
        st.warning("⚠️ No data matches the selected filters.")
        return
    
    # Create visualizer instance
    visualizer = TicketVisualizer(filtered_data)
    
    # Display metrics
    display_metrics(filtered_data)
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["📋 Overview", "⏳ Pending Tickets", "✅ Resolved Tickets"])
    
    with tab1:
        display_overview(visualizer)
    
    with tab2:
        display_pending_tickets(visualizer)
    
    with tab3:
        display_resolved_tickets(visualizer)

def apply_filters(data, date_range, company, branch, status):
    """Apply selected filters to the data"""
    filtered_data = data.copy()
    
    # Date range filter
    if date_range and len(date_range) == 2 and 'Created Date' in data.columns:
        start_date, end_date = date_range
        filtered_data = filtered_data[
            (pd.to_datetime(filtered_data['Created Date']).dt.date >= start_date) &
            (pd.to_datetime(filtered_data['Created Date']).dt.date <= end_date)
        ]
    
    # Company filter
    if company != 'All' and 'Company' in data.columns:
        filtered_data = filtered_data[filtered_data['Company'] == company]
    
    # Branch filter
    if branch != 'All' and 'Branch' in data.columns:
        filtered_data = filtered_data[filtered_data['Branch'] == branch]
    
    # Status filter
    if status != 'All' and 'Status' in data.columns:
        filtered_data = filtered_data[filtered_data['Status'] == status]
    
    return filtered_data

def display_metrics(data):
    """Display key metrics in a row of columns"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_tickets = len(data)
        st.metric("Total Tickets", total_tickets)
    
    with col2:
        if 'Status' in data.columns:
            pending_tickets = len(data[data['Status'].isin(['Open', 'In Progress', 'Pending'])])
            st.metric("Pending Tickets", pending_tickets)
        else:
            st.metric("Pending Tickets", "N/A")
    
    with col3:
        if 'Status' in data.columns:
            resolved_tickets = len(data[data['Status'].isin(['Resolved', 'Closed', 'Completed'])])
            st.metric("Resolved Tickets", resolved_tickets)
        else:
            st.metric("Resolved Tickets", "N/A")
    
    with col4:
        if 'Status' in data.columns and len(data) > 0:
            resolution_rate = (resolved_tickets / total_tickets) * 100
            st.metric("Resolution Rate", f"{resolution_rate:.1f}%")
        else:
            st.metric("Resolution Rate", "N/A")

def display_overview(visualizer):
    """Display overview charts and tables"""
    st.header("📊 Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Tickets by Status")
        status_chart = visualizer.create_status_distribution_chart()
        if status_chart:
            st.plotly_chart(status_chart, use_container_width=True)
        else:
            st.info("No status data available")
    
    with col2:
        st.subheader("Tickets by Priority")
        priority_chart = visualizer.create_priority_distribution_chart()
        if priority_chart:
            st.plotly_chart(priority_chart, use_container_width=True)
        else:
            st.info("No priority data available")
    
    # Timeline chart
    st.subheader("📈 Ticket Creation Timeline")
    timeline_chart = visualizer.create_timeline_chart()
    if timeline_chart:
        st.plotly_chart(timeline_chart, use_container_width=True)
    else:
        st.info("No date data available for timeline")

def display_pending_tickets(visualizer):
    """Display pending tickets analysis"""
    st.header("⏳ Pending Tickets Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Pending Tickets by Assigned User")
        pending_user_chart = visualizer.create_pending_by_user_chart()
        if pending_user_chart:
            st.plotly_chart(pending_user_chart, use_container_width=True)
        else:
            st.info("No assigned user data available")
    
    with col2:
        st.subheader("Pending Tickets by Status")
        pending_status_chart = visualizer.create_pending_by_status_chart()
        if pending_status_chart:
            st.plotly_chart(pending_status_chart, use_container_width=True)
        else:
            st.info("No pending tickets found")
    
    # Pending tickets table
    st.subheader("📋 Pending Tickets Details")
    pending_table = visualizer.get_pending_tickets_table()
    if not pending_table.empty:
        st.dataframe(pending_table, use_container_width=True)
    else:
        st.info("No pending tickets found")

def display_resolved_tickets(visualizer):
    """Display resolved tickets analysis"""
    st.header("✅ Resolved Tickets Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Resolved Tickets by Resolver")
        resolved_user_chart = visualizer.create_resolved_by_resolver_chart()
        if resolved_user_chart:
            st.plotly_chart(resolved_user_chart, use_container_width=True)
        else:
            st.info("No resolver data available")
    
    with col2:
        st.subheader("Resolution Time Distribution")
        resolution_time_chart = visualizer.create_resolution_time_chart()
        if resolution_time_chart:
            st.plotly_chart(resolution_time_chart, use_container_width=True)
        else:
            st.info("No resolution time data available")
    
    # Resolved tickets table
    st.subheader("📋 Resolved Tickets Details")
    resolved_table = visualizer.get_resolved_tickets_table()
    if not resolved_table.empty:
        st.dataframe(resolved_table, use_container_width=True)
    else:
        st.info("No resolved tickets found")

if __name__ == "__main__":
    main()
