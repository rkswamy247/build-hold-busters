import streamlit as st
import pandas as pd
from databricks import sql
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import genie_chat

# Page configuration
st.set_page_config(
    page_title="Hold Busters Dashboard",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# Databricks connection
@st.cache_resource
def get_databricks_connection():
    """
    Create a connection to Databricks SQL Warehouse
    """
    try:
        # Try to get from Streamlit secrets first (recommended)
        if hasattr(st, 'secrets') and 'databricks' in st.secrets:
            return sql.connect(
                server_hostname=st.secrets.databricks.server_hostname,
                http_path=st.secrets.databricks.http_path,
                access_token=st.secrets.databricks.token
            )
        # Fallback to environment variables
        else:
            return sql.connect(
                server_hostname=os.getenv("DATABRICKS_SERVER_HOSTNAME"),
                http_path=os.getenv("DATABRICKS_HTTP_PATH"),
                access_token=os.getenv("DATABRICKS_TOKEN")
            )
    except Exception as e:
        st.error(f"Failed to connect to Databricks: {str(e)}")
        st.info("Please configure your Databricks credentials in .streamlit/secrets.toml")
        return None

# Query functions with caching
@st.cache_data(ttl=600)  # Cache for 10 minutes
def query_databricks(_conn, query):
    """Execute a query and return results as pandas DataFrame"""
    try:
        cursor = _conn.cursor()
        cursor.execute(query)
        # Fetch as Arrow table and convert to pandas
        result = cursor.fetchall_arrow().to_pandas()
        cursor.close()
        return result
    except Exception as e:
        st.error(f"Query error: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=600)
def get_invoices(_conn, schema_name="default"):
    """Fetch invoices from Databricks table"""
    query = f"""
    SELECT 
        Invoice_Id,
        Invoice_Name,
        Vendor__Name,
        PO_Name,
        Invoice_Date__c,
        Total_Amount__c,
        sitetracker__Status__c as Status,
        Days_Pending_Approval__c,
        Integration_Status__c,
        Integration_Error_Message__c,
        Reason__c,
        State__c,
        Approval_Date__c,
        Due_Date_Formula__c
    FROM {schema_name}.invoices
    WHERE Invoice_Date__c IS NOT NULL
    ORDER BY Invoice_Date__c DESC
    """
    return query_databricks(_conn, query)

@st.cache_data(ttl=600)
def get_invoice_lines(_conn, schema_name="default"):
    """Fetch invoice lines from Databricks table"""
    query = f"""
    SELECT 
        Invoice_Line_Id,
        Invoice_Id,
        Project_Id,
        Invoice_Amount__c,
        Invoice_Status__c,
        Infinium_Project_Number__c,
        Company_Code__c,
        Cost_Category_Name__c,
        sitetracker__Quantity__c,
        sitetracker__Unit_Price__c
    FROM {schema_name}.invoice_lines
    """
    return query_databricks(_conn, query)

@st.cache_data(ttl=600)
def get_projects(_conn, schema_name="default"):
    """Fetch projects from Databricks table"""
    query = f"""
    SELECT 
        Project_Id,
        Infinium_Project_Number__c,
        Company__c,
        Infinium_Status__c,
        Approval_Status__c
    FROM {schema_name}.projects
    """
    return query_databricks(_conn, query)

@st.cache_data(ttl=600)
def get_integration_responses(_conn, schema_name="default"):
    """Fetch integration responses from Databricks table"""
    query = f"""
    SELECT 
        Invoice_Id,
        Infinium_Request__c,
        Infinium_Response__c,
        Error_Message__c,
        Operation__c
    FROM {schema_name}.Integration_Responses
    """
    return query_databricks(_conn, query)

@st.cache_data(ttl=600)
def get_purchase_orders(_conn, schema_name="default"):
    """Fetch purchase orders from Databricks table"""
    query = f"""
    SELECT 
        PO_Name,
        PO_Amount,
        Vendor__Name,
        PO_Status__c
    FROM {schema_name}.Purchase_Orders
    """
    return query_databricks(_conn, query)

def insert_linus_request(_conn, request_data, schema_name="default"):
    """Insert a Linus request into the database"""
    try:
        cursor = _conn.cursor()
        
        insert_query = f"""
        INSERT INTO {schema_name}.Linus_Requests (
            Request_Id, Invoice_Id, Invoice_Name, PO_Name, Vendor_Name,
            Invoice_Amount, Months_Into_Year, Total_Approved_PO, 
            Invoiced_Year_To_Date, Remaining_Balance, Total_Pending,
            Expected_Additional, Supplemental_Amount, Request_Date, 
            Created_By, Status, LastModifiedDate
        ) VALUES (
            '{request_data['Request_Id']}',
            '{request_data['Invoice_Id']}',
            '{request_data['Invoice_Name']}',
            '{request_data['PO_Name']}',
            '{request_data['Vendor_Name']}',
            {request_data['Invoice_Amount']},
            {request_data['Months_Into_Year']},
            {request_data['Total_Approved_PO']},
            {request_data['Invoiced_Year_To_Date']},
            {request_data['Remaining_Balance']},
            {request_data['Total_Pending']},
            {request_data['Expected_Additional']},
            {request_data['Supplemental_Amount']},
            CURRENT_TIMESTAMP(),
            'Streamlit App',
            'Pending',
            CURRENT_TIMESTAMP()
        )
        """
        
        cursor.execute(insert_query)
        cursor.close()
        return True
    except Exception as e:
        st.error(f"Error inserting request: {str(e)}")
        return False

# Main app
def main():
    st.title("🔍 Hold Busters - Invoice Analysis Dashboard")
    st.markdown("### Databricks-Powered Invoice Hold Analysis")
    st.markdown("---")
    
    # Initialize Genie session state
    genie_chat.initialize_genie_session_state()
    
    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Track if we should stay on Genie tab (for preserving active tab on rerun)
    if 'stay_on_genie_tab' not in st.session_state:
        st.session_state.stay_on_genie_tab = False
    
    # Sidebar configuration
    st.sidebar.header("⚙️ Configuration")
    
    # Get default schema from secrets
    default_schema = "default"
    if hasattr(st, 'secrets') and 'databricks' in st.secrets:
        if 'default_schema' in st.secrets.databricks:
            default_schema = st.secrets.databricks.default_schema
    
    # Schema selector
    schema_name = st.sidebar.text_input(
        "Databricks Schema Name",
        value=default_schema,
        help="Enter the name of your Databricks schema/database (e.g., default, invoices_db, hackathon/hackathon_build_hold_busters)"
    )
    
    # Get connection
    conn = get_databricks_connection()
    
    if conn is None:
        st.warning("⚠️ Not connected to Databricks. Please configure your credentials.")
        
        with st.expander("📋 Setup Instructions - Click to expand"):
            st.markdown("""
            ### How to configure Databricks connection:
            
            **Option 1: Using secrets.toml (Recommended)**
            
            1. Create a folder `.streamlit` in your project directory
            2. Create a file `.streamlit/secrets.toml` with the following content:
            
            ```toml
            [databricks]
            server_hostname = "dbc-4a93b454-f17b.cloud.databricks.com"
            http_path = "/sql/1.0/warehouses/YOUR_WAREHOUSE_ID"
            token = "YOUR_PERSONAL_ACCESS_TOKEN"
            ```
            
            **Option 2: Using environment variables**
            
            Set these environment variables:
            - `DATABRICKS_SERVER_HOSTNAME` = "dbc-4a93b454-f17b.cloud.databricks.com"
            - `DATABRICKS_HTTP_PATH` = "/sql/1.0/warehouses/YOUR_WAREHOUSE_ID"
            - `DATABRICKS_TOKEN` = "YOUR_PERSONAL_ACCESS_TOKEN"
            
            ---
            
            ### Where to find these values:
            
            1. **server_hostname**: `dbc-4a93b454-f17b.cloud.databricks.com` (already set!)
            
            2. **http_path**: 
               - Go to your Databricks workspace
               - Click "SQL Warehouses" in the left sidebar
               - Select your warehouse
               - Click "Connection details" tab
               - Copy the "HTTP Path" (looks like `/sql/1.0/warehouses/abc123def456`)
            
            3. **token** (Personal Access Token):
               - In Databricks, click your username in top-right
               - Select "User Settings"
               - Go to "Access tokens" tab
               - Click "Generate new token"
               - Give it a name (e.g., "Streamlit App")
               - Set expiration (optional)
               - Copy the token (save it securely!)
            """)
        
        return
    
    st.success("✅ Connected to Databricks!")
    
    # Refresh button
    if st.sidebar.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
    
    # Load data
    with st.spinner("Loading data from Databricks..."):
        try:
            invoices_df = get_invoices(conn, schema_name)
            
            if invoices_df.empty:
                st.warning(f"⚠️ No data found in schema: `{schema_name}`")
                st.info("""
                **Troubleshooting:**
                - Verify the schema name is correct
                - Check that tables exist in your Databricks workspace
                - Ensure your SQL Warehouse is running
                - Verify table names match: `invoices`, `invoice_lines`, `projects`
                """)
                return
            
            # Try to load related tables
            try:
                invoice_lines_df = get_invoice_lines(conn, schema_name)
                projects_df = get_projects(conn, schema_name)
                purchase_orders_df = get_purchase_orders(conn, schema_name)
            except:
                invoice_lines_df = pd.DataFrame()
                projects_df = pd.DataFrame()
                purchase_orders_df = pd.DataFrame()
                
        except Exception as e:
            st.error(f"❌ Error loading data: {str(e)}")
            st.info("Please check your table names and schema configuration")
            return
    
    # Sidebar filters
    st.sidebar.markdown("---")
    st.sidebar.header("🔍 Filters")
    
    status_options = ['All'] + sorted(invoices_df['Status'].unique().tolist())
    selected_status = st.sidebar.multiselect(
        "Invoice Status",
        options=status_options,
        default=['All']
    )
    
    # Apply filters
    filtered_df = invoices_df.copy()
    if 'All' not in selected_status and selected_status:
        filtered_df = filtered_df[filtered_df['Status'].isin(selected_status)]
    
    # Date range filter
    if 'Invoice_Date__c' in filtered_df.columns:
        filtered_df['Invoice_Date__c'] = pd.to_datetime(filtered_df['Invoice_Date__c'])
        min_date = filtered_df['Invoice_Date__c'].min()
        max_date = filtered_df['Invoice_Date__c'].max()
        
        date_range = st.sidebar.date_input(
            "Invoice Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        if len(date_range) == 2:
            filtered_df = filtered_df[
                (filtered_df['Invoice_Date__c'].dt.date >= date_range[0]) &
                (filtered_df['Invoice_Date__c'].dt.date <= date_range[1])
            ]
    
    # KPI Metrics
    st.subheader("📊 Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_invoices = len(filtered_df)
        st.metric("Total Invoices", f"{total_invoices:,}")
    
    with col2:
        on_hold = len(filtered_df[filtered_df['Status'] == 'Hold'])
        hold_pct = (on_hold / total_invoices * 100) if total_invoices > 0 else 0
        st.metric("On Hold", f"{on_hold:,}", f"{hold_pct:.1f}%")
    
    with col3:
        total_amount = filtered_df['Total_Amount__c'].sum()
        st.metric("Total Amount", f"${total_amount:,.2f}")
    
    with col4:
        avg_days = filtered_df['Days_Pending_Approval__c'].mean()
        st.metric("Avg Days Pending", f"{avg_days:.1f}")
    
    st.markdown("---")
    
    # Tabs for different views
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🧞 Genie AI",
        "📈 Overview", 
        "📋 Invoice Details", 
        "🔍 Deep Analysis",
        "🚨 Error Analysis",
        "💾 Custom Query"
    ])
    
    # Overview Tab
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            # Status distribution pie chart
            status_counts = filtered_df['Status'].value_counts()
            fig_status = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                title="Invoice Status Distribution",
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig_status, use_container_width=True)
        
        with col2:
            # Top vendors by amount
            if 'Vendor__Name' in filtered_df.columns:
                top_vendors = filtered_df.groupby('Vendor__Name')['Total_Amount__c'].sum().sort_values(ascending=False).head(10)
                fig_vendors = px.bar(
                    x=top_vendors.values,
                    y=top_vendors.index,
                    orientation='h',
                    title="Top 10 Vendors by Amount",
                    labels={'x': 'Total Amount ($)', 'y': 'Vendor'},
                    color=top_vendors.values,
                    color_continuous_scale='Blues'
                )
                st.plotly_chart(fig_vendors, use_container_width=True)
        
        # Timeline chart
        if 'Invoice_Date__c' in filtered_df.columns:
            timeline_df = filtered_df.groupby(
                filtered_df['Invoice_Date__c'].dt.to_period('M')
            )['Total_Amount__c'].sum().reset_index()
            timeline_df['Invoice_Date__c'] = timeline_df['Invoice_Date__c'].dt.to_timestamp()
            
            fig_timeline = px.line(
                timeline_df,
                x='Invoice_Date__c',
                y='Total_Amount__c',
                title="Invoice Amount Over Time",
                labels={'Invoice_Date__c': 'Date', 'Total_Amount__c': 'Amount ($)'},
                markers=True
            )
            fig_timeline.update_traces(line_color='#1f77b4', line_width=3)
            st.plotly_chart(fig_timeline, use_container_width=True)
    
    # Invoice Details Tab
    with tab3:
        st.subheader("Invoice Details Table")
        
        # Search functionality
        search_term = st.text_input("🔍 Search by Invoice Name, Vendor, or ID", "")
        
        if search_term:
            search_df = filtered_df[
                filtered_df.apply(lambda row: search_term.lower() in str(row).lower(), axis=1)
            ]
        else:
            search_df = filtered_df
        
        # Display count
        st.info(f"Showing {len(search_df)} of {len(filtered_df)} invoices")
        
        # Display dataframe with formatting
        display_df = search_df.copy()
        if 'Invoice_Date__c' in display_df.columns:
            display_df['Invoice_Date__c'] = display_df['Invoice_Date__c'].dt.strftime('%Y-%m-%d')
        
        st.dataframe(
            display_df,
            use_container_width=True,
            height=400
        )
        
        # Download button
        csv = search_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=csv,
            file_name=f"invoices_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    # Deep Analysis Tab
    with tab4:
        st.subheader("Deep Dive Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Days pending distribution
            fig_days = px.histogram(
                filtered_df,
                x='Days_Pending_Approval__c',
                nbins=30,
                title="Distribution of Days Pending Approval",
                labels={'Days_Pending_Approval__c': 'Days Pending'},
                color_discrete_sequence=['#636EFA']
            )
            st.plotly_chart(fig_days, use_container_width=True)
        
        with col2:
            # Amount distribution by status
            fig_amount = px.box(
                filtered_df,
                x='Status',
                y='Total_Amount__c',
                title="Amount Distribution by Status",
                labels={'Total_Amount__c': 'Amount ($)'},
                color='Status'
            )
            st.plotly_chart(fig_amount, use_container_width=True)
        
        # State analysis
        if 'State__c' in filtered_df.columns:
            state_summary = filtered_df.groupby('State__c').agg({
                'Invoice_Id': 'count',
                'Total_Amount__c': 'sum',
                'Days_Pending_Approval__c': 'mean'
            }).reset_index()
            state_summary.columns = ['State', 'Invoice Count', 'Total Amount', 'Avg Days Pending']
            state_summary = state_summary.sort_values('Total Amount', ascending=False)
            
            st.subheader("Summary by State")
            st.dataframe(
                state_summary.style.format({
                    'Total Amount': '${:,.2f}',
                    'Avg Days Pending': '{:.1f}'
                }),
                use_container_width=True
            )
        
        # Integration status analysis
        if 'Integration_Status__c' in filtered_df.columns:
            st.subheader("Integration Status Analysis")
            integration_counts = filtered_df['Integration_Status__c'].value_counts()
            
            col1, col2 = st.columns([1, 2])
            with col1:
                st.dataframe(integration_counts, use_container_width=True)
            with col2:
                fig_integration = px.bar(
                    x=integration_counts.index,
                    y=integration_counts.values,
                    title="Integration Status Distribution",
                    labels={'x': 'Status', 'y': 'Count'},
                    color=integration_counts.values,
                    color_continuous_scale='Reds'
                )
                st.plotly_chart(fig_integration, use_container_width=True)
    
    # Error Analysis Tab
    with tab5:
        st.subheader("🚨 Invoices on Hold - Error Pattern Analysis")
        st.markdown("Drill-down by integration error patterns to identify and resolve holds")
        
        # Filter for invoices on hold
        hold_invoices = filtered_df[filtered_df['Status'] == 'Hold'].copy()
        
        if hold_invoices.empty:
            st.success("🎉 No invoices currently on hold!")
            st.info("All invoices are either approved or in progress.")
        else:
            # Summary metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total on Hold", len(hold_invoices))
            with col2:
                hold_amount = hold_invoices['Total_Amount__c'].sum()
                st.metric("Amount on Hold", f"${hold_amount:,.2f}")
            with col3:
                avg_hold_days = hold_invoices['Days_Pending_Approval__c'].mean()
                st.metric("Avg Days on Hold", f"{avg_hold_days:.1f}")
            
            st.markdown("---")
            
            # Extract error patterns from Integration_Error_Message__c
            if 'Integration_Error_Message__c' in hold_invoices.columns:
                # Clean and extract error patterns
                hold_invoices['Error_Pattern'] = hold_invoices['Integration_Error_Message__c'].fillna('No Error Message')
                
                # Extract first line or main error message
                hold_invoices['Error_Summary'] = hold_invoices['Error_Pattern'].apply(
                    lambda x: str(x).split('\n')[0] if pd.notna(x) else 'No Error Message'
                )
                
                # Group by error pattern
                error_groups = hold_invoices.groupby('Error_Summary').agg({
                    'Invoice_Id': 'count',
                    'Total_Amount__c': 'sum',
                    'Days_Pending_Approval__c': 'mean'
                }).reset_index()
                error_groups.columns = ['Error Pattern', 'Invoice Count', 'Total Amount', 'Avg Days Pending']
                error_groups = error_groups.sort_values('Invoice Count', ascending=False)
                
                # Display error pattern summary
                st.subheader("📊 Error Pattern Summary")
                
                # Bar chart of error patterns
                fig_errors = px.bar(
                    error_groups.head(10),
                    x='Invoice Count',
                    y='Error Pattern',
                    orientation='h',
                    title='Top 10 Most Common Error Patterns',
                    labels={'Invoice Count': 'Number of Invoices', 'Error Pattern': ''},
                    color='Invoice Count',
                    color_continuous_scale='Reds'
                )
                fig_errors.update_layout(height=400, yaxis={'categoryorder': 'total ascending'})
                st.plotly_chart(fig_errors, use_container_width=True)
                
                st.markdown("---")
                
                # Drill-down section
                st.subheader("🔍 Drill-Down by Error Pattern")
                st.markdown("Click to expand each error pattern and see affected invoices")
                
                # Load integration responses
                try:
                    integration_responses = get_integration_responses(conn, schema_name)
                except:
                    integration_responses = pd.DataFrame()
                
                # Create expandable sections for each error pattern
                for idx, row in error_groups.iterrows():
                    error_pattern = row['Error Pattern']
                    invoice_count = row['Invoice Count']
                    total_amt = row['Total Amount']
                    
                    with st.expander(f"🔴 {error_pattern[:100]}... ({invoice_count} invoices, ${total_amt:,.2f})"):
                        # Filter invoices for this error pattern and sort by amount descending
                        pattern_invoices = hold_invoices[hold_invoices['Error_Summary'] == error_pattern].copy()
                        pattern_invoices = pattern_invoices.sort_values('Total_Amount__c', ascending=False)
                        
                        # Calculate Days Since Approval
                        if 'Approval_Date__c' in pattern_invoices.columns:
                            # Use timezone-naive datetime for both to avoid tz-aware/tz-naive mismatch
                            now = pd.Timestamp.now().tz_localize(None)
                            approval_dates = pd.to_datetime(pattern_invoices['Approval_Date__c']).dt.tz_localize(None)
                            pattern_invoices['Days_Since_Approval'] = (now - approval_dates).dt.days
                        else:
                            pattern_invoices['Days_Since_Approval'] = None
                        
                        # Display summary
                        st.markdown(f"**Full Error Message:**")
                        st.text_area(
                            "Error Details",
                            value=error_pattern,
                            height=100,
                            key=f"error_{idx}",
                            label_visibility="collapsed"
                        )
                        
                        st.markdown(f"**Affected Invoices ({len(pattern_invoices)}):**")
                        
                        # Display invoices in a table
                        display_cols = ['Invoice_Name', 'Vendor__Name', 'Total_Amount__c', 
                                       'Days_Pending_Approval__c', 'Invoice_Date__c', 'State__c']
                        available_cols = [col for col in display_cols if col in pattern_invoices.columns]
                        
                        pattern_display = pattern_invoices[available_cols].copy()
                        if 'Invoice_Date__c' in pattern_display.columns:
                            pattern_display['Invoice_Date__c'] = pd.to_datetime(
                                pattern_display['Invoice_Date__c']
                            ).dt.strftime('%Y-%m-%d')
                        
                        # Display invoices as a table
                        st.markdown("---")
                        st.markdown(f"**📋 Invoices (Click a row to view details):**")
                        
                        # Prepare display dataframe
                        display_cols = ['Invoice_Name', 'Vendor__Name', 'PO_Name', 'Total_Amount__c', 
                                       'Days_Since_Approval', 'Invoice_Date__c', 'State__c']
                        available_cols = [col for col in display_cols if col in pattern_invoices.columns]
                        
                        table_display = pattern_invoices[available_cols + ['Invoice_Id']].copy()
                        table_display = table_display.reset_index(drop=True)
                        
                        # Format columns for display
                        if 'Invoice_Date__c' in table_display.columns:
                            table_display['Invoice_Date__c'] = pd.to_datetime(
                                table_display['Invoice_Date__c']
                            ).dt.strftime('%Y-%m-%d')
                        
                        # Rename columns for display
                        column_renames = {
                            'Invoice_Name': 'Invoice',
                            'Vendor__Name': 'Vendor',
                            'PO_Name': 'PO Name',
                            'Total_Amount__c': 'Amount ($)',
                            'Days_Since_Approval': 'Days Since Approval',
                            'Invoice_Date__c': 'Invoice Date',
                            'State__c': 'State'
                        }
                        table_display = table_display.rename(columns=column_renames)
                        
                        # Display the table
                        st.dataframe(
                            table_display.drop('Invoice_Id', axis=1).style.format({
                                'Amount ($)': '${:,.2f}',
                                'Days Since Approval': '{:.0f}'
                            }),
                            use_container_width=True,
                            hide_index=False
                        )
                        
                        # Invoice selector for drill-down
                        st.markdown("---")
                        selected_invoice_name = st.selectbox(
                            "🔎 Select an invoice to view line items and integration response:",
                            options=['-- Select an Invoice --'] + table_display['Invoice'].tolist(),
                            key=f"invoice_selector_{idx}"
                        )
                        
                        if selected_invoice_name and selected_invoice_name != '-- Select an Invoice --':
                            # Get the selected invoice data
                            selected_idx = table_display[table_display['Invoice'] == selected_invoice_name].index[0]
                            invoice_id = table_display.loc[selected_idx, 'Invoice_Id']
                            invoice_row = pattern_invoices[pattern_invoices['Invoice_Id'] == invoice_id].iloc[0]
                            
                            # Show invoice summary
                            st.info(f"📄 **{selected_invoice_name}** | Amount: ${invoice_row.get('Total_Amount__c', 0):,.2f}")
                            
                            # Check if this is a PO amount error
                            # Specific pattern: "The invoice amount is greater than the amount available on the PO"
                            error_pattern_lower = error_pattern.lower()
                            is_po_amount_error = (
                                "invoice amount is greater than" in error_pattern_lower and 
                                "available on the po" in error_pattern_lower
                            )
                            
                            # Debug info - ALWAYS show for troubleshooting
                            st.caption(f"🔍 Error Pattern Check: '{error_pattern[:100]}'...")
                            st.caption(f"✅ PO Amount Error Detected: {is_po_amount_error}")
                            
                            if is_po_amount_error:
                                st.success(f"📨 'Send to Linus' tab is enabled for this invoice!")
                            
                            # Create columns for drill-downs
                            if is_po_amount_error:
                                col1, col2, col3 = st.columns(3)
                            else:
                                col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown("### 📋 Invoice Line Items")
                                if not invoice_lines_df.empty:
                                    invoice_lines = invoice_lines_df[
                                        invoice_lines_df['Invoice_Id'] == invoice_id
                                    ]
                                    
                                    if not invoice_lines.empty:
                                        line_display_cols = ['Invoice_Line_Number__c', 'Invoice_Amount__c', 
                                                             'Invoice_Status__c', 'Cost_Category_Name__c',
                                                             'sitetracker__Quantity__c', 'sitetracker__Unit_Price__c']
                                        available_line_cols = [col for col in line_display_cols if col in invoice_lines.columns]
                                        
                                        # Format and display
                                        line_display = invoice_lines[available_line_cols].copy()
                                        st.dataframe(
                                            line_display,
                                            use_container_width=True,
                                            hide_index=True
                                        )
                                        
                                        # Summary
                                        total_lines = len(invoice_lines)
                                        total_line_amount = invoice_lines['Invoice_Amount__c'].sum() if 'Invoice_Amount__c' in invoice_lines.columns else 0
                                        st.caption(f"📊 {total_lines} line items | Total: ${total_line_amount:,.2f}")
                                    else:
                                        st.info("No line items found")
                                else:
                                    st.warning("Invoice lines data not loaded")
                            
                            with col2:
                                st.markdown("### 🔗 Integration Response")
                                if not integration_responses.empty:
                                    invoice_response = integration_responses[
                                        integration_responses['Invoice_Id'] == invoice_id
                                    ]
                                    
                                    if not invoice_response.empty:
                                        # Get all response fields
                                        operation = invoice_response['Operation__c'].iloc[0] if 'Operation__c' in invoice_response.columns else 'N/A'
                                        error_msg = invoice_response['Error_Message__c'].iloc[0] if 'Error_Message__c' in invoice_response.columns else 'N/A'
                                        infinium_request = invoice_response['Infinium_Request__c'].iloc[0] if 'Infinium_Request__c' in invoice_response.columns else 'N/A'
                                        infinium_response = invoice_response['Infinium_Response__c'].iloc[0] if 'Infinium_Response__c' in invoice_response.columns else 'N/A'
                                        
                                        # Display operation and error
                                        st.markdown(f"**Operation:** `{operation}`")
                                        st.markdown(f"**Error:** {error_msg[:100]}...")
                                        
                                        # Expandable request/response
                                        with st.expander("📤 Infinium Request"):
                                            try:
                                                import json
                                                request_json = json.loads(str(infinium_request))
                                                st.json(request_json)
                                            except:
                                                st.text_area(
                                                    "Raw Request",
                                                    value=str(infinium_request),
                                                    height=150,
                                                    key=f"request_{idx}",
                                                    label_visibility="collapsed"
                                                )
                                        
                                        with st.expander("📥 Infinium Response"):
                                            try:
                                                import json
                                                response_json = json.loads(str(infinium_response))
                                                st.json(response_json)
                                            except:
                                                st.text_area(
                                                    "Raw Response",
                                                    value=str(infinium_response),
                                                    height=150,
                                                    key=f"response_{idx}",
                                                    label_visibility="collapsed"
                                                )
                                    else:
                                        st.warning("⚠️ No integration response found")
                                else:
                                    st.warning("Integration responses data not loaded")
                            
                            # Add "Send to Linus" tab for PO amount errors
                            if is_po_amount_error:
                                with col3:
                                    st.markdown("### 📨 Send to Linus")
                                    
                                    # Debug information
                                    st.caption(f"📦 Purchase Orders loaded: {len(purchase_orders_df)} records")
                                    
                                    # Get PO_Name from the invoice
                                    po_name = invoice_row.get('PO_Name', None)
                                    
                                    if po_name:
                                        st.caption(f"📋 Invoice PO_Name: {po_name}")
                                    else:
                                        st.warning("⚠️ Invoice does not have a PO_Name value")
                                    
                                    if po_name and not purchase_orders_df.empty:
                                        # Get PO details
                                        po_info = purchase_orders_df[purchase_orders_df['PO_Name'] == po_name]
                                        
                                        if not po_info.empty:
                                            total_approved_po = po_info['PO_Amount'].iloc[0] if 'PO_Amount' in po_info.columns else 0
                                            
                                            # Calculate Months into Year (remaining months with 1 decimal)
                                            import datetime as dt
                                            today = dt.datetime.now()
                                            end_of_year = dt.datetime(today.year, 12, 31)
                                            months_remaining = (end_of_year - today).days / 30.0
                                            months_into_year = round(months_remaining, 1)
                                            
                                            # Get all invoices for this PO_Name
                                            po_invoices = invoices_df[invoices_df['PO_Name'] == po_name].copy()
                                            
                                            # Invoiced Year to Date - Sum of Total_Invoice_Amount__c for all invoices (irrespective of status)
                                            # Note: Using Total_Amount__c as Total_Invoice_Amount__c may not exist
                                            invoiced_ytd = po_invoices['Total_Amount__c'].sum() if not po_invoices.empty else 0
                                            
                                            # Remaining Balance - Total Approved PO - Sum for Paid and Committed
                                            paid_committed = po_invoices[
                                                po_invoices['Status'].isin(['Paid', 'Committed'])
                                            ]['Total_Amount__c'].sum() if not po_invoices.empty else 0
                                            remaining_balance = total_approved_po - paid_committed
                                            
                                            # Total Pending - Sum for Draft, Submitted, Approved, Hold
                                            total_pending = po_invoices[
                                                po_invoices['Status'].isin(['Draft', 'Submitted', 'Approved', 'Hold'])
                                            ]['Total_Amount__c'].sum() if not po_invoices.empty else 0
                                            
                                            # Expected Additional - 10% of Total Pending
                                            expected_additional = total_pending * 0.10
                                            
                                            # Supplemental Amount
                                            supplemental_amount = (total_pending + expected_additional) - remaining_balance
                                            
                                            # Display calculated fields
                                            st.markdown("**📊 Calculated Fields:**")
                                            
                                            st.metric("Months into Year", f"{months_into_year}")
                                            st.metric("Total Approved PO", f"${total_approved_po:,.2f}")
                                            st.metric("Invoiced YTD", f"${invoiced_ytd:,.2f}")
                                            st.metric("Remaining Balance", f"${remaining_balance:,.2f}")
                                            st.metric("Total Pending", f"${total_pending:,.2f}")
                                            st.metric("Expected Additional (10%)", f"${expected_additional:,.2f}")
                                            st.metric("**Supplemental Amount**", f"**${supplemental_amount:,.2f}**")
                                            
                                            st.markdown("---")
                                            
                                            # Send to Linus button
                                            if st.button("📨 Send to Linus", key=f"send_linus_{idx}_{invoice_id}", type="primary"):
                                                import uuid
                                                
                                                # Prepare request data
                                                request_data = {
                                                    'Request_Id': f"REQ-{uuid.uuid4().hex[:12].upper()}",
                                                    'Invoice_Id': invoice_id,
                                                    'Invoice_Name': selected_invoice_name,
                                                    'PO_Name': po_name,
                                                    'Vendor_Name': invoice_row.get('Vendor__Name', ''),
                                                    'Invoice_Amount': float(invoice_row.get('Total_Amount__c', 0)),
                                                    'Months_Into_Year': float(months_into_year),
                                                    'Total_Approved_PO': float(total_approved_po),
                                                    'Invoiced_Year_To_Date': float(invoiced_ytd),
                                                    'Remaining_Balance': float(remaining_balance),
                                                    'Total_Pending': float(total_pending),
                                                    'Expected_Additional': float(expected_additional),
                                                    'Supplemental_Amount': float(supplemental_amount)
                                                }
                                                
                                                # Insert into database
                                                if insert_linus_request(conn, request_data, schema_name):
                                                    st.success(f"✅ Request sent to Linus! Request ID: {request_data['Request_Id']}")
                                                    st.balloons()
                                                else:
                                                    st.error("❌ Failed to send request. Please try again.")
                                        
                                        else:
                                            st.warning(f"⚠️ PO {po_name} not found in Purchase Orders")
                                    else:
                                        st.warning("⚠️ PO Name not available or Purchase Orders data not loaded")
                        
                        # Download button for this error pattern
                        csv_pattern = pattern_invoices.to_csv(index=False)
                        st.download_button(
                            label=f"📥 Download Invoices for this Error Pattern",
                            data=csv_pattern,
                            file_name=f"error_pattern_{idx}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv",
                            key=f"download_{idx}"
                        )
                
                # Overall download for all hold invoices
                st.markdown("---")
                csv_all_holds = hold_invoices.to_csv(index=False)
                st.download_button(
                    label="📥 Download All Invoices on Hold",
                    data=csv_all_holds,
                    file_name=f"all_holds_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("Integration_Error_Message__c column not found in data")
                st.dataframe(hold_invoices, use_container_width=True)
    
    # Custom Query Tab
    with tab6:
        st.subheader("Custom SQL Query Tool")
        st.info("Execute custom queries against your Databricks tables")
        
        # Sample queries
        with st.expander("📚 Sample Queries"):
            st.code(f"""
-- Get all invoices on hold
SELECT * FROM {schema_name}.invoices 
WHERE sitetracker__Status__c = 'Hold'
LIMIT 100;

-- Summary by vendor
SELECT 
    Vendor__Name,
    COUNT(*) as invoice_count,
    SUM(Total_Amount__c) as total_amount
FROM {schema_name}.invoices
GROUP BY Vendor__Name
ORDER BY total_amount DESC;

-- Invoices pending longest
SELECT 
    Invoice_Name,
    Vendor__Name,
    Days_Pending_Approval__c,
    Total_Amount__c
FROM {schema_name}.invoices
WHERE sitetracker__Status__c = 'Hold'
ORDER BY Days_Pending_Approval__c DESC
LIMIT 20;
            """, language="sql")
        
        custom_query = st.text_area(
            "Enter your SQL query:",
            value=f"SELECT * FROM {schema_name}.invoices LIMIT 10",
            height=150
        )
        
        if st.button("▶️ Execute Query", type="primary"):
            with st.spinner("Executing query..."):
                result_df = query_databricks(conn, custom_query)
                if not result_df.empty:
                    st.success(f"✅ Query returned {len(result_df)} rows")
                    st.dataframe(result_df, use_container_width=True)
                    
                    # Download results
                    csv = result_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Query Results",
                        data=csv,
                        file_name=f"query_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("Query returned no results")
    
    # Genie AI Tab (Now First!)
    with tab1:
        st.subheader("🧞 Ask Genie About Your Data")
        st.markdown("**Powered by Databricks Genie** - AI that understands your data schema!")
        
        # Note about tab behavior
        if len(st.session_state.chat_history) == 0:
            st.info("💡 **Tip:** After asking a question, you may need to click back to this tab to see the response and continue the conversation.")
        
        # Get Genie Space ID from secrets
        genie_space_id = None
        if hasattr(st, 'secrets') and 'databricks' in st.secrets:
            genie_space_id = st.secrets.databricks.get("genie_space_id")
        
        if not genie_space_id:
            st.error("""
            **Genie Space ID not configured!**
            
            Please add your Genie Space ID to `.streamlit/secrets.toml`:
            ```toml
            [databricks]
            genie_space_id = "your-space-id-here"
            ```
            
            To find your Genie Space ID, run:
            ```
            python find_genie_space_id.py
            ```
            """)
        else:
            # Conversation controls
            col1, col2 = st.columns([4, 1])
            with col2:
                if st.button("🔄 New Conversation"):
                    genie_chat.reset_genie_conversation()
                    st.session_state.chat_history = []
                    
                    # Show feedback status
                    feedback_count = len(genie_chat.load_feedback_memory())
                    if feedback_count > 0:
                        st.success(f"Started new conversation! ({feedback_count} corrections applied)")
                    else:
                        st.success("Started new conversation!")
            
            # Initialize input counter for clearing after submit
            if "input_counter" not in st.session_state:
                st.session_state.input_counter = 0
            
            # Display chat history FIRST (so input is always at bottom)
            for idx, message in enumerate(st.session_state.chat_history):
                if message["role"] == "user":
                    st.markdown(f"**You:** {message['content']}")
                else:
                    st.markdown(f"**Genie:** {message['content']}")
                    
                    # Show query results if available
                    # First check if we have executed results (from manual SQL execution)
                    if "executed_result" in message and message["executed_result"] is not None:
                        st.markdown("**📊 Query Results:**")
                        st.dataframe(message["executed_result"], use_container_width=True)
                    # Otherwise check for Genie's built-in results
                    elif "genie_result" in message and message["genie_result"]:
                        st.markdown("**📊 Query Results:**")
                        try:
                            result = message["genie_result"]
                            
                            # Genie result structure: has 'data_array' with rows and columns
                            if hasattr(result, 'data_array') and result.data_array:
                                # Get column names
                                columns = []
                                if hasattr(result.data_array, 'columns') and result.data_array.columns:
                                    columns = [col.name for col in result.data_array.columns]
                                
                                # Get row data
                                rows = []
                                if hasattr(result.data_array, 'rows') and result.data_array.rows:
                                    for row in result.data_array.rows:
                                        if hasattr(row, 'values'):
                                            rows.append(row.values)
                                
                                # Create DataFrame
                                if rows and columns:
                                    df = pd.DataFrame(rows, columns=columns)
                                    st.dataframe(df, use_container_width=True)
                                elif rows:
                                    # If no column names, just show data
                                    st.dataframe(pd.DataFrame(rows), use_container_width=True)
                                else:
                                    st.info("Query executed successfully but returned no rows")
                            else:
                                st.info("Query executed successfully but returned no data")
                        except Exception as e:
                            st.warning(f"Could not display results: {str(e)}")
                            st.info("Results are available but could not be formatted for display")
                    
                    # Show SQL if available
                    if "sql" in message and message["sql"]:
                        with st.expander("📝 View SQL"):
                            st.code(message["sql"], language="sql")
                    
                    # Feedback buttons
                    col1, col2 = st.columns([1, 10])
                    with col1:
                        if st.button("👍", key=f"thumbs_up_{idx}"):
                            st.success("Thanks for the feedback!")
                    with col2:
                        if st.button("👎", key=f"thumbs_down_{idx}"):
                            st.session_state[f"feedback_mode_{idx}"] = True
                    
                    # Feedback form
                    if st.session_state.get(f"feedback_mode_{idx}"):
                        feedback_text = st.text_area(
                            "What should Genie do better?",
                            key=f"feedback_text_{idx}"
                        )
                        if st.button("Submit Feedback", key=f"submit_feedback_{idx}"):
                            if feedback_text:
                                # Save feedback
                                memory, success = genie_chat.add_feedback_to_memory(
                                    feedback_text=feedback_text,
                                    question=st.session_state.chat_history[idx-1]["content"],
                                    genie_response=message["content"]
                                )
                                
                                if success:
                                    st.session_state.feedback_memory = genie_chat.load_feedback_memory()
                                    st.success(f"✅ Feedback saved! ({len(memory)} corrections total)")
                                    st.session_state[f"feedback_mode_{idx}"] = False
            
            # Add separator before input
            if st.session_state.chat_history:
                st.markdown("---")
            
            # Chat input at the BOTTOM (after chat history)
            with st.form(key=f"genie_form_{st.session_state.input_counter}", clear_on_submit=True):
                user_input = st.text_input(
                    "Ask a question about your data:",
                    placeholder="Example: What are the top 5 vendors by invoice count?",
                    key=f"genie_input_{st.session_state.input_counter}"
                )
                send_button = st.form_submit_button("Send", help="Press Enter to submit the question")
            
            if send_button and user_input:
                # Add user message to history
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": user_input
                })
                
                # Get Genie's response
                progress_container = st.empty()
                with progress_container:
                    with st.spinner("🧞 Genie is analyzing..."):
                        genie_response, error = genie_chat.ask_genie(user_input, genie_space_id)
                
                progress_container.empty()
                
                if error:
                    st.error(f"Genie: {error}")
                    # Still increment counter even on error
                    st.session_state.input_counter += 1
                    st.rerun()
                else:
                    # If Genie generated SQL but no results, execute it ourselves
                    executed_result = None
                    if genie_response.get("sql") and not genie_response.get("genie_result"):
                        try:
                            connection = get_databricks_connection()
                            cursor = connection.cursor()
                            cursor.execute(genie_response["sql"])
                            
                            # Fetch results
                            columns = [desc[0] for desc in cursor.description]
                            rows = cursor.fetchall()
                            
                            # Store as DataFrame for easy display
                            if rows:
                                executed_result = pd.DataFrame(rows, columns=columns)
                            
                            cursor.close()
                        except Exception as exec_error:
                            st.warning(f"Could not execute SQL: {str(exec_error)}")
                    
                    # Add assistant message
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": genie_response["text"],
                        "sql": genie_response.get("sql"),
                        "genie_result": genie_response.get("genie_result"),
                        "executed_result": executed_result
                    })
                
                # Increment counter to clear form for next input
                st.session_state.input_counter += 1
                
                # Force rerun to display new messages
                # Note: This will reset to first tab (Streamlit limitation)
                # User will need to click back to Genie AI tab to continue
                st.rerun()

if __name__ == "__main__":
    main()

