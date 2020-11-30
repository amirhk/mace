import os
import numpy as np
import pandas as pd
pd.options.mode.chained_assignment = None

def load_housing_data():

    raw_data_file = os.path.join(os.path.dirname(__file__), 'housing_raw.csv')
    processed_file = os.path.join(os.path.dirname(__file__), 'housing_processed.csv')

    ##### Boston Housing Data Processing
    raw_df = pd.read_csv(raw_data_file, delim_whitespace=True)
    processed_df = pd.DataFrame()

    # Map class to an integer
    processed_df['price (label)'] = raw_df['MEDV']

    # All features are numerical and require no further processing
    for col in raw_df.columns:
        if col != 'MEDV':
            processed_df[col] = raw_df[col]

    processed_df.to_csv(processed_file, header=True, index=False)
    return processed_df.astype('float64')
