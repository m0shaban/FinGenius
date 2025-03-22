import importlib.util
import json
from flask import current_app
import logging
import os

# Check if anthropic is installed
anthropic_available = importlib.util.find_spec("anthropic") is not None

# Only import if available
if anthropic_available:
    import anthropic
    try:
        # Check current version of anthropic
        import pkg_resources
        anthropic_version = pkg_resources.get_distribution("anthropic").version
        logging.info(f"Using anthropic SDK version {anthropic_version}")
    except:
        anthropic_version = "unknown"
        logging.warning("Unable to determine anthropic SDK version")

class ClaudeClient:
    def __init__(self):
        # Check if anthropic is available at runtime
        if not anthropic_available:
            self.client = None
            self.model = "not-available"
            self.max_tokens = 100
            logging.warning("Anthropic library not installed. Claude AI functions will not work.")
            return
        
        # Get API key from config or environment
        api_key = current_app.config.get('CLAUDE_API_KEY')
        if not api_key or api_key == 'sk-key-placeholder':
            api_key = os.environ.get('CLAUDE_API_KEY')
            
        if not api_key:
            logging.warning("No valid API key provided for Claude. Please configure CLAUDE_API_KEY.")
            self.client = None
            self.model = "not-available"
            self.max_tokens = 100
            return
        
        # Get model from config or env
        self.model = current_app.config.get('CLAUDE_MODEL') or os.environ.get('CLAUDE_MODEL', 'claude-3-haiku-20240307')
        self.max_tokens = current_app.config.get('MAX_TOKENS', 4000)
        
        try:
            # For version 0.3+, create Anthropic client
            if anthropic_version.startswith(('0.3', '0.4', '0.5', '0.6')):
                self.client = anthropic.Anthropic(api_key=api_key)
                self.use_new_api = True
                
                # Ensure model is compatible with 0.3+ API
                if self.model == 'claude-2':
                    self.model = 'claude-3-haiku-20240307'
                    logging.warning(f"Changed model to {self.model} for compatibility with SDK 0.3+")
                
                logging.info(f"Using Anthropic SDK version {anthropic_version} with model {self.model}")
            else:
                # For older versions, use the Client class
                self.client = anthropic.Client(api_key=api_key)
                self.use_new_api = False
                
                # For backwards compatibility with old SDK, don't use claude-3
                if self.model.startswith('claude-3'):
                    self.model = 'claude-2'
                    logging.warning(f"Changed model to {self.model} for compatibility with SDK 0.2.x")
                
                logging.info(f"Using legacy Anthropic SDK with model {self.model}")
        except Exception as e:
            logging.error(f"Failed to initialize Claude client: {e}")
            self.client = None
            self.model = "not-available"
            self.max_tokens = 100

    def analyze_financial_data(self, data_summary, question):
        """Get financial insights from Claude AI"""
        # Return error message if anthropic not available
        if not anthropic_available or not self.client:
            return "Claude AI integration is not available. Please check your API key configuration."
        
        # Create a safer version of the prompt
        try:
            # Create a more detailed prompt with file context
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
                if self.use_new_api:
                    # SDK 0.6.0 with Claude 3 models - try different methods based on the SDK version
                    if hasattr(self.client, 'messages'):
                        # Messages API (newer versions)
                        response = self.client.messages.create(
                            model=self.model,
                            max_tokens=self.max_tokens,
                            messages=[
                                {"role": "user", "content": prompt}
                            ]
                        )
                        return response.content[0].text
                    elif hasattr(self.client, 'message'):
                        # For SDK 0.6.0, use message (singular) instead of messages (plural)
                        response = self.client.message(
                            model=self.model,
                            max_tokens=self.max_tokens,
                            messages=[
                                {"role": "user", "content": prompt}
                            ]
                        )
                        return response.content[0].text
                    else:
                        # Fallback to completion API for older 0.3.x versions
                        response = self.client.completion(
                            prompt=f"{anthropic.HUMAN_PROMPT} {prompt} {anthropic.AI_PROMPT}",
                            model=self.model,
                            max_tokens_to_sample=self.max_tokens,
                            temperature=0.7,
                            stop_sequences=[anthropic.HUMAN_PROMPT]
                        )
                        return response.completion
                else:
                    # Completion API (0.2.x)
                    response = self.client.completion(
                        prompt=f"{anthropic.HUMAN_PROMPT} {prompt} {anthropic.AI_PROMPT}",
                        model=self.model,
                        max_tokens_to_sample=self.max_tokens,
                        temperature=0.7,
                        stop_sequences=[anthropic.HUMAN_PROMPT]
                    )
                    return response['completion']
            except Exception as e:
                current_app.logger.error(f"Claude API error: {str(e)}")
                return f"Error getting AI analysis: {str(e)} (Anthropic version: {anthropic_version})"
        except Exception as e:
            current_app.logger.error(f"Error preparing prompt: {str(e)}")
            return f"Error preparing data for analysis: {str(e)}. Please try a different question or contact support."

    def get_financial_recommendations(self, metrics):
        """Get recommendations based on financial metrics"""
        # Return error message if anthropic not available
        if not anthropic_available or not self.client:
            return "Claude AI integration is not available. Please check your API key configuration."
            
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
            if self.use_new_api:
                # Try different API methods based on SDK version
                if hasattr(self.client, 'messages'):
                    # Newer versions with messages API
                    response = self.client.messages.create(
                        model=self.model,
                        max_tokens=self.max_tokens,
                        messages=[
                            {"role": "user", "content": prompt}
                        ]
                    )
                    return response.content[0].text
                elif hasattr(self.client, 'message'):
                    # For SDK 0.6.0, use message (singular) method
                    response = self.client.message(
                        model=self.model,
                        max_tokens=self.max_tokens,
                        messages=[
                            {"role": "user", "content": prompt}
                        ]
                    )
                    return response.content[0].text
                else:
                    # Fallback to completion
                    response = self.client.completion(
                        prompt=f"{anthropic.HUMAN_PROMPT} {prompt} {anthropic.AI_PROMPT}",
                        model=self.model,
                        max_tokens_to_sample=self.max_tokens,
                        temperature=0.7,
                        stop_sequences=[anthropic.HUMAN_PROMPT]
                    )
                    return response.completion
            else:
                # Completion API (0.2.x)
                response = self.client.completion(
                    prompt=f"{anthropic.HUMAN_PROMPT} {prompt} {anthropic.AI_PROMPT}",
                    model=self.model,
                    max_tokens_to_sample=self.max_tokens,
                    temperature=0.7,
                    stop_sequences=[anthropic.HUMAN_PROMPT]
                )
                return response['completion']
        except Exception as e:
            current_app.logger.error(f"Error getting AI recommendations: {str(e)}")
            return f"Error getting AI recommendations: {str(e)}"

    def get_financial_insights(self, dataframe, analysis_results):
        """Generate automated insights about financial data"""
        if not anthropic_available or not self.client:
            return "Claude AI integration is not available. Please check your API key configuration."
        
        # Convert dataframe to dictionary for JSON serialization
        data_sample = dataframe.head(10).to_dict('records')
        prompt = f"""
        You are a financial analyst. Provide 5 key insights about this financial data.
        
        Data Sample:
        {json.dumps(data_sample, indent=2)}
        
        Analysis Results:
        {json.dumps(analysis_results, indent=2)}
        
        Please provide 5 specific, data-driven insights that would be valuable for financial decision-making.
        Format each insight with a title in bold and a brief explanation.
        """
        try:
            if self.use_new_api:
                # Try different API methods based on SDK version
                if hasattr(self.client, 'messages'):
                    # Newer versions with messages API
                    response = self.client.messages.create(
                        model=self.model,
                        max_tokens=self.max_tokens,
                        messages=[
                            {"role": "user", "content": prompt}
                        ]
                    )
                    return response.content[0].text
                elif hasattr(self.client, 'message'):
                    # For SDK 0.6.0, use message (singular) method
                    response = self.client.message(
                        model=self.model,
                        max_tokens=self.max_tokens,
                        messages=[
                            {"role": "user", "content": prompt}
                        ]
                    )
                    return response.content[0].text
                else:
                    # Fallback to completion
                    response = self.client.completion(
                        prompt=f"{anthropic.HUMAN_PROMPT} {prompt} {anthropic.AI_PROMPT}",
                        model=self.model,
                        max_tokens_to_sample=self.max_tokens,
                        temperature=0.7,
                        stop_sequences=[anthropic.HUMAN_PROMPT]
                    )
                    return response.completion
            else:
                # Completion API (0.2.x)
                response = self.client.completion(
                    prompt=f"{anthropic.HUMAN_PROMPT} {prompt} {anthropic.AI_PROMPT}",
                    model=self.model,
                    max_tokens_to_sample=self.max_tokens,
                    temperature=0.7,
                    stop_sequences=[anthropic.HUMAN_PROMPT]
                )
                return response['completion']
        except Exception as e:
            current_app.logger.error(f"Error generating insights: {str(e)}")
            return f"Error generating insights: {str(e)}"
