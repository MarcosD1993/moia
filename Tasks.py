# Case Study MOIA

### NOTES ###
# negative (-) = earlier
# positive (+) = later

# driver performance based on total shift time diff

### PREP ###
# Import packages
import os
import pandas as pd

from collections import defaultdict
from matplotlib import pyplot as plt

# Import data
dfDrivers = pd.read_csv('/Users/marcos/Downloads/MOIA/drivers.csv', index_col=[0])
dfShifts = pd.read_csv('/Users/marcos/Downloads/MOIA/shifts.csv', index_col=[0])

# Merge data frames
dfMerged = pd.merge(dfDrivers, dfShifts, on='driver_id')

# Get list columns
display(dfMerged.shape)
display(list(dfMerged))

# Change data type of columns
dfMerged['planned_shift_start_timestamp_local_de'] = dfMerged['planned_shift_start_timestamp_local_de'].astype('datetime64')
dfMerged['shift_start_timestamp_local_de'] = dfMerged['shift_start_timestamp_local_de'].astype('datetime64')
dfMerged['planned_shift_end_timestamp_local_de'] = dfMerged['planned_shift_end_timestamp_local_de'].astype('datetime64')
dfMerged['shift_end_timestamp_local_de'] = dfMerged['shift_end_timestamp_local_de'].astype('datetime64')

# Disasseble time columns ans categorize hours
dfMerged['weekday_shift_start'] = dfMerged['shift_start_timestamp_local_de'].dt.day_name()
dfMerged['weekday_shift_end'] = dfMerged['shift_end_timestamp_local_de'].dt.day_name()

bins = [0, 6, 12, 18, 24]
labels = ['Night', 'Morning', 'Afternoon', 'Evening']

dfMerged['tod_shift_start'] = pd.cut(dfMerged['shift_start_timestamp_local_de'].dt.hour, bins, labels=labels, right=False)
dfMerged['tod_shift_end'] = pd.cut(dfMerged['shift_end_timestamp_local_de'].dt.hour, bins, labels=labels, right=False)

### TASK 1 ###
dictTask1 = defaultdict(lambda: defaultdict(list))

# Calculate length of shifts
dfMerged['shift_length'] = dfMerged['shift_end_timestamp_local_de'] - dfMerged['shift_start_timestamp_local_de']

# Calculate time difference and punctuality
dfMerged['diff_shift_start'] = (dfMerged['shift_start_timestamp_local_de'] - dfMerged['planned_shift_start_timestamp_local_de']).dt.total_seconds() / 60
dfMerged['diff_shift_end'] = (dfMerged['shift_end_timestamp_local_de'] - dfMerged['planned_shift_end_timestamp_local_de']).dt.total_seconds() / 60
dfMerged['diff_shift_total'] = dfMerged['diff_shift_start'] + dfMerged['diff_shift_end']

dictTask1['all']['saldo_delay_positive'] = dfMerged[dfMerged['diff_shift_total'] > 0]['diff_shift_total'].sum()
dictTask1['all']['saldo_delay_negative'] = dfMerged[dfMerged['diff_shift_total'] <= 0]['diff_shift_total'].sum()
dictTask1['all']['saldo_total'] = dfMerged['diff_shift_total'].sum()
print('Saldo of positive delay in days:', round(dictTask1['all']['saldo_delay_positive'], 2) / 60 / 24)
print('Saldo of negative delay in days:', round(dictTask1['all']['saldo_delay_negative'], 2) / 60 / 24)
print('Total saldo in hours:', round(dictTask1['all']['saldo_total'], 2) / 60)
print()

dictTask1['all']['rate_punctuality_start'] = dfMerged[dfMerged['diff_shift_start'] <= 0]['diff_shift_start'].count() / len(dfMerged) * 100
dictTask1['all']['rate_punctuality_end'] = dfMerged[dfMerged['diff_shift_end'] <= 0]['diff_shift_end'].count() / len(dfMerged) * 100
dictTask1['all']['rate_punctuality_total'] = dfMerged[dfMerged['diff_shift_total'] <= 0]['diff_shift_total'].count() / len(dfMerged) * 100
print('Punctuality rate start (%):', round(dictTask1['all']['rate_punctuality_start'], 1))
print('Punctuality rate end (%):', round(dictTask1['all']['rate_punctuality_end'], 1))
print('Punctuality rate total (%):', round(dictTask1['all']['rate_punctuality_total'], 1))
print()

# Get overall description of dataset
dfMergedDesc = dfMerged.describe()

# Apply threshold and calculate shares
threshold_avg = 5
#threshold_sum = 60
print('Threshold (avg) in minutes:', threshold_avg)
#print('Threshold (sum) in minutes:', threshold_sum)
print()

print('Shift start')
plt.figure(1)
plt.title('diff_shift_start')
dfMerged['diff_shift_start'].hist()
share_pos = len(dfMerged[dfMerged['diff_shift_start'] >= threshold_avg]) / len(dfMerged) * 100
share_neg = len(dfMerged[dfMerged['diff_shift_start'] <= -threshold_avg]) / len(dfMerged) * 100
print('Share of shifts above positive threshold (%):', round(share_pos, 1))
print('Share of shifts above negative threshold (%):', round(share_neg, 1))
print()

dictTask1['all']['shift_start_share_pos'] = share_pos
dictTask1['all']['shift_start_share_neg'] = share_neg

print('Shift end')
plt.figure(2)
plt.title('diff_shift_end')
dfMerged['diff_shift_end'].hist()
share_pos = len(dfMerged[dfMerged['diff_shift_end'] >= threshold_avg]) / len(dfMerged) * 100
share_neg = len(dfMerged[dfMerged['diff_shift_end'] <= -threshold_avg]) / len(dfMerged) * 100
print('Share of shifts above positive threshold (%):', round(share_pos, 1))
print('Share of shifts above negative threshold (%):', round(share_neg, 1))
print()

