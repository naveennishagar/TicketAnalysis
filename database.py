import os
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import streamlit as st

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Ticket(Base):
    __tablename__ = "tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String, unique=True, index=True)
    requester = Column(String)
    created_user = Column(String)
    requested_date = Column(DateTime)
    ticket_type = Column(String)
    ticket_category = Column(String)
    ticket_sub_category = Column(String)
    company_name = Column(String)
    branch_name = Column(String)
    department_name = Column(String)
    subject = Column(String)
    description = Column(Text)
    current_status = Column(String)
    assign_from = Column(String)
    assigned_to = Column(String)
    assigned_date = Column(DateTime)
    sla = Column(String)
    live_transferred_date = Column(DateTime)
    is_re_submitted = Column(String)
    resolved_date = Column(DateTime)
    no_of_days = Column(Integer)
    no_of_working_days = Column(Integer)
    resolved_by = Column(String)
    last_comment = Column(Text)
    last_remark = Column(Text)
    upload_timestamp = Column(DateTime, default=datetime.utcnow)

class DatabaseManager:
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal
        
    def create_tables(self):
        """Create database tables"""
        Base.metadata.create_all(bind=self.engine)
        
    def get_session(self):
        """Get database session"""
        return self.SessionLocal()
        
    def save_tickets_to_db(self, df):
        """Save tickets DataFrame to database"""
        try:
            session = self.get_session()
            
            # Clear existing data (optional - you might want to keep historical data)
            session.query(Ticket).delete()
            
            # Convert DataFrame to database records
            for _, row in df.iterrows():
                ticket = Ticket(
                    ticket_id=str(row.get('Ticket ID', '')),
                    requester=str(row.get('Requester', '')),
                    created_user=str(row.get('Created User', '')),
                    requested_date=pd.to_datetime(row.get('Created Date'), errors='coerce'),
                    ticket_type=str(row.get('Ticket Type', '')),
                    ticket_category=str(row.get('Category', '')),
                    ticket_sub_category=str(row.get('Ticket Sub Category', '')),
                    company_name=str(row.get('Company', '')),
                    branch_name=str(row.get('Branch', '')),
                    department_name=str(row.get('Department Name', '')),
                    subject=str(row.get('Title', '')),
                    description=str(row.get('Description', '')),
                    current_status=str(row.get('Status', '')),
                    assign_from=str(row.get('Assign From', '')),
                    assigned_to=str(row.get('Assigned User', '')),
                    assigned_date=pd.to_datetime(row.get('Assigned Date'), errors='coerce'),
                    sla=str(row.get('SLA', '')),
                    live_transferred_date=pd.to_datetime(row.get('Live Transferred Date'), errors='coerce'),
                    is_re_submitted=str(row.get('Is Re-Submitted', '')),
                    resolved_date=pd.to_datetime(row.get('Resolved Date'), errors='coerce'),
                    no_of_days=int(row.get('No Of Days', 0)) if pd.notna(row.get('No Of Days')) else 0,
                    no_of_working_days=int(row.get('No Of Working Days', 0)) if pd.notna(row.get('No Of Working Days')) else 0,
                    resolved_by=str(row.get('Resolver', '')),
                    last_comment=str(row.get('Last Comment', '')),
                    last_remark=str(row.get('Last Remark', ''))
                )
                session.add(ticket)
                
            session.commit()
            session.close()
            return True
            
        except Exception as e:
            session.rollback()
            session.close()
            st.error(f"Error saving to database: {str(e)}")
            return False
            
    def load_tickets_from_db(self):
        """Load tickets from database and return as DataFrame"""
        try:
            session = self.get_session()
            tickets = session.query(Ticket).all()
            session.close()
            
            if not tickets:
                return pd.DataFrame()
                
            # Convert to DataFrame
            data = []
            for ticket in tickets:
                data.append({
                    'Ticket ID': ticket.ticket_id,
                    'Requester': ticket.requester,
                    'Created User': ticket.created_user,
                    'Created Date': ticket.requested_date,
                    'Ticket Type': ticket.ticket_type,
                    'Category': ticket.ticket_category,
                    'Ticket Sub Category': ticket.ticket_sub_category,
                    'Company': ticket.company_name,
                    'Branch': ticket.branch_name,
                    'Department Name': ticket.department_name,
                    'Title': ticket.subject,
                    'Description': ticket.description,
                    'Status': ticket.current_status,
                    'Assign From': ticket.assign_from,
                    'Assigned User': ticket.assigned_to,
                    'Assigned Date': ticket.assigned_date,
                    'SLA': ticket.sla,
                    'Live Transferred Date': ticket.live_transferred_date,
                    'Is Re-Submitted': ticket.is_re_submitted,
                    'Resolved Date': ticket.resolved_date,
                    'No Of Days': ticket.no_of_days,
                    'No Of Working Days': ticket.no_of_working_days,
                    'Resolver': ticket.resolved_by,
                    'Last Comment': ticket.last_comment,
                    'Last Remark': ticket.last_remark
                })
                
            return pd.DataFrame(data)
            
        except Exception as e:
            st.error(f"Error loading from database: {str(e)}")
            return pd.DataFrame()
            
    def get_ticket_stats(self):
        """Get basic ticket statistics"""
        try:
            session = self.get_session()
            
            total_tickets = session.query(Ticket).count()
            
            resolved_statuses = ['Closed', 'Completed', 'Auto Completed']
            resolved_count = session.query(Ticket).filter(
                Ticket.current_status.in_(resolved_statuses)
            ).count()
            
            pending_count = total_tickets - resolved_count
            
            session.close()
            
            return {
                'total': total_tickets,
                'resolved': resolved_count,
                'pending': pending_count
            }
            
        except Exception as e:
            st.error(f"Error getting stats: {str(e)}")
            return {'total': 0, 'resolved': 0, 'pending': 0}
            
    def clear_all_data(self):
        """Clear all ticket data from database"""
        try:
            session = self.get_session()
            session.query(Ticket).delete()
            session.commit()
            session.close()
            return True
        except Exception as e:
            st.error(f"Error clearing data: {str(e)}")
            return False