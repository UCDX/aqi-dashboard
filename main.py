from enum import auto
from turtle import width
import pandas as pd
import numpy as np
import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
import plotly.graph_objs as go
import plotly.express as px
from dash.dependencies import Input,Output
from dash import callback_context

import plotly           #(version 4.5.4) pip install plotly==4.5.4
from dash import Dash, dcc, html, dash_table
import plotly.graph_objs as go
from dash.dependencies import Input, Output
import psycopg2

import datetime

from pmdarima import auto_arima
from statsmodels.tsa.statespace.sarimax import SARIMAX



load_figure_template('LUX')

###-------------    PREPROCESO

# --------------- Helpers ---------------


months_name = [
  'null', 'Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 
  'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'
]


# --------------- Functions ---------------


def get_db_connection():
  return psycopg2.connect(
    host= 'school-projects.cf1pikxnxsbu.us-east-2.rds.amazonaws.com',
    database= 'aqi_project',
    user= 'aqi_project_user',
    password= 'b58a74a2700d5f2bfaa2')


def compute_aqi_progress_by_loc_year_month(data):
  print('\n---------Computing aggregations----------')
  aqui_progress_df = data.groupby(
    ['full_location_name', 'calendar_year', 'calendar_month'],
    as_index = False)['aqi'].mean()
  aqui_progress_df['year-month'] = aqui_progress_df.apply(
    lambda row: f'{int(row["calendar_year"]) % 2000}/{months_name[row["calendar_month"]]}', axis = 1)
  aqui_progress_df['month_name'] = aqui_progress_df.apply(
    lambda row: f'{months_name[row["calendar_month"]]}', axis = 1)
  print('\n---------Computing aggregation: done----------')
  return aqui_progress_df


def buid_fig_aqi_progress_by_loc_year_month(data, locations):
  print('\n---------Building figures----------')
  #regions = data['full_location_name'].unique().tolist()
  fig_data = []

  for loc in locations:
    dat_region = data[ data['full_location_name'] == loc ]
    fig_data.append({
      'x': dat_region['year-month'],
      'y': dat_region['aqi'],
      'name': loc
    })
  
  print('\n---------Building figures: done----------')

  return {
    'data': fig_data,
    'layout': {
      'showlegend': True,
      'legend': {
        'orientation':'v',
        'yanchor':'bottom',
        'y':1,
        'xanchor':'center',
        'x':0.5
      },
      'xaxis': {
        'title': 'Año/Mes',
        'tickangle': -90
      },
      'yaxis': {
        'title': 'AQI (Indice de calidad del aire)'
      },
      'margin': {
        'l': 40,
        'r': 10,
        't': 40,
        'b': 80
      }
    }
  }

def buid_fig_mean_polluting_gases():
  global data_air

  df = pd.DataFrame({
    'Gas': ['co', 'no', 'no2', 'o3', 'so2', 'pm2_5', 'pm10', 'nh3'],
    'Сoncentración en μg/m3': [
      data_air['co'].mean(), 
      data_air['no'].mean(),
      data_air['no2'].mean(),
      data_air['o3'].mean(),
      data_air['so2'].mean(),
      data_air['pm2_5'].mean(),
      data_air['pm10'].mean(),
      data_air['nh3'].mean()
    ]
  })

  fig = px.bar(df, x='Gas', y='Сoncentración en μg/m3')

  return fig

# ------------------------------------ Data Warehouse usage ----------------------------------
conexion = get_db_connection()

full_extraction_query = '''
SELECT 
  D_A.AQI,
  D_A.CLASSIFICATION,
  F_AM.CO,
  F_AM.NO,
  F_AM.NO2,
  F_AM.O3,
  F_AM.SO2,
  F_AM.PM2_5,
  F_AM.PM10,
  F_AM.NH3,
  D_GEO.COUNTRY,
  D_GEO.STATE,
  D_GEO.CITY,
  D_GEO.REGION,
  --
  CONCAT(D_GEO.COUNTRY, ', ', D_GEO.STATE, ', ', D_GEO.CITY, ', ', D_GEO.REGION) AS FULL_LOCATION_NAME,
  --
  D_GEO.LAT,
  D_GEO.LON,
  D_D.FULL_DATE,
  D_D.CALENDAR_YEAR,
  D_D.CALENDAR_MONTH,
  D_D.CALENDAR_DAY,
  D_D.MONTH_NAME,
  D_D.DAY_NAME,
  D_D.DAY_OF_WEEK,
  D_T.FULL_TIME,
  D_T.TIME_HOUR,
  D_T.TIME_MINUTE
FROM FACT_AIR_MEASUREMENTS F_AM 
INNER JOIN DIM_GEOGRAPHY D_GEO 
  ON D_GEO.ID = F_AM.GEOGRAPHY_ID 
INNER JOIN DIM_DATE D_D
  ON D_D.ID = F_AM.DATE_ID 
INNER JOIN DIM_TIME D_T 
  ON D_T.ID = F_AM.TIME_ID 
INNER JOIN DIM_AQI D_A
  ON D_A.ID = F_AM.AQI_ID
'''

