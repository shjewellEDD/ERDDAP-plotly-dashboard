import dash
import dash_html_components as html
import dash_design_kit as ddk
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input, State
import pandas as pd
import json
from io import StringIO
import csv
import urllib
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px

app = dash.Dash(__name__)
server = app.server  # expose server variable for Procfile

graph_height = 300

graph_config = {'modeBarButtonsToRemove': ['hoverCompareCartesian', 'select2d', 'lasso2d'],
                'doubleClick': 'reset+autosize', 'toImageButtonOptions': {'height': None, 'width': None, },
                'displaylogo': False}

app.layout = ddk.App([
    ddk.Header([
        ddk.Logo(src=app.get_asset_url('logo.png'), style={
            'max-height': 100,
            'width': 'auto'
        }),
        ddk.Title('TELONAS2'),
        ddk.SectionTitle('', id='final_date'),
        html.Button('Refresh', style={'float': 'right'}, id='refresh', n_clicks=0),
    ]),
    ddk.Block(
        children=[
            dcc.Tabs(id='selected-tab', value='load',
                     children=[
                         dcc.Tab(label="Load", value='load',
                                 children=[ddk.Card(width=100,
                                                    children=[
                                                        dcc.Loading(id='load_loader', children=[
                                                            ddk.Graph(id="load_plot", config=graph_config)])
                                                    ]
                                                    )
                                           ]
                                 ),
                         dcc.Tab(label="Profiles", value='profiles',
                                 children=[ddk.Card(width=100,
                                                    children=[
                                                        dcc.Loading(id='profile_loader', children=[
                                                            ddk.Graph(id="profile_plot", config=graph_config)])
                                                    ]
                                                    )
                                           ]
                                 )
                     ]
                     )
        ]
    ),
    ddk.Card(children=[
        ddk.Block(width=6, children=
        [
            html.Img(src='https://www.pmel.noaa.gov/sites/default/files/PMEL-meatball-logo-sm.png', height=100,
                     width=100),

        ]),
        ddk.Block(width=90, children=[
            html.Div(children=[
                dcc.Link('National Oceanic and Atmospheric Administration', href='https://www.noaa.gov/'),
            ]),
            html.Div(children=[
                dcc.Link('Pacific Marine Environmental Laboratory  |', href='https://www.pmel.noaa.gov/'),
                dcc.Link('  Engineering', href='https://www.pmel.noaa.gov/edd/')
            ]),
            html.Div(children=[
                dcc.Link('oar.pmel.edd-webmaster@noaa.gov', href='mailto:oar.pmel.edd-webmaster@noaa.gov')
            ]),
            html.Div(children=[
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


@app.callback(
    [Output('load_plot', 'figure'),
     Output('profile_plot', 'figure'),
     Output('final_date', 'children')
     ],
    [Input('refresh', 'n_clicks'),
     ],
)
def make_graphs(click):
    load_df = pd.read_csv(
        #'https://data.pmel.noaa.gov/engineering/erddap/tabledap/prawler_load_TELONAS2.csv?time%2CAve_Load%2Clatitude%2Clongitude%2Ctimeseries_id%2CStd_Load%2CMin_Load%2CMax_Load%2CLoad_Temp&orderBy(%22time%22)',
        'https://data.pmel.noaa.gov/engineering/erddap/tabledap/prawler_load_TELONAS2.csv',
        skiprows=[1])
    baro_df = pd.read_csv(
        #'https://data.pmel.noaa.gov/engineering/erddap/tabledap/prawler_baro_TELONAS2.csv?time%2CBaroPres%2Clatitude%2Clongitude%2Ctimeseries_id&orderBy(%22time%22)&time>=2020-11-09T00:10:00Z',
        'https://data.pmel.noaa.gov/engineering/erddap/tabledap/prawler_baro_TELONAS2.csv',
        skiprows=[1])

    last_date = load_df["time"].max()
    load_plots_title = 'Load and Baro data through ' + last_date

    ave_figure = go.Scatter(x=load_df['time'], y=load_df['Ave_Load'], name='Ave_Load', hoverinfo='x+y+name')
    max_figure = go.Scatter(x=load_df['time'], y=load_df['Max_Load'], name='Max_Load', hoverinfo='x+y+name')
    min_figure = go.Scatter(x=load_df['time'], y=load_df['Min_Load'], name='Min_Load', hoverinfo='x+y+name')
    std_figure = go.Scatter(x=load_df['time'], y=load_df['Std_Load'], name='Std_Load', hoverinfo='x+y+name')
    tmp_figure = go.Scatter(x=load_df['time'], y=load_df['Load_Temp'], name='Load_Temp', hoverinfo='x+y+name')
    baro_figure = go.Scatter(x=load_df['time'], y=baro_df['BaroPres'], name='BaroPres', hoverinfo='x+y+name')

    load_plots = make_subplots(rows=3, cols=1, shared_xaxes='all',
                               subplot_titles=("TELONAS2 - Load (lbs)",
                                               "TELONAS2 - Load_Temp (℃)",
                                               "TELONAS2 - BaroPres (hPa)"),
                               shared_yaxes=False, vertical_spacing=0.1)

    load_plots.append_trace(ave_figure, 1, 1)
    load_plots.add_trace(max_figure, 1, 1)
    load_plots.add_trace(min_figure, 1, 1)
    load_plots.add_trace(std_figure, 1, 1)
    load_plots.append_trace(tmp_figure, 2, 1)
    load_plots.append_trace(baro_figure, 3, 1)

    load_plots['layout'].update(height=900,
                                title=' ',
                                hovermode='x unified',
                                xaxis_showticklabels=True, xaxis2_showticklabels=True, xaxis3_showticklabels=True,
                                yaxis_fixedrange=True, yaxis2_fixedrange=True, yaxis3_fixedrange=True,
                                yaxis_title='Load', yaxis2_title='Load Temperature', yaxis3_title='Barometric Pressure',
                                showlegend=False, modebar={'orientation': 'h'}, autosize=True)

    df = pd.read_csv(
        #'https://data.pmel.noaa.gov/engineering/erddap/tabledap/prawler_TELONAS2.csv?time%2Cprofile_id%2CSB_Depth%2CSB_Temp%2CSB_Conductivity%2COptode_Temp%2COptode_Dissolved_O2%2Cwetlab_Chlorophyll&time>=max(time)-2days',
        'https://data.pmel.noaa.gov/engineering/erddap/tabledap/prawler_TELONAS2.csv',
        skiprows=[1])
    tmin = df['time'].min()
    tmax = df['time'].max()
    temp = go.Scatter(x=df["time"], y=df["SB_Depth"],
                      marker=dict(showscale=True, color=df["SB_Temp"], colorscale='Viridis', colorbar=dict(x=.46)),
                      mode='markers', name="SB_Temp", text=df["SB_Temp"])
    cond = go.Scatter(x=df["time"], y=df["SB_Depth"],
                      marker=dict(showscale=True, color=df["SB_Conductivity"], colorscale='Inferno'),
                      mode='markers', name="SB_Conductivity", text=df["SB_Conductivity"])
    profile_plots = make_subplots(rows=1, cols=2, shared_xaxes='all',
                                  subplot_titles=("TELONAS2 - SB_Temp (℃)", "TELONAS2 - SB_Conductivity (mS/cm)"))
    profile_plots.add_trace(temp, row=1, col=1)
    profile_plots.add_trace(cond, row=1, col=2)
    profile_plots['layout'].update(height=750,
                                   xaxis_fixedrange=False,
                                   xaxis2_fixedrange=False,
                                   yaxis_fixedrange=True,
                                   yaxis2_fixedrange=True,
                                   yaxis_title='Depth (m)',
                                   yaxis2_title='Depth (m)',
                                   modebar={'orientation': 'h'},
                                   autosize=True,
                                   showlegend=False,
                                   margin=dict(
                                       l=50,
                                       r=250,
                                       b=50,
                                       t=50,
                                       pad=4
                                   ))
    profile_plots['layout']['yaxis']['autorange'] = "reversed"
    profile_plots['layout']['yaxis2']['autorange'] = "reversed"
    profile_plots_title = "Profiles of SB_Temp and SB_Conductivity from " + str(tmin) + " to " + str(tmax)
    return [load_plots, profile_plots, load_plots_title]


if __name__ == '__main__':
    app.run_server(debug=True)

