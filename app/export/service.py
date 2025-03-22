import pandas as pd
from weasyprint import HTML, CSS
from flask import render_template
import io
import os
from datetime import datetime

class ExportService:
    @staticmethod
    def generate_pdf_report(template_name, **kwargs):
        """Generate PDF report from template"""
        # Render template to HTML
        html_content = render_template(template_name, **kwargs)
        
        # Create PDF from HTML
        pdf_file = io.BytesIO()
        HTML(string=html_content).write_pdf(
            pdf_file,
            stylesheets=[CSS(string='@page { size: A4; margin: 1cm }')]
        )
        pdf_file.seek(0)
        return pdf_file

    @staticmethod
    def generate_excel_report(data, filename):
        """Generate Excel report with multiple sheets"""
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            # Write main data
            if 'data' in data:
                pd.DataFrame(data['data']).to_excel(writer, sheet_name='Data', index=False)
            
            # Write financial ratios
            if 'ratios' in data:
                ratios_df = pd.DataFrame(list(data['ratios'].items()), columns=['Ratio', 'Value'])
                ratios_df.to_excel(writer, sheet_name='Financial Ratios', index=False)
            
            # Write trends
            if 'trends' in data:
                trends_df = pd.DataFrame(data['trends']).transpose()
                trends_df.to_excel(writer, sheet_name='Trends', index=True)
            
            # Write forecasts
            if 'forecasts' in data:
                pd.DataFrame(data['forecasts']).to_excel(writer, sheet_name='Forecasts', index=False)
            
            # Get workbook and add formats
            workbook = writer.book
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'bg_color': '#D9E1F2',
                'border': 1
            })
            
            # Apply formats to all sheets
            for worksheet in writer.sheets.values():
                worksheet.set_column('A:Z', 15)  # Set column width
                worksheet.set_row(0, 20, header_format)  # Apply header format
        
        output.seek(0)
        return output

    @staticmethod
    def generate_comparison_excel(comparison_data, files):
        """Generate Excel report for file comparisons"""
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            # Write summary statistics
            if 'summary_stats' in comparison_data:
                for column, stats in comparison_data['summary_stats'].items():
                    df = pd.DataFrame(stats)
                    df.index = [f.filename for f in files]
                    df.to_excel(writer, sheet_name=f'{column[:30]} Stats')
            
            # Write differences
            if 'differences' in comparison_data:
                diff_df = pd.DataFrame(comparison_data['differences'])
                diff_df.index = [f"{files[i+1].filename} vs {files[0].filename}" 
                               for i in range(len(files)-1)]
                diff_df.to_excel(writer, sheet_name='Differences')
            
            # Format workbook
            workbook = writer.book
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#D9E1F2',
                'border': 1
            })
            
            # Apply formats
            for worksheet in writer.sheets.values():
                worksheet.set_column('A:Z', 15)
                worksheet.set_row(0, 20, header_format)
        
        output.seek(0)
        return output

def generate_pdf(html_content):
    """Generate a PDF from HTML content"""
    try:
        # Try to use WeasyPrint for PDF generation
        import weasyprint
        pdf = weasyprint.HTML(string=html_content).write_pdf()
        return pdf
    except ImportError:
        try:
            # Fallback to pdfkit if WeasyPrint is not available
            import pdfkit
            options = {
                'page-size': 'A4',
                'margin-top': '0.75in',
                'margin-right': '0.75in',
                'margin-bottom': '0.75in',
                'margin-left': '0.75in',
                'encoding': 'UTF-8',
                'quiet': ''
            }
            pdf = pdfkit.from_string(html_content, False, options=options)
            return pdf
        except ImportError:
            # If neither library is available, raise error
            current_app.logger.error("PDF generation failed - neither WeasyPrint nor pdfkit is installed")
            raise ImportError("PDF generation libraries not installed")
