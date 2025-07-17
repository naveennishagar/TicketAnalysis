import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io
from data_processor import DataProcessor
from visualizations import TicketVisualizer
from database import DatabaseManager

USERS = [
    "Gayan Fernando",
    "Dinesh Wickramasinghe",
    "Nihal Rathnayake",
    "Kavindu Dilshan",
    "Imasha Pawan",
    "Indika Gamage",
    "Ruwan Karunachandra",
    "Nadeesha Ranasinghe",
    "Dimuthu Sandaruwan",
    "Pramith Indunil"
]

# Set page configuration
st.set_page_config(
    page_title="Ticket Tracking Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    if 'data' not in st.session_state:
        st.session_state.data = None
    if 'processed_data' not in st.session_state:
        st.session_state.processed_data = None
    if 'db_manager' not in st.session_state:
        st.session_state.db_manager = DatabaseManager()
        st.session_state.db_manager.create_tables()

    st.title("Ticket Analysis by Browns Plantations - IT Department")
    st.markdown("---")
    
    # Sidebar for file upload and filters
    with st.sidebar:
        st.header("Data Management")
        
        # Database controls
        st.subheader("Database Options")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Load from Database"):
                with st.spinner("Loading data from database..."):
                    db_data = st.session_state.db_manager.load_tickets_from_db()
                    if not db_data.empty:
                        st.session_state.data = db_data
                        processor = DataProcessor()
                        st.session_state.processed_data = processor.process_data(db_data)
                        st.success("✅ Data loaded from database!")
                        st.info(f"📈 Total records: {len(db_data)}")
                    else:
                        st.info("No data found in database.")
        
        with col2:
            if st.button("Clear Database", type="secondary"):
                if st.session_state.db_manager.clear_all_data():
                    st.success("Database cleared!")
                    st.session_state.data = None
                    st.session_state.processed_data = None
                    st.rerun()
        
        st.markdown("---")
        
        # File upload
        st.subheader("Upload New Data")
        uploaded_file = st.file_uploader(
            "Upload Excel/CSV file",
            type=['xlsx', 'xls', 'csv'],
            help="Upload an Excel or CSV file with ticket data"
        )
        
        if uploaded_file is not None:
            try:
                # Process the uploaded file
                with st.spinner("Processing file..."):
                    processor = DataProcessor()
                    if uploaded_file.name.endswith('.csv'):
                        data = processor.load_csv_file(uploaded_file)
                    else:
                        data = processor.load_excel_file(uploaded_file)
                    
                    if data is not None:
                        # Save to database
                        if st.session_state.db_manager.save_tickets_to_db(data):
                            st.session_state.data = data
                            st.session_state.processed_data = processor.process_data(data)
                            st.success("✅ File uploaded and saved to database!")
                            st.info(f"📈 Total records: {len(data)}")
                        else:
                            st.error("❌ Failed to save to database.")
                    else:
                        st.error("❌ Failed to process the file. Please check the file format.")
                        
            except Exception as e:
                st.error(f"❌ Error processing file: {str(e)}")
                st.info("Please ensure your file has the expected column structure.")
    
    # Main content area
    if st.session_state.data is not None and st.session_state.processed_data is not None:
        display_dashboard()
    else:
        display_welcome_message()

def display_welcome_message():
    """Display welcome message when no data is loaded"""
    # Show database stats
    db_stats = st.session_state.db_manager.get_ticket_stats()
    
    st.markdown("""
    <div style="text-align: center; padding: 50px;">
        <h2>Welcome to the Ticket Tracking Dashboard</h2>
        <p style="font-size: 18px; color: #666;">
            Upload new data or load existing data from the database.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Database status
    if db_stats['total'] > 0:
        st.info(f"📊 Database contains {db_stats['total']} tickets ({db_stats['resolved']} resolved, {db_stats['pending']} pending)")
        st.info("💡 Click 'Load from Database' in the sidebar to view your data.")
    else:
        st.info("📁 No data in database. Upload an Excel or CSV file to get started.")
    
    st.markdown("""
    <div style="text-align: center; padding: 20px;">
        <p style="font-size: 14px; color: #888;">
            Expected file columns:
            <br>• Ticket ID, Current Status, AssignedTo, Requested Date
            <br>• Company Name, Branch Name, Resolved By, Resolved Date
            <br>• Subject, Description, Ticket Category
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
            selected_branch = st.selectbox("Select Zone", branches)
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
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Overview", "Pending Tickets", "Resolved Tickets", "Resolver Analytics", "Assigned Analytics"])
    
    with tab1:
        display_overview(visualizer)
    
    with tab2:
        display_pending_tickets(visualizer)
    
    with tab3:
        display_resolved_tickets(visualizer)
    
    with tab4:
        display_resolver_analytics(visualizer, filtered_data)
    
    with tab5:
        display_assigned_analytics(visualizer, filtered_data)

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
            resolved_statuses = ['Closed', 'Completed', 'Auto Completed', 'Discard']
            pending_tickets = len(data[~data['Status'].isin(resolved_statuses)])
            st.metric("Pending Tickets", pending_tickets)
        else:
            st.metric("Pending Tickets", "N/A")
    
    with col3:
        if 'Status' in data.columns:
            resolved_statuses = ['Closed', 'Completed', 'Auto Completed']
            resolved_tickets = len(data[data['Status'].isin(resolved_statuses)])
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
    st.header("Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Pending Tickets by Status")
        pending_chart = visualizer.create_pending_status_pie()
        if pending_chart:
            st.plotly_chart(pending_chart, use_container_width=True, key="overview_pending_pie")
        else:
            st.info("No pending tickets data available")
    
    with col2:
        st.subheader("Resolved Tickets by Status")
        resolved_chart = visualizer.create_resolved_status_pie()
        if resolved_chart:
            st.plotly_chart(resolved_chart, use_container_width=True, key="overview_resolved_pie")
        else:
            st.info("No resolved tickets data available")
    
    # Daily tickets line chart
    st.subheader("📈 Daily Tickets Analysis")
    daily_chart = visualizer.create_daily_tickets_line_chart()
    if daily_chart:
        st.plotly_chart(daily_chart, use_container_width=True, key="overview_daily_line")
    else:
        st.info("No date data available for daily analysis")

def display_pending_tickets(visualizer):
    """Display pending tickets analysis"""
    st.header("Pending Tickets Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Pending Tickets by Assigned User")
        pending_user_chart = visualizer.create_pending_by_user_chart()
        if pending_user_chart:
            st.plotly_chart(pending_user_chart, use_container_width=True, key="pending_user_bar")
        else:
            st.info("No assigned user data available")
    
    with col2:
        st.subheader("Pending Tickets by Status")
        pending_status_chart = visualizer.create_pending_by_status_chart()
        if pending_status_chart:
            st.plotly_chart(pending_status_chart, use_container_width=True, key="pending_status_pie")
        else:
            st.info("No pending tickets found")
    
    # Day-wise pending chart
    st.subheader("📈 Day-wise Cumulative Pending Tickets")
    day_wise_pending = visualizer.create_day_wise_pending_chart()
    if day_wise_pending:
        st.plotly_chart(day_wise_pending, use_container_width=True, key="pending_day_wise_line")
    else:
        st.info("No created date data available")
    
    # Pending tickets table
    st.subheader("📋 Pending Tickets Details")
    pending_table = visualizer.get_pending_tickets_table()
    if not pending_table.empty:
        st.dataframe(pending_table, use_container_width=True)
    else:
        st.info("No pending tickets found")

def display_resolved_tickets(visualizer):
    """Display resolved tickets analysis"""
    st.header("Resolved Tickets Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Resolved Tickets by Resolver")
        resolved_user_chart = visualizer.create_resolved_by_resolver_chart()
        if resolved_user_chart:
            st.plotly_chart(resolved_user_chart, use_container_width=True, key="resolved_user_bar")
        else:
            st.info("No resolver data available")
    
    with col2:
        st.subheader("Resolved Tickets by Status")
        resolved_status_chart = visualizer.create_resolved_status_pie()
        if resolved_status_chart:
            st.plotly_chart(resolved_status_chart, use_container_width=True, key="resolved_status_pie")
        else:
            st.info("No resolved status data available")
    
    # Day-wise resolved chart
    st.subheader("📈 Day-wise Cumulative Resolved Tickets")
    day_wise_chart = visualizer.create_day_wise_resolved_chart()
    if day_wise_chart:
        st.plotly_chart(day_wise_chart, use_container_width=True, key="resolved_day_wise_line")
    else:
        st.info("No resolved date data available")
    
    # Resolved tickets table
    st.subheader("📋 Resolved Tickets Details")
    resolved_table = visualizer.get_resolved_tickets_table()
    if not resolved_table.empty:
        st.dataframe(resolved_table, use_container_width=True)
    else:
        st.info("No resolved tickets found")

def display_resolver_analytics(visualizer, data):
    st.header("Resolver Personal Analytics")
    resolvers = ['All'] + sorted(USERS)
    selected_resolver = st.selectbox("Select Resolver", resolvers)
    if selected_resolver != 'All':
        filtered = data[data['Resolver'] == selected_resolver]
        if not filtered.empty:
            vis = TicketVisualizer(filtered)
            display_metrics(filtered)
            col1, col2 = st.columns(2)
            with col1:
                resolved_status_chart = vis.create_resolved_status_pie()
                if resolved_status_chart:
                    st.plotly_chart(resolved_status_chart, key="resolver_resolved_pie")
            with col2:
                resolved_chart = vis.create_daily_resolved_chart()
                if resolved_chart:
                    st.plotly_chart(resolved_chart, key="resolver_daily_resolved")
            st.subheader("Resolved Tickets Details")
            resolved_table = vis.get_resolved_tickets_table()
            if not resolved_table.empty:
                st.dataframe(resolved_table)
            else:
                st.info("No resolved tickets")
        else:
            st.info("No data for this resolver")
    else:
        st.info("Select a resolver to view analytics")

def display_assigned_analytics(visualizer, data):
    st.header("Assigned Member Personal Analytics")
    assigned = ['All'] + sorted(USERS)
    selected_assigned = st.selectbox("Select Assigned Member", assigned)
    if selected_assigned != 'All':
        filtered = data[data['Assigned User'] == selected_assigned]
        if not filtered.empty:
            vis = TicketVisualizer(filtered)
            display_metrics(filtered)
            col1, col2 = st.columns(2)
            with col1:
                assigned_chart = vis.create_daily_assigned_chart()
                if assigned_chart:
                    st.plotly_chart(assigned_chart, key="assigned_daily_assigned")
            with col2:
                pending_user_chart = vis.create_pending_by_status_chart()
                if pending_user_chart:
                    st.plotly_chart(pending_user_chart, key="assigned_pending_status_pie")
            st.subheader("Pending Tickets Details")
            pending_table = vis.get_pending_tickets_table()
            if not pending_table.empty:
                st.dataframe(pending_table)
            else:
                st.info("No pending tickets")
        else:
            st.info("No data for this assigned member")
    else:
        st.info("Select an assigned member to view analytics")

main()
