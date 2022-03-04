import os
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import  date, timedelta
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import warnings
# ========================================================================================#
warnings.filterwarnings('ignore')
os.chdir(os.path.dirname(os.path.realpath('__file__')))
# ========================================================================================#

all_country_df = pd.read_csv('data/countries-aggregated.csv')
world_df = pd.read_csv('data/worldwide-aggregate.csv')
world_df['Confirmed_diff'] = world_df['Confirmed'].diff()
world_df['Deaths_diff'] = world_df['Deaths'].diff()
world_df.fillna(0, inplace=True)
world_df['Confirmed_diff_precent'] = world_df['Confirmed_diff'] / world_df['Confirmed']
world_df['Deaths_diff_precent'] = world_df['Deaths_diff'] / world_df['Deaths']
reference_df = pd.read_csv('data/reference.csv')

# =========================================================================================#
def geo_Map(date_value, Case_Type):
    all_country_special_day_df = all_country_df[all_country_df['Date']==date_value].reset_index(drop=True)
    geo_df = all_country_special_day_df.merge(reference_df[['Combined_Key','iso3','Lat', 'Long_']],
                                 how='left', left_on='Country', right_on='Combined_Key')
    geo_df.dropna(inplace=True)
    fig = px.scatter_geo(
        geo_df, 
        lat='Lat',
        lon='Long_',
        locations="iso3", 
        size=Case_Type,
        hover_name='Country',
        projection="natural earth",
        size_max=15,
    )
    
    fig.update_geos(
        bgcolor='#f8f8f8',
        resolution=50,
#         showcoastlines=True, coastlinecolor="RebeccaPurple",
#         showland=True, landcolor="#e8e8e8",
        showocean=True, oceancolor="#f9f9f9",
#         showlakes=True, lakecolor="Blue",
#         showrivers=True, rivercolor="Blue"
    )
    
    fig.update_layout(autosize=False, height=280,margin=dict(l=5, r=5, b=0, t=0, pad=4),
                      paper_bgcolor="#f8f8f8", )
    return fig

# ========================================================================================#
def top_Country_bar_Chart(date_value, Case_Type, agg_type):
    if agg_type =='day':
        special_day_df = all_country_df[all_country_df['Date']==date_value].reset_index(drop=True)[['Country',Case_Type]]
        date_values = date_value.split('-')
        date_value = date(int(date_values[0]), int(date_values[1]), int(date_values[2]))
        previous_day = str(date_value - timedelta(1))
        previous_day_df = all_country_df[all_country_df['Date']==previous_day].reset_index(drop=True)[['Country',Case_Type]]
        final_df = previous_day_df.merge(special_day_df, how='inner', on='Country')
        final_df.columns = ['Country', 'X', 'Y']
        final_df['Y_new'] = final_df['Y'] - final_df['X']
        df = final_df[['Country', 'Y_new']].sort_values('Y_new', ascending=False).head(15)
    else:
        df = all_country_df[all_country_df['Date']==date_value].reset_index(drop=True)[['Country',Case_Type]]
        df.columns = ['Country', 'Y_new']
        df = df.sort_values('Y_new', ascending=False).head(15)
        
    df.sort_values('Y_new', ascending=True, inplace=True) 
    lay = go.Layout(paper_bgcolor='#fff',
                    plot_bgcolor='rgba(0,0,0,0)')

    fig = go.Figure(data=[go.Bar(
                x=df['Y_new'] , y=df['Country'],
                text=[str(format(round(i),",")) for i in df['Y_new']],
                marker=dict(color='#088fbd',
                    line=dict(
                        color='#f1f1f1',
                        width=1),
                ),
                textposition='inside',
                orientation='h'
            )], layout=lay)

    fig.update_xaxes(title='x', visible=False, showticklabels=False)
    fig.update_yaxes(title='', visible=True, showticklabels=True)
    fig.update_layout(autosize=False, margin=dict(l=0, r=5, b=5, t=5, pad=4),
                      paper_bgcolor="#f8f8f8")
    return fig
