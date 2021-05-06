import dash
import dash_html_components as html
import dash_design_kit as ddk
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input, State
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from plotly.subplots import make_subplots
import datetime
import json

app = dash.Dash(__name__)
server = app.server  # expose server variable for Procfile

base_url = 'http://dunkel.pmel.noaa.gov:8336/erddap/tabledap/osmc_gts'
days_ago = 14
location_date = 'now-' + str(days_ago) + 'days'
vars = 'platform_code,platform_type,time,latitude,longitude,observation_depth,sst,atmp,precip,ztmp,zsal,slp,windspd,winddir,wvht,waterlevel,clouds,dewpoint,uo,vo,wo,rainfall_rate,hur,sea_water_elec_conductivity,sea_water_pressure,rlds,rsds,waterlevel_met_res,waterlevel_wrt_lcd,water_col_ht,wind_to_direction,lon360'
surface_variables = ['sst','atmp','precip','slp','windspd','winddir','wvht','clouds','dewpoint',]
unused_variables = ['uo','vo','wo','waterlevel','rainfall_rate','hur','sea_water_elec_conductivity','sea_water_pressure','rlds','rsds','waterlevel_met_res','waterlevel_wrt_lcd','water_col_ht','wind_to_direction']
depth_variables = ['ztmp','zsal']

location_url = 'http://dunkel.pmel.noaa.gov:8336/erddap/tabledap/osmc_gts.csv?platform_code%2Cplatform_type%2Ctime%2Clongitude%2Clatitude&distinct()&orderByMax("platform_code,time")&time>=' + location_date+'&latitude<90&latitude>-90'
# location_url = 'http://dunkel.pmel.noaa.gov:8336/erddap/tabledap/osmc_gts.csv?platform_code%2Cplatform_type%2Ctime%2Clongitude%2Clatitude&distinct()&orderByMax("platform_code,time")&time>=' + location_date+'&latitude<90&latitude>-90&platform_code=~"(VRJZ9|32315|3101602|52006|TIBC1|3100006)"'

# At least do this...
graph_config = {'displaylogo': False}

height_of_row=345;

invisible = {'display':'none'}
visible = {'display':'block'}

platform_color = {
    'AUTONOMOUS PINNIPEDS': '#FF0000',
    'C-MAN WEATHER STATIONS': '#FF7F00', 
    'CLIMATE REFERENCE MOORED BUOYS': '#FFD400', 
    'DRIFTING BUOYS (GENERIC)': '#FFFF00', 
    'GLIDERS': '#BFFF00',
    'ICE BUOYS': '#6AFF00',
    'MOORED BUOYS (GENERIC)': '#00EAFF',
    'OCEAN TRANSPORT STATIONS (GENERIC)': '#0095FF',
    'PROFILING FLOATS AND GLIDERS (GENERIC)': '#0040FF',
    'RESEARCH': '#AA00FF',
    'SHIPS (GENERIC)': '#FF00AA',
    'SHORE AND BOTTOM STATIONS (GENERIC)': '#EDB9B9',
    'TIDE GAUGE STATIONS (GENERIC)': '#E7E9B9',
    'TROPICAL MOORED BUOYS': '#B9EDE0',
    'TSUNAMI WARNING STATIONS': '#B9D7ED',
    'UNKNOWN': '#DCB9ED',
    'UNMANNED SURFACE VEHICLE': '#8F2323',
    'VOLUNTEER OBSERVING SHIPS': '#8F6A23',
    'VOLUNTEER OBSERVING SHIPS (GENERIC)': '#4F8F23',
    'VOSCLIM': '#23628F',
    'WEATHER AND OCEAN OBS': '#6B238F',
    'WEATHER BUOYS': '#000000',
    'WEATHER OBS': '#737373',
}

