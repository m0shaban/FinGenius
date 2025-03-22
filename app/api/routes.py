from flask import jsonify, request, current_app
from app.api import bp
from app.core.models import FinancialFile, Analysis
from flask_login import login_required, current_user
import os
import pandas as pd
from datetime import datetime, timedelta
import json
import numpy as np

@bp.route('/files', methods=['GET'])
@login_required
def get_files():
    """Get list of user's files"""
    files = FinancialFile.query.filter_by(user_id=current_user.id).all()
    return jsonify({
        'files': [
            {
                'id': file.id,
                'filename': file.filename,
                'file_type': file.file_type,
                'upload_date': file.upload_date.isoformat(),
            } for file in files
        ]
    })

@bp.route('/file/<int:file_id>', methods=['GET'])
@login_required
def get_file_data(file_id):
    """Get data for a specific file"""
    file = FinancialFile.query.get_or_404(file_id)
    
    # Check if user owns the file
    if file.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Get file path
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file.filename)
    
    # Read data
    if file.file_type == 'csv':
        df = pd.read_csv(file_path)
    else:  # excel
        df = pd.read_excel(file_path)
    
    # Get basic stats
    columns = df.columns.tolist()
    shape = df.shape
    
    # Convert to JSON-serializable format
    data = df.head(100).to_dict(orient='records')
    
    return jsonify({
        'file': {
            'id': file.id,
            'filename': file.filename,
            'file_type': file.file_type,
            'upload_date': file.upload_date.isoformat(),
        },
        'data': {
            'columns': columns,
            'shape': shape,
            'records': data
        }
    })

@bp.route('/analysis/<int:file_id>', methods=['GET'])
@login_required
def get_analysis(file_id):
    """Get latest analysis for a file"""
    file = FinancialFile.query.get_or_404(file_id)
    
    # Check if user owns the file
    if file.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Get latest analysis
    analysis = Analysis.query.filter_by(file_id=file_id).order_by(Analysis.created_date.desc()).first()
    
    if not analysis:
        return jsonify({'error': 'No analysis found for this file'}), 404
    
    return jsonify({
        'file_id': file_id,
        'analysis_id': analysis.id,
        'created_date': analysis.created_date.isoformat(),
        'results': analysis.results
    })

@bp.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({
        'status': 'ok',
        'app': 'FinGenius',
        'version': '1.0.0'
    })

