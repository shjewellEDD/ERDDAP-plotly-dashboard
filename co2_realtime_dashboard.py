'''
Data layout
{0: 'latitude',
1: 'longitude',
2: 'time',
3: 'trajectory',
4: 'SOG',
5: 'SOG_FILTERED_MEAN',
6: 'SOG_FILTERED_STDDEV',
7: 'SOG_FILTERED_MAX',
8: 'SOG_FILTERED_MIN',
9: 'COG',
10: 'COG_FILTERED_MEAN',
11: 'COG_FILTERED_STDDEV',
12: 'HDG',
13: 'HDG_FILTERED_MEAN',
14: 'HDG_FILTERED_STDDEV',
15: 'ROLL_FILTERED_MEAN',
16: 'ROLL_FILTERED_STDDEV',
17: 'ROLL_FILTERED_PEAK',
18: 'PITCH_FILTERED_MEAN',
19: 'PITCH_FILTERED_STDDEV',
20: 'PITCH_FILTERED_PEAK',
21: 'HDG_WING',
22: 'WING_HDG_FILTERED_MEAN',
23: 'WING_HDG_FILTERED_STDDEV',
24: 'WING_ROLL_FILTERED_MEAN',
25: 'WING_ROLL_FILTERED_STDDEV',
26: 'WING_ROLL_FILTERED_PEAK',
27: 'WING_PITCH_FILTERED_MEAN',
28: 'WING_PITCH_FILTERED_STDDEV',
29: 'WING_PITCH_FILTERED_PEAK',
30: 'WING_ANGLE',
31: 'WIND_FROM_MEAN',
32: 'WIND_FROM_STDDEV',
33: 'WIND_SPEED_MEAN',
34: 'WIND_SPEED_STDDEV',
35: 'UWND_MEAN',
36: 'UWND_STDDEV',
37: 'VWND_MEAN',
38: 'VWND_STDDEV',
39: 'WWND_MEAN',
40: 'WWND_STDDEV',
41: 'GUST_WND_MEAN',
42: 'GUST_WND_STDDEV',
43: 'WIND_MEASUREMENT_HEIGHT_MEAN',
44: 'WIND_MEASUREMENT_HEIGHT_STDDEV',
45: 'TEMP_AIR_MEAN',
46: 'TEMP_AIR_STDDEV',
47: 'RH_MEAN',
48: 'RH_STDDEV',
49: 'BARO_PRES_MEAN',
50: 'BARO_PRES_STDDEV',
51: 'PAR_AIR_MEAN',
52: 'PAR_AIR_STDDEV',
53: 'TEMP_IR_SEA_WING_UNCOMP_MEAN',
54: 'TEMP_IR_SEA_WING_UNCOMP_STDDEV',
55: 'INSTRUMENT_STATE',
56: 'ASVCO2_GENERAL_ERROR_FLAGS',
57: 'ASVCO2_ZERO_ERROR_FLAGS',
58: 'ASVCO2_SPAN_ERROR_FLAGS',
59: 'ASVCO2_SECONDARYSPAN_ERROR_FLAGS',
60: 'ASVCO2_EQUILIBRATEANDAIR_ERROR_FLAGS',
61: 'ASVCO2_RTC_ERROR_FLAGS',
62: 'ASVCO2_FLOWCONTROLLER_FLAGS',
63: 'ASVCO2_LICOR_FLAGS',
64: 'CO2DETECTOR_TEMP_MEAN_ASVCO2',
65: 'CO2DETECTOR_TEMP_STDDEV_ASVCO2',
66: 'CO2DETECTOR_PRESS_UNCOMP_STDDEV_ASVCO2',
67: 'CO2DETECTOR_PRESS_MEAN_ASVCO2',
68: 'CO2_MEAN_ASVCO2',
69: 'CO2_STDDEV_ASVCO2',
70: 'RH_MEAN_ASVCO2',
71: 'RH_STDDEV_ASVCO2',
72: 'RH_TEMP_MEAN_ASVCO2',
73: 'RH_TEMP_STDDEV_ASVCO2',
74: 'CO2DETECTOR_RAWSAMPLE_MEAN_ASVCO2',
75: 'CO2DETECTOR_RAWSAMPLE_STDDEV_ASVCO2',
76: 'CO2DETECTOR_RAWREFERENCE_MEAN_ASVCO2',
77: 'CO2DETECTOR_RAWREFERENCE_STDDEV_ASVCO2',
78: 'O2_MEAN_ASVCO2',
79: 'O2_STDDEV_ASVCO2',
80: 'XCO2_DRY_SW_MEAN_ASVCO2',
81: 'XCO2_DRY_AIR_MEAN_ASVCO2',
82: 'CO2DETECTOR_ZERO_COEFFICIENT_ASVCO2',
83: 'CO2DETECTOR_SPAN_COEFFICIENT_ASVCO2',
84: 'CO2DETECTOR_SECONDARY_COEFFICIENT_ASVCO2',
85: 'WAVE_DOMINANT_PERIOD',
86: 'WAVE_SIGNIFICANT_HEIGHT',
87: 'TEMP_DEPTH_HALFMETER_MEAN',
88: 'TEMP_DEPTH_HALFMETER_STDDEV',
89: 'TEMP_SBE37_MEAN',
90: 'TEMP_SBE37_STDDEV',
91: 'SAL_SBE37_MEAN',
92: 'SAL_SBE37_STDDEV',
93: 'COND_SBE37_MEAN',
94: 'COND_SBE37_STDDEV',
95: 'O2_CONC_SBE37_MEAN',
96: 'O2_CONC_SBE37_STDDEV',
97: 'O2_SAT_SBE37_MEAN',
98: 'O2_SAT_SBE37_STDDEV',
99: 'CHLOR_WETLABS_MEAN',
100: 'CHLOR_WETLABS_STDDEV'}

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
                {'label': 'XCO2 Residuals', 'value': 'co2_res'},
                {'label': 'XCO2 Delta',     'value': 'co2_delt'},
                {'label': 'CO2 Pres. Mean', 'value': 'co2_det_state'},
                {'label': 'CO2 Mean',       'value': 'co2_mean_zp'},
                {'label': 'CO2 Mean SP',    'value': 'co2_mean_sp'},
                {'label': 'CO2 Span & Temp','value': 'co2_span_temp'},
                {'label': 'CO2 Zero Temp',  'value': 'co2_zero_temp'},
                {'label': 'CO2 STDDEV',     'value': 'co2_stddev'},
                {'label': 'O2 Mean',        'value': 'o2_mean'},
                {'label': 'CO2 Span',       'value': 'co2_span'},
                {'label': 'CO2 Zero',       'value': 'co2_zero'}
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
                                 children=[ddk.Graph(id='primary-graphic')#,
                                           #ddk.Graph(id='graphic-2'),
                                           #ddk.Graph(id='graphic-3')
                                            ]
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
                dhtml.Label(['Select X']),
                dcc.Dropdown(
                    id="select_x",
                    style={'backgroundColor': colors['background']},
                    options=dataset.co2_custom_data(),
                    value=dataset.co2_custom_data()[0]['value'],
                    clearable=False
                ),
                # dhtml.Label(['Select Y']),
                # dcc.Dropdown(
                #     id="select_y",
                #     style={'backgroundColor': colors['background'],
                #            'textColor': colors['text']},
                #     options=dataset.ret_vars(),
                #     value=dataset.ret_vars()[1]['value'],
                #     clearable=False
                # )
                ],
            ),
    ]),
    # ddk.Card(children=[
    #     ddk.Block(width=6, children=
    #     [
    #         dhtml.Img(src='https://www.pmel.noaa.gov/sites/default/files/PMEL-meatball-logo-sm.png', height=100,
    #                  width=100),
    #
    #     ]),
    #     ddk.Block(width=90, children=[
    #         dhtml.Div(children=[
    #             dcc.Link('National Oceanic and Atmospheric Administration', href='https://www.noaa.gov/'),
    #         ]),
    #         dhtml.Div(children=[
    #             dcc.Link('Pacific Marine Environmental Laboratory  |', href='https://www.pmel.noaa.gov/'),
    #             dcc.Link('  Engineering', href='https://www.pmel.noaa.gov/edd/')
    #         ]),
    #         dhtml.Div(children=[
    #             dcc.Link('oar.pmel.edd-webmaster@noaa.gov', href='mailto:oar.pmel.edd-webmaster@noaa.gov')
    #         ]),
    #         dhtml.Div(children=[
    #             dcc.Link('DOC |', href='https://www.commerce.gov/'),
    #             dcc.Link(' NOAA |', href='https://www.noaa.gov/'),
    #             dcc.Link(' OAR |', href='https://www.research.noaa.gov/'),
    #             dcc.Link(' PMEL |', href='https://www.pmel.noaa.gov/'),
    #             dcc.Link(' Privacy Policy |', href='https://www.noaa.gov/disclaimer'),
    #             dcc.Link(' Disclaimer |', href='https://www.noaa.gov/disclaimer'),
    #             dcc.Link(' Accessibility', href='https://www.pmel.noaa.gov/accessibility')
    #         ])
    #     ])
    # ])
])

])

'''
========================================================================================================================
Callbacks
'''

#engineering data selection
@app.callback(
    Output('primary-graphic', 'figure'),
    [Input('select_x', 'value'),
     Input('date-picker', 'start_date'),
     Input('date-picker', 'end_date')
     ])

def plot_evar(selection, t_start, t_end):

    def co2_raw():
        '''
        'co2_raw'
            Primary: XCO2_DRY_SW_MEAN_ASVCO2 & XCO2_DRY_AIR_MEAN_ASVCO2
            Secondary: SSS and SST
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

    def co2_res(data):
        '''
        'co2_res'
            Primary: Calculate residual of XCO2_DRY_SW_MEAN_ASVCO2 & XCO2_DRY_AIR_MEAN_ASVCO2
            Secondary: O2_SAT_SBE37_MEAN and/or O2_MEAN_ASVCO2
            '''
        pass

    def co2_delt(data):
        '''
        'co2_delt'
            Primary: calculated pressure differentials between like states
        '''
        pass

    def co2_det_state(data):
        '''
        'co2_det_state'
            Primary: CO2DETECTOR_PRESS_MEAN_ASVCO2 for each state
        '''
        pass

    def co2_mean_zp(data):
        '''
        'co2_mean_zp'
            Primary: CO2_MEAN_ASVCO2 for ZPON, ZPOFF and ZPPCAL
            Secondary: CO2DETECTOR_TEMP_MEAN_ASVCO2 for ZPOFF
        '''
        pass

    def co2_mean_sp(data):
        '''
        'co2_mean_sp'
            Primary: CO2_MEAN_ASVCO2 for SPON, SPOFF, SPPCAL
            Secondary: CO2_MEAN_ASVCO2 SPOFF
        '''
        pass

    def co2_span_temp(data):
        '''
        'co2_span_temp'
            Primary: CO2DETECTOR_SPAN_COEFFICIENT_ASVCO2 vs. SPOFF CO2DETECTOR_TEMP_MEAN_ASVCO2
        '''
        pass

    def co2_zero_temp(data):
        '''
        'co2_zero_temp'
            Primary: CO2DETECTOR_ZERO_COEFFICIENT_ASVCO2 vs. ZPOFF CO2DETECTOR_TEMP_MEAN_ASVCO2
        '''
        pass

    def co2_stddev(data):
        '''
        'co2_stddev'
            Primary: CO2_STDDEV_ASVCO2
        '''
        pass

    def o2_mean(data):
        '''
        'o2_mean'
            Primary: O2_MEAN_ASVCO2 for APOFF and EPOFF
        '''
        pass

    def co2_span(data):
        '''
        'co2_span'
            Primary: CO2DETECTOR_SPAN_COEFFICIENT_ASVCO2
            Secondary: CO2DETECTOR_TEMP_MEAN_ASVCO2 for SPOFF
        '''
        pass

    def co2_zero(data):
        '''
        'co2_zero'
            Primary: CO2DETECTOR_ZERO_COEFFICIENT_ASVCO2
            Secondary: CO2DETECTOR_TEMP_MEAN_ASVCO2 for ZPOFF
        '''
        pass

    def switch_plot(case):
        return {'co2_raw':      co2_raw,
        'co2_res':          co2_res,
        'co2_delt':         co2_delt,
        'co2_det_state':    co2_det_state,
        'co2_mean_zp':      co2_mean_zp,
        'co2_mean_sp':      co2_mean_sp,
        'co2_span_temp':    co2_span_temp,
        'co2_zero_temp':    co2_zero_temp,
        'co2_stddev':       co2_stddev,
        'o2_mean':          o2_mean,
        'co2_span':         co2_span,
        'co2_zero':         co2_zero
        }.get(case)

    states = ['ZPON', 'ZPOFF', 'ZPPCAL', 'SPON', 'SPOFF', 'SPPCAL', 'EPON', 'EPOFF', 'APON', 'APOFF']

    data = dataset.ret_data(t_start=t_start, t_end=t_end)

    plotters = switch_plot(selection)

    pri_fig = plotters[1]
    #sec_fig = plotters[2]
    #ter_fig = plotters[3]


    #efig = px.scatter(data, y=y_set, x=x_set)#, color="sepal_length", color_continuous_scale='oxy')


    # pri_fig.update_layout(
    #     plot_bgcolor=colors['background'],
    #     paper_bgcolor=colors['background'],
    #     font_color=colors['text']
    # )

    return pri_fig

if __name__ == '__main__':
    #app.run_server(host='0.0.0.0', port=8050, debug=True)


    app.run_server(debug=True)