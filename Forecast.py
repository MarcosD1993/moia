# Forecast

# Import packages
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

from datetime import date, datetime, timedelta
from pandas.tseries.offsets import DateOffset
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller

# Import data
dfMerged = pd.read_csv('Task1_data/dfMerged.csv')

# Change data type of columns
dfMerged['planned_shift_start_timestamp_local_de'] = dfMerged['planned_shift_start_timestamp_local_de'].astype('datetime64')
dfMerged['shift_start_timestamp_local_de'] = dfMerged['shift_start_timestamp_local_de'].astype('datetime64')
dfMerged['planned_shift_end_timestamp_local_de'] = dfMerged['planned_shift_end_timestamp_local_de'].astype('datetime64')
dfMerged['shift_end_timestamp_local_de'] = dfMerged['shift_end_timestamp_local_de'].astype('datetime64')

# Group by shift end
dfMerged['shift_end_date'] = dfMerged['shift_start_timestamp_local_de'].dt.date

dfGroupByShiftEnd = dfMerged.groupby('shift_end_date').sum()

# ARIMA forecast
# Autoregressive Integrated Moving Average
# Three key variables:
# p = number of lags / order of AR terms
# d = order of differencing
# q = number of lagged forecast errors / order of MA terms
# Confidence interval: 95%

# Enter variable to predict
# 'completed_shifts', 'has_accident', or 'diff_shift_total'
variable_predict = 'diff_shift_total'

# Set prediction period
date_base = sorted(dfMerged['shift_end_date'])[-1]
date_prediction = date_base + timedelta(days=3)

# Prepare data
dfForecast = dfGroupByShiftEnd.copy()

# Generate plot
dfForecast[variable_predict].plot(title='Available data for ' + variable_predict)

# Check if data is stationary
# p-value > 0.05 (significance level) = not stationary -> differencing is needed (d > 0)
# p-value <= 0.05 (significance level) = stationary -> differencing not needed (d = 0)
result = adfuller(dfForecast[variable_predict])
dict(zip(['adf', 'pvalue', 'usedlag', 'nobs', 'critical' 'values', 'icbest'], result))

# Differencing 1
dfForecast['1difference'] = dfForecast[variable_predict] - dfForecast[variable_predict].shift(1)
dfForecast['1difference'].plot()

result = adfuller(dfForecast['1difference'].dropna())
dict(zip(['adf', 'pvalue', 'usedlag', 'nobs', 'critical' 'values', 'icbest'], result))

# Differencing 2
dfForecast['2difference'] = dfForecast['1difference'] - dfForecast['1difference'].shift(1)
dfForecast['2difference'].plot()

result = adfuller((dfForecast['2difference']).dropna())
dict(zip(['adf', 'pvalue', 'usedlag', 'nobs', 'critical' 'values', 'icbest'], result))

# ACF and PACF
# p = number of lags above the significance level in Partial Autocorrelation
# d = number of lags above the significance level in Autocorrelation
# q = number of lags above the significance level in Autocorrelation
fig1 = plot_acf(dfForecast[variable_predict].dropna(), title='Autocorrelation - Original')
fig2 = plot_pacf(dfForecast[variable_predict].dropna(), title='Partial Autocorrelation - Original', method='ywm', lags=(dfForecast[variable_predict].dropna().shape[0] // 2) - 1)

fig1 = plot_acf(dfForecast['1difference'].dropna(), title='Autocorrelation - Difference 1')
fig2 = plot_pacf(dfForecast['1difference'].dropna(), title='Partial Autocorrelation - Difference 1', method='ywm', lags=(dfForecast['1difference'].dropna().shape[0] // 2) - 1)

fig1 = plot_acf(dfForecast['2difference'].dropna(), title='Autocorrelation - Difference 2')
fig2 = plot_pacf(dfForecast['2difference'].dropna(), title='Partial Autocorrelation - Difference 2', method='ywm', lags=(dfForecast['2difference'].dropna().shape[0] // 2) - 1)

# Modelling
model = ARIMA(dfForecast[variable_predict], order=(4, 0, 0))
results = model.fit()

# Add future dates
days_future = int((date_prediction - date_base).days)
new_days = [dfForecast.index[-1] + timedelta(days=x) for x in range(1, days_future + 1)]
dfPrediction = pd.DataFrame(index=new_days, columns=dfForecast.columns)

# Prediction
dfResults = pd.concat([dfForecast, dfPrediction])
dfResults.index.name = 'shift_end_date'

dfResults['predictions'] = list(results.predict(start=0, end=(len(dfForecast) + days_future) - 1))
value_day_one_original = dfResults[[variable_predict, 'predictions']][variable_predict][0]
dfResults['predictions'][0] = value_day_one_original
dfResults[[variable_predict, 'predictions']].plot(title='Prediction for ' + variable_predict + ' (sum)')
display(dfResults['predictions'])