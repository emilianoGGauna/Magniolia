import pandas as pd
import numpy as np
import plotly.express as px
import plotly.io as pio

class per:

    @staticmethod
    def perform_data_analysis(df, column_names):
        analysis_results = {}

        # Set DataFrame columns
        df.columns = np.array(column_names)
        
        # Exclude columns with 'Id' in their name
        df = df[[col for col in df.columns if 'Id' not in col]]

        # Convert strings to numeric if appropriate
        for col in df.columns:
            try:
                if df[col].dtype == 'object':
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            except Exception as e:
                print(f"Error processing column {col}: {e}")

        # Descriptive Statistics
        analysis_results['descriptive_stats'] = df.describe(include='all').to_html()

        # Missing Values
        analysis_results['missing_values'] = df.isnull().sum().to_frame('Missing Values').to_html()

        # Data Types
        analysis_results['data_types'] = df.dtypes.to_frame('Data Types').to_html()

        # Unique Values
        analysis_results['unique_values'] = df.nunique().to_frame('Unique Values').to_html()

        # Category Counts for Categorical Data
        categorical_columns = df.select_dtypes(exclude=[np.number]).columns
        category_counts = {col: df[col].value_counts() for col in categorical_columns}
        analysis_results['category_counts'] = {col: counts.to_frame('Counts').to_html() for col, counts in category_counts.items()}

        # Correlation Matrix
        numeric_df = df.select_dtypes(include=[np.number])
        if not numeric_df.empty:
            corr_matrix = numeric_df.corr()

            # Filtra las columnas donde todas las correlaciones son cero
            relevant_columns = corr_matrix.columns[corr_matrix.abs().sum() > 0]
            filtered_corr_matrix = corr_matrix[relevant_columns].loc[relevant_columns]

            if not filtered_corr_matrix.empty and filtered_corr_matrix.shape[0] > 1:
                corr_matrix_fig = px.imshow(filtered_corr_matrix, text_auto=True)
                analysis_results['correlation_matrix'] = pio.to_html(corr_matrix_fig, full_html=False)


        return analysis_results
