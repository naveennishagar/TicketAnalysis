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
        """Create a pie chart showing distribution of pending and resolved tickets"""
        if 'Status' not in self.data.columns or self.data.empty:
            return None
        resolved_statuses = ['Closed', 'Completed', 'Auto Completed']
        counts = {
            'Pending': len(self.data[~self.data['Status'].isin(resolved_statuses + ['Discard'])]),
            'Resolved': len(self.data[self.data['Status'].isin(resolved_statuses)])
        }
        if counts['Pending'] + counts['Resolved'] == 0:
            return None
        fig = px.pie(names=counts.keys(), values=counts.values(), title="Pending vs Resolved Tickets")
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=400)
        return fig
    
    def create_timeline_chart(self):
        """Create a line chart showing daily ticket counts for the user"""
        if 'Created Date' not in self.data.columns or self.data.empty:
            return None
        df = self.data.copy()
        df['Date'] = pd.to_datetime(df['Created Date']).dt.date
        daily_counts = df.groupby('Date').size().reset_index(name='Count')
        daily_counts = daily_counts.sort_values('Date')
        fig = px.line(daily_counts, x='Date', y='Count', title="Daily Ticket Creation", markers=True)
        fig.update_layout(height=400, xaxis_title="Date", yaxis_title="Number of Tickets")
        return fig
    
    def create_pending_status_pie(self):
        """Create a pie chart showing pending tickets distribution by status"""
        if 'Status' not in self.data.columns or self.data.empty:
            return None
        resolved_statuses = ['Closed', 'Completed', 'Auto Completed', 'Discard']
        pending_data = self.data[~self.data['Status'].isin(resolved_statuses)]
        if pending_data.empty:
            return None
        status_counts = pending_data['Status'].value_counts()
        fig = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title="Pending Tickets by Status",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_traces(textposition='inside', textinfo='percent+label', hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>')
        fig.update_layout(height=400, showlegend=True)
        return fig

    def create_resolved_status_pie(self):
        """Create a pie chart showing resolved tickets distribution by status"""
        if 'Status' not in self.data.columns or self.data.empty:
            return None
        resolved_statuses = ['Closed', 'Completed', 'Auto Completed']
        resolved_data = self.data[self.data['Status'].isin(resolved_statuses)]
        if resolved_data.empty:
            return None
        status_counts = resolved_data['Status'].value_counts()
        fig = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title="Resolved Tickets by Status",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.update_traces(textposition='inside', textinfo='percent+label', hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>')
        fig.update_layout(height=400, showlegend=True)
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
    
    def create_daily_tickets_line_chart(self):
        """Create a line chart showing daily total, resolved, and pending tickets"""
        if 'Created Date' not in self.data.columns or 'Status' not in self.data.columns or self.data.empty:
            return None
        
        self.data['Date'] = pd.to_datetime(self.data['Created Date']).dt.date
        resolved_statuses = ['Closed', 'Completed', 'Auto Completed']
        
        daily_data = self.data.groupby('Date').agg(
            total=('Ticket ID', 'count')
        ).reset_index()
        
        daily_resolved = self.data[self.data['Status'].isin(resolved_statuses)].groupby('Date').agg(
            resolved=('Ticket ID', 'count')
        ).reset_index()
        
        daily_pending = self.data[~self.data['Status'].isin(resolved_statuses + ['Discard'])].groupby('Date').agg(
            pending=('Ticket ID', 'count')
        ).reset_index()
        
        daily_data = daily_data.merge(daily_resolved, on='Date', how='left').merge(daily_pending, on='Date', how='left').fillna(0)
        daily_data = daily_data.sort_values('Date')
        daily_data['Date Str'] = daily_data['Date'].astype(str)
        
        fig = px.line(
            daily_data.melt(id_vars=['Date Str'], value_vars=['total', 'resolved', 'pending']),
            x='Date Str',
            y='value',
            color='variable',
            title="Daily Tickets: Total, Resolved, Pending",
            markers=True
        )
        
        fig.update_traces(
            hovertemplate='<b>%{x}</b><br>%{data.name}: %{y}<extra></extra>'
        )
        
        fig.update_layout(
            height=400,
            xaxis_title="Date",
            yaxis_title="Number of Tickets",
            hovermode='x unified',
            legend_title="Ticket Type"
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
        if 'Assigned By' in pending_tickets.columns:
            display_columns.append('Assigned By')
        if 'Priority' in pending_tickets.columns:
            display_columns.append('Priority')
        if 'Created Date' in pending_tickets.columns:
            display_columns.append('Created Date')
        if 'Company' in pending_tickets.columns:
            display_columns.append('Company')
        
        
        table_data = pending_tickets[display_columns].copy()
        
        # Format dates
        if 'Created Date' in table_data.columns:
            table_data['Created Date'] = pd.to_datetime(table_data['Created Date']).dt.strftime('%Y-%m-%d')
        
        return table_data

    def create_day_wise_pending_chart(self):
        """Create a simple line chart showing day-wise cumulative pending tickets"""
        if 'Created Date' not in self.data.columns or self.data.empty:
            return None
        
        resolved_statuses = ['Closed', 'Completed', 'Auto Completed', 'Discard']
        pending_tickets = self.data[~self.data['Status'].isin(resolved_statuses)]
        
        if pending_tickets.empty:
            return None
        
        pending_tickets['Created Date'] = pd.to_datetime(pending_tickets['Created Date'])
        daily_pending = pending_tickets.groupby(pending_tickets['Created Date'].dt.date).size().reset_index()
        daily_pending.columns = ['Date', 'Count']
        daily_pending = daily_pending.sort_values('Date')
        daily_pending['Cumulative'] = daily_pending['Count'].cumsum()
        
        fig = px.line(
            daily_pending,
            x='Date',
            y='Cumulative',
            title="Day-wise Cumulative Pending Tickets",
            markers=True
        )
        
        fig.update_traces(
            hovertemplate='<b>%{x}</b><br>Cumulative Pending: %{y}<extra></extra>',
            line=dict(width=3, color='red'),
            marker=dict(size=8)
        )
        
        fig.update_layout(
            height=400,
            xaxis_title="Date",
            yaxis_title="Cumulative Pending Tickets",
            hovermode='x unified'
        )
        
        return fig

    def create_day_wise_resolved_chart(self):
        """Create a simple line chart showing day-wise cumulative resolved tickets"""
        if 'Resolved Date' not in self.data.columns or self.data.empty:
            return None
        
        resolved_statuses = ['Closed', 'Completed', 'Auto Completed']
        resolved_tickets = self.data[self.data['Status'].isin(resolved_statuses)]
        
        if resolved_tickets.empty:
            return None
        
        resolved_tickets['Resolved Date'] = pd.to_datetime(resolved_tickets['Resolved Date'])
        daily_resolved = resolved_tickets.groupby(resolved_tickets['Resolved Date'].dt.date).size().reset_index()
        daily_resolved.columns = ['Date', 'Count']
        daily_resolved = daily_resolved.sort_values('Date')
        daily_resolved['Cumulative'] = daily_resolved['Count'].cumsum()
        
        fig = px.line(
            daily_resolved,
            x='Date',
            y='Cumulative',
            title="Day-wise Cumulative Resolved Tickets",
            markers=True
        )
        
        fig.update_traces(
            hovertemplate='<b>%{x}</b><br>Cumulative Resolved: %{y}<extra></extra>',
            line=dict(width=3),
            marker=dict(size=8)
        )
        
        fig.update_layout(
            height=400,
            xaxis_title="Date",
            yaxis_title="Cumulative Resolved Tickets",
            hovermode='x unified'
        )
        
        return fig
    
    def create_daily_resolved_chart(self):
        """Create a line chart showing daily resolved ticket counts for the user"""
        if 'Resolved Date' not in self.data.columns or self.data.empty:
            return None
        df = self.data.copy()
        df['Date'] = pd.to_datetime(df['Resolved Date']).dt.date
        daily_counts = df.groupby('Date').size().reset_index(name='Count')
        daily_counts = daily_counts.sort_values('Date')
        fig = px.line(daily_counts, x='Date', y='Count', title="Daily Ticket Resolved", markers=True)
        fig.update_layout(height=400, xaxis_title="Date", yaxis_title="Number of Tickets")
        return fig

    def create_daily_assigned_chart(self):
        """Create a line chart showing daily assigned ticket counts for the user"""
        if 'Created Date' not in self.data.columns or self.data.empty:
            return None
        df = self.data.copy()
        df['Date'] = pd.to_datetime(df['Created Date']).dt.date
        daily_counts = df.groupby('Date').size().reset_index(name='Count')
        daily_counts = daily_counts.sort_values('Date')
        fig = px.line(daily_counts, x='Date', y='Count', title="Daily Ticket Assigned", markers=True)
        fig.update_layout(height=400, xaxis_title="Date", yaxis_title="Number of Tickets")
        return fig

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
        if 'Assigned By' in resolved_tickets.columns:
            display_columns.append('Assigned By')
        if 'Priority' in resolved_tickets.columns:
            display_columns.append('Priority')
        if 'Created Date' in resolved_tickets.columns:
            display_columns.append('Created Date')
        if 'Resolved Date' in resolved_tickets.columns:
            display_columns.append('Resolved Date')
        if 'Company' in resolved_tickets.columns:
            display_columns.append('Company')
        
        
        table_data = resolved_tickets[display_columns].copy()
        
        # Format dates
        if 'Created Date' in table_data.columns:
            table_data['Created Date'] = pd.to_datetime(table_data['Created Date']).dt.strftime('%Y-%m-%d')
        if 'Resolved Date' in table_data.columns:
            table_data['Resolved Date'] = pd.to_datetime(table_data['Resolved Date']).dt.strftime('%Y-%m-%d')
        
        return table_data
