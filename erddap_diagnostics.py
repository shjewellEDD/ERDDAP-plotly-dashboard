'''
TODO:
    Dataset.get_data() is being called repeatedly for each pass. Why?
'''

import dash
import dash_design_kit as ddk  # Only available on Dash Enterprise
import dash_core_components as dcc
from dash.dependencies import Input, Output
import dash_table
import plotly.express as px
import dash_html_components as dhtml

#non-plotly imports
import pandas as pd
from lxml import html
import datetime
from datetime import date
import requests
import io
import urllib

#import logging

#logging.basicConfig(filename='dash_log.log', encoding='utf-8', level=logging.DEBUG)
#logger = logging.getLogger('debug_logger')
#filehandler_dbg = logging.FileHandler(logger.name, mode='w')

prawlers = [
            {'label':   'TELONAS2', 'value': 'https://data.pmel.noaa.gov/engineering/erddap/tabledap/prawler_eng_TELONAS2.csv'},
            {'label':   'M200', 'value': 'http://redwing:8080/erddap/tabledap/TELOM200_PRAWE_M200.csv'},
            {'label':   'MCL0', 'value': 'http://redwing:8080/erddap/tabledap/TELOMCL0_PRAWE_MCL0.csv'}
            ]

dataset_dict = {
            'TELONAS2': 'https://data.pmel.noaa.gov/engineering/erddap/tabledap/prawler_eng_TELONAS2.csv',
            'M200': 'http://redwing:8080/erddap/tabledap/TELOM200_PRAWE_M200.csv',
            'MCL0': 'http://redwing:8080/erddap/tabledap/TELOMCL0_PRAWE_MCL0.csv'
            }
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
                 },
            'Eng':
                {'url': 'https://data.pmel.noaa.gov/engineering/erddap/tabledap/prawler_eng_TELONAS2.csv',
                 'win': 14,
                 'res': 7}
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
    #dataset object,
    #it takes requested data and generates windows and corresponding urls
    #logger.info('New dataset initializing')

    def __init__(self, url, window_start=False, window_end=False):
        self.url = url
        self.t_start, self.t_end = self.data_dates()
        if window_start:
            self.w_start = window_start
            self.w_end = window_end
        else:
            self.w_end = self.t_end
            self.w_start = self.t_end - datetime.timedelta(days=7)
        self.data, self.vars = self.get_data()

    #opens metadata page and returns start and end datestamps
    def data_dates(self):
        page = (requests.get(self.url[:-3] + "das")).text

        indx = page.find('Float64 actual_range')
        mdx = page.find(',', indx)
        endx = page.find(";", mdx)
        start_time = datetime.datetime.utcfromtimestamp(float(page[(indx + 21):mdx]))
        end_time = datetime.datetime.utcfromtimestamp(float(page[(mdx + 2):endx]))

        return start_time, end_time

    def gen_url(self, data_start, data_end):
        if type(data_start) == type('string'):
            self.base = self.url + "?&time>=" + data_start + 'Z&time<=' + data_end + 'Z'
        else:
            self.base = self.url + "?&time>=" + gen_erddap_date(data_start) + '&time<=' + gen_erddap_date(data_end)

        return self.base


    def get_data(self):

        #self.data = pd.read_csv(self.windows[self.dates[date_bin]], skiprows=[1])

        print(self.gen_url(self.w_start, self.w_end))

        try:
            self.data = pd.read_csv(self.gen_url(self.w_start, self.w_end), skiprows=[1])
        except urllib.error.HTTPError:
            self.base = requests.get(self.gen_url(self.w_start, self.w_end))
            self.data = pd.read_csv(io.StringIO(self.gen_url(self.w_start, self.w_end)), skiprows=[1])


        skipvars = ['time', 'Time', 'TIME', 'latitude', 'longitude']

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

    def ret_times(self):
        return self.w_start, self.w_end



# sci_set = Dataset(set_meta['TELONAS2']['url'])
# load_set = Dataset(set_meta['Load']['url'])
# baro_set = Dataset(set_meta['Baro']['url'])
eng_set = Dataset(set_meta['Eng']['url'])
eng_data = eng_set.ret_data()
eng_vars = eng_set.ret_vars()
eng_start, eng_end = eng_set.ret_times()

graph_height = 300

graph_config = {'modeBarButtonsToRemove' : ['hoverCompareCartesian','select2d', 'lasso2d'],
                'doubleClick':  'reset+autosize', 'toImageButtonOptions': { 'height': None, 'width': None, },
                'displaylogo': False}

colors = {'background': '#111111', 'text': '#7FDBFF'}

