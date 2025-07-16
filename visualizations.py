import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class TicketVisualizer:
    """Class to create various visualizations for ticket data"""
    
    def __init__(self, data):
        self.data = data
        self.colors = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e',
            'success': '#2ca02c',
            'danger': '#d62728',
            'warning': '#ff7f0e',
            'info': '#17a2b8'
        }
    
    def create_status_distribution_chart(self):
        """Create a pie chart showing ticket distribution by status"""
        if 'Status' not in self.data.columns or self.data.empty:
            return None
        
        status_counts = self.data['Status'].value_counts()
        
        fig = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title="Ticket Distribution by Status",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        )
        
        fig.update_layout(
            height=400,
            showlegend=True,
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.01)
        )
        
        return fig
    
    def create_priority_distribution_chart(self):
        """Create a bar chart showing ticket distribution by priority"""
        if 'Priority' not in self.data.columns or self.data.empty:
            return None
        
        priority_counts = self.data['Priority'].value_counts()
        
        fig = px.bar(
            x=priority_counts.index,
            y=priority_counts.values,
            title="Ticket Distribution by Priority",
            labels={'x': 'Priority', 'y': 'Count'},
            color=priority_counts.values,
            color_continuous_scale='RdYlBu_r'
        )
        
        fig.update_traces(
            hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>'
        )
        
        fig.update_layout(
            height=400,
            xaxis_title="Priority",
            yaxis_title="Number of Tickets",
            showlegend=False
        )
        
        return fig
    
    def create_timeline_chart(self):
        """Create a timeline chart showing ticket creation over time"""
        if 'Created Date' not in self.data.columns or self.data.empty:
            return None
        
        # Group by date
        timeline_data = self.data.groupby(self.data['Created Date'].dt.date).size().reset_index()
        timeline_data.columns = ['Date', 'Count']
        
        fig = px.line(
            timeline_data,
            x='Date',
            y='Count',
            title="Ticket Creation Timeline",
            markers=True
        )
        
        fig.update_traces(
            hovertemplate='<b>%{x}</b><br>Tickets Created: %{y}<extra></extra>',
            line=dict(width=3),
            marker=dict(size=8)
        )
        
        fig.update_layout(
            height=400,
            xaxis_title="Date",
            yaxis_title="Number of Tickets Created",
            hovermode='x unified'
        )
        
        return fig
    
    def create_pending_by_user_chart(self):
        """Create a bar chart showing pending tickets by assigned user"""
        if 'Assigned User' not in self.data.columns or self.data.empty:
            return None
        
        # Get pending tickets
        resolved_statuses = ['Closed', 'Completed', 'Auto Completed', 'Discard']
        pending_tickets = self.data[~self.data['Status'].isin(resolved_statuses)]
        
        if pending_tickets.empty:
            return None
        
        user_counts = pending_tickets['Assigned User'].value_counts()
        
        fig = px.bar(
            x=user_counts.values,
            y=user_counts.index,
            title="Pending Tickets by Assigned User",
            labels={'x': 'Number of Pending Tickets', 'y': 'Assigned User'},
            orientation='h',
            color=user_counts.values,
            color_continuous_scale='Reds'
        )
        
        fig.update_traces(
            hovertemplate='<b>%{y}</b><br>Pending Tickets: %{x}<extra></extra>'
        )
        
        fig.update_layout(
            height=max(400, len(user_counts) * 30),
            showlegend=False,
            yaxis={'categoryorder': 'total ascending'}
        )
        
        return fig
    
    def create_pending_by_status_chart(self):
        """Create a pie chart showing pending tickets by status"""
        if 'Status' not in self.data.columns or self.data.empty:
            return None
        
        # Get pending tickets
        resolved_statuses = ['Closed', 'Completed', 'Auto Completed', 'Discard']
        pending_tickets = self.data[~self.data['Status'].isin(resolved_statuses)]
        
        if pending_tickets.empty:
            return None
        
        status_counts = pending_tickets['Status'].value_counts()
        
        fig = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title="Pending Tickets by Status",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        )
        
        fig.update_layout(
            height=400,
            showlegend=True
        )
        
        return fig
    
    def create_resolved_by_resolver_chart(self):
        """Create a bar chart showing resolved tickets by resolver"""
        if 'Resolver' not in self.data.columns or self.data.empty:
            return None
        
        # Get resolved tickets
        resolved_statuses = ['Closed', 'Completed', 'Auto Completed']
        resolved_tickets = self.data[self.data['Status'].isin(resolved_statuses)]
        
        if resolved_tickets.empty or resolved_tickets['Resolver'].isna().all():
            return None
        
        resolver_counts = resolved_tickets['Resolver'].value_counts()
        
        fig = px.bar(
            x=resolver_counts.values,
            y=resolver_counts.index,
            title="Resolved Tickets by Resolver",
            labels={'x': 'Number of Resolved Tickets', 'y': 'Resolver'},
            orientation='h',
            color=resolver_counts.values,
            color_continuous_scale='Greens'
        )
        
        fig.update_traces(
            hovertemplate='<b>%{y}</b><br>Resolved Tickets: %{x}<extra></extra>'
        )
        
        fig.update_layout(
            height=max(400, len(resolver_counts) * 30),
            showlegend=False,
            yaxis={'categoryorder': 'total ascending'}
        )
        
        return fig
    
    def create_resolution_time_chart(self):
        """Create a histogram showing resolution time distribution"""
        if 'Created Date' not in self.data.columns or 'Resolved Date' not in self.data.columns:
            return None
        
        # Get resolved tickets with both dates
        resolved_tickets = self.data[
            (self.data['Status'].isin(['Closed', 'Completed', 'Auto Completed'])) &
            (self.data['Created Date'].notna()) &
            (self.data['Resolved Date'].notna())
        ]
        
        if resolved_tickets.empty:
            return None
        
        # Calculate resolution time in days
        resolution_time = (resolved_tickets['Resolved Date'] - resolved_tickets['Created Date']).dt.days
        resolution_time = resolution_time.dropna()
        
        if resolution_time.empty:
            return None
        
        fig = px.histogram(
            x=resolution_time,
            title="Resolution Time Distribution",
            labels={'x': 'Resolution Time (Days)', 'y': 'Number of Tickets'},
            nbins=20
        )
        
        fig.update_traces(
            hovertemplate='<b>%{x} days</b><br>Tickets: %{y}<extra></extra>'
        )
        
        fig.update_layout(
            height=400,
            xaxis_title="Resolution Time (Days)",
            yaxis_title="Number of Tickets",
            bargap=0.1
        )
        
        return fig
    
    def get_pending_tickets_table(self):
        """Get a formatted table of pending tickets"""
        if self.data.empty:
            return pd.DataFrame()
        
        # Get pending tickets
        resolved_statuses = ['Closed', 'Completed', 'Auto Completed', 'Discard']
        pending_tickets = self.data[~self.data['Status'].isin(resolved_statuses)]
        
        if pending_tickets.empty:
            return pd.DataFrame()
        
        # Select and format columns for display
        display_columns = []
        if 'Ticket ID' in pending_tickets.columns:
            display_columns.append('Ticket ID')
        if 'Status' in pending_tickets.columns:
            display_columns.append('Status')
        if 'Assigned User' in pending_tickets.columns:
            display_columns.append('Assigned User')
        if 'Priority' in pending_tickets.columns:
            display_columns.append('Priority')
        if 'Created Date' in pending_tickets.columns:
            display_columns.append('Created Date')
        if 'Company' in pending_tickets.columns:
            display_columns.append('Company')
        if 'Branch' in pending_tickets.columns:
            display_columns.append('Branch')
        
        table_data = pending_tickets[display_columns].copy()
        
        # Format dates
        if 'Created Date' in table_data.columns:
            table_data['Created Date'] = pd.to_datetime(table_data['Created Date']).dt.strftime('%Y-%m-%d')
        
        return table_data
    
    def get_resolved_tickets_table(self):
        """Get a formatted table of resolved tickets"""
        if self.data.empty:
            return pd.DataFrame()
        
        # Get resolved tickets
        resolved_statuses = ['Closed', 'Completed', 'Auto Completed']
        resolved_tickets = self.data[self.data['Status'].isin(resolved_statuses)]
        
        if resolved_tickets.empty:
            return pd.DataFrame()
        
        # Select and format columns for display
        display_columns = []
        if 'Ticket ID' in resolved_tickets.columns:
            display_columns.append('Ticket ID')
        if 'Status' in resolved_tickets.columns:
            display_columns.append('Status')
        if 'Resolver' in resolved_tickets.columns:
            display_columns.append('Resolver')
        if 'Priority' in resolved_tickets.columns:
            display_columns.append('Priority')
        if 'Created Date' in resolved_tickets.columns:
            display_columns.append('Created Date')
        if 'Resolved Date' in resolved_tickets.columns:
            display_columns.append('Resolved Date')
        if 'Company' in resolved_tickets.columns:
            display_columns.append('Company')
        if 'Branch' in resolved_tickets.columns:
            display_columns.append('Branch')
        
        table_data = resolved_tickets[display_columns].copy()
        
        # Format dates
        if 'Created Date' in table_data.columns:
            table_data['Created Date'] = pd.to_datetime(table_data['Created Date']).dt.strftime('%Y-%m-%d')
        if 'Resolved Date' in table_data.columns:
            table_data['Resolved Date'] = pd.to_datetime(table_data['Resolved Date']).dt.strftime('%Y-%m-%d')
        
        return table_data
