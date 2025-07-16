# Ticket Tracking Dashboard

## Overview

This repository contains a Streamlit-based ticket tracking dashboard application that allows users to upload Excel files containing ticket data and visualize various metrics and trends. The application provides interactive charts and analytics for ticket management, including status distribution, priority analysis, and performance metrics.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit - A Python-based web framework for building data applications
- **Layout**: Wide layout with expandable sidebar for controls and main content area for visualizations
- **State Management**: Streamlit's session state for maintaining data across user interactions
- **Visualization**: Plotly Express and Plotly Graph Objects for interactive charts and graphs

### Backend Architecture
- **Core Components**: 
  - `app.py` - Main application entry point and UI orchestration
  - `data_processor.py` - Data loading, validation, and transformation logic
  - `visualizations.py` - Chart generation and visualization components
- **Data Processing**: Pandas for data manipulation and analysis
- **File Handling**: Excel file upload and processing capabilities

### Data Storage
- **Primary Storage**: PostgreSQL database with SQLAlchemy ORM
- **Session Storage**: Streamlit session state for temporary data persistence
- **File Format**: Excel (.xlsx, .xls) and CSV (.csv) input files
- **Database Schema**: Comprehensive ticket table with all data fields

## Key Components

### Database Manager (`database.py`)
- **Purpose**: Handles PostgreSQL database operations and data persistence
- **Key Features**:
  - SQLAlchemy ORM for database operations
  - Ticket model with comprehensive schema
  - Data saving and loading from database
  - Database statistics and management
- **Operations**: Create tables, save tickets, load tickets, clear data

### Data Processor (`data_processor.py`)
- **Purpose**: Handles Excel/CSV file loading, validation, and data cleaning
- **Key Features**:
  - Column validation with flexible matching
  - Data type standardization
  - Error handling and user feedback
  - Support for both Excel and CSV formats
- **Required Columns**: Ticket ID, Current Status, AssignedTo, Requested Date
- **Optional Columns**: Resolved By, Resolved Date, Company Name, Branch Name, Ticket Category, Subject, Description

### Ticket Visualizer (`visualizations.py`)
- **Purpose**: Creates interactive charts and visualizations
- **Chart Types**:
  - Status distribution (pie chart)
  - Priority distribution (bar chart)
  - Performance metrics and trends
- **Styling**: Custom color schemes and responsive design

### Main Application (`app.py`)
- **Purpose**: Orchestrates the user interface and component interactions
- **Features**:
  - File upload interface
  - Data processing workflow
  - Visualization rendering
  - Error handling and user feedback

## Data Flow

1. **File Upload**: User uploads Excel file through Streamlit file uploader
2. **Data Validation**: DataProcessor validates required columns and data integrity
3. **Data Processing**: Raw data is cleaned, standardized, and prepared for analysis
4. **Visualization**: TicketVisualizer generates interactive charts from processed data
5. **Display**: Charts and metrics are rendered in the Streamlit interface
6. **State Management**: Processed data is stored in session state for reuse

## External Dependencies

### Core Libraries
- **streamlit**: Web application framework
- **pandas**: Data manipulation and analysis
- **plotly**: Interactive visualization library
- **numpy**: Numerical computing support
- **datetime**: Date and time handling

### File Processing
- **openpyxl/xlrd**: Excel file reading capabilities (implicit through pandas)
- **io**: File stream handling

## Deployment Strategy

### Development Environment
- **Platform**: Replit-compatible Python environment
- **Entry Point**: `app.py` serves as the main application file
- **Dependencies**: Managed through requirements.txt or direct installation

### Production Considerations
- **Scalability**: Single-user sessions with in-memory data storage
- **Performance**: Optimized for medium-sized Excel files
- **Security**: File upload validation and error handling

### Architectural Decisions

1. **Streamlit Choice**: Selected for rapid prototyping and ease of deployment, providing built-in file upload and visualization capabilities
2. **Modular Design**: Separated concerns into distinct classes (DataProcessor, TicketVisualizer) for maintainability
3. **In-Memory Storage**: Chosen for simplicity and fast access, suitable for dashboard use cases
4. **Pandas Integration**: Leveraged for powerful data manipulation and Excel file processing
5. **Plotly Visualization**: Selected for interactive charts that enhance user experience

### Known Limitations
- No persistent data storage between sessions
- Limited to Excel file inputs
- Single-user concurrent access model
- Memory constraints for very large datasets