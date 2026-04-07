"""
Excel export module for JobPilot applications tracker.
"""

import pandas as pd
from pathlib import Path
from tracker.tracker import load_applications
from datetime import datetime


def export_to_excel(output_path: str = None) -> str:
    """
    Export all applications to an Excel file with formatting.
    
    Args:
        output_path: Path to save Excel file (default: data/applications_export_YYYYMMDD.xlsx)
    
    Returns:
        Path to the exported file
    """
    # Load applications
    applications = load_applications()
    
    if not applications:
        raise ValueError("No applications to export")
    
    # Convert to list of dicts
    data = [app.model_dump() for app in applications]
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Reorder columns for better readability
    column_order = [
        'title', 'company', 'status', 'date_applied', 'date_updated',
        'location', 'source', 'salary', 'url', 'job_id',
        'resume_used', 'notes', 'contact_name', 'contact_email',
        'interview_date', 'offer_amount', 'cover_letter'
    ]
    
    # Only include columns that exist
    existing_cols = [col for col in column_order if col in df.columns]
    df = df[existing_cols]
    
    # Format column names
    df.columns = [col.replace('_', ' ').title() for col in df.columns]
    
    # Generate filename if not provided
    if not output_path:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = f"data/applications_export_{timestamp}.xlsx"
    
    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Create Excel writer with xlsxwriter engine for formatting
    with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Applications', index=False)
        
        # Get workbook and worksheet objects
        workbook = writer.book
        worksheet = writer.sheets['Applications']
        
        # Define formats
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4472C4',
            'font_color': 'white',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })
        
        status_formats = {
            'Applied': workbook.add_format({'bg_color': '#D9E1F2', 'border': 1}),
            'Interview': workbook.add_format({'bg_color': '#FFF2CC', 'border': 1}),
            'Offer': workbook.add_format({'bg_color': '#C6EFCE', 'border': 1}),
            'Rejected': workbook.add_format({'bg_color': '#FFC7CE', 'border': 1}),
            'Withdrawn': workbook.add_format({'bg_color': '#D9D9D9', 'border': 1})
        }
        
        cell_format = workbook.add_format({'border': 1, 'valign': 'top'})
        date_format = workbook.add_format({'border': 1, 'num_format': 'yyyy-mm-dd'})
        url_format = workbook.add_format({'border': 1, 'font_color': 'blue', 'underline': 1})
        
        # Write headers with formatting
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
        
        # Set column widths
        column_widths = {
            'Title': 30,
            'Company': 25,
            'Status': 12,
            'Date Applied': 12,
            'Date Updated': 12,
            'Location': 20,
            'Source': 10,
            'Salary': 15,
            'Url': 40,
            'Job Id': 15,
            'Resume Used': 20,
            'Notes': 40,
            'Contact Name': 20,
            'Contact Email': 25,
            'Interview Date': 12,
            'Offer Amount': 15,
            'Cover Letter': 30
        }
        
        for col_num, col_name in enumerate(df.columns.values):
            width = column_widths.get(col_name, 15)
            worksheet.set_column(col_num, col_num, width)
        
        # Apply conditional formatting to Status column
        status_col_idx = list(df.columns).index('Status') if 'Status' in df.columns else None
        
        if status_col_idx is not None:
            for row_num in range(1, len(df) + 1):
                status_value = df.iloc[row_num - 1]['Status']
                format_to_use = status_formats.get(status_value, cell_format)
                worksheet.write(row_num, status_col_idx, status_value, format_to_use)
        
        # Apply URL formatting
        url_col_idx = list(df.columns).index('Url') if 'Url' in df.columns else None
        if url_col_idx is not None:
            for row_num in range(1, len(df) + 1):
                url_value = df.iloc[row_num - 1]['Url']
                worksheet.write_url(row_num, url_col_idx, url_value, url_format, string=url_value)
        
        # Freeze the header row
        worksheet.freeze_panes(1, 0)
        
        # Add auto-filter
        worksheet.autofilter(0, 0, len(df), len(df.columns) - 1)
    
    print(f"[excel] ✓ Exported {len(df)} applications to {output_path}")
    return output_path


def export_summary_to_excel(output_path: str = None) -> str:
    """
    Export application statistics and summary to Excel.
    
    Args:
        output_path: Path to save Excel file
    
    Returns:
        Path to the exported file
    """
    from tracker.tracker import summary, get_by_status
    from tracker.models import JobStatus
    
    applications = load_applications()
    
    if not applications:
        raise ValueError("No applications to export")
    
    # Generate filename if not provided
    if not output_path:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = f"data/applications_summary_{timestamp}.xlsx"
    
    # Create Excel writer
    with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
        workbook = writer.book
        
        # Sheet 1: All Applications
        all_data = [app.model_dump() for app in applications]
        df_all = pd.DataFrame(all_data)
        df_all.to_excel(writer, sheet_name='All Applications', index=False)
        
        # Sheet 2: Summary Statistics
        stats = summary()
        df_summary = pd.DataFrame(list(stats.items()), columns=['Status', 'Count'])
        df_summary.to_excel(writer, sheet_name='Summary', index=False)
        
        # Format summary sheet
        summary_sheet = writer.sheets['Summary']
        chart = workbook.add_chart({'type': 'pie'})
        
        # Configure the chart
        chart.add_series({
            'name': 'Application Status Distribution',
            'categories': ['Summary', 1, 0, len(stats) - 1, 0],  # Exclude 'total' row
            'values': ['Summary', 1, 1, len(stats) - 1, 1],
        })
        
        chart.set_title({'name': 'Application Status Distribution'})
        chart.set_style(10)
        
        summary_sheet.insert_chart('D2', chart)
        
        # Sheet 3-7: Applications by status
        for status in JobStatus:
            status_apps = get_by_status(status)
            if status_apps:
                status_data = [app.model_dump() for app in status_apps]
                df_status = pd.DataFrame(status_data)
                sheet_name = status.value.title()
                df_status.to_excel(writer, sheet_name=sheet_name, index=False)
    
    print(f"[excel] ✓ Exported summary report to {output_path}")
    return output_path


# CLI integration
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "summary":
        export_summary_to_excel()
    else:
        export_to_excel()