import pandas as pd
import numpy as np
from datetime import datetime
import streamlit as st

class DataProcessor:
    """Class to handle Excel file processing and data manipulation"""
    
    def __init__(self):
        self.required_columns = [
            'Ticket ID', 'Current Status', 'AssignedTo', 'Requested Date'
        ]
        self.optional_columns = [
            'Resolved By', 'Resolved Date', 'Company Name', 'Branch Name', 
            'Ticket Category', 'Subject', 'Description', 'Requester',
            'Created User', 'Ticket Type', 'Ticket Sub Category',
            'Department Name', 'SLA', 'No Of Days', 'No Of Working Days'
        ]
    
    def load_excel_file(self, uploaded_file):
        """Load and validate Excel file"""
        try:
            # Read Excel file
            df = pd.read_excel(uploaded_file)
            return self._process_uploaded_data(df)
            
        except Exception as e:
            st.error(f"❌ Error reading Excel file: {str(e)}")
            return None
    
    def load_csv_file(self, uploaded_file):
        """Load and validate CSV file"""
        try:
            # Read CSV file
            df = pd.read_csv(uploaded_file)
            return self._process_uploaded_data(df)
            
        except Exception as e:
            st.error(f"❌ Error reading CSV file: {str(e)}")
            return None
    
    def _process_uploaded_data(self, df):
        """Common processing logic for uploaded data"""
        # Basic validation
        if df.empty:
            st.error("❌ The uploaded file is empty.")
            return None
        
        # Check for required columns (flexible matching)
        missing_columns = self.validate_columns(df)
        if missing_columns:
            st.error(f"❌ Missing required columns: {', '.join(missing_columns)}")
            st.info("Expected columns: " + ", ".join(self.required_columns))
            return None
        
        # Clean and standardize the data
        df = self.clean_data(df)
        
        return df
    
    def validate_columns(self, df):
        """Validate that required columns exist (case-insensitive)"""
        df_columns_lower = [col.lower().strip() for col in df.columns]
        missing_columns = []
        
        for req_col in self.required_columns:
            if req_col.lower() not in df_columns_lower:
                missing_columns.append(req_col)
        
        return missing_columns
    
    def clean_data(self, df):
        """Clean and standardize the data"""
        # Create a copy to avoid modifying original
        df_clean = df.copy()
        
        # Standardize column names (case-insensitive matching)
        column_mapping = {}
        df_columns_lower = {col.lower().strip(): col for col in df_clean.columns}
        
        # Map required columns
        for req_col in self.required_columns:
            if req_col.lower() in df_columns_lower:
                column_mapping[df_columns_lower[req_col.lower()]] = req_col
        
        # Map optional columns
        for opt_col in self.optional_columns:
            if opt_col.lower() in df_columns_lower:
                column_mapping[df_columns_lower[opt_col.lower()]] = opt_col
        
        # Map common column variations to standard names
        column_variations = {
            'Current Status': 'Status',
            'AssignedTo': 'Assigned User',
            'Requested Date': 'Created Date',
            'Resolved By': 'Resolver',
            'Company Name': 'Company',
            'Branch Name': 'Branch',
            'Ticket Category': 'Category',
            'Subject': 'Title'
        }
        
        # Apply column variations mapping
        for old_name, new_name in column_variations.items():
            if old_name in column_mapping.values():
                # Find the actual column name that maps to old_name
                actual_col = next(k for k, v in column_mapping.items() if v == old_name)
                column_mapping[actual_col] = new_name
        
        # Rename columns
        df_clean = df_clean.rename(columns=column_mapping)
        
        # Clean date columns with specific format handling
        date_columns = ['Created Date', 'Resolved Date']
        for date_col in date_columns:
            if date_col in df_clean.columns:
                # Handle the specific date format from your CSV (e.g., "27-Mar-24 11:02:44 AM")
                df_clean[date_col] = pd.to_datetime(df_clean[date_col], errors='coerce', dayfirst=True)
        
        # Clean text columns
        text_columns = ['Status', 'Assigned User', 'Resolver', 'Company', 'Branch', 'Priority', 'Category']
        for text_col in text_columns:
            if text_col in df_clean.columns:
                df_clean[text_col] = df_clean[text_col].astype(str).str.strip()
                df_clean[text_col] = df_clean[text_col].replace('nan', np.nan)
        
        # Handle Ticket ID
        if 'Ticket ID' in df_clean.columns:
            df_clean['Ticket ID'] = df_clean['Ticket ID'].astype(str).str.strip()
        
        # Remove completely empty rows
        df_clean = df_clean.dropna(how='all')
        
        return df_clean
    
    def process_data(self, df):
        """Process data for analysis"""
        processed_data = {
            'total_tickets': len(df),
            'pending_tickets': self.get_pending_tickets(df),
            'resolved_tickets': self.get_resolved_tickets(df),
            'status_distribution': self.get_status_distribution(df),
            'user_distribution': self.get_user_distribution(df),
            'company_distribution': self.get_company_distribution(df),
            'priority_distribution': self.get_priority_distribution(df)
        }
        
        return processed_data
    
    def get_pending_tickets(self, df):
        """Get pending tickets (not resolved/closed)"""
        if 'Status' not in df.columns:
            return pd.DataFrame()
        
        # Based on your CSV, the non-resolved statuses include various active states
        resolved_statuses = ['Closed', 'Completed', 'Auto Completed', 'Discard']
        pending_tickets = df[~df['Status'].isin(resolved_statuses)]
        
        return pending_tickets
    
    def get_resolved_tickets(self, df):
        """Get resolved tickets"""
        if 'Status' not in df.columns:
            return pd.DataFrame()
        
        resolved_statuses = ['Closed', 'Completed', 'Auto Completed']
        resolved_tickets = df[df['Status'].isin(resolved_statuses)]
        
        return resolved_tickets
    
    def get_status_distribution(self, df):
        """Get distribution of tickets by status"""
        if 'Status' not in df.columns:
            return pd.Series()
        
        return df['Status'].value_counts()
    
    def get_user_distribution(self, df):
        """Get distribution of tickets by assigned user"""
        if 'Assigned User' not in df.columns:
            return pd.Series()
        
        return df['Assigned User'].value_counts()
    
    def get_company_distribution(self, df):
        """Get distribution of tickets by company"""
        if 'Company' not in df.columns:
            return pd.Series()
        
        return df['Company'].value_counts()
    
    def get_priority_distribution(self, df):
        """Get distribution of tickets by priority"""
        if 'Priority' not in df.columns:
            return pd.Series()
        
        return df['Priority'].value_counts()
    
    def calculate_resolution_time(self, df):
        """Calculate resolution time for resolved tickets"""
        if 'Created Date' not in df.columns or 'Resolved Date' not in df.columns:
            return pd.Series()
        
        resolved_tickets = self.get_resolved_tickets(df)
        if resolved_tickets.empty:
            return pd.Series()
        
        # Calculate resolution time in days
        resolution_time = (resolved_tickets['Resolved Date'] - resolved_tickets['Created Date']).dt.days
        
        return resolution_time.dropna()
