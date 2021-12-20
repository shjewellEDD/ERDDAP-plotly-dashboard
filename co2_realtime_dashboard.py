'''

TODO:
    Select date range
    Group and select data by SN
        Maybe Instrument state as well?

    Improve Style sheet
        Seperate out data and flags

    Improve style sheet

    Improve Plotting
        Break up each data chunk (eg O2_CONC) and give a seperate plot to Real, MEAN and STDDEV

    Statistics
        Make options for choosing residual calculation:
            Remainder
            Mean
            Least Squares

'''

import dash
import dash_design_kit as ddk  # Only available on Dash Enterprise
import dash_core_components as dcc
from dash.dependencies import Input, Output
import dash_table
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots  import make_subplots
import dash_html_components as dhtml

#non-plotly imports
import pandas as pd
from lxml import html
import datetime
from datetime import date
import requests
import io
import urllib

skipvars = ['latitude', 'longitude']
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

''' class used for holding useful information about the ERDDAP databases
========================================================================================================================
'''

class Dataset:
    #dataset object,
    #it takes requested data and generates windows and corresponding urls
    #logger.info('New dataset initializing')

    def __init__(self, url, window_start=False, window_end=False):
        self.url = url
        self.flags = pd.DataFrame
        self.data, self.vars = self.get_data()
        self.t_start, self.t_end = self.data_dates()
        self.set_names, self.flags = self.catagorize()

        #self.co2_vars

    #opens metadata page and returns start and end datestamps
    def data_dates(self):
        '''
        Currently the meta data states a start in 1969, which seems unrealistic
        Let's actually use hard coded dates. We may need to fix
        :return:
        '''
        page = (requests.get(self.url[:-3] + "das")).text

        indx = page.find('Float64 actual_range')
        mdx = page.find(',', indx)
        endx = page.find(";", mdx)
        # start_time = datetime.datetime.utcfromtimestamp(float(page[(indx + 21):mdx]))
        # end_time = datetime.datetime.utcfromtimestamp(float(page[(mdx + 2):endx]))

        #prevents dashboard from trying to read data from ... THE FUTURE!
        # if end_time > datetime.datetime.now():
        #     end_time = datetime.datetime.now()

        if self.data['time'].min() < datetime.datetime.utcfromtimestamp(float(page[(indx + 21):mdx])):
            start_time = datetime.datetime.utcfromtimestamp(float(page[(indx + 21):mdx]))
        else:
            start_time = self.data['time'].min()

        if self.data['time'].max() > datetime.datetime.utcfromtimestamp(float(page[(mdx + 2):endx])):
            end_time = self.data['time'].max()
        else:
            end_time = datetime.datetime.utcfromtimestamp(float(page[(mdx + 2):endx]))

        return start_time, end_time


    def get_data(self):

        self.data = pd.read_csv(self.url, skiprows=[1], low_memory=False)
        temp = self.data['time'].apply(from_erddap_date)
        #self.serials = (self.data['SN_ASVCO2'].unique()).tolist()
        #self.data = self.data.select_dtypes(include='float64')
        self.data['time'] = temp
        self.flags.assign(temp)

        dat_vars = self.data.columns


        # for set in list(data.keys()):
        self.vars = []
        for var in list(dat_vars):
            # if var in skipvars:
            #     continue

            if 'FLAG' in var:
                self.flags.assign(self.data[var])
                #self.data.drop(self.data[var], axis='columns')

            if str(self.data[var].dtype) == 'object':
                continue

            self.vars.append({'label': var, 'value': var})


        return self.data, self.vars

    def co2_custom_data(self):

        sets = [{'label': 'XCO2 Mean',      'value': 'co2_raw'},
                # {'label': 'XCO2 Residuals', 'value': 'co2_res'},
                # {'label': 'XCO2 Delta',     'value': 'co2_delt'},
                # {'label': 'CO2 Pres. Mean', 'value': 'co2_det_state'},
                # {'label': 'CO2 Mean',       'value': 'co2_mean_zp'},
                # {'label': 'CO2 Mean SP',    'value': 'co2_mean_sp'},
                # {'label': 'CO2 Span & Temp','value': 'co2_span_temp'},
                # {'label': 'CO2 Zero Temp',  'value': 'co2_zero_temp'},
                # {'label': 'CO2 STDDEV',     'value': 'co2_stddev'},
                # {'label': 'O2 Mean',        'value': 'o2_mean'},
                # {'label': 'CO2 Span',       'value': 'co2_span'},
                # {'label': 'CO2 Zero',       'value': 'co2_zero'}
        ]

        return sets


    def catagorize(self):

        sets = set()
        flags = pd.DataFrame
        base_sets = {}

        subsets = {0:   '_MEAN',
                   1:   '_STDDEV',
                   2:   '_MAX',
                   3:   '_MIN'
                   }

        for col in self.data.columns:

            for n in subsets:

                if "FLAG" in col:

                    flags.assign(self.data[col])
                    continue

                elif subsets[n] in col:

                    sets.add(col.replace(subsets[n], ''))

                    try:
                        base_sets[col.replace(subsets[n], '')][subsets[n]] = col
                    except KeyError:
                        base_sets[col.replace(subsets[n], '')] = {subsets[n]: col}


                    continue

            #drop_list =

        return base_sets, flags

    def ret_data(self, **kwargs):

        w_start = kwargs.get('t_start', self.t_start)
        w_end = kwargs.get('t_end', self.t_end)

        #self.data['datetime'] = self.data.loc[:, 'time'].apply(from_erddap_date)

        return self.data[(w_start <= self.data['time']) & (self.data['time'] <= w_end)]

    def ret_vars(self):

        return self.vars