dictTask1['all']['shift_end_share_pos'] = share_pos
dictTask1['all']['shift_end_share_neg'] = share_neg

print('Shift total')
plt.figure(3)
plt.title('diff_shift_total')
dfMerged['diff_shift_total'].hist()
share_pos = len(dfMerged[dfMerged['diff_shift_total'] >= threshold_avg]) / len(dfMerged) * 100
share_neg = len(dfMerged[dfMerged['diff_shift_total'] <= -threshold_avg]) / len(dfMerged) * 100
print('Share of shifts above positive threshold (%):', round(share_pos, 1))
print('Share of shifts above negative threshold (%):', round(share_neg, 1))
print()

dictTask1['all']['shift_total_share_pos'] = share_pos
dictTask1['all']['shift_total_share_neg'] = share_neg

# Group results
diff_column = 'diff_shift_total'

## By driver
dfGroupByDriver = dfMerged.groupby('driver_id')[diff_column].describe()
dfGroupByDriver['sum'] = list(dfMerged.groupby('driver_id')[diff_column].sum())
dfGroupByDriver = dfGroupByDriver.merge(dfDrivers, on='driver_id')
dfGroupByDriver['shift_length_avg'] = list(dfMerged.groupby('driver_id')['shift_length'].mean())
dfGroupByDriver['accidents_sum'] = list(dfMerged.groupby('driver_id')['has_accident'].sum())
dfGroupByDriver['rating_cnt'] = list(dfMerged.groupby('driver_id')['customer_driver_rating'].count())
dfGroupByDriver['rating_avg'] = list(dfMerged.groupby('driver_id')['customer_driver_rating'].mean())

### Weight and categorize ratings
cats, bins = pd.cut(dfGroupByDriver['rating_cnt'], 5, retbins=True)
bins = list(bins)
labels = [1.1, 1.2, 1.3, 1.4, 1.5]

dfGroupByDriver['rating_weight'] = pd.cut(dfGroupByDriver['rating_cnt'], bins, labels=labels, right=False)
dfGroupByDriver['rating_avg_weighted'] = dfGroupByDriver['rating_avg'] * dfGroupByDriver['rating_weight'].astype(float)

bins = [0, 2.5, 5, 7.5]
labels = ['Bad', 'Okay', 'Good']

dfGroupByDriver['rating_cat'] = pd.cut(dfGroupByDriver['rating_avg_weighted'], bins, labels=labels, right=False)

### Categorize amount of shifts
bins = [0, 50, 100, 150]
labels = ['Beginner', 'Advanced', 'Expert']

dfGroupByDriver['skill_level'] = pd.cut(dfGroupByDriver['completed_shifts'], bins, labels=labels, right=False)

## By area
dfGroupByArea = dfMerged.groupby('service_area_id')[diff_column].describe()
dfGroupByArea['sum'] = list(dfMerged.groupby('service_area_id')[diff_column].sum())
dfGroupByArea['shift_length_avg'] = list(dfMerged.groupby('service_area_id')['shift_length'].mean())
dfGroupByArea['accidents_sum'] = list(dfMerged.groupby('service_area_id')['has_accident'].sum())
dfGroupByArea['shifts_cnt'] = list(dfMerged.groupby('service_area_id')['shift_id'].count())

for area_id in dfMerged['service_area_id'].unique():
    print('Area ID:', area_id)
    dictTask1[area_id]['rate_punctuality_start'] = dfMerged[(dfMerged['service_area_id'] == area_id) & (dfMerged['diff_shift_start'] <= 0)]['diff_shift_start'].count() / len(dfMerged) * 100
    dictTask1[area_id]['rate_punctuality_end'] = dfMerged[(dfMerged['service_area_id'] == area_id) & (dfMerged['diff_shift_end'] <= 0)]['diff_shift_end'].count() / len(dfMerged) * 100
    dictTask1[area_id]['rate_punctuality_total'] = dfMerged[(dfMerged['service_area_id'] == area_id) & (dfMerged['diff_shift_total'] <= 0)]['diff_shift_total'].count() / len(dfMerged) * 100
    print('Punctuality rate start (%):', round(dictTask1[area_id]['rate_punctuality_start'], 1))
    print('Punctuality rate end (%):', round(dictTask1[area_id]['rate_punctuality_end'], 1))
    print('Punctuality rate total (%):', round(dictTask1[area_id]['rate_punctuality_total'], 1))
    print()

    share_pos = len(dfMerged[(dfMerged['service_area_id'] == area_id) & (dfMerged['diff_shift_total'] >= threshold_avg)]) / len(dfMerged) * 100
    share_neg = len(dfMerged[(dfMerged['service_area_id'] == area_id) & (dfMerged['diff_shift_total'] <= -threshold_avg)]) / len(dfMerged) * 100
    print('Share of shifts above positive threshold (%):', round(share_pos, 1))
    print('Share of shifts above negative threshold (%):', round(share_neg, 1))
    print()

    dictTask1[area_id]['shift_total_share_pos'] = share_pos
    dictTask1[area_id]['shift_total_share_neg'] = share_neg

### Add data on centrality of each area when having data on more areas

## By weekday
dfWeekdayShiftStart = dfMerged.groupby('weekday_shift_start')[diff_column].describe()
dfWeekdayShiftStart['sum'] = list(dfMerged.groupby('weekday_shift_start')[diff_column].sum())
dfWeekdayShiftStart['shift_length_avg'] = list(dfMerged.groupby('weekday_shift_start')['shift_length'].mean())
dfWeekdayShiftStart['accidents_sum'] = list(dfMerged.groupby('weekday_shift_start')['has_accident'].sum())
dfWeekdayShiftStart['shifts_cnt'] = list(dfMerged.groupby('weekday_shift_start')['shift_id'].count())
dfWeekdayShiftStart.sort_values(by=['mean'])
dfWeekdayShiftStart.sort_values(by=['sum'])

