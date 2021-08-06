'''
TODO:
Display dates are coming back wrong. Why?
'''


import dash
import dash_design_kit as ddk  # Only available on Dash Enterprise
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import dash_html_components as html
import datetime
import requests


# graph_config = {'modeBarButtonsToRemove': ['hoverCompareCartesian', 'select2d', 'lasso2d'],
#                 'doubleClick': 'reset+autosize', 'toImageButtonOptions': {'height': None, 'width': None, },
#                 'displaylogo': False}

window = 14
resolution = 7

url_base = 'https://data.pmel.noaa.gov/engineering/erddap/tabledap/prawler_TELONAS2.csv'
eng_base = 'https://data.pmel.noaa.gov/engineering/erddap/tabledap/prawler_eng_TELONAS2'

eng_set = [ {'label': 'None', 'value':   ''},
            {'label': 'Number of Trips', 'value':    'Ntrips'},
            {'label': 'Depth', 'value':   'depth'},
            {'label': 'Truck Mode', 'value':   'TruckMode'},
            {'label': 'Climb Mode', 'value':   'ClimbMode'},
            ]

#data = pd.read_csv(url_base + ".csv", skiprows=[1])
#data = pd.read_csv('https://data.pmel.noaa.gov/engineering/erddap/tabledap/prawler_TELONAS2.csv?&time>=2020-11-09T00:10:00Z&time<=2020-11-23T00:10:00Z', skiprows=[1])
# Need to come up with a way to generate this without the whole dataset
# Maybe from metadata

#vars = {}

# will need to be altered for multi-set displays


def data_dates(url):
    page = (requests.get(url[:-3] + "das")).text

    indx = page.find('Float64 actual_range')
    mdx = page.find(',', indx)
    endx = page.find(";", mdx)
    start_time = datetime.datetime.utcfromtimestamp(float(page[(indx + 21):mdx]))
    end_time = datetime.datetime.utcfromtimestamp(float(page[(mdx + 2):endx]))

    return start_time, end_time


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


def gen_url(o_url, t_start, window):
    base = o_url + "?&time>=" + gen_erddap_date(t_start) + '&' + gen_erddap_date(
        t_start - datetime.timedelta(days=window))

    return base


def latest_data(url, window):
    tstart, tend = data_dates(url)

    postdate = tend - datetime.timedelta(days=window)

    if postdate < tstart:
        postdate = tstart
    else:
        postdate = gen_erddap_date(postdate)

    return postdate


# generate sets of start and stop dates for the windows
def gen_windows(url, window, res):
    window_dict = {}
    dstart, dstop = data_dates(url)

    # snapshots are the number of windows we will need to cover the entire dataset

    snapshots = round((dstop - dstart).days / res) + 1

    # the first date is special as it will be from an odd start time

    t_date = str(dstart.year) + "-" + str(dstart.month).zfill(2) + '-' + str(dstart.day).zfill(2)
    t_url = url + "?&time>=" + gen_erddap_date(dstart) + '&time<=' + gen_erddap_date(
        dstart + datetime.timedelta(days=window))
    t0 = dstop - datetime.timedelta(snapshots * res)

    window_dict = {t_date: t_url}

    for n in range(snapshots):

        nstart = t0 + datetime.timedelta(days=res * n)
        t_date = str(nstart.year) + "-" + str(nstart.month).zfill(2) + '-' + str(nstart.day).zfill(2)
        t_url = url + "?&time>=" + gen_erddap_date(nstart) + '&time<=' + gen_erddap_date(
            nstart + datetime.timedelta(days=window))

        window_dict[t_date] = t_url

    return window_dict

windows = gen_windows(url_base, 14, 7)
dates = list(windows.keys())
# because Plotly desires dictionaries in everything, here's a dictionary
# if it's stupid and it works, it's not stupid
display_dates = dict(zip(range(len(dates)), dates))
data = pd.read_csv(windows[dates[-1]], skiprows=[1])

def gen_var_list(data):

    skipvars = ['time', 'Time', 'TIME']

    # for set in list(data.keys()):
    var_list = []
    for var in list(data.columns):
        if var in skipvars:
            continue

        var_list.append({'label': var, 'value': var})

    vars = {'sci': var_list}

    return vars

vars = gen_var_list(data)
external_stylesheets = ['https://codepen.io./chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div([
        html.Label(['Science Load']),
        ddk.Card(width=100,
                 children=[ddk.Graph(id='sci-graphic',
                                     figure=px.scatter(data,
                                                       y=data['SB_Depth'],
                                                       x=data['time']
                                                      )
                                     )],
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
        html.Label(['Traverse Overlay']),
        dcc.Dropdown(
            id="sci_overlay",
            options=eng_set,
            value=eng_set[0]['value']
            # multi=True
        ),
        dcc.Slider(
            id='sci_range',
            min=0,
            max=len(dates),
            marks=display_dates,
            value=len(dates)-1
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

    new_url = windows[display_dates[sci_range]]
    new_data = pd.read_csv(new_url, skiprows=[1])
    vars = gen_var_list(new_data)
    sfig = px.scatter(new_data, y=select_sci, x='time')

    sfig.update_layout()

    return sfig, vars['sci']

@app.callback(
    [Output('sci-graphic', 'figure')],
    [Input('sci_range', 'value'),
    Input('sci_overlay', 'value')])
def plot_soverlay(sci_range, sci_overlay):

    new_url = windows[display_dates[sci_range]]
    new_data = pd.read_csv(new_url, skiprows=[1])
    vars = gen_var_list(new_data)
    sfig = px.scatter(new_data, y=select_sci, x='time')

    sfig.update_layout()

    return sfig
# #
# @app.callback(
#     Output('sci-graphic', 'figure'),
#     Input('sci_range', 'value'),
#     Input('select_sci', 'value'))
# def refresh_range(sci_range,select_sci):
#     new_url = windows[display_dates[sci_range]]
#     new_data = pd.read_csv(new_url, skiprows=[1])
#     plot_svar(select_sci, new_data)



if __name__ == '__main__':
    #app.run_server(host='0.0.0.0', port=8050, debug=True)
    app.run_server(debug=True)