#=========================================================================================#
def area_chart_world(Case_Type, agg_type):
    if agg_type == 'day':
        col_y = Case_Type + "_diff"
    else:
        col_y = Case_Type
    
     
    fig = px.area(world_df, x='Date', y=col_y,template='plotly_white')
    fig.update_layout(plot_bgcolor='rgba(0, 0, 0, 0)')
    fig.update_xaxes(title='', visible=True, showticklabels=True)
    fig.update_yaxes(title='', visible=True, showticklabels=True)
    fig.update_layout(autosize=False, height=205, margin=dict(l=0, r=15, b=0, t=5, pad=4),
                      paper_bgcolor='#f8f8f8')
    return fig

# ========================================================================================#
def area_chart_special_country(Case_Type, agg_type, country_Name):
    if agg_type == 'day':
        Case_Type = Case_Type + "_diff"
        
    country_df = all_country_df[all_country_df['Country']==country_Name]
    country_df.loc[:,['Confirmed_diff']] = country_df['Confirmed'].diff()
    country_df.loc[:,['Deaths_diff']] = country_df['Deaths'].diff()
    country_df.loc[:,['Confirmed_diff']] = country_df.loc[:,['Confirmed_diff']].apply(lambda x:np.maximum(x, 0))
    country_df.loc[:,['Deaths_diff']] = country_df.loc[:,['Deaths_diff']].apply(lambda x:np.maximum(x, 0))
    country_df.fillna(0, inplace=True)
    
    fig = px.area(country_df, x='Date', y=Case_Type,template='plotly_white')
    fig.update_layout(plot_bgcolor='rgba(0, 0, 0, 0)')
    fig.update_xaxes(title='', visible=True, showticklabels=True)
    fig.update_yaxes(title='', visible=True, showticklabels=True)
    fig.update_layout(autosize=False, height=210, margin=dict(l=0, r=15, b=0, t=5, pad=4),
                      paper_bgcolor="#f8f8f8")
    return fig

# ========================================================================================#
countryLabel = [{'label': country, 'value': country} for country in [*all_country_df.Country.unique()]]
agg_dict = {'day':'New', 'cumulative':'Cumulative'}
case_dict = {'Deaths':'Deaths', 'Confirmed':'Positive'}
# =======================================================================================#
def calcuate_precent(date_value, case_Type, agg_Type):
    date_values = date_value.split('-')
    previous_day = str(date(int(date_values[0]), int(date_values[1]), int(date_values[2])) - timedelta(1))
    if agg_Type == 'day':
        col = case_Type+'_diff'
    else:
        col = case_Type
        
    current_value = (world_df[world_df['Date']==date_value][col].values *100)[0]
    previous_value = (world_df[world_df['Date']==previous_day][col].values *100)[0]
    deathPrecent  = str(round(((current_value-previous_value) / previous_value)*100,2))+"% vs Previous Day"
    return deathPrecent
# =======================================================================================#
def calcuateCase(date_value, case_Type, agg_Type):
    if agg_Type == 'day':
        col = case_Type + '_diff'
    else:
        col = case_Type

    return format(int(world_df[world_df['Date']==date_value][col]), ',')

# ===============================layout=================================================#
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, 
                external_stylesheets=external_stylesheets,
                update_title='Loading...',
                title='Covid-19 Tracker'

)

server = app.server