for weekday in dfMerged['weekday_shift_start'].unique():
    print('Weekday (Start):', weekday)
    dictTask1[weekday + ' (Start)']['rate_punctuality_start'] = dfMerged[(dfMerged['weekday_shift_start'] == weekday) & (dfMerged['diff_shift_start'] <= 0)]['diff_shift_start'].count() / len(dfMerged[dfMerged['weekday_shift_start'] == weekday]) * 100
    dictTask1[weekday + ' (Start)']['rate_punctuality_end'] = dfMerged[(dfMerged['weekday_shift_start'] == weekday) & (dfMerged['diff_shift_end'] <= 0)]['diff_shift_end'].count() / len(dfMerged[dfMerged['weekday_shift_start'] == weekday]) * 100
    dictTask1[weekday + ' (Start)']['rate_punctuality_total'] = dfMerged[(dfMerged['weekday_shift_start'] == weekday) & (dfMerged['diff_shift_total'] <= 0)]['diff_shift_total'].count() / len(dfMerged[dfMerged['weekday_shift_start'] == weekday]) * 100
    print('Punctuality rate start (%):', round(dictTask1[weekday + ' (Start)']['rate_punctuality_start'], 1))
    print('Punctuality rate end (%):', round(dictTask1[weekday + ' (Start)']['rate_punctuality_end'], 1))
    print('Punctuality rate total (%):', round(dictTask1[weekday + ' (Start)']['rate_punctuality_total'], 1))
    print()

    share_pos = len(dfMerged[(dfMerged['weekday_shift_start'] == weekday) & (dfMerged['diff_shift_total'] >= threshold_avg)]) / len(dfMerged) * 100
    share_neg = len(dfMerged[(dfMerged['weekday_shift_start'] == weekday) & (dfMerged['diff_shift_total'] <= -threshold_avg)]) / len(dfMerged) * 100
    print('Share of shifts above positive threshold (%):', round(share_pos, 1))
    print('Share of shifts above negative threshold (%):', round(share_neg, 1))
    print()

    dictTask1[weekday + ' (Start)']['shift_total_share_pos'] = share_pos
    dictTask1[weekday + ' (Start)']['shift_total_share_neg'] = share_neg

dfWeekdayShiftEnd = dfMerged.groupby('weekday_shift_end')[diff_column].describe()
dfWeekdayShiftEnd['sum'] = list(dfMerged.groupby('weekday_shift_end')[diff_column].sum())
dfWeekdayShiftEnd['shift_length_avg'] = list(dfMerged.groupby('weekday_shift_end')['shift_length'].mean())
dfWeekdayShiftEnd['accidents_sum'] = list(dfMerged.groupby('weekday_shift_end')['has_accident'].sum())
dfWeekdayShiftEnd['shifts_cnt'] = list(dfMerged.groupby('weekday_shift_end')['shift_id'].count())
dfWeekdayShiftEnd.sort_values(by=['mean'])
dfWeekdayShiftEnd.sort_values(by=['sum'])

for weekday in dfMerged['weekday_shift_end'].unique():
    print('Weekday (End):', weekday)
    dictTask1[weekday + ' (End)']['rate_punctuality_start'] = dfMerged[(dfMerged['weekday_shift_end'] == weekday) & (dfMerged['diff_shift_start'] <= 0)]['diff_shift_start'].count() / len(dfMerged[dfMerged['weekday_shift_end'] == weekday]) * 100
    dictTask1[weekday + ' (End)']['rate_punctuality_end'] = dfMerged[(dfMerged['weekday_shift_end'] == weekday) & (dfMerged['diff_shift_end'] <= 0)]['diff_shift_end'].count() / len(dfMerged[dfMerged['weekday_shift_end'] == weekday]) * 100
    dictTask1[weekday + ' (End)']['rate_punctuality_total'] = dfMerged[(dfMerged['weekday_shift_end'] == weekday) & (dfMerged['diff_shift_total'] <= 0)]['diff_shift_total'].count() / len(dfMerged[dfMerged['weekday_shift_end'] == weekday]) * 100
    print('Punctuality rate start (%):', round(dictTask1[weekday + ' (End)']['rate_punctuality_start'], 1))
    print('Punctuality rate end (%):', round(dictTask1[weekday + ' (End)']['rate_punctuality_end'], 1))
    print('Punctuality rate total (%):', round(dictTask1[weekday + ' (End)']['rate_punctuality_total'], 1))
    print()

    share_pos = len(dfMerged[(dfMerged['weekday_shift_end'] == weekday) & (dfMerged['diff_shift_total'] >= threshold_avg)]) / len(dfMerged) * 100
    share_neg = len(dfMerged[(dfMerged['weekday_shift_end'] == weekday) & (dfMerged['diff_shift_total'] <= -threshold_avg)]) / len(dfMerged) * 100
    print('Share of shifts above positive threshold (%):', round(share_pos, 1))
    print('Share of shifts above negative threshold (%):', round(share_neg, 1))
    print()

    dictTask1[weekday + ' (End)']['shift_total_share_pos'] = share_pos
    dictTask1[weekday + ' (End)']['shift_total_share_neg'] = share_neg

