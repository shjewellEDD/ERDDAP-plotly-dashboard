'''
TODO:
    Make labels human readable
    Better plotting system, or at least a skiplist instead of if/then
    Read in Seabird depth from the prawxxx data
'''

import dash
import dash_table
import dash_design_kit as ddk  # Only available on Dash Enterprise
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.io as pio
import dash_html_components as dhtml

import pandas as pd
from lxml import html
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
            'http://eclipse.pmel.noaa.gov/rudics/TELO/RC02/'#,
            #'https://data.pmel.noaa.gov/engineering/erddap/tabledap/prawler_eng_TELONAS2.csv'
            ]

prawlers = [{'label':   'RM12', 'value':    'http://eclipse.pmel.noaa.gov/rudics/TELO/RM12/'},
            {'label':   'RC02', 'value':    'http://eclipse.pmel.noaa.gov/rudics/TELO/RC02/'},
            {'label':   'RC12', 'value':    'http://eclipse.pmel.noaa.gov/rudics/TELO/RC12/'}#,
            #{'label':   'TELONAS2', 'value': 'https://data.pmel.noaa.gov/engineering/erddap/tabledap/prawler_eng_TELONAS2.csv'}
            ]

rudic_sets = {'RM12':   'http://eclipse.pmel.noaa.gov/rudics/TELO/RM12/',
              'RC02':   'http://eclipse.pmel.noaa.gov/rudics/TELO/RC02/',
              'RC12':   'http://eclipse.pmel.noaa.gov/rudics/TELO/RC12/',
              #'TELONAS2':   'https://data.pmel.noaa.gov/engineering/erddap/tabledap/prawler_eng_TELONAS2.csv'}
              }

rudics_vars = [
            {'label':   'current location (in meters)', 'value':    'MM'},
            {'label':   'current direction',            'value':    'DD'},
            {'label':   'Error Counter',                'value':    'EC'},
            {'label':   'Error timeout',                'value':    'ET'},
            {'label':   'Trip number',                  'value':    'TS'},
            {'label':   'Vacuum',                       'value':    'VM'},
            {'label':   'Park timer',                   'value':    'PT'},
            {'label':   'Water detection flag',         'value':    'WD'},
            {'label':   'Climb down mode',              'value':    'CM'}
            ]


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
        self.eng_data = self.get_data()
        self.eng_data = self.preprocessing()
        self.err_state, self.fail_state = self.secondary_calcs()
        self.vars = self.gen_vars()

    def get_data(self):

        if 'rudics' in self.url:

            return self.get_rudics_data()

        if 'erddap' in self.url:

            return self.get_erddap_data()

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

    def get_erddap_data(self):

        self.eng_data = pd.read_csv(self.url, skiprows=[1])

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

            self.fail_state.loc[:, 'tdiff'] = (self.fail_state.loc[:, 'datetime'].diff()).astype('timedelta64[m]')
            self.fail_state.loc[:, 'ftrips'] = (self.fail_state.loc[:, 'TS'].diff())
            self.fail_state.loc[:, 'dfx'] = (self.fail_state.loc[:, 'TS'].diff()) * abs(
                self.eng_data.loc[0, 'LL'] - self.eng_data.loc[0, 'UL'])

        self.error_state = self.eng_data[self.eng_data.loc[:, 'EC'].diff() != 0]

        if not self.error_state.empty:

            self.error_state.loc[:, 'tdiff'] = (self.error_state.loc[:, 'datetime'].diff()).astype('timedelta64[m]')
            self.error_state.loc[:, 'etrips'] = (self.error_state.loc[:, 'TS'].diff())
            self.fail_state.loc[:, 'dex'] = (self.fail_state.loc[:, 'TS'].diff()) * abs(
                self.eng_data.loc[0, 'LL'] - self.eng_data.loc[0, 'UL'])


        return self.error_state, self.fail_state

    def gen_vars(self):

        self.vars = rudics_vars

        if not self.fail_state.empty:
            self.vars.append({'label': 'Time to Failure', 'value': 'TtFail'})
            self.vars.append({'label': 'Trips to Failure', 'value': 'ftrips'})
            self.vars.append({'label': 'Distance to Failure', 'value': 'dfx'})


        if not self.error_state.empty:
            self.vars.append({'label': 'Time to Error', 'value': 'TtErr'})
            self.vars.append({'label': 'Trips to Error', 'value': 'etrips'})
            self.vars.append({'label': 'Distance to Error', 'value': 'dex'})

        return self.vars

'''
========================================================================================================================
Dash App
'''