app.layout = html.Div([
    html.Div([
#=========================================Header===============================================#
        html.H2(['Global Covid-19 Tracker'], 
            style={'color': 'rgb(248, 248, 248)',
                   'paddingTop': '10px',
                   'height':'25px',
                   'textAlign': 'center',
                   'fontSize': '35px',
                   'fontFamily': 'initial'}),
    
        html.H5(['January 21, 2020 - October 21,2021'], 
            style={'textAlign':'center',
                  'color':'#F8F8F8',
                  'paddingBottom':'7px',
                  'fontSize': '12px',
                  'fontFamily': 'cursive'})
    
    ], className='row', style={'backgroundColor':'#001f3f'}),

#===========================================Input=================================================#
    #input
    html.Div([
        # list input
        html.Div([
#         ===================================Cumumlative or New=====================================         #
            # cumulativeorDay
            dcc.Dropdown(
                id='Input',
                options=[
                    {'label': 'Cumulative', 'value': 'cumulative'},
                    {'label': 'New', 'value': 'day'}
                ],
                value='day',
                clearable=False,
                searchable=False
        )], className='three columns', style={'backgroundColor':'#f8f8f8', 'color':'#000', 'width':'27%'}),
        
#         ===================================Country List=====================================         #        
        # country list
        html.Div([
            dcc.Dropdown(
                id='Input2',
                options=countryLabel,
                value='Egypt',
                clearable=False
        )], className='three columns', style={'backgroundColor':'#f8f8f8', 'color':'#000','width':'27%', 'margin-left':'2%'}),

#         ===================================Cases Type=====================================         #        
        # casesType
        html.Div([
            dcc.Dropdown(
                id='Input3',
                options=[
                    {'label': 'Positive', 'value': 'Confirmed'},
                    {'label': 'Deaths', 'value': 'Deaths'},
                ],
                value='Confirmed',
                clearable=False,
                searchable=False
        )], className='three columns', style={'backgroundColor':'#f8f8f8', 'color':'#000', 'width':'29%', 'margin-left':'2%'}),

#         ===================================Date Input=====================================         #            
        #date input
        html.Div([
            dcc.DatePickerSingle(
                id='datetime',
                min_date_allowed=date(2020, 1, 22),
                max_date_allowed=date(2021, 10, 21),
                initial_visible_month=date(2021, 10, 21),
                date=date(2021, 10, 21),
                display_format = 'DD/MM/YYYY',
                style={"align": "right"}
            ),
        ], className='two columns',style={'backgroundColor':'#f8f8f8', 'color':'#000', 'width':'11%', 'margin-left':'2%'})
        
        
    ], className='row',style={'backgroundColor':'#f8f8f8', 'color':'#000'}),
    
#===========================================Output==================================================#
    # output
    html.Div([
        
#         ===================================Left Side=====================================         #
        # left
        html.Div([
            
            #left top
            html.Div([
                html.P(id='topLeft', style={'textAlign':'center', 'paddingTop': '3px'}),
                dcc.Loading(
                    id="loading-1",
                    children=[dcc.Graph(id='output', figure={}),],
                    type="default",
                ),
                
            ], className='row', style={'backgroundColor': '#f8f8f8', 'maxHeight': '240px', 'borderBottom':'1px outset #000'}),
            
            #left bottom
            html.Div([
                html.P(id='country', style={'textAlign':'center','paddingTop': '5px',}),
                dcc.Loading(
                    id="loading-2",
                    children=[dcc.Graph(id='outputBottom', figure={}),],
                    type="default",
                ),
            ], className='row', style={ 'backgroundColor': '#f8f8f8', 'maxHeight': '200px'})
            
        ], className='three columns',
        style={"textAlign": 'center', 'width': '35%', 'margin': '0px', 'backgroundColor': '#7FDBFF'}),
        
#         ===================================Mid Side=====================================           #        
        # mid
        html.Div([
            # mid top
            html.Div([
                html.P('Natural Earth Map', style={'textAlign':'center', 'paddingTop': '5px', 'backgroundColor':'#39CCCC'}),
                dcc.Loading(
                    id="loading-3",
                    children=[dcc.Graph(id='output2', figure={})],
                    type="default",
                ),
                
            ], className='row', style={'backgroundColor':'#f8f8f8'}),
            
            # bottom-mid chart
            html.Div([
                html.P('Total Cases in The World',
                       style={'textAlign':'center', 'paddingTop':'5px',
                              'borderBottom':'1px outset #000', 'backgroundColor':'#39CCCC'}),
                # left-bottom 
                html.Div([
                    html.H4('Postive', style={'textAlign':'center', 'font-family': 'ui-rounded'}),
                    html.H6(id='positiveCumulative', style={'textAlign':'center', 'font-family': 'cursive', 'color':'#088fbd'}),
                    html.P(id='positivePrecent', style={'textAlign':'center', 'font-family': 'system-ui'}),

                ], className='two columns',
                style={"textAlign": 'center', 'width': '50%', 'margin': '0px', }),
                
                # right-bottom
                html.Div([
                    html.H4('Death', style={'textAlign':'center', 'font-family': 'ui-rounded'}),
                    html.H6(id='DeathsCumulative', style={'textAlign':'center', 'font-family': 'cursive', 'color':'#d50b0b'}),
                    html.P(id='deathPrecent', style={'textAlign':'center', 'font-family': 'system-ui'}),
                    
                ], className='two column',
                style={"textAlign": 'center', 'width': '50%', 'border-left':'1px solid #000', 'margin': '0px'}),
                
            ], className='row', style={'backgroundColor':'#f8f8f8'}),
            
        ], className='five columns',
        style={"textAlign": 'center', 'width': '30%', 'margin': '0px', 'backgroundColor': '#7FDBFF',
               'border-left':'1px inset #000','border-right':'1px inset #000'}),
        
#         ===================================Right Side=====================================             #
        # right
        html.Div([
            html.P(id='leftTitle', style={'textAlign':'center', 'paddingTop': '5px', 'backgroundColor':'#f8f8f8'}),
            dcc.Loading(
                id="loading-4",
                children=[dcc.Graph(id='barChart', figure={})],
                type="default",
            )
        ], className='four columns',
        style={"textAlign": 'center', 'width': '35%', 'margin': '0px', 'backgroundColor': '#f8f8f8'})
    ], className='row'),

    # floor    
    html.Div([    
    ],className='row', style={'backgroundColor':'#001f3f', 'height':'10px'}),
    
], className='row', style={'backgroundColor':'#f8f8f8', 'marginTop': '-12px' })