## By time of day
dfGroupByToDShiftStart = dfMerged.groupby('tod_shift_start')[diff_column].describe()
dfGroupByToDShiftStart['sum'] = list(dfMerged.groupby('tod_shift_start')[diff_column].sum())
dfGroupByToDShiftStart['shift_length_avg'] = list(dfMerged.groupby('tod_shift_start')['shift_length'].mean())
dfGroupByToDShiftStart['accidents_sum'] = list(dfMerged.groupby('tod_shift_start')['has_accident'].sum())
dfGroupByToDShiftStart['shifts_cnt'] = list(dfMerged.groupby('tod_shift_start')['shift_id'].count())
dfGroupByToDShiftStart.sort_values(by=['mean'])
dfGroupByToDShiftStart.sort_values(by=['sum'])

for timeofday in dfMerged['tod_shift_start'].unique():
    print('Time of day (Start):', timeofday)
    dictTask1[timeofday + ' (Start)']['rate_punctuality_start'] = dfMerged[(dfMerged['tod_shift_start'] == timeofday) & (dfMerged['diff_shift_start'] <= 0)]['diff_shift_start'].count() / len(dfMerged[dfMerged['tod_shift_start'] == timeofday]) * 100
    dictTask1[timeofday + ' (Start)']['rate_punctuality_end'] = dfMerged[(dfMerged['tod_shift_start'] == timeofday) & (dfMerged['diff_shift_end'] <= 0)]['diff_shift_end'].count() / len(dfMerged[dfMerged['tod_shift_start'] == timeofday]) * 100
    dictTask1[timeofday + ' (Start)']['rate_punctuality_total'] = dfMerged[(dfMerged['tod_shift_start'] == timeofday) & (dfMerged['diff_shift_total'] <= 0)]['diff_shift_total'].count() / len(dfMerged[dfMerged['tod_shift_start'] == timeofday]) * 100
    print('Punctuality rate start (%):', round(dictTask1[timeofday + ' (Start)']['rate_punctuality_start'], 1))
    print('Punctuality rate end (%):', round(dictTask1[timeofday + ' (Start)']['rate_punctuality_end'], 1))
    print('Punctuality rate total (%):', round(dictTask1[timeofday + ' (Start)']['rate_punctuality_total'], 1))
    print()

    share_pos = len(dfMerged[(dfMerged['tod_shift_start'] == timeofday) & (dfMerged['diff_shift_total'] >= threshold_avg)]) / len(dfMerged) * 100
    share_neg = len(dfMerged[(dfMerged['tod_shift_start'] == timeofday) & (dfMerged['diff_shift_total'] <= -threshold_avg)]) / len(dfMerged) * 100
    print('Share of shifts above positive threshold (%):', round(share_pos, 1))
    print('Share of shifts above negative threshold (%):', round(share_neg, 1))
    print()

    dictTask1[timeofday + ' (Start)']['shift_total_share_pos'] = share_pos
    dictTask1[timeofday + ' (Start)']['shift_total_share_neg'] = share_neg

dfGroupByToDShiftEnd = dfMerged.groupby('tod_shift_end')[diff_column].describe()
dfGroupByToDShiftEnd['sum'] = list(dfMerged.groupby('tod_shift_end')[diff_column].sum())
dfGroupByToDShiftEnd['shift_length_avg'] = list(dfMerged.groupby('tod_shift_end')['shift_length'].mean())
dfGroupByToDShiftEnd['accidents_sum'] = list(dfMerged.groupby('tod_shift_end')['has_accident'].sum())
dfGroupByToDShiftEnd['shifts_cnt'] = list(dfMerged.groupby('tod_shift_end')['shift_id'].count())
dfGroupByToDShiftEnd.sort_values(by=['mean'])
dfGroupByToDShiftEnd.sort_values(by=['sum'])

for timeofday in dfMerged['tod_shift_end'].unique():
    print('Time of day (End):', timeofday)
    dictTask1[timeofday + ' (End)']['rate_punctuality_start'] = dfMerged[(dfMerged['tod_shift_end'] == timeofday) & (dfMerged['diff_shift_start'] <= 0)]['diff_shift_start'].count() / len(dfMerged[dfMerged['tod_shift_end'] == timeofday]) * 100
    dictTask1[timeofday + ' (End)']['rate_punctuality_end'] = dfMerged[(dfMerged['tod_shift_end'] == timeofday) & (dfMerged['diff_shift_end'] <= 0)]['diff_shift_end'].count() / len(dfMerged[dfMerged['tod_shift_end'] == timeofday]) * 100
    dictTask1[timeofday + ' (End)']['rate_punctuality_total'] = dfMerged[(dfMerged['tod_shift_end'] == timeofday) & (dfMerged['diff_shift_total'] <= 0)]['diff_shift_total'].count() / len(dfMerged[dfMerged['tod_shift_end'] == timeofday]) * 100
    print('Punctuality rate start (%):', round(dictTask1[timeofday + ' (End)']['rate_punctuality_start'], 1))
    print('Punctuality rate end (%):', round(dictTask1[timeofday + ' (End)']['rate_punctuality_end'], 1))
    print('Punctuality rate total (%):', round(dictTask1[timeofday + ' (End)']['rate_punctuality_total'], 1))
    print()

    share_pos = len(dfMerged[(dfMerged['tod_shift_end'] == timeofday) & (dfMerged['diff_shift_total'] >= threshold_avg)]) / len(dfMerged) * 100
    share_neg = len(dfMerged[(dfMerged['tod_shift_end'] == timeofday) & (dfMerged['diff_shift_total'] <= -threshold_avg)]) / len(dfMerged) * 100
    print('Share of shifts above positive threshold (%):', round(share_pos, 1))
    print('Share of shifts above negative threshold (%):', round(share_neg, 1))
    print()

    dictTask1[timeofday + ' (End)']['shift_total_share_pos'] = share_pos
    dictTask1[timeofday + ' (End)']['shift_total_share_neg'] = share_neg

### Combination of weekday and time of day