app.layout = ddk.App([
    dcc.Store(id='download-format'),
    dcc.Store(id='current-platform_code'),
    ddk.Header([
        ddk.Logo(src=app.get_asset_url('logo.png')),
        ddk.Title('OSMC Dashboard'),
        ddk.SectionTitle('', id='sub-title'),
    ]),
    ddk.Row([
        ddk.Card(width=70, children=[
                ddk.CardHeader(id="map-title", title="Platform Locations", 
                    children=[
                        ddk.Row(children=[
                            ddk.Block(width=80, children=[
                                dcc.Dropdown(
                                    style=dict(width='180px'),
                                    id='download-dropdown',
                                    options=[
                                        {'label': 'HTML', 'value': '.htmlTable'},
                                        {'label': 'CSV', 'value': '.csv'},
                                        {'label': 'netCDF', 'value': '.ncCF'},
                                        {'label': 'GeoJSON', 'value': '.geoJson'}
                                    ],
                                    placeholder='Download Format',
                                    disabled=True
                                )
                            ]),
                            ddk.Block(id='download-block', width=20, style={'display':'none'}, children=[
                                html.A('Data',id='download-link', href="", target='_blank', 
                                style={'line-height':'41px', 'padding-right':'10px', 'padding-left':'10px'}
                                )
                            ])
                        ])
                    ]
                ),
            dcc.Loading(id='map-loader', children=[dcc.Graph(id='location-map', config=graph_config),]),
        ]),
        ddk.Card(children=[
            ddk.CardHeader(id="trace-title", title=''),
            dcc.Loading(id='trace-loader', children=[ddk.Graph(id='location-trace', config=graph_config)])
        ], width=30),
        html.Div(id='data-div', style={'display':'none'}),
    ]),
    ddk.Row([
        ddk.Card(width=100, children=[
                ddk.CardHeader(id="plots-title", title='', modal=True, fullscreen=True, modal_config={'width': 80, 'height': 80}),
                dcc.Loading(id='plot-loader', children=[dcc.Graph(id='plots', config=graph_config),]),
        ]),
    ]),
        ddk.Card(children=[
        ddk.Block(width=6, children=
        [
            html.Img(src='https://www.pmel.noaa.gov/sites/default/files/PMEL-meatball-logo-sm.png', height=100, width=100),
        
        ]),
        ddk.Block(width=90, children=[
            html.Div(children=[
                dcc.Link('National Oceanic and Atmospheric Administration', href='https://www.noaa.gov/'),
            ]),
            html.Div(children=[
                dcc.Link('Pacific Marine Environmental Laboratory', href='https://www.pmel.noaa.gov/'),  
            ]),
            html.Div(children=[
                dcc.Link('oar.pmel.webmaster@noaa.gov', href='mailto:oar.pmel.webmaster@noaa.gov')
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
    [
        Output('location-map', 'figure'),
        Output('sub-title', 'children'),
    ],
    [
        Input('data-div', 'children')
    ]
)
def load_platforms(click):
    df = pd.read_csv(
        location_url,
        skiprows=[1])
    platform_count = df.shape[0]
    title = 'Locations for ' + str(platform_count) + ' platforms reporting for the past '+ str(days_ago) + ' days'
    location_map = px.scatter_geo(df, lat='latitude', lon='longitude', 
                                    color="platform_type",
                                    color_discrete_map=platform_color,
                                    hover_data=['latitude', 'longitude', 'platform_code'],
                                    projection="equirectangular", custom_data=['platform_code'])
    location_map.update_layout(legend=dict(
            orientation="v",
            yanchor="top",
            y=1.0,
            xanchor="right",
            x=1.3
    ), clickmode='event+select')    
    location_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})                            
    location_map.update_geos(
        resolution=50,
        showcoastlines=True, coastlinecolor="RebeccaPurple",
        showland=True, landcolor="LightGreen",
        showocean=True, oceancolor="Azure",
        showlakes=True, lakecolor="Blue",  
    )
    location_map.update_traces(marker_size=10, unselected=dict(marker=dict(opacity=.65)),)
    return [location_map, title]


@app.callback([
   Output('map-title', 'title'),
   Output('download-dropdown', 'disabled'),
   Output('current-platform_code', 'data')
],
[
    Input('location-map', 'clickData')
],
)
def data_url(selection):
    code_json = {}
    if selection is None:
        return ['Platform Location Map', True, json.dumps(code_json)]
    fst_point = selection['points'][0]
    code = fst_point['customdata'][0]
    code_json['platform_code'] = code
    return ['Platform Location Map - ' + str(code) + ' is selected.', False, json.dumps(code_json)]

@app.callback([
   Output('download-block', 'style'),
   Output('download-format', 'data')
   
],
[
    Input('download-dropdown', 'value')
],
[
    State('download-format', 'data')
])
def set_download(format, data):
    if data is not None:
        format_json = json.loads(data)
    else:
        format_json = {}
    if format is None:
        return [invisible, json.dumps(format_json)]
    else:
        format_json['format']=format
        return [visible, json.dumps(format_json)]

@app.callback([
    Output('download-link', 'href'),
],
[
    Input('download-format', 'data'),
    Input('current-platform_code', 'data')
],
[
    State('download-format', 'data'),
    State('current-platform_code', 'data')
]
)
def set_download_url(change_format, change_code, format, code):
    set_format = '.htmlTable'
    set_code = ' '
    if change_format is not None:
        f_json = json.loads(change_format)
        if 'format' in f_json:
            set_format = f_json['format']
    elif format is not None:
        f_json = json.loads(format)
        if 'format' in f_json:
            set_format = f_json['format']
    
    if change_code is not None:
        c_json = json.loads(change_code)
        if 'platform_code' in c_json:
            set_code = c_json['platform_code']
    elif code is not None:
        c_json = json.loads(code)
        if 'platform_code' in c_json:
            set_code = c_json['platform_code']
    return [base_url + set_format + '?' + vars + '&platform_code="'+ set_code + '"&time>=now-'+str(days_ago)+'days']


@app.callback([
    Output('location-trace', 'figure'),
    Output('trace-title', 'title'),
    Output('plots', 'figure'),
    Output('plots-title', 'title')
],[
    Input('location-map', 'clickData')
], prevent_initial_call=True)
def location_trace(selection):
    if selection is None:
        raise dash.exceptions.PreventUpdate()
    fst_point = selection['points'][0]
    code = fst_point['customdata'][0]
    df = pd.read_csv('http://dunkel.pmel.noaa.gov:8336/erddap/tabledap/osmc_gts.csv?' + vars + '&platform_code="' + code + '"&orderBy("time,observation_depth")&time>now-14days', skiprows=[1])
    locs_wnan = df.drop_duplicates(['time'])
    df1 = locs_wnan.dropna(axis=1, how='all').copy()
    df1.loc[:,'platform_code'] = df1['platform_code'].astype(str)
    df1.loc[:,'millis'] = pd.to_datetime(df1['time']).astype(np.int64)
    df1.loc[:, 'text_time'] = df1['time'].astype(str)
    df1.loc[:, 'time'] = pd.to_datetime(df1['time'])
    df1.loc[:,'text'] = df1['text_time'] + "<br>" + df1['platform_code']
    location_trace = go.Figure(data=go.Scattergeo(lat=df1["latitude"], lon=df1["longitude"], 
        marker=dict(color=df1["millis"], colorscale='Blues', size=8),
        text=df1["text"],))
    location_trace.update_layout(
        height=500, width=500, margin={"r":0,"t":0,"l":0,"b":0},
    )
    trace_title = 'Locations for ' + str(code) + " (white=oldest)"
    
    location_trace.update_geos(fitbounds='locations', resolution=50,
        showcoastlines=True, coastlinecolor="RebeccaPurple",
        showland=True, landcolor="LightGreen",
        showocean=True, oceancolor="Azure",
        showlakes=True, lakecolor="Blue", projection=dict(type="mercator"))

    subplots = {}
    titles = []
    for var in surface_variables:
        dfvar = df[['time',var]].copy()
        dfvar.loc[:, 'text_time'] = dfvar['time'].astype(str)
        dfvar.loc[:, 'time'] = pd.to_datetime(dfvar['time'])
        dfvar.dropna(subset=[var], how='all', inplace=True) # do we want to drop nan or not, may have rows from other parameters that are "false" nan!!!
        if dfvar.shape[0] > 2:
            varplot = go.Scatter(x=dfvar['time'], y=dfvar[var], name=var)
            subplots[var] = varplot
            titles.append(var)

    for var in depth_variables:
        dfvar = df[['time', 'observation_depth', var]].copy()  
        dfvar.loc[:, 'text_time'] = dfvar['time'].astype(str)
        dfvar.loc[:, 'time'] = pd.to_datetime(dfvar['time'])
        dfvar = dfvar.sort_values(["time", "observation_depth"], ascending = (True, True))
        dfvar.dropna(subset=[var], how='all', inplace=True)
        colorscale='Inferno'
        if var == 'zsal':
            colorscale='Viridis'
        if dfvar.shape[0] > 2:
            depths = pd.unique(dfvar['observation_depth'])
            if var == 'ztmp':
                xp = .45
            else:
                xp = 1.0
            if len(depths) > 1:
                varplot = go.Scatter(x=dfvar['time'], y=dfvar['observation_depth'], 
                                     marker=dict(symbol='square', showscale=True, color=dfvar[var], colorscale=colorscale,),
                                     mode='markers', name=var, text=dfvar[var])
                titles.append(var)
            else:
                varplot = go.Scatter(x=dfvar['time'], y=dfvar[var], name=var)
                titles.append(var + ' at depth ' + str(depths[0]))
            subplots[var] = varplot

    num_plots = len(subplots)
    if num_plots == 0:
        raise dash.exceptions.PreventUpdate()
    num_rows = int(num_plots/3)
    if num_rows == 0:
        num_rows = num_rows + 1
    if num_plots > 3 and num_plots%3 > 0:
        num_rows = num_rows + 1
    row_h = []
    for i in range(0, num_rows):
        row_h.append(1/num_rows)
    graph_height = height_of_row*num_rows
    num_cols = min(num_plots, 3)
    plots = make_subplots(rows=num_rows, cols=num_cols, shared_xaxes='all', subplot_titles=titles, shared_yaxes=False, row_heights=row_h)
    plot_index=1
    col=1
    row=1
    for plot in subplots:
        current_plot = subplots[plot]
        
        if plot == 'ztmp' or plot == 'zsal':
            if plot_index == 1: 
                yax = 'yaxis'
                xax = 'xaxis'
            else:
                yax = 'yaxis'+str(plot_index)
                xax = 'xaxis'+str(plot_index) 
            current_plot['marker']['colorbar']['len'] = plots['layout'][yax]['domain'][1]-plots['layout'][yax]['domain'][0]
            current_plot['marker']['colorbar']['y'] = (plots['layout'][yax]['domain'][1] + plots['layout'][yax]['domain'][0])/2
            current_plot['marker']['colorbar']['x'] = plots['layout'][xax]['domain'][1]
            current_plot['marker']['colorbar']['yanchor'] = 'middle'
            plots['layout'][yax]['autorange'] = "reversed"
        plots.add_trace(current_plot, row=row, col=col)
        plot_index = plot_index + 1
        if plot_index > 1:
            if col == 3:
                row = row + 1
        col = plot_index%3
        if col==0:
            col = 3

    for i in range(0, len(subplots)):
        if i == 0:
            key={'xaxis_showticklabels':True}
        else:
            key = {'xaxis' + str(i) + "_showticklabels": True}
        plots['layout'].update(**key)

    plots['layout'].update(height=graph_height, margin=dict( l=80, r=80, b=80, t=80, ))
    # plots.update_traces(marker_colorbar_lenmode='fraction', marker_colorbar_len=row_h[0], marker_colorbar_yanchor='middle', showlegend=False)
    plots.update_traces(showlegend=False)
    # plots.update_traces(selector=dict(name='ztmp'), marker_colorbar={})
    plots_title = 'Plots for ' + str(code)
    return [location_trace, trace_title, plots, plots_title]

if __name__ == '__main__':
    app.run_server(debug=True)