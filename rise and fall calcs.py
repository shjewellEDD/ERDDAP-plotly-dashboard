'''
Plots to generate
    NTrips
    Total Climb time
    Total Descent time
    Time Per Trip
    Trips per day
'''

import pandas as pd
import datetime
import numpy as np
from matplotlib import pyplot as plt

#sci = pd.read_csv('https://data.pmel.noaa.gov/engineering/erddap/tabledap/prawler_TELONAS2.csv', skiprows=[1])
#load = pd.read_csv('https://data.pmel.noaa.gov/engineering/erddap/tabledap/prawler_load_TELONAS2.csv', skiprows=[1])
#baro = pd.read_csv('https://data.pmel.noaa.gov/engineering/erddap/tabledap/prawler_baro_TELONAS2.csv', skiprows=[1])
eng = pd.read_csv('https://data.pmel.noaa.gov/engineering/erddap/tabledap/prawler_eng_TELONAS2.csv', skiprows=[1])

cols = eng.columns

# manual way
df = pd.DataFrame(eng['time'].str.split('T').to_list(), columns=['date', 'time'])
time = pd.DataFrame(df['date'].str.split('-').to_list(), columns=['year', 'month', 'day'])
date = pd.DataFrame(df['time'].str.split(':').to_list(), columns=['hour', 'min', 'secs'])

# easy way
conv_dt = (pd.to_datetime(eng['time'])).dt.tz_localize(None)
delt = (conv_dt - conv_dt[0]).dt.total_seconds()

print(time, date)