print('\n---------Extracting from DW----------')
data_air = pd.read_sql(full_extraction_query, conexion)
locations = data_air['full_location_name'].unique().tolist()
conexion.close()
print('\n---------Extraction: done----------')



###--------Sección para dataframes con nuevos datos  

###pronmedio ce calidad del aire en cancun
data_cancun = data_air[ data_air['full_location_name'] == 'México, Quintana Roo, Cancún, Centro' ]
counts_cancun = pd.value_counts(data_cancun['aqi'])
df2= counts_cancun.to_frame()
df3=df2
df3['percent'] = (df2['aqi'] / df2['aqi'].sum()) * 100
df3['index'] = df3.index
label_cancun = ['1','2','3','4']
fig_cancun = px.pie(values=df3['percent'], names= label_cancun, width=400, height=400, title='CANCUN', color=label_cancun, color_discrete_map={
                                 '1':'#30A4DF',
                                 '2':'#FC6ECD',
                                 '3':'#616161',
                                 '4':'#E1121E'})



### promedio de calidad del aire en cdmx

data_cdmx = data_air[ data_air['full_location_name'] == 'México, CDMX, CDMX, Ángel de la Independencia' ]
counts_cdmx = pd.value_counts(data_cdmx['aqi'])
df4= counts_cdmx.to_frame()
df5=df4
df5['percent'] = (df4['aqi'] / df4['aqi'].sum()) * 100
df5['index'] = df5.index

label_cdmx = ['4','5','1','2','3']
fig_cdmx = px.pie(values=df5['percent'], names= label_cdmx, width=400, height=400 , title='CDMX', color=label_cdmx, color_discrete_map={
                                  '4':'#E1121E',
                                  '5':'#000000',
                                 '1':'#30A4DF',
                                 '2':'#FC6ECD',
                                 '3':'#616161'
                                 
                                 })


###--------------SECCION PAREA EL MODELO DE PREDICCION DE SERIES DE TIEMPO
layout2 = dict(
    title="Predicción de calidad del aire 2023",
    showlegend=True,
    xaxis=dict(title="Mes"),
    yaxis=dict(title="AQI (Indice de calidad del aire)"),
    margin=dict(l=40, r=0, t=40, b=30)
)

def serie_aqi_mes(data):
  aqi_mean = data.groupby(
    ['full_location_name', 'calendar_year', 'calendar_month'],
    as_index = False)['aqi'].mean()

  cancun = aqi_mean.loc[aqi_mean['full_location_name'] == 'México, Quintana Roo, Cancún, Centro']
  cdmx = aqi_mean.loc[aqi_mean['full_location_name'] == 'México, CDMX, CDMX, Ángel de la Independencia']
  cancun = cancun.iloc[:,2:4]
  cdmx = cdmx.iloc[:, 2:4]
  #cancun = cancun.set_index('calendar_month')
  #cdmx= cdmx.set_index('calendar_month')
  nueva_fila1 = {'calendar_month':11,'aqi':1.247777}
  nueva_fila2 = {'calendar_month':12,'aqi':1.11112}
  nueva_fila3 = {'calendar_month':11,'aqi':3.075402}
  nueva_fila4 = {'calendar_month':12,'aqi':3.997656}
  cancun=cancun.append(nueva_fila1, ignore_index=True) 
  cancun=cancun.append(nueva_fila2, ignore_index=True) 
  cdmx=cdmx.append(nueva_fila3, ignore_index=True) 
  cdmx=cdmx.append(nueva_fila4, ignore_index=True) 
  
  return cancun, cdmx
series_ind=serie_aqi_mes(data_air)

###- cancun

modelcn = SARIMAX(series_ind[0]['aqi'], #modelo con todos los datos de cancun 2021, 2022
                order = (0,0,1), 
                seasonal_order =(0,1,1,12))
  
resultcn = modelcn.fit()

predictionscn = resultcn.predict(24, 35, #pedimos prediccion del año 2023 basandonos en los nuevos index que tendrian
                             typ = 'levels').rename("Predictions")


