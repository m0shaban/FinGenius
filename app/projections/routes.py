from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import login_required, current_user
from app.projections import bp
from app.core.models import FinancialFile

@bp.route('/projections')
@login_required
def projections():
    """Financial projections page"""
    # Get recent files for the file selector
    recent_files = FinancialFile.query.filter_by(user_id=current_user.id).order_by(
        FinancialFile.upload_date.desc()).limit(10).all()
    
    return render_template('projections/projections.html', recent_files=recent_files)
