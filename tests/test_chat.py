from app.chat.claude_client import ClaudeClient
from unittest.mock import patch

def test_chat_access(auth_client, test_file):
    """Test chat interface access."""
    response = auth_client.get(f'/chat/discuss/{test_file.id}')
    assert response.status_code == 200
    assert b'AI Financial Assistant' in response.data

@patch('app.chat.claude_client.ClaudeClient.analyze_financial_data')
def test_ask_question(mock_analyze, auth_client, test_file):
    """Test asking questions through chat."""
    mock_analyze.return_value = "Test analysis response"
    
    response = auth_client.post('/chat/ask', data={
        'file_id': test_file.id,
        'question': 'What are the key metrics?'
    })
    
    assert response.status_code == 200
    assert b'Test analysis response' in response.data