serie_predicha_cancun = pd.DataFrame()
serie_predicha_cancun ['aqi']= predictionscn
serie_predicha_cancun['mes'] = [1,2,3,4,5,6,7,8,9,10,11,12]

###cdmx

modelmx = SARIMAX(series_ind[1]['aqi'], #modelo con todos los datos de cdmx 2021, 2022
                order = (1,0,1), 
                seasonal_order =(0,1,0,12))
  
resultmx = modelmx.fit()

predictionsmx = resultmx.predict(24, 35, #pedimos prediccion del año 2023 basandonos en los nuevos index que tendrian
                             typ = 'levels').rename("Predictions")

serie_predicha_cdmx = pd.DataFrame()
serie_predicha_cdmx ['aqi']= predictionsmx
serie_predicha_cdmx['mes'] = [1,2,3,4,5,6,7,8,9,10,11,12]







###--------------Build the figures / dropdowns------------------------------------

x = np.random.sample(100)
y = np.random.sample(100)
z = np.random.choice(a = ['a','b','c'], size = 100)

df1 = pd.DataFrame({'x': x, 'y':y, 'z':z}, index = range(100))

fig1 = px.scatter(df1, x= x, y = y, color = z)

SIDEBAR_STYLE = {
  'top': 98,
  'left': 0,
  'bottom': 0,
  'width': '24rem',
  'height': '380vh',
  'padding': '2rem 1rem',
  'background-color': '#A4CEE7',
}


sidebar = html.Div(
  [
    html.H2('Filtros'),
    html.Hr(),
    html.P('FECHAS'),
    dbc.Nav(
      [
        #PARA LA FECHA
      ],
      vertical=True,
      pills=True,
    ),
    html.Hr(),
    html.P('CIUDAD PARA COMPARACIÓN DE AQI ENTRE AÑOS'),
    dbc.Nav(
      [
        dcc.Dropdown(locations, locations[0], id='locations-dropdown')
      ],
      vertical=True,
      pills=True,
    ),
  ],
  style=SIDEBAR_STYLE,
)


###---------------Create the layout of the app ------------------------

app = dash.Dash(external_stylesheets=[dbc.themes.LUX])