# Top 5 (lowest/highest diff)
## Drivers
dfTopDriversPosMean = dfGroupByDriver.nlargest(5, 'mean')
dfTopDriversNegMean = dfGroupByDriver.nsmallest(5, 'mean')

dfTopDriversPosSum = dfGroupByDriver.nlargest(5, 'sum')
dfTopDriversNegSum = dfGroupByDriver.nsmallest(5, 'sum')

### Sort by completed shifts, accidents, ratings etc.

## Areas
dfTopAreasPosMean = dfGroupByArea.nlargest(5, 'mean')
dfTopAreasNegMean = dfGroupByArea.nsmallest(5, 'mean')

dfTopAreasPosSum = dfGroupByArea.nlargest(5, 'sum')
dfTopAreasNegSum = dfGroupByArea.nsmallest(5, 'sum')

### Sort by number of shifts, accidents etc.

## Share of drivers
### All
dfST = dfGroupByDriver[dfGroupByDriver['has_safety_training'] == 1]
share = len(dfST) / len(dfGroupByDriver) * 100
print('Share of drivers with safety training (%):', round(share, 1))
print()

dictTask1['all']['drivers_share_st'] = share

dfAcc = dfGroupByDriver[dfGroupByDriver['accidents_sum'] > 0]
share = len(dfAcc) / len(dfGroupByDriver) * 100
print('Share of drivers with accident(s) (%):', round(share, 1))
print()

dictTask1['all']['drivers_share_acc'] = share

share_bad = len(dfGroupByDriver[dfGroupByDriver['rating_cat'] == 'Bad']) / len(dfGroupByDriver) * 100
share_okay = len(dfGroupByDriver[dfGroupByDriver['rating_cat'] == 'Okay']) / len(dfGroupByDriver) * 100
share_good = len(dfGroupByDriver[dfGroupByDriver['rating_cat'] == 'Good']) / len(dfGroupByDriver) * 100
print('Share of bad drivers based on ratings (%):', round(share_bad, 1))
print('Share of okay drivers based on ratings (%):', round(share_okay, 1))
print('Share of good drivers based on ratings (%):', round(share_good, 1))
print()

dictTask1['all']['drivers_share_bad'] = share_bad
dictTask1['all']['drivers_share_okay'] = share_okay
dictTask1['all']['drivers_share_good'] = share_good

dfSkills = pd.DataFrame(round(dfGroupByDriver['skill_level'].value_counts() / len(dfGroupByDriver) * 100, 2))

share_beginners = len(dfGroupByDriver[dfGroupByDriver['skill_level'] == 'Beginner']) / len(dfGroupByDriver) * 100
share_advanced = len(dfGroupByDriver[dfGroupByDriver['skill_level'] == 'Advanced']) / len(dfGroupByDriver) * 100
share_experts = len(dfGroupByDriver[dfGroupByDriver['skill_level'] == 'Expert']) / len(dfGroupByDriver) * 100
print('Share of beginners (%):', round(share_beginners, 1))
print('Share of advanced drivers (%):', round(share_advanced, 1))
print('Share of experts (%):', round(share_experts, 1))
print()

dictTask1['all']['drivers_share_beginners'] = share_beginners
dictTask1['all']['drivers_share_advanced'] = share_advanced
dictTask1['all']['drivers_share_experts'] = share_experts

### Prep: above threshold
dfPosAbove = dfGroupByDriver[dfGroupByDriver['mean'] >= threshold_avg]
dfNegAbove = dfGroupByDriver[dfGroupByDriver['mean'] <= -threshold_avg]

share_pos = len(dfPosAbove) / len(dfGroupByDriver) * 100
share_neg = len(dfNegAbove) / len(dfGroupByDriver) * 100
print('Share of drivers above positive threshold (%):', round(share_pos, 1))
print('Share of drivers above negative threshold (%):', round(share_neg, 1))
print()

dictTask1['above_pos']['drivers_share'] = share_pos
dictTask1['above_neg']['drivers_share'] = share_neg

### Prep: below threshold
dfPosBelow = dfGroupByDriver[dfGroupByDriver['mean'] <= threshold_avg]
dfNegBelow = dfGroupByDriver[dfGroupByDriver['mean'] >= -threshold_avg]

### Safety training
dfPosSTBelow = dfGroupByDriver[(dfGroupByDriver['mean'] <= threshold_avg) & (dfGroupByDriver['has_safety_training'] == 1)]
dfNegSTBelow = dfGroupByDriver[(dfGroupByDriver['mean'] >= -threshold_avg) & (dfGroupByDriver['has_safety_training'] == 1)]

share_pos = len(dfPosSTBelow) / len(dfGroupByDriver) * 100
share_neg = len(dfNegSTBelow) / len(dfGroupByDriver) * 100
print('Share of drivers below positive threshold with safety training (%):', round(share_pos, 1))
print('Share of drivers below negative threshold with safety training (%):', round(share_neg, 1))
print()

dictTask1['below_pos']['drivers_share_st'] = share_pos
dictTask1['below_neg']['drivers_share_st'] = share_neg

dfPosSTAbove = dfGroupByDriver[(dfGroupByDriver['mean'] >= threshold_avg) & (dfGroupByDriver['has_safety_training'] == 1)]
dfNegSTAbove = dfGroupByDriver[(dfGroupByDriver['mean'] <= -threshold_avg) & (dfGroupByDriver['has_safety_training'] == 1)]

share_pos = len(dfPosSTAbove) / len(dfGroupByDriver) * 100
share_neg = len(dfNegSTAbove) / len(dfGroupByDriver) * 100
print('Share of drivers above positive threshold with safety training (%):', round(share_pos, 1))
print('Share of drivers above negative threshold with safety training (%):', round(share_neg, 1))
print()

dictTask1['above_pos']['drivers_share_st'] = share_pos
dictTask1['above_neg']['drivers_share_st'] = share_neg