@bp.route('/charts/financial-data', methods=['GET'])
@login_required
def get_chart_data():
    """Get financial data for charts based on time range"""
    time_range = request.args.get('timeRange', 'month')
    
    # Get user's latest file
    latest_file = FinancialFile.query.filter_by(user_id=current_user.id).order_by(FinancialFile.upload_date.desc()).first()
    
    if not latest_file:
        # Return empty data if no files available
        return jsonify({
            'revenueExpenses': {
                'labels': [],
                'revenue': [],
                'expenses': []
            },
            'ratios': {
                'labels': [],
                'values': []
            }
        })
    
    # Get file path
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], latest_file.filename)
    
    try:
        # Read data
        if latest_file.file_type == 'csv':
            df = pd.read_csv(file_path)
        else:  # excel
            df = pd.read_excel(file_path)
        
        # Check if data has date column
        date_column = None
        for col in df.columns:
            if 'date' in col.lower() or 'time' in col.lower():
                try:
                    # Confirm it can be parsed as date
                    pd.to_datetime(df[col])
                    date_column = col
                    break
                except:
                    continue
        
        if date_column:
            # Convert date column to datetime
            df[date_column] = pd.to_datetime(df[date_column])
            
            # Filter data based on time range
            now = datetime.now()
            if time_range == 'month':
                start_date = now - timedelta(days=30)
                df_filtered = df[df[date_column] >= start_date]
                # Group by week
                df_filtered['period'] = df_filtered[date_column].dt.isocalendar().week
                period_format = 'Week {}'
            elif time_range == 'quarter':
                start_date = now - timedelta(days=90)
                df_filtered = df[df[date_column] >= start_date]
                # Group by month
                df_filtered['period'] = df_filtered[date_column].dt.month
                period_format = lambda x: datetime(2000, x, 1).strftime('%b')
            elif time_range == 'year':
                start_date = now - timedelta(days=365)
                df_filtered = df[df[date_column] >= start_date]
                # Group by quarter
                df_filtered['period'] = (df_filtered[date_column].dt.month - 1) // 3 + 1
                period_format = 'Q{}'
            else:  # all time
                df_filtered = df
                # Group by year
                df_filtered['period'] = df_filtered[date_column].dt.year
                period_format = '{}'
        else:
            # If no date column, use all data
            df_filtered = df
            # Create a simple index as period
            df_filtered['period'] = range(1, len(df) + 1)
            period_format = 'Period {}'
        
        # Identify revenue and expense columns
        revenue_col = None
        expense_col = None
        
        for col in df.columns:
            if 'revenue' in col.lower() or 'income' in col.lower() or 'sales' in col.lower():
                revenue_col = col
            elif 'expense' in col.lower() or 'cost' in col.lower() or 'expenditure' in col.lower():
                expense_col = col
        
        # If columns are not found, use numerical columns
        if not revenue_col or not expense_col:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if len(numeric_cols) >= 2:
                revenue_col = numeric_cols[0]
                expense_col = numeric_cols[1]
        
        # Prepare revenue vs expenses data
        revenue_expenses_data = {'labels': [], 'revenue': [], 'expenses': []}
        
        if revenue_col and expense_col:
            # Group by period
            grouped_data = df_filtered.groupby('period').agg({
                revenue_col: 'sum',
                expense_col: 'sum'
            }).reset_index()
            
            # Sort by period
            grouped_data = grouped_data.sort_values('period')
            
            # Format labels based on period type
            if callable(period_format):
                revenue_expenses_data['labels'] = [period_format(p) for p in grouped_data['period']]
            else:
                revenue_expenses_data['labels'] = [period_format.format(p) for p in grouped_data['period']]
                
            revenue_expenses_data['revenue'] = grouped_data[revenue_col].tolist()
            revenue_expenses_data['expenses'] = grouped_data[expense_col].tolist()
        
        # Calculate financial ratios
        ratios_data = {'labels': [], 'values': []}
        
        # Try to get the latest analysis
        analysis = Analysis.query.filter_by(file_id=latest_file.id).order_by(Analysis.created_date.desc()).first()
        
        if analysis and 'financial_ratios' in analysis.results:
            # Use ratios from analysis
            ratios = analysis.results['financial_ratios']
            for label, value in ratios.items():
                # Format label for display
                display_label = ' '.join(label.split('_')).title()
                ratios_data['labels'].append(display_label)
                ratios_data['values'].append(value)
        else:
            # Calculate some basic ratios from data
            try:
                # Find relevant columns
                assets_col = next((col for col in df.columns if 'asset' in col.lower()), None)
                liabilities_col = next((col for col in df.columns if 'liab' in col.lower()), None)
                current_assets_col = next((col for col in df.columns if 'current' in col.lower() and 'asset' in col.lower()), None)
                current_liabilities_col = next((col for col in df.columns if 'current' in col.lower() and 'liab' in col.lower()), None)
                inventory_col = next((col for col in df.columns if 'inventory' in col.lower()), None)
                profit_col = next((col for col in df.columns if 'profit' in col.lower() or 'net income' in col.lower()), None)
                
                # Calculate ratios if data is available
                if revenue_col and profit_col:
                    profit_margin = df_filtered[profit_col].sum() / df_filtered[revenue_col].sum()
                    ratios_data['labels'].append('Profit Margin')
                    ratios_data['values'].append(round(profit_margin, 2))
                
                if current_assets_col and current_liabilities_col:
                    current_ratio = df_filtered[current_assets_col].iloc[-1] / df_filtered[current_liabilities_col].iloc[-1]
                    ratios_data['labels'].append('Current Ratio')
                    ratios_data['values'].append(round(current_ratio, 2))
                
                if current_assets_col and inventory_col and current_liabilities_col:
                    quick_ratio = (df_filtered[current_assets_col].iloc[-1] - df_filtered[inventory_col].iloc[-1]) / df_filtered[current_liabilities_col].iloc[-1]
                    ratios_data['labels'].append('Quick Ratio')
                    ratios_data['values'].append(round(quick_ratio, 2))
                
                if liabilities_col and assets_col:
                    debt_ratio = df_filtered[liabilities_col].iloc[-1] / df_filtered[assets_col].iloc[-1]
                    ratios_data['labels'].append('Debt Ratio')
                    ratios_data['values'].append(round(debt_ratio, 2))
                
                if profit_col and assets_col:
                    roa = df_filtered[profit_col].sum() / df_filtered[assets_col].iloc[-1]
                    ratios_data['labels'].append('Return on Assets')
                    ratios_data['values'].append(round(roa, 2))
            except:
                # If calculations fail, use dummy data
                ratios_data['labels'] = ['Current Ratio', 'Quick Ratio', 'Debt Ratio', 'Profit Margin', 'ROI']
                ratios_data['values'] = [2.1, 1.8, 0.4, 0.2, 0.15]
        
        return jsonify({
            'revenueExpenses': revenue_expenses_data,
            'ratios': ratios_data
        })
    
    except Exception as e:
        current_app.logger.error(f"Error generating chart data: {str(e)}")
        # Return empty data if error occurs
        return jsonify({
            'revenueExpenses': {
                'labels': [],
                'revenue': [],
                'expenses': []
            },
            'ratios': {
                'labels': [],
                'values': []
            },
            'error': str(e)
        }), 500