external_stylesheets = ['https://codepen.io./chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__)

app.layout = ddk.App([
    ddk.Header([
        ddk.Logo(src=app.get_asset_url('logo.png'), style={
            'max-height': 100,
            'width': 'auto'
        }),
        ddk.Title('Prawler Engineering Diagnostic Dashboard'),
        ddk.SectionTitle('', id='final_date'),
        dhtml.Button('Refresh', style={'float': 'right'}, id='refresh', n_clicks=0),
    ]),
dhtml.Div(style={'backgroundColor': colors['background']},
          children=[
    dhtml.Div(style={'backgroundColor': colors['background']},
              children=[
        ddk.Card(width=66,
                 style={'backgroundColor': colors['background']},
                 children=[dcc.Loading(id='load_loader',
                                 children=[ddk.Graph(id='eng-graphic',)]
                                       ),
                            dhtml.Label(['Prawler ID']),
                            dcc.DatePickerRange(
                                id='date-picker',
                                style={'backgroundColor': colors['background']},
                                min_date_allowed=eng_set.t_start.date(),
                                max_date_allowed=eng_set.t_end.date(),
                                start_date=(eng_set.t_end - datetime.timedelta(days=7)).date(),
                                end_date=eng_set.t_end.date()
                           ),
                            dcc.Dropdown(
                                id="select_eng",
                                style={'backgroundColor': colors['background']},
                                options=prawlers,
                                value=prawlers[0]['value'],
                                clearable=False
                            ),
                            dhtml.Label(['Engineering Variables']),
                            dcc.Dropdown(
                                id="select_var",
                                style={'backgroundColor': colors['background'],
                                       'textColor': colors['text']},
                                options=eng_set.ret_vars(),
                                value=eng_set.ret_vars()[0]['value'],
                                clearable=False
                            ),
                ],
            ),
        ddk.Card(width=34,
                 style={'backgroundColor': colors['background']},
                 children=[dcc.Textarea(id='t_mean',
                                        value='',
                                        style={'width': '100%', 'height': 40,
                                               'backgroundColor': colors['background']},
                                        ),
                            dash_table.DataTable(id='table',
                                                 style_table={'backgroundColor': colors['background']},
                                                 style_cell={'backgroundColor': colors['background']})
                           ])
    ]),
    ddk.Card(children=[
        ddk.Block(width=6, children=
        [
            dhtml.Img(src='https://www.pmel.noaa.gov/sites/default/files/PMEL-meatball-logo-sm.png', height=100,
                     width=100),

        ]),
        ddk.Block(width=90, children=[
            dhtml.Div(children=[
                dcc.Link('National Oceanic and Atmospheric Administration', href='https://www.noaa.gov/'),
            ]),
            dhtml.Div(children=[
                dcc.Link('Pacific Marine Environmental Laboratory  |', href='https://www.pmel.noaa.gov/'),
                dcc.Link('  Engineering', href='https://www.pmel.noaa.gov/edd/')
            ]),
            dhtml.Div(children=[
                dcc.Link('oar.pmel.edd-webmaster@noaa.gov', href='mailto:oar.pmel.edd-webmaster@noaa.gov')
            ]),
            dhtml.Div(children=[
                dcc.Link('DOC |', href='https://www.commerce.gov/'),
                dcc.Link(' NOAA |', href='https://www.noaa.gov/'),
                dcc.Link(' OAR |', href='https://www.research.noaa.gov/'),
                dcc.Link(' PMEL |', href='https://www.pmel.noaa.gov/'),
                dcc.Link(' Privacy Policy |', href='https://www.noaa.gov/disclaimer'),
                dcc.Link(' Disclaimer |', href='https://www.noaa.gov/disclaimer'),
                dcc.Link(' Accessibility', href='https://www.pmel.noaa.gov/accessibility')
            ])
        ])
    ])
])

])

'''
========================================================================================================================
Callbacks
'''

#engineering data selection
@app.callback(
    [Output('eng-graphic', 'figure'),
     Output('select_var', 'options'),
     Output('table', 'data'),
     Output('table', 'columns'),
     Output('t_mean', 'value')],
    [Input('select_eng', 'value'),
     Input('select_var', 'value'),
     Input('date-picker', 'start_date'),
     Input('date-picker', 'end_date')])

def plot_evar(dataset, select_var, start_date, end_date):

    eng_set = Dataset(dataset, start_date, end_date)
    new_data = eng_set.ret_data()
    vars = eng_set.ret_vars()
    t_mean = ''

    efig = px.scatter(new_data, y=select_var, x='time')

    columns = [{"name": 'Date', "id": 'time'},
               {'name': select_var, 'id': select_var}]

    try:
        table_data = new_data.to_dict('records')
    except TypeError:
        table_data = new_data.to_dict()

    efig.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text']
    )

    return efig, vars, table_data, columns, t_mean


if __name__ == '__main__':
    #app.run_server(host='0.0.0.0', port=8050, debug=True)
    app.run_server(debug=True)