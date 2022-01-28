# Predictor

### NOTES ###
# predict performance (mean or sum) of a specific driver based on all data avalailable on:
# safety training, year license issued, completed shifts, average shift length, accidents, average rating weighted

# Import packages
import pandas as pd

from collections import defaultdict
from sklearn.feature_selection import f_regression
from sklearn.linear_model import LinearRegression

# Load drivers data
dfGroupByDriver = pd.read_csv('Task1_data/dfGroupByDriver.csv')

# Convert duration to seconds
dfGroupByDriver['shift_length_avg_sec'] = pd.to_timedelta(dfGroupByDriver['shift_length_avg']).dt.total_seconds()

# Set list of required columns
list_columns_required = [
    'mean',
    'sum',
    'has_safety_training',
    'driving_licence_issued_year',
    'completed_shifts',
    'shift_length_avg_sec',
    'accidents_sum',
    'rating_avg_weighted'
]

# Remove unrequired columns and drop NAs
dfData = dfGroupByDriver[list_columns_required].copy()
dfData = dfData.dropna()

# Set variables for regression
list_variables_independent = [
    'has_safety_training',
    'driving_licence_issued_year',
    'completed_shifts',
    'shift_length_avg_sec',
    'accidents_sum',
    'rating_avg_weighted'
    ]

list_variables_dependent = [
    'mean',
    'sum'
]

# Set parameters of driver to predict performance for
parameters_driver = {
    'has_safety_training': 1,
    'driving_licence_issued_year': 2010,
    'completed_shifts': 30,
    'shift_length_avg_sec': 20000.00,
    'accidents_sum': 1,
    'rating_avg_weighted': 4.0
    }

# Loop over dependent variables
for variable_dependent in list_variables_dependent:
    # Inform about dependent variable
    print('Dependent variable:', variable_dependent)

    # Set data
    X = dfData[list_variables_independent].values
    y = dfData[variable_dependent]

    # Run regression
    freg = f_regression(X,y)
    p = freg[1]

    model = LinearRegression()
    model.fit(X, y)
    r2 = model.score(X, y)
    r2_adj = 1-(1-model.score(X, y))*(len(y)-1)/(len(y)-X.shape[1]-1)
    print('R2:', r2)
    print('R2 adjusted:', r2_adj)

    # Build summary data frame
    dfSummary = pd.DataFrame(model.coef_, list_variables_independent, columns=['Coefficients'])
    dfSummary['p-Values'] = p
    dfSummary.index.name = 'Independent variable'
    display(dfSummary)

    # Predict performance
    prediction = model.predict([list(parameters_driver.values())])
    print('Prediction in minutes: ', round(prediction[0], 2))
    print()