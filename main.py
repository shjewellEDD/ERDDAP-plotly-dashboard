'''
TODO:

ERDDAP refrence databases:

using .subset gives different information that .csv
Like a lot.
Why?

https://data.pmel.noaa.gov/engineering/erddap/tabledap/prawler_TELON001.csv
https://data.pmel.noaa.gov/engineering/erddap/tabledap/prawler_baro_TELONAS2.csv    #barometric data
https://data.pmel.noaa.gov/engineering/erddap/tabledap/prawler_TELONAS2.csv         #general scientific data
https://data.pmel.noaa.gov/engineering/erddap/tabledap/prawler_eng_TELONAS2.csv     #engeneering data, do we need this?
https://data.pmel.noaa.gov/engineering/erddap/tabledap/prawler_load_TELONAS2.csv    #engeneering data, do we need this?

We can pull out min and max by using the info sheet, eg:
https://data.pmel.noaa.gov/engineering/erddap/info/prawler_baro_TELONAS2.csv

'''
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt


def open_ERRDAP_csv(path):
    errdap_dat = pd.read_csv(path)

    print(errdap_dat.shape)

    return errdap_dat

def gen_path():



def download_data(path):

    data = pd.read_csv(path)


def clean_data(data):
    # print(data.head())
    # print(data.tail())

    data.drop("altitude", inplace=True, axis=1)
    data.drop("time", inplace=True,axis=1)
    data.drop(labels=0, inplace=True)
    data['latitude'] = pd.to_numeric(list(data['latitude']), downcast='float')
    data['longitude'] = pd.to_numeric(list(data['longitude']), downcast='float')
    data['r667'] = pd.to_numeric(list(data['r667']), downcast='float')

    data.dropna()

    # print(data.head())
    # print(data.tail())

    return data


def spatial_analysis(data):

    # xl = range(data["logitude"].min, data["longitude"].max+1)
    # x = dict(zip(xl, range(1, len(xl))))
    # yl = range(data["latitude"].min, data["latitude"].max+1)
    # y = dict(zip(yl, range(1, len(yl))))
    #
    # bins = np.array((y, x))

    step = 1

    to_bin = lambda x: np.floor(x / step) * step
    data['latbin'] = data.latitude.map(to_bin)
    data['lonbin'] = data.longitude.map(to_bin)
    groups = data.groupby(('latbin', 'lonbin'))



def decimate(data, factor):

    # this could be use IFF we ensure data is properly indexed
    # df1 = df[df.index % factor == 0]

    print("in progress")

def map_area(data):

    #data.plot.scatter(x='latitude', y='longitude')
    #data.plot.scatter(x='latitude',c y='longitude', c='r')

    fig, ax = plt.subplots(subplot_kw={"projection": "3d"})

    surf = ax.plot_trisurf(data["latitude"], data["longitude"], data["r667"])
    plt.show()

def query_formatter(date):

    basepath = 'https://data.pmel.noaa.gov/engineering/erddap/tabledap/prawler_baro_TELONAS2.csv?'


if __name__ == '__main__':
    data = open_ERRDAP_csv("C:\\Users\\jewell\\Documents\\ERRDAP Testing\\GoM 667nm Modis Reflectance.csv")

    clean_data(data)
    spatial_analysis(data)

    print(data.head())
    print(data.tail())

    #map_area(data)

    #print("stop")
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