### Accidents
dfPosAccBelow = dfGroupByDriver[(dfGroupByDriver['mean'] <= threshold_avg) & (dfGroupByDriver['accidents_sum'] > 0)]
dfNegAccBelow = dfGroupByDriver[(dfGroupByDriver['mean'] >= -threshold_avg) & (dfGroupByDriver['accidents_sum'] > 0)]

share_pos = len(dfPosAccBelow) / len(dfGroupByDriver) * 100
avg_pos = dfPosAccBelow['accidents_sum'].mean()
share_neg = len(dfNegAccBelow) / len(dfGroupByDriver) * 100
avg_neg = dfNegAccBelow['accidents_sum'].mean()
print('Share of drivers below positive threshold with accident(s) (%):', round(share_pos, 1))
print('Average number of accidents of these drivers:', round(avg_pos, 2))
print('Share of drivers below negative threshold with accident(s) (%):', round(share_neg, 1))
print('Average number of accidents of these drivers:', round(avg_neg, 2))
print()

dictTask1['below_pos']['drivers_share_acc'] = share_pos
dictTask1['below_pos']['drivers_avg_acc'] = avg_pos
dictTask1['below_neg']['drivers_share_acc'] = share_neg
dictTask1['below_neg']['drivers_avg_acc'] = avg_neg

dfPosAccAbove = dfGroupByDriver[(dfGroupByDriver['mean'] >= threshold_avg) & (dfGroupByDriver['accidents_sum'] > 0)]
dfNegAccAbove = dfGroupByDriver[(dfGroupByDriver['mean'] <= -threshold_avg) & (dfGroupByDriver['accidents_sum'] > 0)]

share_pos = len(dfPosAccAbove) / len(dfGroupByDriver) * 100
avg_pos = dfPosAccAbove['accidents_sum'].mean()
share_neg = len(dfNegAccAbove) / len(dfGroupByDriver) * 100
avg_neg = dfNegAccAbove['accidents_sum'].mean()
print('Share of drivers above positive threshold with accident(s) (%):', round(share_pos, 1))
print('Average number of accidents of these drivers:', round(avg_pos, 2))
print('Share of drivers above negative threshold with accident(s) (%):', round(share_neg, 1))
print('Average number of accidents of these drivers:', round(avg_neg, 2))
print()

dictTask1['above_pos']['drivers_share_acc'] = share_pos
dictTask1['above_pos']['drivers_avg_acc'] = avg_pos
dictTask1['above_neg']['drivers_share_acc'] = share_neg
dictTask1['above_neg']['drivers_avg_acc'] = avg_neg

### Completed Shifts
avg_below_pos = dfPosBelow['completed_shifts'].mean()
print('Below threshold: Average number of shifts:', round(avg_below_pos, 2))
avg_above_pos = dfPosAbove['completed_shifts'].mean()
print('Above threshold: Average number of shifts:', round(avg_above_pos, 2))
print()

avg_below_neg = dfNegAbove['completed_shifts'].mean()
print('Below negative threshold: Average number of shifts:', round(avg_below_neg, 2))
avg_above_neg = dfNegBelow['completed_shifts'].mean()
print('Above negative threshold: Average number of shifts:', round(avg_above_neg, 2))
print()

dictTask1['below_pos']['drivers_shifts_avg'] = avg_below_pos
dictTask1['above_pos']['drivers_shifts_avg'] = avg_above_pos
dictTask1['below_neg']['drivers_shifts_avg'] = avg_below_neg
dictTask1['above_neg']['drivers_shifts_avg'] = avg_above_neg

### Year License Issued
dfPosBelowDesc = dfPosBelow['driving_licence_issued_year'].describe()
dfPosAboveDesc = dfPosAbove['driving_licence_issued_year'].describe()

dfNegBelowDesc = dfNegBelow['driving_licence_issued_year'].describe()
dfNegAboveDesc = dfNegAbove['driving_licence_issued_year'].describe()

avg_below_pos = int(dfPosBelow['driving_licence_issued_year'].mean())
print('Below threshold: Average year license issued:', avg_below_pos)
avg_above_pos = int(dfPosAbove['driving_licence_issued_year'].mean())
print('Above threshold: Average year license issued:', avg_above_pos)
print()

avg_below_neg = int(dfNegBelow['driving_licence_issued_year'].mean())
print('Below negative threshold: Average year license issued:', avg_below_neg)
avg_above_neg = int(dfNegAbove['driving_licence_issued_year'].mean())
print('Above negative threshold: Average year license issued:', avg_above_neg)
print()

dictTask1['below_pos']['drivers_license_year_avg'] = avg_below_pos
dictTask1['above_pos']['drivers_license_year_avg'] = avg_above_pos
dictTask1['below_neg']['drivers_license_year_avg'] = avg_below_neg
dictTask1['above_neg']['drivers_license_year_avg'] = avg_above_neg

### Rating
avg_below_pos = dfPosBelow['rating_cnt'].mean()
print('Below threshold: Average amount of ratings:', round(avg_below_pos, 2))
avg_above_pos = dfPosAbove['rating_cnt'].mean()
print('Above threshold: Average amount of ratings:', round(avg_above_pos, 2))
print()

avg_below_neg = dfNegBelow['rating_cnt'].mean()
print('Below negative threshold: Average amount of ratings:', round(avg_below_neg, 2))
avg_above_neg = dfNegAbove['rating_cnt'].mean()
print('Above negative threshold: Average amount of ratings:', round(avg_above_neg, 2))
print()

dictTask1['below_pos']['drivers_ratings_cnt_avg'] = avg_below_pos
dictTask1['above_pos']['drivers_ratings_cnt_avg'] = avg_above_pos
dictTask1['below_neg']['drivers_ratings_cnt_avg'] = avg_below_neg
dictTask1['above_neg']['drivers_ratings_cnt_avg'] = avg_above_neg

