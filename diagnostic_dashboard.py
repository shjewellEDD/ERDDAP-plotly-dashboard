'''
TODO:
    Come up with a system to display failures
    Mean time to
        Error
        Failure
    Show as a table
'''

import dash
import dash_design_kit as ddk  # Only available on Dash Enterprise
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import dash_html_components as dhtml
from lxml import html
import time
import calendar
from datetime import datetime
import requests
import datetime


'''
DATA EXAMPLE
DT,                   MM,  DD,PN, SR, IR, UL,  LL,  IP,  ET,    TS,    EC,    VM,   PT,   WD, TM,CM,CL
2021-08-06T19:42:31Z, 000, D, 08, 08, 15, 004, 045, 250, 02500, 00094, 00001, 0636, 0000, 0,  0, 0, 0
'''

int_indx = ['MM', 'PN', 'SR', 'IR', 'UL',  'LL', 'IP', 'ET', 'TS', 'EC', 'VM', 'PT', 'WD', 'TM', 'CM', 'CL']

# user inputs
base_url = ['http://eclipse.pmel.noaa.gov/rudics/TELO/RM12/',
            'http://eclipse.pmel.noaa.gov/rudics/TELO/RC12/',
            'http://eclipse.pmel.noaa.gov/rudics/TELO/RC02/'
            ]

prawlers = [{'label':   'RM12', 'value':    'http://eclipse.pmel.noaa.gov/rudics/TELO/RM12/'},
            {'label':   'RC02', 'value':    'http://eclipse.pmel.noaa.gov/rudics/TELO/RC02/'},
            {'label':   'RC12', 'value':    'http://eclipse.pmel.noaa.gov/rudics/TELO/RC12/'}]

rudic_sets = {'RM12':   'http://eclipse.pmel.noaa.gov/rudics/TELO/RM12/',
              'RC02':   'http://eclipse.pmel.noaa.gov/rudics/TELO/RC02/',
              'RC12':   'http://eclipse.pmel.noaa.gov/rudics/TELO/RC12/'}


def gen_urls(base):

    r = requests.get(base)
    webpage = html.fromstring(r.content)
    links = webpage.xpath('//a/@href')

    return links[5:]

# generates datetime.datetime object from ERDDAP compatable date
def from_erddap_date(edate):
    redate = datetime.datetime(year=int(edate[:4]),
                               month=int(edate[5:7]),
                               day=int(edate[8:10]),
                               hour=int(edate[11:13]),
                               minute=int(edate[14:16]),
                               second=int(edate[17:19]))

    return redate


def gen_dataset(url):
    datasets = gen_urls(url)
    start = ''
    eng_data = pd.DataFrame()

    for set in datasets:

        cur_set = url + '//' + set
        # set_n = set_n + 1

        r = requests.get(cur_set)
        # content = str(r.content).split('\\n')
        content = str(r.content).split('%%')

        for sect in content:

            if "PRAWE" in sect:

                block = sect.split('\\r\\n')
                header = block[1].split(',')

                for line in block:

                    if 'Z' in line:
                        elems = line.split(',')
                        eng_data = eng_data.append(pd.DataFrame([elems], columns=header))



    # for col in int_indx:
    #     #
    #     #     eng_data[col] = eng_data[col].astype('int')

    non_int_sets = []

    for col in list(eng_data.columns):

        try:
            eng_data.loc[:, col] = eng_data.loc[:, col].astype('int')
        except ValueError:
            non_int_sets.append(col)

    eng_data.loc[:, 'datetime'] = pd.to_datetime(eng_data.loc[:, 'DT'].apply(from_erddap_date))
    eng_data.loc[:, 'tdiff'] = eng_data.loc[:, 'datetime'].diff()

    return eng_data


def gen_vars(data):
    vars = []
    for var in list(data.columns):

        if var == 'DT':
            continue

        vars.append({'label': var, 'value': var})

    return vars

external_stylesheets = ['https://codepen.io./chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__)

data = gen_dataset(base_url[0])
var_list = gen_vars(data)

app.layout = dhtml.Div([
    dhtml.Div([
        dhtml.Label(['Science Load']),
        ddk.Card(width=100,
                 children=[ddk.Graph(id='eng-graphic',
                                     figure=px.scatter(data,
                                                       x='datetime',
                                                       y='EC')
                                     )
                          ],
                 )
    ]),
    dhtml.Div([
        dhtml.Label(['Diagnostic Data']),
        dcc.Dropdown(
            id="select_set",
            options=prawlers,
            value=prawlers[0]['value']
            #multi=True
        ),
        dhtml.Label(['Engineering Variables']),
        dcc.Dropdown(
            id="select_var",
            options=var_list,
            value='datetime'
        )

    ])
])

# scientific data selection
@app.callback(
    [Output('eng-graphic', 'figure'),
     Output('select_var', 'options')],
    [Input('select_set', 'value'),
     Input('select_var', 'value')
     ])

def plot_diag(select_set, select_var):

    data = gen_dataset(select_set)
    var_list = gen_vars(data)

    figure = px.scatter(data,
                        y=data.loc[:, select_var],
                        x=data.loc[:, 'datetime']
                        )

    #figure = px.plot(data, y=data['EC'])

    figure.update_layout()

    return figure, var_list

if __name__ == '__main__':
    #app.run_server(host='0.0.0.0', port=8050, debug=True)
    app.run_server(debug=True)