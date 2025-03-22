# FinGenius Project

## Description
This repository contains the FinGenius project, a comprehensive financial analysis web application that helps businesses analyze financial statements, create projections, and gain AI-powered insights.

## Features

- **Financial Data Analysis**: Upload and analyze financial statements
- **Interactive Dashboard**: Visualize key financial metrics and trends
- **Financial Projections**: Generate data-driven financial forecasts
- **AI-Powered Insights**: Get intelligent recommendations based on your financial data
- **What-If Analysis**: Test different financial scenarios
- **SWOT Analysis**: Document and track business strengths, weaknesses, opportunities, and threats
- **SMART Goals**: Set and track financial goals

## Installation

```bash
# Clone the repository
git clone https://github.com/m0shaban/FinGenius.git

# Navigate to the project directory
cd FinGenius

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Set up environment variables
# Create a .env file with necessary configuration

# Run the development server
python run.py

# Or use the toolkit for easier management
fingenius_toolkit.bat
```

## Deployment on Render
This project is configured for deployment on Render. Follow these steps:

1. Push your code to GitHub
2. Create a new Web Service on Render
3. Connect to your GitHub repository
4. Use the following settings:
   - **Environment**: Python 3
   - **Build Command**: `bash build.sh`
   - **Start Command**: `gunicorn wsgi:app`
5. Add the following environment variables:
   - `SECRET_KEY`: A secure random string (or let Render generate one)
   - `FLASK_APP`: run.py
   - `FLASK_DEBUG`: false
   - `LOG_TO_STDOUT`: true
   - `DEEPSEEK_API_KEY`: Your DeepSeek API key (if applicable)
   - `CLAUDE_API_KEY`: Your Claude API key (if applicable)

#### Troubleshooting Deployment
If you encounter deployment issues:
1. Check the application logs in Render dashboard
2. Verify that all dependencies are installed by running `python healthcheck.py`
3. Ensure all required environment variables are set
4. Common issues:
   - Missing dependencies in requirements.txt
   - Database configuration issues
   - File permission problems with upload directories
   - Flask factory pattern issues with Gunicorn

#### Development vs Production
In development:
- Use `python run.py` for local testing
- Set `FLASK_DEBUG=1` for debugging features
- SQLite database is used by default

In production:
- Gunicorn serves the application
- Debug mode is disabled
- PostgreSQL database can be configured using `DATABASE_URL`
- Logs are sent to stdout

## License
MIT License
