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

class current_data:
    def __init__(self, url):
        self.url = url
        self.eng_data = self.get_rudics_data()
        self.eng_data = self.preprocessing()
        self.err_state, self.fail_state = self.secondary_calcs()
        self.vars = self.gen_vars()


    def get_rudics_data(self):
        self.eng_data = pd.DataFrame([])
        datasets = gen_urls(self.url)
        start = ''

        for set in datasets:

            cur_set = self.url + '//' + set
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
                            self.eng_data = self.eng_data.append(pd.DataFrame([elems], columns=header))

        return self.eng_data

    def preprocessing(self):

        non_int_sets = []

        for col in list(self.eng_data.columns):

            try:
                self.eng_data.loc[:, col] = self.eng_data.loc[:, col].astype('int')
            except ValueError:
                non_int_sets.append(col)

        self.eng_data.loc[:, 'datetime'] = pd.to_datetime(self.eng_data.loc[:, 'DT'].apply(from_erddap_date))
        self.eng_data.loc[:, 'tdiff'] = self.eng_data.loc[:, 'datetime'].diff()

        for col in int_indx:

            self.eng_data[col] = self.eng_data[col].astype('int')

        return self.eng_data

    def secondary_calcs(self):
        '''
        Calculating Extra Variables:
        Better Datetimes
        Time Differentials
        Time to Error
        Time to Failure
        '''

        self.fail_state = self.eng_data[self.eng_data['DD'] == 'F']

        if not self.fail_state.empty:
        #     self.fail_state = False
        # else:
           self.fail_state.loc[:, 'tdiff'] = self.fail_state.loc[:, 'datetime'].diff()

        self.error_state = self.eng_data[self.eng_data.loc[:, 'EC'].diff() != 0]

        if not self.error_state.empty:
        #     self.error_state = False
        # else:
            self.error_state.loc[:, 'tdiff'] = self.error_state.loc[:, 'datetime'].diff()

        return self.error_state, self.fail_state

    def gen_vars(self):

        self.vars = []

        if not self.fail_state.empty:
            self.vars.append({'label': 'Failures', 'value': 'DD'})
            self.vars.append({'label': 'Time to Failure', 'value': 'TtFail'})

        if not self.error_state.empty:
            self.vars.append({'label': 'Errors', 'value': 'EC'})
            self.vars.append({'label': 'Time to Error', 'value': 'TtErr'})

        return self.vars


external_stylesheets = ['https://codepen.io./chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__)

cur_set = current_data(base_url[0])
data = cur_set.eng_data
var_list = cur_set.vars

app.layout = dhtml.Div([
    dhtml.Div([
        dhtml.Label(['Science Load']),
        ddk.Card(width=100,
                 children=[ddk.Graph(id='eng-graphic'#,
                                     # figure=px.scatter(data,
                                     #                   x='datetime',
                                     #                   y='EC')
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
            value=var_list[0]['value']
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
    # plotly doesn't let you change data from the outside scope, so we have to reload every time

    cur_set = current_data(select_set)
    data = cur_set.eng_data

    if select_var == 'TtFail':
        figure = px.scatter(cur_set.fail_state,
                            y=cur_set.fail_state.loc[:, 'tdiff'].astype('timedelta64[m]'),
                            x=cur_set.fail_state.loc[:, 'datetime'],
                            )
        figure.update_layout(
                            xaxis_title = "Time to Failure (minutes)",
                            yaxis_title = "Date"
                            )
    elif select_var == 'TtErr':
        figure = px.scatter(cur_set.err_state,
                            y=cur_set.err_state.loc[:, 'tdiff'].astype('timedelta64[m]'),
                            x=cur_set.err_state.loc[:, 'datetime'])
        figure.update_layout(
                            yaxis_title = "Time to Error (minutes)",
                            xaxis_title = "Date"
                            )
    elif select_var == 'EC':
        figure = px.scatter(cur_set.eng_data,
                            y=cur_set.eng_data.loc[:, select_var],
                            x=cur_set.eng_data.loc[:, 'datetime']
                            )
        figure.update_layout(xaxis_title = "Date",
                             yaxis_title = 'Error #')
    elif select_var == 'DD':
        figure = px.scatter(cur_set.eng_data,
                            y=cur_set.eng_data.loc[:, select_var],
                            x=cur_set.eng_data.loc[:, 'datetime']
                            )
        figure.update_layout(xaxis_title = "Date",
                             yaxis_title = 'Failure')


    return figure, cur_set.vars

if __name__ == '__main__':
    #app.run_server(host='0.0.0.0', port=8050, debug=True)

    app.run_server(debug=True)