external_stylesheets = ['https://codepen.io./chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__)

cur_set = current_data(base_url[0])
data = cur_set.eng_data
var_list = cur_set.vars

graph_height = 300

graph_config = {'modeBarButtonsToRemove' : ['hoverCompareCartesian','select2d', 'lasso2d'],
                'doubleClick':  'reset+autosize', 'toImageButtonOptions': { 'height': None, 'width': None, },
                'displaylogo': False}

colors = {'background': '#111111','text': '#7FDBFF'}

app.layout = ddk.App([
    ddk.Header([
        ddk.Logo(src=app.get_asset_url('logo.png'), style={
            'max-height':100,
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
                                 children=[ddk.Graph(id='eng-graphic')]
                                       ),
                            dhtml.Label(['Prawler ID']),
                            dcc.Dropdown(
                                id="select_set",
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
                                options=var_list,
                                value=var_list[0]['value'],
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

# scientific data selection
@app.callback(
    [Output('eng-graphic', 'figure'),
     Output('select_var', 'options'),
     Output('table', 'data'),
     Output('table', 'columns'),
     Output('t_mean', 'value')],
    [Input('select_set', 'value'),
     Input('select_var', 'value')
     ])

def plot_diag(select_set, select_var):
    # plotly doesn't let you change data from the outside scope, so we have to reload every time

    cur_set = current_data(select_set)
    data = cur_set.eng_data

    t_mean = ''

    if select_var == 'TtFail':
        figure = px.scatter(cur_set.fail_state,
                            y=cur_set.fail_state.loc[:, 'tdiff'],#.astype('timedelta64[m]'),
                            x=cur_set.fail_state.loc[:, 'datetime']
                            )
        t_mean = 'Mean time to fail: ' + str(round(cur_set.fail_state.loc[:, 'tdiff'].mean())) + ' minutes'
        table_data = cur_set.fail_state.iloc[1:].to_dict('records')
        columns = [{"name": 'Date', "id": 'datetime'},
                   {'name': 'Time to Failure (minutes)', 'id': 'tdiff'}]

        figure.update_layout(
                            xaxis_title = "Time to Failure (minutes)",
                            yaxis_title = "Date",
                            template='plotly_dark'
                            )
    elif select_var == 'TtErr':
        figure = px.scatter(cur_set.err_state,
                            y=cur_set.err_state.loc[:, 'tdiff'],#.astype('timedelta64[m]'),
                            x=cur_set.err_state.loc[:, 'datetime'])
        t_mean = 'Mean time to error: ' + str(round(cur_set.err_state.loc[:, 'tdiff'].mean())) + ' minutes'
        table_data = cur_set.error_state.iloc[1:].to_dict('records')
        columns = [{"name": 'Date', "id": 'datetime'},
                   {'name': 'Time to Error (minutes)', 'id': 'tdiff'}]
        figure.update_layout(
                            yaxis_title="Time to Error (minutes)",
                            xaxis_title="Date",
                            template='plotly_dark'
                            )
    elif select_var == 'EC':
        figure = px.scatter(cur_set.eng_data,
                            y=cur_set.eng_data.loc[:, select_var],
                            x=cur_set.eng_data.loc[:, 'datetime']
                            )
        if not cur_set.err_state.empty:
            t_mean = 'Mean time to error: ' + str(round(cur_set.err_state.loc[:, 'tdiff'].mean())) + ' minutes'
        table_data = cur_set.eng_data.iloc[1:].to_dict('records')
        columns = [{"name": 'Date', "id": 'datetime'},
                   {'name': 'Error Count', 'id': 'EC'}]
        figure.update_layout(xaxis_title = "Date",
                             yaxis_title = 'Error #',
                             template='plotly_dark'
                             )
    elif select_var == 'DD':
        figure = px.scatter(cur_set.eng_data,
                            y=cur_set.eng_data.loc[:, select_var],
                            x=cur_set.eng_data.loc[:, 'datetime']
                            )
        if not cur_set.fail_state.empty:
            t_mean = 'Mean time to fail: ' + str(round(cur_set.fail_state.loc[:, 'tdiff'].mean())) + ' minutes'
        table_data = cur_set.eng_data.to_dict('records')
        columns = [{"name": 'Date', "id": 'datetime'},
                   {'name': 'Direction', 'id': 'DD'}]
        figure.update_layout(xaxis_title="Date",
                             yaxis_title='State',
                             template='plotly_dark'
                             )
    else:
        figure = px.scatter(cur_set.eng_data,
                            y=cur_set.eng_data.loc[:, select_var],
                            x=cur_set.eng_data.loc[:, 'datetime']
                            )
        t_mean = ''
        table_data = cur_set.eng_data.to_dict('records')
        columns = [{"name": 'Date', "id": 'datetime'},
                   {'name': select_var, 'id': select_var}]
        figure.update_layout(xaxis_title="Date",
                             yaxis_title=select_var,
                             template='plotly_dark'
                             )

    figure.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text']
    )

    return figure, cur_set.vars, table_data, columns, t_mean

if __name__ == '__main__':
    #app.run_server(host='0.0.0.0', port=8050, debug=True)
    app.run_server(debug=True)