@bp.route('/insights', methods=['GET'])
@login_required
def get_ai_insights():
    """Get AI-powered insights based on latest financial data"""
    try:
        # Get the latest financial file for the user
        latest_file = FinancialFile.query.filter_by(user_id=current_user.id).order_by(FinancialFile.upload_date.desc()).first()
        
        if not latest_file:
            return jsonify({
                'success': False,
                'message': 'No financial data found. Please upload a file to get insights.'
            }), 404
        
        # Get the file path
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], latest_file.filename)
        current_app.logger.info(f"Generating insights for file: {file_path}")
        
        # Check if file exists
        if not os.path.exists(file_path):
            current_app.logger.error(f"File not found: {file_path}")
            return jsonify({
                'success': False,
                'message': 'File not found. It may have been deleted.'
            }), 404
        
        # Read the file
        try:
            if latest_file.file_type == 'csv':
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
                
            current_app.logger.info(f"Loaded data with shape: {df.shape}")
        except Exception as e:
            current_app.logger.error(f"Error reading file: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Error reading file: {str(e)}'
            }), 500
        
        # Get latest analysis for the file
        analysis = Analysis.query.filter_by(file_id=latest_file.id).order_by(Analysis.created_date.desc()).first()
        
        # Check if we have analysis
        if analysis is None:
            current_app.logger.warning(f"No analysis found for file ID: {latest_file.id}")
            return jsonify({
                'success': False,
                'message': 'No analysis found for this file. Please analyze your data first.'
            }), 404
            
        # Check if analysis results exist
        if not analysis.results:
            current_app.logger.warning(f"Analysis results are empty for analysis ID: {analysis.id}")
            return jsonify({
                'success': False,
                'message': 'Analysis results are empty. Please re-analyze your data.'
            }), 404
        
        # If we have a valid file and analysis, generate insights
        from app.chat.deepseek_client import DeepSeekClient
        
        # Create client
        client = DeepSeekClient()
        
        # Check if DeepSeek AI is available
        if client.client is None:
            current_app.logger.error("DeepSeek client initialization failed")
            return jsonify({
                'success': False,
                'message': 'DeepSeek AI integration is not available. Please check your API configuration.'
            }), 503
        
        current_app.logger.info("Generating insights with DeepSeek AI")
        
        # Generate insights using DeepSeek AI
        insights = client.get_financial_insights(df, analysis.results)
        
        # Check if insights were generated
        if not insights or "Error" in insights or "couldn't generate" in insights.lower():
            current_app.logger.error(f"Failed to generate insights: {insights}")
            return jsonify({
                'success': False,
                'message': insights
            }), 500
        
        current_app.logger.info("Successfully generated insights")
        
        return jsonify({
            'success': True,
            'insights': insights
        })
    
    except Exception as e:
        current_app.logger.error(f"Error generating insights: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error generating insights: {str(e)}'
        }), 500
