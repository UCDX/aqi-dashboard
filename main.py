import plotly           #(version 4.5.4) pip install plotly==4.5.4
from dash import Dash, dcc, html, dash_table
import plotly.graph_objs as go
from dash.dependencies import Input, Output
import psycopg2
import pandas as pd
import datetime


# --------------- Helpers ---------------


months_name = [
  'null', 'Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 
  'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'
]


# --------------- Functions ---------------


def get_db_connection():
  return psycopg2.connect(
    host= "school-projects.cf1pikxnxsbu.us-east-2.rds.amazonaws.com",
    database= "aqi_project",
    user= "aqi_project_user",
    password= "b58a74a2700d5f2bfaa2")


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
      'xaxis': {
        'title': 'Año/Mes'
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


# ------------------------------------ Data Warehouse usage ----------------------------------
conexion = get_db_connection()

full_extraction_query = """
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
"""

print('\n---------Extracting from DW----------')
data_air = pd.read_sql(full_extraction_query, conexion)
locations = data_air['full_location_name'].unique().tolist()
conexion.close()
print('\n---------Extraction: done----------')


# ---------- Dashboard ---------- 

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Calidad del aire"
app.layout = html.Div([
  html.H1('Dashboard de calidad del aire'),
  dcc.Tabs(
    id="tabs-example-graph",
    value='tab-0-example-graph',
    children=[
      dcc.Tab(label='Tabla de clasificación', value='tab-0-example-graph'),
      dcc.Tab(label='Índice de la calidad del aire', value='tab-1-example-graph'),
      dcc.Tab(label='Nombre temporal', value='tab-2-example-graph'),
  ]),
  html.Div(id='tabs-content-example-graph')
])


@app.callback(
  Output('tabs-content-example-graph', 'children'),
  Input('tabs-example-graph', 'value'))
def render_content(tab):
  if tab == 'tab-0-example-graph':
    clasificacion = pd.DataFrame()

    clasificaciones = ['Buena', 'Regular', 'Moderada', 'Pobre', 'Muy pobre']
    indice= [1, 2, 3, 4, 5]
    no2=['0-50', '50 - 100', '100 - 200', '200 - 400', '> 400 ']
    pm10=['0-25', '25 - 50', '50 - 90', '90 - 180', '> 180 ']
    o3=['0-60', '60 - 120', '120 - 180', '180 - 240', '> 240 ']
    pm2=['0-15', '15 - 30', '40 - 55', '55 - 110', '> 110 ']

    clasificacion['Clasificacion'] = clasificaciones

    clasificacion['Indice'] = indice
    clasificacion['NO_2'] = no2
    clasificacion['PM_10'] = pm10
    clasificacion['O_3'] = o3
    clasificacion['PM_2.5'] = pm2

    return html.Div([ 
      html.H3(
        'Clasificación de la calidad del aire'),
        dash_table.DataTable(
          id='table',
          columns=[{"name": i, "id": i} for i in clasificacion.columns],
          data=clasificacion.to_dict('records'),)      
    ])
  elif tab == 'tab-1-example-graph':
    return html.Div([
      html.H3(
        'Progreso de la calidad del aire por mes'),
        dcc.Graph(
          id='aqi-per-month',
          figure = buid_fig_aqi_progress_by_loc_year_month(
            compute_aqi_progress_by_loc_year_month(data_air),
            locations),
          style={
            'height': 300, 
            #'width': 1300,
            'margin': 'auto'
          }
        ),

        html.H3('Comparación de la calidad del aire entre años'),
        dcc.Dropdown(locations, locations[0], id='locations-dropdown'),

        dcc.Graph(
          id='aqi-by-year',
          style={
            'height': 300, 
            #'width': 1300,
            'margin': 'auto'
          }
        ),

        html.H3('Porcentajes del puntaje de calidad del aire'),

        dcc.Graph(
          id='aqi-percentage',
          style={
            'height': 300, 
            'width': 1300,
            'type':'bar'
          }
        )
                 
    ])
  elif tab == 'tab-2-example-graph':
    return html.Div([
      html.H3('Tab content 2 - Todo aquí es de ejemplo - Cambiar.'),
      dcc.Graph(
        id='graph-2-tabs-dcc',
        figure={
          'data': [{
            'x': [1, 2, 3],
            'y': [5, 10, 6],
            'type': 'bar'
          }]
        }
      )
    ])


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


@app.callback(
  Output('aqi-percentage', 'figure'),
  Input('locations-dropdown', 'value'))
def update_location_filer_aqi_percentage(loc):
  global data_air
  data = data_air[ data_air['full_location_name'] == loc ]
  counts = pd.value_counts(data['aqi'])
  df2= counts.to_frame()
  df3=df2
  df3['percent'] = (df2['aqi'] / df2['aqi'].sum()) * 100
  df3['index'] = df3.index
  return {
    'data': [{
      'x': df3["index"],
      'y': df3["percent"],
      'name': 'Porcentajes',
      'type': 'bar'
    }],
    'layout': {
      'showlegend': True,
      'xaxis': {
        'title': 'Índice de la calidad del aire'
      },
      'yaxis': {
        'title': 'Porcentaje'
      }
    }
  }


if __name__ == '__main__':
  app.run_server(debug=True, port = 8000)