'''
========================================================================================================================
Start Dashboard
'''

set_url = 'http://dunkel.pmel.noaa.gov:9290/erddap/tabledap/asvco2_gas_validation_all_fixed_station_mirror.csv'
rt_url = 'https://data.pmel.noaa.gov/generic/erddap/tabledap/sd_shakedown_collection.csv'
set_loc = 'D:\Data\CO2 Sensor tests\\asvco2_gas_validation_all_fixed_station_mirror.csv'

dataset = Dataset(rt_url)


graph_height = 300

graph_config = {'modeBarButtonsToRemove' : ['hoverCompareCartesian','select2d', 'lasso2d'],
                'doubleClick':  'reset+autosize', 'toImageButtonOptions': { 'height': None, 'width': None, },
                'displaylogo': False}

colors = {'background': '#111111', 'text': '#7FDBFF'}

external_stylesheets = ['https://codepen.io./chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__)

app.layout = ddk.App([
    ddk.Header([
        # ddk.Logo(src=app.get_asset_url('logo.png'), style={
        #     'max-height': 100,
        #     'width': 'auto'
        # }),
        ddk.Title('ASVCO2 Reporting'),
        ddk.SectionTitle('', id='final_date'),
        dhtml.Button('Refresh', style={'float': 'right'}, id='refresh', n_clicks=0),
    ]),
dhtml.Div(style={'backgroundColor': colors['background']},
          children=[
    dhtml.Div(style={'backgroundColor': colors['background']},
              children=[
        ddk.Card(width=75,
                 style={'backgroundColor': colors['background']},
                 children=[dcc.Loading(id='graph_car',
                                 children=[ddk.Graph(id='graphs', config=graph_config)]
                                       )
                           ]
                 ),
      # dhtml.Div(style={'backgroundColor': colors['background']},
      #          children=[
        ddk.Card(width=25,
                style={'backgroundColor': colors['background']},
               children=[dcc.DatePickerRange(
                    id='date-picker',
                    style={'backgroundColor': colors['background']},
                    min_date_allowed=dataset.t_start,
                    max_date_allowed=dataset.t_end,
                    start_date=dataset.t_end - datetime.timedelta(days=14),
                    end_date=dataset.t_end
                ),
                dhtml.Label(['Select Set']),
                dcc.Dropdown(
                    id="select_x",
                    style={'backgroundColor': colors['background']},
                    options=dataset.co2_custom_data(),
                    value=dataset.co2_custom_data()[0]['value'],
                    clearable=False
                )
                ]
            )
    ])
])

])

'''
========================================================================================================================
Callbacks
'''

#engineering data selection
@app.callback(
    Output('graphs', 'figure'),
    [Input('select_x', 'value'),
     Input('date-picker', 'start_date'),
     Input('date-picker', 'end_date')
     ])

def plot_evar(selection, t_start, t_end):

    def co2_raw(df):
        '''
        'co2_raw'
            Primary: XCO2_DRY_SW_MEAN_ASVCO2 & XCO2_DRY_AIR_MEAN_ASVCO2
            Secondary: SSS and SST
        '''

        # for instr in states:

        # df['XCO2_DRY_SW_MEAN_ASVCO2'].dropna()
        # df['XCO2_DRY_AIR_MEAN_ASVCO2'].dropna()
        # df['SAL_SBE37_MEAN'].dropna()
        # df['time'].dropna()

        sw = go.Scatter(x=df['time'], y=df['XCO2_DRY_SW_MEAN_ASVCO2'].dropna(), name='Seawater CO2', hoverinfo='x+y+name')
        air = go.Scatter(x=df['time'], y=df['XCO2_DRY_AIR_MEAN_ASVCO2'].dropna(), name='CO2 Air', hoverinfo='x+y+name')
        sss = go.Scatter(x=df['time'], y=df['SAL_SBE37_MEAN'].dropna(), name='SSS', hoverinfo='x+y+name')
        sst = go.Scatter(x=df['time'], y=df['TEMP_SBE37_MEAN'].dropna(), name='SST', hoverinfo='x+y+name')

        load_plots = make_subplots(rows=3, cols=1, shared_xaxes='all',
                                   subplot_titles=("XCO2 DRY", "SSS", "SST"),
                                   shared_yaxes=False, vertical_spacing=0.1)

        load_plots.append_trace(sw, row=1, col=1)
        load_plots.add_trace(air, row=1, col=1)
        load_plots.append_trace(sss, row=2, col=1)
        load_plots.append_trace(sst, row=3, col=1)


        load_plots['layout'].update(height=900,
                                    title=' ',
                                    hovermode='x unified',
                                    xaxis_showticklabels=True,
                                    xaxis2_showticklabels=True, xaxis3_showticklabels=True,
                                    yaxis_fixedrange=True,
                                    yaxis2_fixedrange=True, yaxis3_fixedrange=True,
                                    yaxis_title='Dry CO2',
                                    yaxis2_title='Salinity', yaxis3_title='SW Temp',
                                    showlegend=False, modebar={'orientation': 'h'}, autosize=True)

        return load_plots

    def co2_res(data):
        '''
        'co2_res'
            Primary: Calculate residual of XCO2_DRY_SW_MEAN_ASVCO2 & XCO2_DRY_AIR_MEAN_ASVCO2
            Secondary: O2_SAT_SBE37_MEAN and/or O2_MEAN_ASVCO2
            '''
        fig = go.Figure()

        # for instr in states:
        data['WIND_FROM_MEAN'].dropna()
        data['time'].dropna()

        fig = px.scatter(data,
                         y='WIND_FROM_MEAN',
                         x='time',
                         color='INSTRUMENT_STATE',
                         symbol='INSTRUMENT_STATE')

        sec = go.Figure()

        return {1: fig}

    def co2_delt(data):
        '''
        'co2_delt'
            Primary: calculated pressure differentials between like states
        '''
        fig = go.Figure()

        # for instr in states:

        data['WIND_FROM_MEAN'].dropna()
        data['time'].dropna()

        fig = px.scatter(data,
                         y='WIND_FROM_MEAN',
                         x='time',
                         color='INSTRUMENT_STATE',
                         symbol='INSTRUMENT_STATE')

        sec = go.Figure()

        return fig

    def co2_det_state(data):
        '''
        'co2_det_state'
            Primary: CO2DETECTOR_PRESS_MEAN_ASVCO2 for each state
        '''
        fig = go.Figure()

        # for instr in states:

        data['WIND_FROM_MEAN'].dropna()
        data['time'].dropna()

        fig = px.scatter(data,
                         y='WIND_FROM_MEAN',
                         x='time',
                         color='INSTRUMENT_STATE',
                         symbol='INSTRUMENT_STATE')

        sec = go.Figure()

        return {1: fig}

    def co2_mean_zp(data):
        '''
        'co2_mean_zp'
            Primary: CO2_MEAN_ASVCO2 for ZPON, ZPOFF and ZPPCAL
            Secondary: CO2DETECTOR_TEMP_MEAN_ASVCO2 for ZPOFF
        '''
        fig = go.Figure()

        # for instr in states:

        data['WIND_FROM_MEAN'].dropna()
        data['time'].dropna()

        fig = px.scatter(data,
                         y='WIND_FROM_MEAN',
                         x='time',
                         color='INSTRUMENT_STATE',
                         symbol='INSTRUMENT_STATE')

        sec = go.Figure()

        return {1: fig}

    def co2_mean_sp(data):
        '''
        'co2_mean_sp'
            Primary: CO2_MEAN_ASVCO2 for SPON, SPOFF, SPPCAL
            Secondary: CO2_MEAN_ASVCO2 SPOFF
        '''
        fig = go.Figure()

        # for instr in states:

        data['WIND_FROM_MEAN'].dropna()
        data['time'].dropna()

        fig = px.scatter(data,
                         y='WIND_FROM_MEAN',
                         x='time',
                         color='INSTRUMENT_STATE',
                         symbol='INSTRUMENT_STATE')

        sec = go.Figure()

        return {1: fig}

    def co2_span_temp(data):
        '''
        'co2_span_temp'
            Primary: CO2DETECTOR_SPAN_COEFFICIENT_ASVCO2 vs. SPOFF CO2DETECTOR_TEMP_MEAN_ASVCO2
        '''
        fig = go.Figure()

        # for instr in states:

        data['WIND_FROM_MEAN'].dropna()
        data['time'].dropna()

        fig = px.scatter(data,
                         y='WIND_FROM_MEAN',
                         x='time',
                         color='INSTRUMENT_STATE',
                         symbol='INSTRUMENT_STATE')

        sec = go.Figure()

        return {1: fig}

    def co2_zero_temp(data):
        '''
        'co2_zero_temp'
            Primary: CO2DETECTOR_ZERO_COEFFICIENT_ASVCO2 vs. ZPOFF CO2DETECTOR_TEMP_MEAN_ASVCO2
        '''
        fig = go.Figure()

        # for instr in states:

        data['WIND_FROM_MEAN'].dropna()
        data['time'].dropna()

        fig = px.scatter(data,
                         y='WIND_FROM_MEAN',
                         x='time',
                         color='INSTRUMENT_STATE',
                         symbol='INSTRUMENT_STATE')

        sec = go.Figure()

        return {1: fig}

    def co2_stddev(data):
        '''
        'co2_stddev'
            Primary: CO2_STDDEV_ASVCO2
        '''
        fig = go.Figure()

        # for instr in states:

        data['WIND_FROM_MEAN'].dropna()
        data['time'].dropna()

        fig = px.scatter(data,
                         y='WIND_FROM_MEAN',
                         x='time',
                         color='INSTRUMENT_STATE',
                         symbol='INSTRUMENT_STATE')

        sec = go.Figure()

        return {1: fig}

    def o2_mean(data):
        '''
        'o2_mean'
            Primary: O2_MEAN_ASVCO2 for APOFF and EPOFF
        '''
        fig = go.Figure()

        # for instr in states:

        data['WIND_FROM_MEAN'].dropna()
        data['time'].dropna()

        fig = px.scatter(data,
                         y='WIND_FROM_MEAN',
                         x='time',
                         color='INSTRUMENT_STATE',
                         symbol='INSTRUMENT_STATE')

        sec = go.Figure()

        return {1: fig}

    def co2_span(data):
        '''
        'co2_span'
            Primary: CO2DETECTOR_SPAN_COEFFICIENT_ASVCO2
            Secondary: CO2DETECTOR_TEMP_MEAN_ASVCO2 for SPOFF
        '''
        fig = go.Figure()

        # for instr in states:

        data['WIND_FROM_MEAN'].dropna()
        data['time'].dropna()

        fig = px.scatter(data,
                         y='WIND_FROM_MEAN',
                         x='time',
                         color='INSTRUMENT_STATE',
                         symbol='INSTRUMENT_STATE')

        sec = go.Figure()

        return {1: fig}

    def co2_zero(data):
        '''
        'co2_zero'
            Primary: CO2DETECTOR_ZERO_COEFFICIENT_ASVCO2
            Secondary: CO2DETECTOR_TEMP_MEAN_ASVCO2 for ZPOFF
        '''
        fig = go.Figure()

        # for instr in states:

        data['WIND_FROM_MEAN'].dropna()
        data['time'].dropna()

        fig = px.scatter(data,
                         y='WIND_FROM_MEAN',
                         x='time',
                         color='INSTRUMENT_STATE',
                         symbol='INSTRUMENT_STATE')

        sec = go.Figure()

        return {1: fig}

    def switch_plot(case, data):
        return {'co2_raw':      co2_raw(data),
        'co2_res':          co2_res(data),
        'co2_delt':         co2_delt(data),
        'co2_det_state':    co2_det_state(data),
        'co2_mean_zp':      co2_mean_zp(data),
        'co2_mean_sp':      co2_mean_sp(data),
        'co2_span_temp':    co2_span_temp(data),
        'co2_zero_temp':    co2_zero_temp(data),
        'co2_stddev':       co2_stddev(data),
        'o2_mean':          o2_mean(data),
        'co2_span':         co2_span(data),
        'co2_zero':         co2_zero(data)
        }.get(case)

    states = ['ZPON', 'ZPOFF', 'ZPPCAL', 'SPON', 'SPOFF', 'SPPCAL', 'EPON', 'EPOFF', 'APON', 'APOFF']

    data = dataset.ret_data(t_start=t_start, t_end=t_end)

    plotters = switch_plot(selection, data)

    #pri_fig = plotters[1]
    #sec_fig = plotters[2]
    #ter_fig = plotters[3]

    #efig = px.scatter(data, y=y_set, x=x_set)#, color="sepal_length", color_continuous_scale='oxy')


    plotters.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text']
    )

    return plotters

if __name__ == '__main__':
    #app.run_server(host='0.0.0.0', port=8050, debug=True)


    app.run_server(debug=True)