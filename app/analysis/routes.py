import os
import pandas as pd
import json
from flask import render_template, request, jsonify, current_app, flash, redirect, url_for, session
from flask_login import login_required, current_user
from app.analysis import bp
from app.analysis.service import FinancialAnalyzer
from app.core.models import FinancialFile, Analysis, db

@bp.route('/analyze/<int:file_id>', methods=['GET', 'POST'])
@login_required
def analyze_file(file_id):
    file = FinancialFile.query.get_or_404(file_id)
    
    # Security check - make sure user owns the file
    if file.user_id != current_user.id:
        flash('You do not have permission to analyze this file')
        return redirect(url_for('core.dashboard'))
    
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file.filename)
    
    # Read the file data with pandas
    try:
        if file.file_type == 'csv':
            df = pd.read_csv(file_path)
        else:  # Excel files
            df = pd.read_excel(file_path)
        
        # Basic file stats
        rows, cols = df.shape
        column_names = df.columns.tolist()
        
        # Get a sample of the data (first 5 rows)
        sample_data = df.head(5).to_html(classes='table table-striped')
        
        # Create financial analyzer instance
        analyzer = FinancialAnalyzer(df)
        
        # Generate analysis results
        financial_ratios = analyzer.calculate_financial_ratios()
        correlation_matrix = analyzer.generate_correlation_matrix()
        trends = analyzer.find_trends()
        
        # Generate charts for numeric columns
        charts = {}
        numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
        for column in numeric_columns[:5]:  # Limit to first 5 numeric columns to avoid too many charts
            charts[column] = analyzer.generate_time_series_chart(column)
        
        # Save analysis results to database
        analysis_results = {
            'financial_ratios': financial_ratios,
            'trends': trends
        }
        
        new_analysis = Analysis(
            file_id=file.id,
            analysis_type='financial_metrics',
            results=analysis_results
        )
        db.session.add(new_analysis)
        db.session.commit()
        
        return render_template('analysis/analysis_results.html', 
                              file=file,
                              ratios=financial_ratios,
                              correlation_matrix=correlation_matrix,
                              trends=trends,
                              charts=charts,
                              numeric_columns=numeric_columns)
                              
    except Exception as e:
        flash(f'Error analyzing file: {str(e)}')
        return redirect(url_for('core.dashboard'))

@bp.route('/forecast/<int:file_id>', methods=['GET', 'POST'])
@login_required
def forecast(file_id):
    file = FinancialFile.query.get_or_404(file_id)
    
    # Security check - make sure user owns the file
    if file.user_id != current_user.id:
        flash('You do not have permission to forecast this file')
        return redirect(url_for('core.dashboard'))
    
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file.filename)
    
    if request.method == 'POST':
        try:
            column = request.form.get('column')
            periods = int(request.form.get('periods', 3))
            
            # Read the file data
            if file.file_type == 'csv':
                df = pd.read_csv(file_path)
            else:  # Excel files
                df = pd.read_excel(file_path)
            
            analyzer = FinancialAnalyzer(df)
            forecast_result = analyzer.forecasting_simple(column, periods)
            
            if forecast_result is not None:
                forecast_data = forecast_result.to_dict(orient='records')
                
                # Save forecast to database
                analysis_results = {
                    'forecast_column': column,
                    'periods': periods,
                    'forecast_data': forecast_data
                }
                
                new_analysis = Analysis(
                    file_id=file.id,
                    analysis_type='forecast',
                    results=analysis_results
                )
                db.session.add(new_analysis)
                db.session.commit()
                
                return render_template('analysis/forecast_results.html',
                                      file=file,
                                      column=column,
                                      forecast_data=forecast_data)
            else:
                flash(f'Unable to forecast column: {column}')
                return redirect(url_for('analysis.analyze_file', file_id=file.id))
                
        except Exception as e:
            flash(f'Error forecasting: {str(e)}')
            return redirect(url_for('analysis.analyze_file', file_id=file.id))
    
    # GET request - show forecast form
    try:
        # Read the file data
        if file.file_type == 'csv':
            df = pd.read_csv(file_path)
        else:  # Excel files
            df = pd.read_excel(file_path)
        
        numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
        
        return render_template('analysis/forecast_form.html',
                              file=file,
                              numeric_columns=numeric_columns)
                              
    except Exception as e:
        flash(f'Error reading file: {str(e)}')
        return redirect(url_for('core.dashboard'))
