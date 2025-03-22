import os
import io
from app.core.models import FinancialFile
from werkzeug.datastructures import FileStorage

def test_home_page(client):
    """Test home page loads."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Welcome to FinGenius' in response.data

def test_dashboard_requires_login(client):
    """Test dashboard requires authentication."""
    response = client.get('/dashboard', follow_redirects=True)
    assert b'Please log in' in response.data

def test_dashboard_access(auth_client, test_user):
    """Test authenticated user can access dashboard."""
    response = auth_client.get('/dashboard')
    assert response.status_code == 200
    assert b'Financial Dashboard' in response.data

def test_file_upload(auth_client, app):
    """Test file upload functionality."""
    data = {
        'date,revenue,expenses\n'
        '2023-01-01,1000,500\n'
        '2023-02-01,1200,600'
    }
    file = FileStorage(
        stream=io.BytesIO(data.encode('utf-8')),
        filename='test_upload.csv',
        content_type='text/csv'
    )
    
    response = auth_client.post(
        '/upload',
        data={'file': file},
        content_type='multipart/form-data',
        follow_redirects=True
    )
    
    assert response.status_code == 200
    assert b'uploaded successfully' in response.data
    
    # Check file was saved
    with app.app_context():
        uploaded_file = FinancialFile.query.filter_by(filename='test_upload.csv').first()
        assert uploaded_file is not None
        assert os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], 'test_upload.csv'))

def test_view_file(auth_client, test_file):
    """Test file viewing functionality."""
    response = auth_client.get(f'/view_file/{test_file.id}')
    assert response.status_code == 200
    assert test_file.filename.encode() in response.data