app.layout = html.Div(
  [
    # Header
    html.Div(
      [
        html.P('🌎', style={'text-align':'center','font-size':'110pt'}),
        html.H1(
          children='DASHBOARD DE CALIDAD DEL AIRE', style={'text-align':'center', 'color':'#ffffff'},
        )
      ], 
      style={'background-color': '#000000', 'height': '38vh'},
    ),
    # Body
    html.Div([
      dbc.Row([
        # Sidebar
        dbc.Col(sidebar,  width=3),
        # Main section
        dbc.Col( html.Div([
          # AQI general info.
          dbc.Row([ 
            dbc.Card(
              dbc.CardBody([
                html.H4('Promedio de calidad del aire en Cancún', style={'text-align':'center'}),
                dbc.Row([
                  dbc.Col( html.P( '1.27', style={'top':'30px', 'text-align':'right','font-size':'40pt', 'color':'#36C8DC'} )),
                  dbc.Col( html.Img(src='https://cdn-icons-png.flaticon.com/512/594/594846.png', width=68)) 
                ]),
                
                
                html.H4('Promedio de calidad del aire en Ciudad de México', style={'text-align':'center'}),
                dbc.Row([
                  dbc.Col(html.P('3.08' ,  style={'top':'30px', 'text-align':'right','font-size':'40pt', 'color':'#878787'} ) ),
                  dbc.Col(html.Img(src='https://cdn-icons-png.flaticon.com/512/594/594840.png', width=68) )  
                ]),
              ]),
              style={'top':'30px','width': '30rem', 'height': '40vh', 'left':'15px'},
            ),
              
            dbc.Card(
              dbc.CardBody([
                html.H4('AQI - Puntaje de calidad del aire', style={'text-align':'center'}),
                html.P(
                  'Significado de los puntajes de la calidad del aire', style={'text-align':'center'}
                ),
                html.Div([
                  dbc.Row([
                    dbc.Col( html.Img(src='https://cdn-icons-png.flaticon.com/512/594/594846.png', width=68)),
                    dbc.Col( html.Img(src='https://cdn-icons-png.flaticon.com/512/5853/5853933.png', width=68)),
                    dbc.Col( html.Img(src='https://cdn-icons-png.flaticon.com/512/594/594840.png', width=68)),
                    dbc.Col( html.Img(src='https://cdn-icons-png.flaticon.com/512/595/595005.png', width=68)),
                    dbc.Col( html.Img(src='https://cdn-icons-png.flaticon.com/512/481/481037.png', width=68)),
                  ]),
                  dbc.Row([
                    dbc.Col(html.P('1 Buena', style={'text-align':'left','font-size':'10pt'})),
                    dbc.Col(html.P('2 Regular', style={'text-align':'left','font-size':'10pt'})),
                    dbc.Col(html.P('3 Moderada', style={'text-align':'left','font-size':'10pt'})),
                    dbc.Col(html.P('4 Pobre', style={'text-align':'left','font-size':'10pt'})),
                    dbc.Col(html.P('5 Muy pobre', style={'text-align':'left','font-size':'10pt'}))                                            
                  ]),
                ]) 
              ]),
              style={'top':'30px','width': '38rem', 'height': '40vh', 'left':'30px'},
            )
          ]),
          # Main charts.
          dbc.Row([ 
            html.P(' '), html.P(' '),
            html.P(' '), html.P(' '),
            html.H3('Progreso de la calidad del aire por mes'),
            dcc.Graph(
              id='aqi-per-month',
              figure = buid_fig_aqi_progress_by_loc_year_month(
                compute_aqi_progress_by_loc_year_month(data_air),
                locations),
              style={
                'height': 400, 
                'width': '90%',
                'margin': 'auto'
              }
            ),

            html.P(' '), html.P(' '),
            html.H3('Comparación de la calidad del aire entre años'),
            dcc.Graph(
              id='aqi-by-year',
              style={
                'height': 300, 
                'width': '90%',
                'margin': 'auto'
              }
            ),

            html.P(' '), html.P(' '),
            html.H3('Promedio de la concentración de gases contaminantes'),
            dcc.Graph(
              id='mean-polluting-gases',
              figure = buid_fig_mean_polluting_gases(),
              style={
                'width': '90%',
                'margin': 'auto'
              }
            ),

             html.P("."), 
                                    
            html.H3('PORCENTAJES DE AQI POR CIUDAD'),
            dbc.Row([
                                                dbc.Col(
                                                      dcc.Graph(
                                                      id='percents_cancun',
                                                      figure=fig_cancun
                                                      )
                                                  ),
                                                dbc.Col( 
                                                   dcc.Graph(
                                                  id='percents_cdmx',
                                                  figure=fig_cdmx
                                                  )
                                                  ) 
                                                ])

                                  ,
                                    html.P("."), 
                                    html.H3('Predicción de calidad del aire 2023'),
                                         dcc.Graph(
                                          id='aqi_2023',
                                          figure=dict(
                                              data=[
                                                  
                                                  dict(
                                                      x= serie_predicha_cancun ['mes'],
                                                      y= serie_predicha_cancun ['aqi'],
                                                      name="CANCUN",
                                                      marker=dict(
                                                          color="cyan"
                                                      )
                                                  )
                                              ],
                                              layout=layout2
                                          ),
                                          style={
                                              'height': 300, 
                                              'width': 1000,
                                              'margin': 'auto'
                                          }
                                      ),
                                      html.P("."), 
                                       dcc.Graph(
                                          id='aqi_2023_2',
                                          figure=dict(
                                              data=[
                                                  
                                                  dict(
                                                      x= serie_predicha_cdmx ['mes'],
                                                      y= serie_predicha_cdmx ['aqi'],
                                                      name="CDMX",
                                                      marker=dict(
                                                          color="blue"
                                                      )
                                                  )
                                              ],
                                              layout=layout2
                                          ),
                                          style={
                                              'height': 300, 
                                              'width': 1000,
                                              'margin': 'auto'
                                          }
                                      )



          ])
        ]))
      ])
    ])
  ],
  style ={'background-color': '#F3F3F3 '}
)

@app.callback(
  Output('aqi-by-year', 'figure'),
  Input('locations-dropdown', 'value'))

def update_location_filter_aqi_by_year(loc):
  global data_air
  data = compute_aqi_progress_by_loc_year_month(data_air[ data_air['full_location_name'] == loc ])
  available_years = data['calendar_year'].unique().tolist()
  fig_data = []
  for year in available_years:
    year_data = data[ data['calendar_year'] == year ]
    fig_data.append({
      'x': year_data['month_name'],
      'y': year_data['aqi'],
      'name': str(year)
    })
  return {
    'data': fig_data,
    'layout': {
      'showlegend': True,
      'xaxis': {
        'title': 'Mes'
      },
      'yaxis': {
        'title': 'AQI (Indice de calidad del aire)'
      },
      'margin': {
        'l': 40,
        'r': 0,
        't': 40,
        'b': 30
      }
    }
  }

if __name__ == '__main__':
  app.run_server(debug=True, port = 8000)
