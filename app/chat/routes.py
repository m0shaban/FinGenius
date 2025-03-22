from flask import render_template, request, jsonify, current_app, flash, redirect, url_for
from flask_login import login_required, current_user
from app.chat import bp
# Update import to use DeepSeek client instead of Claude
from app.chat.deepseek_client import DeepSeekClient, openai_available
from app.core.models import FinancialFile, Analysis, db
import pandas as pd
import numpy as np
import os
import json
from datetime import datetime

# Custom JSON encoder to handle pandas Timestamp and numpy types
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (pd.Timestamp, datetime)):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif pd.isna(obj):
            return None
        return super().default(obj)

def serialize_dataframe(df):
    """Safely convert DataFrame to JSON-serializable dictionary"""
    # Convert DataFrame to records and handle special data types
    records = json.loads(json.dumps(df.head(5).to_dict('records'), cls=CustomJSONEncoder))
    return records

@bp.route('/discuss/<int:file_id>')
@login_required
def discuss(file_id):
    file = FinancialFile.query.get_or_404(file_id)
    
    if file.user_id != current_user.id:
        flash('Access denied')
        return redirect(url_for('core.dashboard'))
    
    # Get file metadata for display in the chat interface
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file.filename)
    try:
        # Read basic file info to show in the chat interface
        df = pd.read_csv(file_path) if file.file_type == 'csv' else pd.read_excel(file_path)
        file_stats = {
            'rows': len(df),
            'columns': list(df.columns),
            'date_range': f"{df['date'].min()} to {df['date'].max()}" if 'date' in df.columns else 'N/A'
        }
    except Exception as e:
        file_stats = {'error': str(e)}
        
    return render_template('chat/discuss.html', file=file, file_stats=file_stats)

@bp.route('/ask', methods=['POST'])
@login_required
def ask():
    try:
        file_id = request.form.get('file_id')
        question = request.form.get('question')
        
        file = FinancialFile.query.get_or_404(file_id)
        if file.user_id != current_user.id:
            return jsonify({'error': 'Access denied'}), 403
            
        # Get file data
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file.filename)
        df = pd.read_csv(file_path) if file.file_type == 'csv' else pd.read_excel(file_path)
        
        # Get latest analysis
        analysis = Analysis.query.filter_by(file_id=file_id).order_by(Analysis.created_date.desc()).first()
        
        # Prepare data summary with more detailed information
        numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
        
        # Use custom serialization to handle special data types
        data_summary = {
            'filename': file.filename,
            'file_type': file.file_type,
            'upload_date': file.upload_date.strftime('%Y-%m-%d'),
            'shape': df.shape,
            'columns': df.columns.tolist(),
            'numeric_columns': numeric_columns,
            'sample_data': serialize_dataframe(df),
            'summary_stats': json.loads(json.dumps(df[numeric_columns].describe().to_dict(), cls=CustomJSONEncoder)),
            'analysis_results': analysis.results if analysis else None
        }
        
        # Track interaction in database
        chat_interaction = {
            'question': question,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Update analysis with chat history if it exists
        if analysis:
            if 'chat_history' not in analysis.results:
                analysis.results['chat_history'] = []
            analysis.results['chat_history'].append(chat_interaction)
            db.session.commit()
        
        # Get AI response - Update to use DeepSeek client
        deepseek = DeepSeekClient()
        response = deepseek.analyze_financial_data(data_summary, question)
        
        # Save response to chat history
        if analysis:
            analysis.results['chat_history'][-1]['response'] = response
            db.session.commit()
        
        return jsonify({'response': response, 'file_stats': data_summary})
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        current_app.logger.error(f"Chat error: {error_details}")
        return jsonify({'error': f"Error processing request: {str(e)}"}), 500

@bp.route('/get_insights/<int:file_id>')
@login_required
def get_insights(file_id):
    """Get automated insights about the file"""
    try:
        file = FinancialFile.query.get_or_404(file_id)
        if file.user_id != current_user.id:
            return jsonify({'error': 'Access denied'}), 403
            
        # Load file data
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file.filename)
        df = pd.read_csv(file_path) if file.file_type == 'csv' else pd.read_excel(file_path)
        
        # Get latest analysis
        analysis = Analysis.query.filter_by(file_id=file_id).order_by(Analysis.created_date.desc()).first()
        
        if not analysis:
            return jsonify({'error': 'No analysis found'}), 404
            
        # Generate prompt for insights - Update to use DeepSeek client
        deepseek = DeepSeekClient()
        insights = deepseek.get_financial_insights(df, analysis.results)
        
        return jsonify({'insights': insights})
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        current_app.logger.error(f"Insights error: {error_details}")
        return jsonify({'error': f"Error generating insights: {str(e)}"}), 500

@bp.route('/chat_history/<int:file_id>')
@login_required
def chat_history(file_id):
    """Get chat history for a file"""
    try:
        file = FinancialFile.query.get_or_404(file_id)
        if file.user_id != current_user.id:
            return jsonify({'error': 'Access denied'}), 403
            
        analysis = Analysis.query.filter_by(file_id=file_id).order_by(Analysis.created_date.desc()).first()
        
        if not analysis or 'chat_history' not in analysis.results:
            return jsonify({'history': []})
            
        return jsonify({'history': analysis.results['chat_history']})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/health_check')
@login_required
def health_check():
    """Check the health of the DeepSeek client"""
    try:
        if not openai_available:
            return jsonify({
                'openai_available': False,
                'error': 'OpenAI library not installed'
            })
        
        import openai
        deepseek = DeepSeekClient()
        
        client_info = {
            'openai_available': True,
            'openai_version': openai_version if 'openai_version' in globals() else 'unknown',
            'client_initialized': deepseek.client is not None,
            'model': deepseek.model,
            'base_url': deepseek.base_url
        }
        
        # Test API
        if deepseek.client is not None:
            try:
                response = deepseek.client.chat.completions.create(
                    model=deepseek.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": "Say hello"}
                    ],
                    max_tokens=10
                )
                client_info['api_test'] = {
                    'success': True,
                    'response': response.choices[0].message.content
                }
            except Exception as e:
                client_info['api_test'] = {
                    'success': False,
                    'error': str(e)
                }
        
        return jsonify(client_info)
    except Exception as e:
        return jsonify({'error': str(e)})
