import dash
import dash_design_kit as ddk  # Only available on Dash Enterprise
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import dash_html_components as html

# it has to be a list of dicts, which is one of the more annoying results I've found
# datasets = [
#     {'label': 'TELON1', 'value': 'https://data.pmel.noaa.gov/engineering/erddap/tabledap/prawler_TELON001.csv'},
#     {'label': 'TELONAS2 Barometric', 'value': 'https://data.pmel.noaa.gov/engineering/erddap/tabledap/prawler_baro_TELONAS2.csv'},
#     {'label': 'TELONAS2 General', 'value': 'https://data.pmel.noaa.gov/engineering/erddap/tabledap/prawler_TELONAS2.csv'},
#     {'label': 'TELONAS2 Engineering', 'value': 'https://data.pmel.noaa.gov/engineering/erddap/tabledap/prawler_eng_TELONAS2.csv'},
#     {'label': 'TELONAS2 Load', 'value': 'https://data.pmel.noaa.gov/engineering/erddap/tabledap/prawler_load_TELONAS2.csv'}
# ]
#
# datasets = [
#     {'label': 'TELON1', 'value': 'https://data.pmel.noaa.gov/engineering/erddap/tabledap/prawler_TELON001.csv'},
#     {'label': 'TELONAS2 Barometric', 'value': 'https://data.pmel.noaa.gov/engineering/erddap/tabledap/prawler_baro_TELONAS2.csv'},
#     {'label': 'TELONAS2 General', 'value': 'https://data.pmel.noaa.gov/engineering/erddap/tabledap/prawler_TELONAS2.csv'},
#     {'label': 'TELONAS2 Engineering', 'value': 'https://data.pmel.noaa.gov/engineering/erddap/tabledap/prawler_eng_TELONAS2.csv'},
#     {'label': 'TELONAS2 Load', 'value': 'https://data.pmel.noaa.gov/engineering/erddap/tabledap/prawler_load_TELONAS2.csv'}
# ]

# data = {
#     'baro' : pd.read_csv('http://redwing:8080/erddap/tabledap/TELOM200_BARO.csv', skiprows=[1]),
#     'gps' : pd.read_csv('http://redwing:8080/erddap/tabledap/TELOM200_GPS_M200.csv', skiprows=[1]),
#     'eng' : pd.read_csv('http://redwing:8080/erddap/tabledap/TELOM200_PRAWE_M200.csv', skiprows=[1]),
#     'sci' : pd.read_csv('http://redwing:8080/erddap/tabledap/TELOM200_PRAWC_M200.csv', skiprows=[1]),
#     'wind' : pd.read_csv('http://redwing:8080/erddap/tabledap/TELOM200_WIND.csv', skiprows=[1])
# }

#df = pd.read_csv('https://plotly.github.io/datasets/country_indicators.csv')
#df = pd.read_csv(datasets[['TELONAS2 General']])

#available_indicators = df['Indicator Name'].unique()
#vailable_variables = df.columnns

vars = {}
skipvars = ['time', 'Time']

for set in list(data.keys()):
    var_list = []
    for var in list(data[set].columns):
        if var in skipvars:
            continue

        var_list.append({'label': var, 'value': var})

    vars[set] = var_list

external_stylesheets = ['https://codepen.io./chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__)

app.layout = html.Div([
    #Baro
    html.Div([
        html.Label(['Barometric Pressure']),
        ddk.Card(width=100,
                 children=[ddk.Graph(id='baro-graphic',
                                     figure=px.scatter(data['baro'],
                                                         y=data['baro']['BaroPres'],
                                                         x=data['baro']['time']
                                                        )
                                    )],
                 )
            ]),
    html.Div([
        #html.H3('Column 1'),
        html.Label(['Scientific Data']),
        dcc.Dropdown(
            id="select_sci",
            options=vars['sci'],
            value=vars['sci'][0]['value']
            #multi=True
        ),
        ddk.Card(width=100,
                 children=[ddk.Graph(id='sci-graphic')],
                 ),
        html.Label(['Wind Data']),
        dcc.Dropdown(
            id="select_wind",
            options=vars['wind'],
            value=vars['wind'][0]['value']
            #multi=True
        ),
        ddk.Card(width=100,
                 children=[ddk.Graph(id='wind-graphic')],
                 )
    ]),
    html.Div([
        #html.H3('Column 2'),
        html.Label(['GPS Data']),
        dcc.Dropdown(
            id="select_gps",
            options=vars['gps'],
            value=vars['gps'][0]['value']
            #multi=True
        ),
        ddk.Card(width=100,
                 children=[ddk.Graph(id='gps-graphic')],
                 ),
        html.Label(['Engineering Data']),
        dcc.Dropdown(
            id="select_eng",
            options=vars['eng'],
            value=vars['eng'][0]['value']
            #multi=True
        ),
        ddk.Card(width=100,
                 children=[ddk.Graph(id='eng-graphic')],
                 )
    ])
])

#scientific
@app.callback(
    Output('sci-graphic', 'figure'),
    Input('select_sci', 'value'))
def plot_svar(select_sci):
    sfig = px.scatter(data['sci'], y=select_sci, x='time')

    return sfig

#wind
@app.callback(
    Output('wind-graphic', 'figure'),
    Input('select_wind', 'value'))
def plot_wvar(select_wind):
    wfig = px.scatter(data['wind'], y=select_wind, x='time')

    return wfig

#gps
@app.callback(
    Output('gps-graphic', 'figure'),
    Input('select_gps', 'value'))
def plot_gvar(select_gps):
    gfig = px.scatter(data['gps'], y=select_gps, x='Time')

    return gfig

#engineering
@app.callback(
    Output('eng-graphic', 'figure'),
    Input('select_eng', 'value'))
def plot_evar(select_eng):
    efig = px.scatter(data['eng'], y=select_eng, x='time')

    return efig



if __name__ == '__main__':
    app.run_server(debug=True)