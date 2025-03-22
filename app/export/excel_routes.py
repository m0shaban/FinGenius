"""
Excel-only export functionality that doesn't depend on WeasyPrint
This module provides export functionality that works without WeasyPrint
"""
from flask import send_file, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from app.export import excel_only_bp
from app.core.models import FinancialFile, Analysis
import pandas as pd
import os
from datetime import datetime
import io
import logging

# Setup logging
logger = logging.getLogger(__name__)

@excel_only_bp.route('/pdf/analysis/<int:file_id>')
@login_required
def export_analysis_pdf(file_id):
    """Redirect to Excel export with a message when PDF export is not available"""
    flash('PDF export is not available. Please install WeasyPrint dependencies to enable this feature. Using Excel export instead.')
    return redirect(url_for('export.export_analysis_excel', file_id=file_id))

@excel_only_bp.route('/excel/analysis/<int:file_id>')
@login_required
def export_analysis_excel(file_id):
    try:
        file = FinancialFile.query.get_or_404(file_id)
        if file.user_id != current_user.id:
            flash('Access denied')
            return redirect(url_for('core.dashboard'))
        
        # Get file data
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file.filename)
        df = pd.read_csv(file_path) if file.file_type == 'csv' else pd.read_excel(file_path)
        
        # Get latest analysis
        analysis = Analysis.query.filter_by(file_id=file_id).order_by(Analysis.created_date.desc()).first()
        
        if not analysis:
            flash('No analysis found for this file')
            return redirect(url_for('core.view_file', file_id=file_id))
        
        # Basic Excel export without requiring WeasyPrint
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Data', index=False)
            
            # Add financial ratios if available
            if 'financial_ratios' in analysis.results:
                ratios = pd.DataFrame(list(analysis.results['financial_ratios'].items()), 
                                    columns=['Ratio', 'Value'])
                ratios.to_excel(writer, sheet_name='Ratios', index=False)
            
            # Apply simple formatting
            workbook = writer.book
            for worksheet in writer.sheets.values():
                worksheet.set_column('A:Z', 15)
                
        output.seek(0)
        
        return send_file(
            output,
            download_name=f'analysis_{file.filename}_{datetime.now():%Y%m%d}.xlsx',
            as_attachment=True,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        logger.error(f"Error generating Excel: {str(e)}")
        flash(f'Error generating Excel: {str(e)}')
        return redirect(url_for('core.view_file', file_id=file_id))

@excel_only_bp.route('/excel/comparison/<path:file_ids>')
@login_required
def export_comparison_excel(file_ids):
    try:
        file_id_list = [int(id) for id in file_ids.split(',')]
        files = []
        
        for file_id in file_id_list:
            file = FinancialFile.query.get_or_404(file_id)
            if file.user_id != current_user.id:
                flash('Access denied')
                return redirect(url_for('core.dashboard'))
            files.append(file)
            
        # Basic comparison data export
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            for i, file in enumerate(files):
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file.filename)
                df = pd.read_csv(file_path) if file.file_type == 'csv' else pd.read_excel(file_path)
                df.to_excel(writer, sheet_name=f'File {i+1}', index=False)
                
            # Summary sheet
            summary = pd.DataFrame({
                'Filename': [f.filename for f in files],
                'Row Count': [pd.read_csv(os.path.join(current_app.config['UPLOAD_FOLDER'], f.filename)).shape[0] 
                            if f.file_type == 'csv' else 
                            pd.read_excel(os.path.join(current_app.config['UPLOAD_FOLDER'], f.filename)).shape[0] 
                            for f in files]
            })
            summary.to_excel(writer, sheet_name='Summary', index=False)
            
        output.seek(0)
        
        return send_file(
            output,
            download_name=f'comparison_{datetime.now():%Y%m%d}.xlsx',
            as_attachment=True,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        logger.error(f"Error generating comparison Excel: {str(e)}")
        flash(f'Error generating comparison Excel: {str(e)}')
        return redirect(url_for('core.dashboard'))
