import dash
import dash_design_kit as ddk  # Only available on Dash Enterprise
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import dash_html_components as html
import datetime
import requests

import logging

logging.basicConfig(filename='dash_log.log', encoding='utf-8', level=logging.DEBUG)
logger = logging.getLogger('debug_logger')

# graph_config = {'modeBarButtonsToRemove': ['hoverCompareCartesian', 'select2d', 'lasso2d'],
#                 'doubleClick': 'reset+autosize', 'toImageButtonOptions': {'height': None, 'width': None, },
#                 'displaylogo': False}

window = 14
resolution = 7

url_base = 'https://data.pmel.noaa.gov/engineering/erddap/tabledap/prawler_TELONAS2.csv'

#data = pd.read_csv(url_base + ".csv", skiprows=[1])
#data = pd.read_csv('https://data.pmel.noaa.gov/engineering/erddap/tabledap/prawler_TELONAS2.csv?&time>=2020-11-09T00:10:00Z&time<=2020-11-23T00:10:00Z', skiprows=[1])
# Need to come up with a way to generate this without the whole dataset
# Maybe from metadata

#vars = {}

# will need to be altered for multi-set displays

# ======================================================================================================================
# helpful functions

# generates ERDDAP compatable date
def gen_erddap_date(edate):
    erdate = (str(edate.year) + "-"
              + str(edate.month).zfill(2) + '-'
              + str(edate.day).zfill(2) + "T"
              + str(edate.hour).zfill(2) + ":"
              + str(edate.minute).zfill(2) + ":"
              + str(edate.second).zfill(2) + "Z")

    return erdate


# generates datetime.datetime object from ERDDAP compatable date
def from_erddap_date(edate):
    redate = datetime.datetime(year=int(edate[:4]),
                               month=int(edate[5:7]),
                               day=int(edate[8:10]),
                               hour=int(edate[11:13]),
                               minute=int(edate[14:16]),
                               second=int(edate[17:19]))

    return redate

# class used for holding useful information about the ERDDAP databases
# ======================================================================================================================

class Dataset:
    logger.info('New dataset initializing')

    def __init__(self, url, window, resolution):
        self.url = url
        self.t_start, self.t_end = self.data_dates()
        logger.info('Start and ending dates calculated')
        logger.info(str(self.t_start))
        logger.info(str(self.t_end))
        self.win_size = window
        self.resolution = resolution
        self.windows = self.gen_windows()
        self.dates = list(self.windows.keys())
        logger.info('Windows calculated')
        self.display_dates = dict(zip(range(len(self.dates)), self.dates))
        logger.info('Dates calculated')

    def data_dates(self):
        page = (requests.get(self.url[:-3] + "das")).text

        indx = page.find('Float64 actual_range')
        mdx = page.find(',', indx)
        endx = page.find(";", mdx)
        start_time = datetime.datetime.utcfromtimestamp(float(page[(indx + 21):mdx]))
        end_time = datetime.datetime.utcfromtimestamp(float(page[(mdx + 2):endx]))

        return start_time, end_time


    def gen_url(self):
        self.base = self.url + "?&time>=" + gen_erddap_date(self.t_start) + '&' + gen_erddap_date(
            self.t_start - datetime.timedelta(days=self.win_size))

        return self.base


    def latest_data(self, win_size):

        self.last_date = self.t_end - datetime.timedelta(days=self.win_size)

        if self.last_date < self.t_start:
            self.last_date = self.t_start
        else:
            self.last_date = gen_erddap_date(self.last_date)

        return self.last_date


    # generate sets of start and stop dates for the windows
    def gen_windows(self):
        self.windows = {}

        # snapshots are the number of windows we will need to cover the entire dataset

        snapshots = round((self.t_end - self.t_start).days / self.resolution) + 1

        # the first date is special as it will be from an odd start time

        t_date = str(self.t_start.year) + "-" + str(self.t_start.month).zfill(2) + '-' + str(self.t_start.day).zfill(2)
        t_url = self.url + "?&time>=" + gen_erddap_date(self.t_start) + '&time<=' + gen_erddap_date(
            self.t_start + datetime.timedelta(days=self.win_size))
        t0 = self.t_end - datetime.timedelta(snapshots * self.resolution)

        self.windows = {t_date: t_url}

        for n in range(snapshots):

            nstart = t0 + datetime.timedelta(days=self.resolution * n)
            t_date = str(nstart.year) + "-" + str(nstart.month).zfill(2) + '-' + str(nstart.day).zfill(2)
            t_url = self.url + "?&time>=" + gen_erddap_date(nstart) + '&time<=' + gen_erddap_date(
                nstart + datetime.timedelta(days=self.win_size))

            self.windows[t_date] = t_url

        return self.windows

    def get_data(self, date_bin):

        data = pd.read_csv(self.windows[self.dates[date_bin]], skiprows=[1])

        skipvars = ['time', 'Time', 'TIME']

        # for set in list(data.keys()):
        var_list = []
        for var in list(data.columns):
            if var in skipvars:
                continue

            var_list.append({'label': var, 'value': var})

        vars = {'sci': var_list}

        return data, vars

#windows = gen_windows(url_base, 14, 7)
#dates = list(windows.keys())
# because Plotly desires dictionaries in everything, here's a dictionary
# if it's stupid and it works, it's not stupid
#display_dates = dict(zip(range(len(dates)), dates))
#data = pd.read_csv(windows[dates[-1]], skiprows=[1])

base_set = Dataset(url_base, window, resolution)

data, vars = base_set.get_data(-1)
external_stylesheets = ['https://codepen.io./chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div([
        html.Label(['Science Load']),
        ddk.Card(width=100,
                 children=[dcc.Loading(id='sci_loader', children=
                     ddk.Graph(id='sci-graphic',
                                     figure=px.scatter(data,
                                                       y=data['SB_Depth'],
                                                       x=data['time']
                                                      )
                                     ))],
                 )
    ]),
    html.Div([
        html.Label(['Scientific Data']),
        dcc.Dropdown(
            id="select_sci",
            options=vars['sci'],
            value=vars['sci'][0]['value']
            #multi=True
        ),
        dcc.Slider(
            id='sci_range',
            min=0,
            max=len(base_set.dates),
            marks=base_set.display_dates,
            value=len(base_set.dates)-1
        )

    ])
])

#scientific data selection
@app.callback(
    [Output('sci-graphic', 'figure'),
    Output('select_sci', 'options')],
    [Input('sci_range', 'value'),
    Input('select_sci', 'value')])
def plot_svar(sci_range, select_sci):

    new_url = base_set.windows[base_set.display_dates[sci_range]]
    new_data, vars = base_set.get_data(sci_range)
    sfig = px.scatter(new_data, y=select_sci, x='time')

    sfig.update_layout()

    return sfig, vars['sci']



if __name__ == '__main__':
    #app.run_server(host='0.0.0.0', port=8050, debug=True)
    app.run_server(debug=True)