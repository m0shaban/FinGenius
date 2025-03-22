from flask import render_template, request, jsonify, current_app, flash, redirect, url_for
from flask_login import login_required, current_user
from app.comparison import bp
from app.comparison.service import ComparisonService
from app.core.models import FinancialFile
import pandas as pd
import os

@bp.route('/select')
@login_required
def select_files():
    files = FinancialFile.query.filter_by(user_id=current_user.id).all()
    return render_template('comparison/select.html', files=files)

@bp.route('/compare', methods=['POST'])
@login_required
def compare_files():
    file_ids = request.form.getlist('file_ids')
    
    if len(file_ids) < 2:
        flash('Please select at least two files to compare')
        return redirect(url_for('comparison.select_files'))
        
    try:
        # Load dataframes
        dataframes = []
        files = []
        
        for file_id in file_ids:
            file = FinancialFile.query.get_or_404(file_id)
            
            if file.user_id != current_user.id:
                flash('Access denied to one or more files')
                return redirect(url_for('comparison.select_files'))
                
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file.filename)
            df = pd.read_csv(file_path) if file.file_type == 'csv' else pd.read_excel(file_path)
            
            dataframes.append(df)
            files.append(file)
            
        # Create comparison service
        comparison = ComparisonService(dataframes)
        
        # Generate comparisons
        summary_stats = comparison.compare_summary_statistics()
        differences = comparison.calculate_differences()
        
        # Generate charts for common numeric columns
        charts = {}
        for col in comparison.common_columns:
            if pd.api.types.is_numeric_dtype(dataframes[0][col]):
                charts[col] = comparison.generate_comparison_chart(col)
                
        correlation_diffs = comparison.generate_correlation_comparison()
        
        return render_template('comparison/results.html',
                             files=files,
                             summary_stats=summary_stats,
                             differences=differences,
                             charts=charts,
                             correlation_diffs=correlation_diffs)
                             
    except Exception as e:
        flash(f'Error comparing files: {str(e)}')
        return redirect(url_for('comparison.select_files'))