avg_below_pos = dfPosBelow['rating_avg'].mean()
print('Below threshold: Average mean of ratings:', round(avg_below_pos, 2))
avg_above_pos = dfPosAbove['rating_avg'].mean()
print('Above threshold: Average mean of ratings:', round(avg_above_pos, 2))
print()

avg_below_neg = dfNegBelow['rating_avg'].mean()
print('Below negative threshold: Average mean of ratings:', round(avg_below_neg, 2))
avg_above_neg = dfNegAbove['rating_avg'].mean()
print('Above negative threshold: Average mean of ratings:', round(avg_above_neg, 2))
print()

dictTask1['below_pos']['drivers_ratings_avg_avg'] = avg_below_pos
dictTask1['above_pos']['drivers_ratings_avg_avg'] = avg_above_pos
dictTask1['below_neg']['drivers_ratings_avg_avg'] = avg_below_neg
dictTask1['above_neg']['drivers_ratings_avg_avg'] = avg_above_neg

share_bad = len(dfPosBelow[dfPosBelow['rating_cat'] == 'Bad']) / len(dfPosBelow) * 100
share_okay = len(dfPosBelow[dfPosBelow['rating_cat'] == 'Okay']) / len(dfPosBelow) * 100
share_good = len(dfPosBelow[dfPosBelow['rating_cat'] == 'Good']) / len(dfPosBelow) * 100
print('Below threshold: Share of bad drivers based on ratings (%):', round(share_bad, 1))
print('Below threshold: Share of okay drivers based on ratings (%):', round(share_okay, 1))
print('Below threshold: Share of good drivers based on ratings (%):', round(share_good, 1))
print()

dictTask1['below_pos']['drivers_share_bad'] = share_bad
dictTask1['below_pos']['drivers_share_okay'] = share_okay
dictTask1['below_pos']['drivers_share_good'] = share_good

share_bad = len(dfPosAbove[dfPosAbove['rating_cat'] == 'Bad']) / len(dfPosAbove) * 100
share_okay = len(dfPosAbove[dfPosAbove['rating_cat'] == 'Okay']) / len(dfPosAbove) * 100
share_good = len(dfPosAbove[dfPosAbove['rating_cat'] == 'Good']) / len(dfPosAbove) * 100
print('Above threshold: Share of bad drivers based on ratings (%):', round(share_bad, 1))
print('Above threshold: Share of okay drivers based on ratings (%):', round(share_okay, 1))
print('Above threshold: Share of good drivers based on ratings (%):', round(share_good, 1))
print()

dictTask1['above_pos']['drivers_share_bad'] = share_bad
dictTask1['above_pos']['drivers_share_okay'] = share_okay
dictTask1['above_pos']['drivers_share_good'] = share_good

share_bad = len(dfNegBelow[dfNegBelow['rating_cat'] == 'Bad']) / len(dfNegBelow) * 100
share_okay = len(dfNegBelow[dfNegBelow['rating_cat'] == 'Okay']) / len(dfNegBelow) * 100
share_good = len(dfNegBelow[dfNegBelow['rating_cat'] == 'Good']) / len(dfNegBelow) * 100
print('Below negative threshold: Share of bad drivers based on ratings (%):', round(share_bad, 1))
print('Below negative threshold: Share of okay drivers based on ratings (%):', round(share_okay, 1))
print('Below negative threshold: Share of good drivers based on ratings (%):', round(share_good, 1))
print()

dictTask1['below_neg']['drivers_share_bad'] = share_bad
dictTask1['below_neg']['drivers_share_okay'] = share_okay
dictTask1['below_neg']['drivers_share_good'] = share_good

share_bad = len(dfNegAbove[dfNegAbove['rating_cat'] == 'Bad']) / len(dfNegAbove) * 100
share_okay = len(dfNegAbove[dfNegAbove['rating_cat'] == 'Okay']) / len(dfNegAbove) * 100
share_good = len(dfNegAbove[dfNegAbove['rating_cat'] == 'Good']) / len(dfNegAbove) * 100
print('Above negative threshold: Share of bad drivers based on ratings (%):', round(share_bad, 1))
print('Above negative threshold: Share of okay drivers based on ratings (%):', round(share_okay, 1))
print('Above negative threshold: Share of good drivers based on ratings (%):', round(share_good, 1))
print()

dictTask1['above_neg']['drivers_share_bad'] = share_bad
dictTask1['above_neg']['drivers_share_okay'] = share_okay
dictTask1['above_neg']['drivers_share_good'] = share_good

### Skill level
share_beginners = len(dfPosBelow[dfPosBelow['skill_level'] == 'Beginner']) / len(dfPosBelow) * 100
share_advanced = len(dfPosBelow[dfPosBelow['skill_level'] == 'Advanced']) / len(dfPosBelow) * 100
share_experts = len(dfPosBelow[dfPosBelow['skill_level'] == 'Expert']) / len(dfPosBelow) * 100
print('Below threshold: Share of beginners (%):', round(share_beginners, 1))
print('Below threshold: Share of advanced drivers (%):', round(share_advanced, 1))
print('Below threshold: Share of experts (%):', round(share_experts, 1))
print()

dictTask1['below_pos']['drivers_share_beginners'] = share_beginners
dictTask1['below_pos']['drivers_share_advanced'] = share_advanced
dictTask1['below_pos']['drivers_share_experts'] = share_experts

