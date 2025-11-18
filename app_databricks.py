import streamlit as st
import pandas as pd
from databricks import sql
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

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

# Databricks connection (automatically authenticated in Databricks environment)
@st.cache_resource
def get_databricks_connection():
    """
    Create a connection to Databricks SQL Warehouse
    In Databricks Apps, authentication is handled automatically
    """
    try:
        # In Databricks environment, use environment variables
        return sql.connect(
            server_hostname=os.environ.get("DATABRICKS_SERVER_HOSTNAME", "dbc-4a93b454-f17b.cloud.databricks.com"),
            http_path=os.environ.get("DATABRICKS_HTTP_PATH", "/sql/1.0/warehouses/b1bcf72a9e8b65b8"),
            access_token=os.environ.get("DATABRICKS_TOKEN")
        )
    except Exception as e:
        st.error(f"Failed to connect to Databricks: {str(e)}")
        st.info("Ensure your Databricks App is configured with the correct SQL Warehouse.")
        return None

# Query functions with caching
@st.cache_data(ttl=600)  # Cache for 10 minutes
def query_databricks(_conn, query):
    """Execute a query and return results as pandas DataFrame"""
    try:
        cursor = _conn.cursor()
        cursor.execute(query)
        result = cursor.fetchall_arrow().to_pandas()
        cursor.close()
        return result
    except Exception as e:
        st.error(f"Query error: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=600)
def get_invoices(_conn, schema_name):
    """Fetch invoices from Databricks table"""
    query = f"""
    SELECT 
        Invoice_Id,
        Invoice_Name,
        Vendor__Name,
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
def get_invoice_lines(_conn, schema_name):
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
def get_projects(_conn, schema_name):
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
def get_integration_responses(_conn, schema_name):
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

# Main app
def main():
    st.title("🔍 Hold Busters - Invoice Analysis Dashboard")
    st.markdown("### Databricks-Powered Invoice Hold Analysis")
    st.markdown("---")
    
    # Sidebar configuration
    st.sidebar.header("⚙️ Configuration")
    
    # Schema selector - default for Databricks deployment
    schema_name = st.sidebar.text_input(
        "Databricks Schema Name",
        value="hackathon.hackathon_build_hold_busters",
        help="Enter the name of your Databricks schema/database"
    )
    
    # Get connection
    conn = get_databricks_connection()
    
    if conn is None:
        st.warning("⚠️ Not connected to Databricks.")
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
                st.info("Verify the schema name and ensure tables exist")
                return
            
            # Try to load related tables
            try:
                invoice_lines_df = get_invoice_lines(conn, schema_name)
                projects_df = get_projects(conn, schema_name)
            except:
                invoice_lines_df = pd.DataFrame()
                projects_df = pd.DataFrame()
                
        except Exception as e:
            st.error(f"❌ Error loading data: {str(e)}")
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
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Overview", 
        "📋 Invoice Details", 
        "🔍 Deep Analysis",
        "🚨 Error Analysis",
        "💾 Custom Query"
    ])
    
    with tab1:
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
    
    with tab2:
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
        
        # Display dataframe
        display_df = search_df.copy()
        if 'Invoice_Date__c' in display_df.columns:
            display_df['Invoice_Date__c'] = display_df['Invoice_Date__c'].dt.strftime('%Y-%m-%d')
        
        st.dataframe(display_df, use_container_width=True, height=400)
        
        # Download button
        csv = search_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=csv,
            file_name=f"invoices_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    with tab3:
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
    
    with tab4:
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
                        # Filter invoices for this error pattern
                        pattern_invoices = hold_invoices[hold_invoices['Error_Summary'] == error_pattern]
                        
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
                        
                        # Create clickable invoice rows with drill-down
                        st.markdown("---")
                        st.markdown(f"**📋 Click on any invoice to see details:**")
                        
                        # Display each invoice as an expandable row
                        for inv_idx, invoice_row in pattern_invoices.iterrows():
                            invoice_id = invoice_row['Invoice_Id']
                            invoice_name = invoice_row.get('Invoice_Name', invoice_id)
                            vendor = invoice_row.get('Vendor__Name', 'N/A')
                            amount = invoice_row.get('Total_Amount__c', 0)
                            days_pending = invoice_row.get('Days_Pending_Approval__c', 0)
                            
                            # Create expandable section for each invoice
                            with st.expander(f"📄 {invoice_name} | {vendor} | ${amount:,.2f} | {days_pending:.0f} days pending"):
                                # Show basic invoice info
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.markdown(f"**Invoice ID:** `{invoice_id}`")
                                    if 'Invoice_Date__c' in invoice_row:
                                        inv_date = pd.to_datetime(invoice_row['Invoice_Date__c']).strftime('%Y-%m-%d')
                                        st.markdown(f"**Invoice Date:** {inv_date}")
                                with col2:
                                    st.markdown(f"**Vendor:** {vendor}")
                                    if 'State__c' in invoice_row:
                                        st.markdown(f"**State:** {invoice_row['State__c']}")
                                with col3:
                                    st.markdown(f"**Amount:** ${amount:,.2f}")
                                    st.markdown(f"**Days Pending:** {days_pending:.0f}")
                                
                                st.markdown("---")
                                
                                # Drill-down 1: Invoice Line Details
                                with st.expander("📋 **Invoice Line Items**", expanded=True):
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
                                            st.caption(f"📊 Total: {total_lines} line items | ${total_line_amount:,.2f}")
                                        else:
                                            st.info("No line items found for this invoice")
                                    else:
                                        st.warning("Invoice lines data not loaded")
                                
                                # Drill-down 2: Integration Response Details
                                with st.expander("🔗 **Integration Response Details**", expanded=True):
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
                                            col1, col2 = st.columns(2)
                                            with col1:
                                                st.markdown(f"**Operation:** `{operation}`")
                                            with col2:
                                                st.markdown(f"**Error Message:** {error_msg}")
                                            
                                            st.markdown("---")
                                            
                                            # Display Infinium Request
                                            st.markdown("**📤 Infinium Request:**")
                                            try:
                                                import json
                                                request_json = json.loads(str(infinium_request))
                                                st.json(request_json)
                                            except:
                                                st.text_area(
                                                    "Raw Request",
                                                    value=str(infinium_request),
                                                    height=150,
                                                    key=f"request_{idx}_{inv_idx}",
                                                    label_visibility="collapsed"
                                                )
                                            
                                            # Display Infinium Response
                                            st.markdown("**📥 Infinium Response:**")
                                            try:
                                                import json
                                                response_json = json.loads(str(infinium_response))
                                                st.json(response_json)
                                            except:
                                                st.text_area(
                                                    "Raw Response",
                                                    value=str(infinium_response),
                                                    height=150,
                                                    key=f"response_{idx}_{inv_idx}",
                                                    label_visibility="collapsed"
                                                )
                                        else:
                                            st.warning("⚠️ No integration response found for this invoice")
                                            st.info("This invoice may not have been processed through the integration system yet.")
                                    else:
                                        st.warning("Integration responses data not loaded")
                                
                                # Download button for this specific invoice
                                invoice_csv = invoice_row.to_frame().T.to_csv(index=False)
                                st.download_button(
                                    label="📥 Download Invoice Data",
                                    data=invoice_csv,
                                    file_name=f"invoice_{invoice_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                    mime="text/csv",
                                    key=f"download_inv_{idx}_{inv_idx}"
                                )
                        
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
    
    with tab5:
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

if __name__ == "__main__":
    main()

