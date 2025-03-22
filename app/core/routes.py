import os
from werkzeug.utils import secure_filename
import pandas as pd
from flask import render_template, flash, redirect, url_for, request, current_app, send_from_directory, jsonify
from flask_login import login_required, current_user
from app.core import bp
from app.core.models import FinancialFile, Analysis  # Added Analysis import
from app import db
from sqlalchemy.exc import OperationalError, InvalidRequestError
from datetime import datetime

ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard page with financial overview"""
    # Get recent files for the user
    recent_files = FinancialFile.query.filter_by(user_id=current_user.id).order_by(
        FinancialFile.upload_date.desc()).limit(5).all()
    
    # Get recent analyses with error handling for missing user_id column
    try:
        recent_analyses = Analysis.query.filter_by(user_id=current_user.id).order_by(
            Analysis.created_date.desc()).limit(5).all()
    except (OperationalError, InvalidRequestError) as e:
        # Fall back to join with files if user_id column doesn't exist or has issues
        try:
            recent_analyses = Analysis.query.join(FinancialFile).filter(
                FinancialFile.user_id == current_user.id).order_by(
                Analysis.created_date.desc()).limit(5).all()
        except Exception as inner_e:
            current_app.logger.error(f"Error joining with files: {str(inner_e)}")
            recent_analyses = []
    except Exception as e:
        current_app.logger.error(f"Unexpected error getting analyses: {str(e)}")
        recent_analyses = []
    
    return render_template('dashboard.html',
                           title='Dashboard',
                           recent_files=recent_files,
                           recent_analyses=recent_analyses,
                           now=datetime.now())

@bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['file']
        
        # If user does not select file, browser also
        # submits an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Save file info to database
            file_type = filename.rsplit('.', 1)[1].lower()
            new_file = FinancialFile(
                filename=filename,
                file_type=file_type,
                user_id=current_user.id
            )
            db.session.add(new_file)
            db.session.commit()
            
            flash(f'File {filename} uploaded successfully')
            return redirect(url_for('core.dashboard'))
        else:
            flash('Allowed file types are csv, xlsx, xls')
            return redirect(request.url)
            
    return render_template('upload.html')

@bp.route('/view_file/<int:file_id>')
@login_required
def view_file(file_id):
    """View details of a specific file"""
    # Get the file
    file = FinancialFile.query.get_or_404(file_id)
    
    # Check if user owns the file
    if file.user_id != current_user.id:
        flash('Access denied')
        return redirect(url_for('core.dashboard'))
    
    # Get file path
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file.filename)
    
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            flash(f'File not found: {file.filename}. It may have been deleted from the server.', 'danger')
            return redirect(url_for('core.dashboard'))
            
        # Read data
        if file.file_type == 'csv':
            df = pd.read_csv(file_path)
        else:  # excel
            df = pd.read_excel(file_path)
        
        # Get basic stats
        columns = df.columns.tolist()
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        
        # Calculate statistics
        stats = {}
        stats['columns'] = numeric_cols
        stats['metrics'] = ['count', 'mean', 'min', '25%', '50%', '75%', 'max', 'std']
        stats['data'] = {}
        
        if not numeric_cols:
            # No numeric columns to analyze
            stats['data'] = {'count': {col: len(df) for col in columns}}
        else:
            # Generate statistics for numeric columns
            for metric in stats['metrics']:
                stats['data'][metric] = {}
                desc = df.describe().to_dict()
                
                for col in numeric_cols:
                    if col in desc:
                        if metric in desc[col]:
                            stats['data'][metric][col] = desc[col][metric]
                        else:
                            stats['data'][metric][col] = None
                    else:
                        stats['data'][metric][col] = None
        
        # Get last analysis
        last_analysis = Analysis.query.filter_by(file_id=file_id).order_by(Analysis.created_date.desc()).first()
        
        # Prepare sample data for template
        data = {
            'columns': columns,
            'shape': df.shape,
            'records': df.head(100).replace({np.nan: None}).to_dict('records'),
            'sample_data': df.head(5).to_dict('records')
        }
        
        return render_template(
            'view_file.html', 
            file=file, 
            data=data, 
            stats=stats,
            last_analysis=last_analysis
        )
    except Exception as e:
        current_app.logger.error(f"Error reading file: {str(e)}")
        flash(f'Error reading file: {str(e)}', 'danger')
        return redirect(url_for('core.dashboard'))

@bp.route('/api/files/first')
@login_required
def get_first_file():
    """API endpoint to get the first file ID for a user"""
    file = FinancialFile.query.filter_by(user_id=current_user.id).order_by(FinancialFile.id.desc()).first()
    if file:
        return jsonify({'file_id': file.id})
    return jsonify({'file_id': None, 'message': 'No files found. Please upload a file first.'})

@bp.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@bp.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