share_beginners = len(dfPosAbove[dfPosAbove['skill_level'] == 'Beginner']) / len(dfPosAbove) * 100
share_advanced = len(dfPosAbove[dfPosAbove['skill_level'] == 'Advanced']) / len(dfPosAbove) * 100
share_experts = len(dfPosAbove[dfPosAbove['skill_level'] == 'Expert']) / len(dfPosAbove) * 100
print('Above threshold: Share of beginners (%):', round(share_beginners, 1))
print('Above threshold: Share of advanced drivers (%):', round(share_advanced, 1))
print('Above threshold: Share of experts (%):', round(share_experts, 1))
print()

dictTask1['above_pos']['drivers_share_beginners'] = share_beginners
dictTask1['above_pos']['drivers_share_advanced'] = share_advanced
dictTask1['above_pos']['drivers_share_experts'] = share_experts

share_beginners = len(dfNegBelow[dfNegBelow['skill_level'] == 'Beginner']) / len(dfNegBelow) * 100
share_advanced = len(dfNegBelow[dfNegBelow['skill_level'] == 'Advanced']) / len(dfNegBelow) * 100
share_experts = len(dfNegBelow[dfNegBelow['skill_level'] == 'Expert']) / len(dfNegBelow) * 100
print('Below negative threshold: Share of beginners (%):', round(share_beginners, 1))
print('Below negative threshold: Share of advanced drivers (%):', round(share_advanced, 1))
print('Below negative threshold: Share of experts (%):', round(share_experts, 1))
print()

dictTask1['below_neg']['drivers_share_beginners'] = share_beginners
dictTask1['below_neg']['drivers_share_advanced'] = share_advanced
dictTask1['below_neg']['drivers_share_experts'] = share_experts

share_beginners = len(dfNegAbove[dfNegAbove['skill_level'] == 'Beginner']) / len(dfNegAbove) * 100
share_advanced = len(dfNegAbove[dfNegAbove['skill_level'] == 'Advanced']) / len(dfNegAbove) * 100
share_experts = len(dfNegAbove[dfNegAbove['skill_level'] == 'Expert']) / len(dfNegAbove) * 100
print('Above negative threshold: Share of beginners (%):', round(share_beginners, 1))
print('Above negative threshold: Share of advanced drivers (%):', round(share_advanced, 1))
print('Above negative threshold: Share of experts (%):', round(share_experts, 1))
print()

dictTask1['above_neg']['drivers_share_beginners'] = share_beginners
dictTask1['above_neg']['drivers_share_advanced'] = share_advanced
dictTask1['above_neg']['drivers_share_experts'] = share_experts

# Do similar analysis with areas when having data on more areas

# Export results
dfTask1 = pd.DataFrame.from_dict(dictTask1)
display(dfTask1)

if not os.path.exists('Task1_data'):
    os.makedirs('Task1_data')

dfMerged.to_csv('Task1_data/dfMerged.csv')

dfGroupByDriver.to_csv('Task1_data/dfGroupByDriver.csv')

dfTask1.to_csv('Task1_data/dfTask1.csv')

### TASK 2 ###
dictTask2 = defaultdict(lambda: defaultdict(list))

# Calculate probabilities
## Too late: above threshold vs. below threshold
dictTask2['above_pos']['prob_acc'] = dictTask1['above_pos']['drivers_share_acc'] / dictTask1['all']['drivers_share_acc']
dictTask2['above_neg']['prob_acc'] = dictTask1['above_neg']['drivers_share_acc'] / dictTask1['all']['drivers_share_acc']

dictTask2['above_pos']['prob_bad'] = dictTask1['above_pos']['drivers_share_bad'] / dictTask1['all']['drivers_share_bad']
dictTask2['above_pos']['prob_okay'] = dictTask1['above_pos']['drivers_share_okay'] / dictTask1['all']['drivers_share_okay']
dictTask2['above_pos']['prob_good'] = dictTask1['above_pos']['drivers_share_good'] / dictTask1['all']['drivers_share_good']

dictTask2['above_neg']['prob_bad'] = dictTask1['above_neg']['drivers_share_bad'] / dictTask1['all']['drivers_share_bad']
dictTask2['above_neg']['prob_okay'] = dictTask1['above_neg']['drivers_share_okay'] / dictTask1['all']['drivers_share_okay']
dictTask2['above_neg']['prob_good'] = dictTask1['above_neg']['drivers_share_good'] / dictTask1['all']['drivers_share_good']

## Too early: above threshold vs. below threshold
dictTask2['below_pos']['prob_acc'] = dictTask1['below_pos']['drivers_share_acc'] / dictTask1['all']['drivers_share_acc']
dictTask2['below_neg']['prob_acc'] = dictTask1['below_neg']['drivers_share_acc'] / dictTask1['all']['drivers_share_acc']

dictTask2['below_pos']['prob_bad'] = dictTask1['below_pos']['drivers_share_bad'] / dictTask1['all']['drivers_share_bad']
dictTask2['below_pos']['prob_okay'] = dictTask1['below_pos']['drivers_share_okay'] / dictTask1['all']['drivers_share_okay']
dictTask2['below_pos']['prob_good'] = dictTask1['below_pos']['drivers_share_good'] / dictTask1['all']['drivers_share_good']

dictTask2['below_neg']['prob_bad'] = dictTask1['below_neg']['drivers_share_bad'] / dictTask1['all']['drivers_share_bad']
dictTask2['below_neg']['prob_okay'] = dictTask1['below_neg']['drivers_share_okay'] / dictTask1['all']['drivers_share_okay']
dictTask2['below_neg']['prob_good'] = dictTask1['below_neg']['drivers_share_good'] / dictTask1['all']['drivers_share_good']

# Multiple regression

# Export results
dfTask2 = pd.DataFrame.from_dict(dictTask2)
display(dfTask2)

if not os.path.exists('Task2_data'):
    os.makedirs('Task2_data')

dfTask2.to_csv('Task2_data/dfTask2.csv')

### FORECAST ###