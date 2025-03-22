import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import base64

class ComparisonService:
    def __init__(self, dataframes):
        """Initialize with list of dataframes to compare"""
        self.dfs = dataframes
        self.common_columns = self._get_common_columns()
        
    def _get_common_columns(self):
        """Find columns that exist in all dataframes"""
        if not self.dfs:
            return []
        common = set(self.dfs[0].columns)
        for df in self.dfs[1:]:
            common = common.intersection(set(df.columns))
        return list(common)
        
    def compare_summary_statistics(self):
        """Compare basic statistics for common numeric columns"""
        results = {}
        
        for col in self.common_columns:
            if pd.api.types.is_numeric_dtype(self.dfs[0][col]):
                stats = []
                for i, df in enumerate(self.dfs):
                    stats.append({
                        'mean': df[col].mean(),
                        'median': df[col].median(),
                        'std': df[col].std(),
                        'min': df[col].min(),
                        'max': df[col].max()
                    })
                results[col] = stats
                
        return results
        
    def calculate_differences(self):
        """Calculate percentage differences between datasets"""
        if len(self.dfs) < 2:
            return {}
            
        differences = {}
        for col in self.common_columns:
            if pd.api.types.is_numeric_dtype(self.dfs[0][col]):
                base_mean = self.dfs[0][col].mean()
                if base_mean != 0:
                    diffs = []
                    for df in self.dfs[1:]:
                        curr_mean = df[col].mean()
                        pct_diff = ((curr_mean - base_mean) / base_mean) * 100
                        diffs.append(pct_diff)
                    differences[col] = diffs
                    
        return differences
        
    def generate_comparison_chart(self, column):
        """Generate a comparative visualization for a specific column"""
        if column not in self.common_columns:
            return None
            
        plt.figure(figsize=(10, 6))
        
        for i, df in enumerate(self.dfs):
            if pd.api.types.is_numeric_dtype(df[column]):
                plt.plot(range(len(df)), df[column], label=f'Dataset {i+1}')
                
        plt.title(f'Comparison of {column}')
        plt.xlabel('Data Points')
        plt.ylabel(column)
        plt.legend()
        plt.grid(True)
        
        # Convert plot to base64 string
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        
        return f'data:image/png;base64,{img_str}'
        
    def generate_correlation_comparison(self):
        """Compare correlation matrices between datasets"""
        correlation_diffs = {}
        
        if len(self.dfs) < 2:
            return {}
            
        base_corr = self.dfs[0].select_dtypes(include=[np.number]).corr()
        
        for i, df in enumerate(self.dfs[1:], 1):
            curr_corr = df.select_dtypes(include=[np.number]).corr()
            common_cols = set(base_corr.columns) & set(curr_corr.columns)
            
            if common_cols:
                diff_matrix = pd.DataFrame(index=common_cols, columns=common_cols)
                for col1 in common_cols:
                    for col2 in common_cols:
                        base_val = base_corr.loc[col1, col2]
                        curr_val = curr_corr.loc[col1, col2]
                        diff_matrix.loc[col1, col2] = curr_val - base_val
                        
                correlation_diffs[f'dataset_{i+1}_vs_1'] = diff_matrix.to_dict()
                
        return correlation_diffs
