import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import io
import base64
from flask import current_app
from datetime import datetime

class FinancialAnalyzer:
    def __init__(self, dataframe):
        self.df = dataframe
        
    def calculate_financial_ratios(self):
        """Calculate common financial ratios based on the available columns"""
        ratios = {}
        columns = self.df.columns
        
        # Standardize column names (lowercase)
        std_columns = [col.lower() for col in columns]
        col_map = dict(zip(std_columns, columns))
        
        # Profit Margin
        if all(x in std_columns for x in ['revenue', 'net income']):
            revenue_col = col_map['revenue']
            net_income_col = col_map['net income']
            ratios['profit_margin'] = (self.df[net_income_col] / self.df[revenue_col]).mean()
        
        # Gross Margin
        if all(x in std_columns for x in ['revenue', 'cost of goods sold']):
            revenue_col = col_map['revenue']
            cogs_col = col_map['cost of goods sold']
            ratios['gross_margin'] = ((self.df[revenue_col] - self.df[cogs_col]) / self.df[revenue_col]).mean()
        
        # Return on Assets (ROA)
        if all(x in std_columns for x in ['net income', 'total assets']):
            net_income_col = col_map['net income']
            assets_col = col_map['total assets']
            ratios['roa'] = (self.df[net_income_col] / self.df[assets_col]).mean()
        
        # Return on Equity (ROE)
        if all(x in std_columns for x in ['net income', 'equity']):
            net_income_col = col_map['net income']
            equity_col = col_map['equity']
            ratios['roe'] = (self.df[net_income_col] / self.df[equity_col]).mean()
        
        # Current Ratio
        if all(x in std_columns for x in ['current assets', 'current liabilities']):
            current_assets_col = col_map['current assets']
            current_liabilities_col = col_map['current liabilities']
            ratios['current_ratio'] = (self.df[current_assets_col] / self.df[current_liabilities_col]).mean()
        
        # Debt to Equity
        if all(x in std_columns for x in ['total debt', 'equity']):
            debt_col = col_map['total debt']
            equity_col = col_map['equity']
            ratios['debt_to_equity'] = (self.df[debt_col] / self.df[equity_col]).mean()
        
        # Try to calculate any available ratio even if column names don't match standard names
        # Look for columns containing 'revenue' or 'income'
        revenue_cols = [col for col in columns if 'revenue' in col.lower() or 'income' in col.lower()]
        # Look for columns containing 'profit'
        profit_cols = [col for col in columns if 'profit' in col.lower() or 'margin' in col.lower()]
        
        if revenue_cols and profit_cols:
            ratios['estimated_profit_margin'] = (self.df[profit_cols[0]] / self.df[revenue_cols[0]]).mean()
        
        return ratios
    
    def generate_time_series_chart(self, column_name):
        """Generate a time series chart for a specified column"""
        # Try to find date column
        date_cols = [col for col in self.df.columns if 'date' in col.lower() or 'period' in col.lower()]
        
        if not date_cols:
            # If no date column is found, try to use the index if it's datetime
            if isinstance(self.df.index, pd.DatetimeIndex):
                date_col = self.df.index
            else:
                # Create a sequence of dates
                date_col = pd.date_range(start='1/1/2023', periods=len(self.df), freq='M')
        else:
            date_col = self.df[date_cols[0]]
            # Try to convert to datetime if it's not already
            if not pd.api.types.is_datetime64_any_dtype(date_col):
                try:
                    date_col = pd.to_datetime(date_col)
                except:
                    # If conversion fails, use a sequence
                    date_col = pd.date_range(start='1/1/2023', periods=len(self.df), freq='M')
        
        # Create matplotlib figure
        plt.figure(figsize=(10, 6))
        plt.plot(date_col, self.df[column_name])
        plt.title(f'{column_name} Over Time')
        plt.xlabel('Date')
        plt.ylabel(column_name)
        plt.grid(True)
        plt.tight_layout()
        
        # Save figure to a base64 string
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        
        return f'data:image/png;base64,{img_str}'
    
    def generate_correlation_matrix(self):
        """Generate a correlation matrix for numeric columns"""
        # Select only numeric columns
        numeric_df = self.df.select_dtypes(include=['number'])
        
        if numeric_df.empty:
            return None
        
        # Calculate correlation matrix
        corr_matrix = numeric_df.corr()
        
        # Create heatmap
        plt.figure(figsize=(10, 8))
        plt.matshow(corr_matrix, fignum=1)
        plt.colorbar()
        
        # Add column names as ticks
        plt.xticks(range(len(corr_matrix.columns)), corr_matrix.columns, rotation=90)
        plt.yticks(range(len(corr_matrix.columns)), corr_matrix.columns)
        
        # Save figure to a base64 string
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        
        return f'data:image/png;base64,{img_str}'
    
    def find_trends(self):
        """Identify trends in the financial data"""
        # Select only numeric columns
        numeric_df = self.df.select_dtypes(include=['number'])
        
        if numeric_df.empty:
            return {}
        
        trends = {}
        
        # Calculate growth rates for each numeric column
        for col in numeric_df.columns:
            if len(numeric_df[col]) > 1:
                # Calculate growth rate
                first_val = numeric_df[col].iloc[0]
                last_val = numeric_df[col].iloc[-1]
                
                if first_val != 0:
                    growth_rate = ((last_val - first_val) / first_val) * 100
                    trends[col] = {
                        'growth_rate': growth_rate,
                        'trend': 'increasing' if growth_rate > 0 else 'decreasing'
                    }
        
        return trends
    
    def forecasting_simple(self, column_name, periods=3):
        """Simple forecasting using linear regression"""
        if column_name not in self.df.columns:
            return None
            
        # Create a sequence of periods
        x = np.array(range(len(self.df))).reshape(-1, 1)
        y = self.df[column_name].values
        
        # Linear regression
        from sklearn.linear_model import LinearRegression
        model = LinearRegression()
        model.fit(x, y)
        
        # Predict future periods
        future_x = np.array(range(len(self.df), len(self.df) + periods)).reshape(-1, 1)
        future_y = model.predict(future_x)
        
        # Create DataFrame for results
        result = pd.DataFrame()
        result['period'] = range(1, periods + 1)
        result['forecast'] = future_y
        
        return result