#============================================CallBack=====================================================#

@app.callback(
    Output('output', 'figure'),
    Output('outputBottom', 'figure'),
    Output('output2', 'figure'),
    Output('barChart', 'figure'),
    Output('topLeft', 'children'),
    Output('country', 'children'),
    Output('leftTitle', 'children'),
    Output('positiveCumulative', 'children'),
    Output('DeathsCumulative', 'children'),
    Output('positivePrecent', 'children'),
    Output('deathPrecent', 'children'),
    Input('datetime', 'date'),
    Input('Input', 'value'),
    Input('Input2', 'value'),
    Input('Input3', 'value')
)

#==============================================Update Output========================================#

def update_output(date_value, agg_type, countryName, casesType):

    fig=area_chart_world(casesType,agg_type)

    fig2=area_chart_special_country(casesType, agg_type, countryName)
    
    fig_geo = geo_Map(date_value, casesType)
        
    fig_barchart = top_Country_bar_Chart(date_value, casesType, agg_type)
    
    title_left_top = agg_dict[agg_type] +  " " + case_dict[casesType] +" Cases in The World" 
    
    title_left_bottom = agg_dict[agg_type] + " " + case_dict[casesType] +" Cases in " + countryName

    left_title = 'Top Countries have '+ agg_dict[agg_type] + " " + case_dict[casesType] +" Cases"
    
    positiveCase  = calcuateCase(date_value, 'Confirmed', agg_type)
    
    deathCase  = calcuateCase(date_value, 'Deaths', agg_type)
    
    positivePrecent  = calcuate_precent(date_value, 'Confirmed', agg_type)
    
    deathPrecent  = calcuate_precent(date_value, 'Deaths', agg_type)
    
    return fig, fig2, fig_geo, fig_barchart, title_left_top, title_left_bottom, left_title, positiveCase, deathCase, positivePrecent, deathPrecent


#================================================Run Code==============================================#

if __name__ == '__main__':
    app.run_server(debug=True)