import importlib.util
import json
import logging
import os
import sys
from flask import current_app

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("deepseek")

# Ensure we're using proper detection of OpenAI package
try:
    import openai
    openai_available = True
    openai_version = openai.__version__
    logger.info(f"OpenAI package is available, version: {openai_version}")
except ImportError:
    openai_available = False
    openai_version = "Not installed"
    logger.error("OpenAI package is not installed. Install with: pip install openai==1.3.3")

class DeepSeekClient:
    def __init__(self):
        # Check if openai is available at runtime
        if not openai_available:
            logger.error("OpenAI library not installed. DeepSeek AI functions will not work.")
            self.client = None
            self.model = "not-available"
            self.max_tokens = 100
            return
        
        # Get API key directly from environment
        api_key = os.environ.get('DEEPSEEK_API_KEY')
        
        # Fallback to config if not in environment
        if not api_key:
            api_key = current_app.config.get('DEEPSEEK_API_KEY')
            logger.info("Using DeepSeek API key from Flask config")
        else:
            logger.info("Using DeepSeek API key from environment variable")
            
        # Log the key (first 4 chars) for debugging
        if api_key:
            logger.info(f"API key: {api_key[:4]}...")
        else:
            logger.error("No DeepSeek API key found in environment or config")
            
        # Validate the API key
        if not api_key or api_key in ['api-key-placeholder', 'your-api-key-here', 'your_actual_api_key_here']:
            logger.error("DeepSeek API key is missing or is a placeholder value")
            self.client = None
            self.model = "not-available"
            self.max_tokens = 100
            return
            
        # Get other settings
        self.model = os.environ.get('DEEPSEEK_MODEL') or current_app.config.get('DEEPSEEK_MODEL', 'deepseek-chat')
        self.max_tokens = int(os.environ.get('MAX_TOKENS', 4000))
        self.base_url = os.environ.get('DEEPSEEK_BASE_URL') or current_app.config.get('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
        
        logger.info(f"DeepSeek configuration - Model: {self.model}, Base URL: {self.base_url}")
        
        try:
            # Initialize the OpenAI client with DeepSeek base URL
            self.client = openai.OpenAI(api_key=api_key, base_url=self.base_url)
            logger.info("DeepSeek client initialized successfully")
            
            # Test connection
            try:
                test_response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": "test"}],
                    max_tokens=5
                )
                logger.info("Connection test successful")
            except Exception as e:
                logger.error(f"Connection test failed: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to initialize DeepSeek client: {str(e)}")
            self.client = None
            self.model = "not-available"
            self.max_tokens = 100
    
    def analyze_financial_data(self, data_summary, question):
        """Get financial insights from DeepSeek AI"""
        # Return error message if openai not available
        if not openai_available or not self.client:
            return "DeepSeek AI integration is not available. Please check your API key configuration."
        
        # Create a better prompt with file context
        try:
            prompt = f"""
            You are a financial analyst assistant specialized in analyzing uploaded financial data files. Analyze the following financial data and answer the question:

            File Information:
            - Filename: {data_summary['filename']}
            - File Type: {data_summary['file_type']}
            - Uploaded: {data_summary['upload_date']}
            - Rows: {data_summary['shape'][0]}, Columns: {data_summary['shape'][1]}
            
            Available Columns: {', '.join(data_summary['columns'])}
            
            Sample Data (first 5 rows):
            {json.dumps(data_summary['sample_data'], indent=2)}
            
            Summary Statistics:
            {json.dumps(data_summary['summary_stats'], indent=2)}
            
            User Question: {question}

            Provide a professional and detailed answer that directly addresses the user's question. Use specific numbers and insights from the data. Format your response using markdown for better readability. Include bullet points for key insights and recommendations where appropriate.
            """

            try:
                # Use DeepSeek API via OpenAI client
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful financial assistant providing detailed analysis based on data."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=self.max_tokens
                )
                return response.choices[0].message.content
            except Exception as e:
                current_app.logger.error(f"DeepSeek API error: {str(e)}")
                return f"Error getting AI analysis: {str(e)} (OpenAI version: {openai_version})"
        except Exception as e:
            current_app.logger.error(f"Error preparing prompt: {str(e)}")
            return f"Error preparing data for analysis: {str(e)}. Please try a different question or contact support."

    def get_financial_recommendations(self, metrics):
        """Get recommendations based on financial metrics"""
        # Return error message if openai not available
        if not openai_available or not self.client:
            return "DeepSeek AI integration is not available. Please check your API key configuration."
            
        prompt = f"""
        As a financial advisor, analyze these metrics and provide recommendations:

        Financial Metrics:
        {json.dumps(metrics, indent=2)}

        Provide:
        1. Key observations
        2. Areas of concern
        3. Specific recommendations for improvement
        4. Potential opportunities
        
        Format your response using markdown for better readability.
        """

        try:
            # Use DeepSeek API via OpenAI client
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a financial advisor providing professional recommendations."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            current_app.logger.error(f"Error getting AI recommendations: {str(e)}")
            return f"Error getting AI recommendations: {str(e)}"

    def get_financial_insights(self, dataframe, analysis_results):
        """Generate automated insights about financial data using reasoning model"""
        if not openai_available or not self.client:
            return "DeepSeek AI integration is not available. Please check your API key configuration."
        
        try:
            # Convert dataframe to dictionary for JSON serialization
            data_sample = dataframe.head(10).to_dict('records')
            
            # Prepare a more specific prompt for financial insights
            prompt = f"""
            You are a financial analyst specialized in extracting insights from financial data.
            
            Based on the provided financial data and analysis results, provide 5 key insights that would help the business owner make decisions.
            
            Data Sample:
            {json.dumps(data_sample, indent=2)}
            
            Analysis Results:
            {json.dumps(analysis_results, indent=2)}
            
            Format your response as 5 clear sections, each with a bold heading for the insight name followed by a concise explanation.
            Focus on:
            1. Revenue/profit trends
            2. Financial health indicators
            3. Key risks or opportunities
            4. Comparison to industry benchmarks if available
            5. Actionable recommendations
            
            Make your insights specific, data-driven, and directly tied to the numbers provided.
            """
            
            # Use DeepSeek Reasoner model for more complex analysis
            reasoner_model = current_app.config.get('DEEPSEEK_REASONER_MODEL') or os.environ.get('DEEPSEEK_REASONER_MODEL', 'deepseek-reasoner')
            
            response = self.client.chat.completions.create(
                model=reasoner_model,
                messages=[
                    {"role": "system", "content": "You are a financial expert providing in-depth analysis with reasoning."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens
            )
            logger.info("Successfully generated financial insights")
            return response.choices[0].message.content
        except Exception as e:
            current_app.logger.error(f"Error generating insights: {str(e)}")
            return f"We couldn't generate insights at this moment. Error: {str(e)}"
