


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
filehandler_dbg = logging.FileHandler(logger.name, mode='w')

graph_config = {'modeBarButtonsToRemove': ['hoverCompareCartesian', 'select2d', 'lasso2d'],
                'doubleClick': 'reset+autosize', 'toImageButtonOptions': {'height': None, 'width': None, },
                'displaylogo': False}

window = 14
resolution = 7

set_meta = {'TELONAS2':
                {'url': 'https://data.pmel.noaa.gov/engineering/erddap/tabledap/prawler_TELONAS2.csv',
                 'win': 14,
                 'res': 7
                 },
            'Load':
                {'url': 'https://data.pmel.noaa.gov/engineering/erddap/tabledap/prawler_load_TELONAS2.csv',
                 'win': 14,
                 'res': 7
                 },
            'Baro':
                {'url': 'https://data.pmel.noaa.gov/engineering/erddap/tabledap/prawler_baro_TELONAS2.csv',
                 'win': 14,
                 'res': 7
                 }
            }

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
        logger.info([str(self.t_start), str(self.t_end)])
        self.win_size = window
        self.resolution = resolution
        self.windows = self.gen_windows()
        self.dates = list(self.windows.keys())
        logger.info('Windows calculated')
        self.display_dates = dict(zip(range(len(self.dates)), sorted(self.dates)))
        logger.info('Dates calculated')
        logger.info(self.dates)
        self.data, self.vars = self.get_data(-1)

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

        self.data = pd.read_csv(self.windows[self.dates[date_bin]], skiprows=[1])

        skipvars = ['time', 'Time', 'TIME']

        # for set in list(data.keys()):
        self.vars = []
        for var in list(self.data.columns):
            if var in skipvars:
                continue

            self.vars.append({'label': var, 'value': var})

        return self.data, self.vars

    def ret_data(self):

        return self.data

    def ret_vars(self):

        return self.vars



sci_set = Dataset(set_meta['TELONAS2']['url'], set_meta['TELONAS2']['win'], set_meta['TELONAS2']['res'])
eng_set = Dataset(set_meta['Load']['url'], set_meta['Load']['win'], set_meta['Load']['res'])
baro_set = Dataset(set_meta['Baro']['url'], set_meta['Baro']['win'], set_meta['Baro']['res'])

external_stylesheets = ['https://codepen.io./chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div([
        html.Label(['Science Load']),
        ddk.Card(width=100,
                 children=[dcc.Loading(id='sci_loader', children=
                     ddk.Graph(id='sci-graphic',
                                     figure=px.scatter(sci_set.ret_data(),
                                                       y=sci_set.ret_data()[sci_set.ret_vars()[0]['value']],
                                                       x=sci_set.ret_data()['time']
                                                      )
                                     )
                                )],
                 )
    ]),
    html.Div([
        html.Label(['Scientific Data']),
        dcc.Dropdown(
            id="select_sci",
            options=sci_set.ret_vars(),
            value=sci_set.ret_vars()[0]['value']
            #multi=True
        ),
        dcc.Slider(
            id='sci_range',
            min=0,
            max=len(sci_set.dates[-1]),
            marks=sci_set.display_dates,
            value=len(sci_set.dates)-1
        )
    ]),
    html.Div([
        html.Label(['Engineering Load']),
        ddk.Card(width=100,
                 children=[dcc.Loading(id='eng_loader', children=
                 ddk.Graph(id='eng-graphic',
                           figure=px.scatter(eng_set.ret_data(),
                                             y=eng_set.ret_data()[eng_set.ret_vars()[0]['value']],
                                             x=eng_set.ret_data()['time']
                                             )
                           )
                                       )],
                 )
    ]),
    html.Div([
        html.Label(['Engineering Data']),
        dcc.Dropdown(
            id="select_eng",
            options=eng_set.ret_vars(),
            value=eng_set.ret_vars()[0]['value']
            # multi=True
        ),
        dcc.Slider(
            id='eng_range',
            min=0,
            max=len(eng_set.dates[-1]),
            marks=eng_set.display_dates,
            value=len(eng_set.dates)-1
        )

    ]),
    html.Div([
        html.Label(['Baro Load']),
        ddk.Card(width=100,
                 children=[dcc.Loading(id='baro_loader', children=
                 ddk.Graph(id='baro-graphic',
                           figure=px.scatter(baro_set.ret_data(),
                                             y=baro_set.ret_data()[baro_set.ret_vars()[0]['value']],
                                             x=baro_set.ret_data()['time']
                                             )
                           )
                                       )],
                 )
    ]),
    html.Div([
        html.Label(['Baro Data']),
        dcc.Dropdown(
            id="select_baro",
            options=baro_set.ret_vars(),
            value=baro_set.ret_vars()[0]['value']
            # multi=True
        ),
        dcc.Slider(
            id='baro_range',
            min=0,
            max=len(baro_set.dates[-1]),
            marks=baro_set.display_dates,
            value=len(baro_set.dates) - 1
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

    new_data, vars = sci_set.get_data(sci_range)
    sfig = px.scatter(new_data, y=new_data[select_sci], x=new_data['time'])

    sfig.update_layout()

    return sfig, vars

#engineering data selection
@app.callback(
    [Output('eng-graphic', 'figure'),
    Output('select_eng', 'options')],
    [Input('eng_range', 'value'),
    Input('select_eng', 'value')])
def plot_svar(eng_range, select_eng):

    new_data, vars = eng_set.get_data(eng_range)
    efig = px.scatter(new_data, y=new_data[select_eng], x=new_data['time'])

    efig.update_layout()

    return efig, vars

#engineering data selection
@app.callback(
    [Output('baro-graphic', 'figure'),
    Output('select_baro', 'options')],
    [Input('baro_range', 'value'),
    Input('select_baro', 'value')])
def plot_svar(baro_range, select_baro):

    new_data, vars = baro_set.get_data(baro_range)
    efig = px.scatter(new_data, y=new_data[select_baro], x=new_data['time'])

    efig.update_layout()

    return efig, vars




if __name__ == '__main__':
    #app.run_server(host='0.0.0.0', port=8050, debug=True)
    app.run_server(debug=True)