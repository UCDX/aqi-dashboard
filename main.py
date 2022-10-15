import plotly           #(version 4.5.4) pip install plotly==4.5.4
from dash import Dash, dcc, html, dash_table
import plotly.graph_objs as go
from dash.dependencies import Input, Output
import psycopg2
import pandas as pd
import datetime


# ---------- Conexión a la base de datos ----------
conexion = psycopg2.connect(
  host= "school-projects.cf1pikxnxsbu.us-east-2.rds.amazonaws.com",
  database= "aqi_project",
  user= "aqi_project_user",
  password= "b58a74a2700d5f2bfaa2")
# Almacenamos los datos en una dataframe
data_air = pd.read_sql("SELECT * FROM air_measurements", conexion)
# Cerramos la conexión
conexion.close()

# ---------- Preprocesamiento ----------
df = data_air
df["date"] = df["unix_measurement_dt"].apply(lambda r: datetime.datetime.fromtimestamp(r))
df["month"] = df["date"].dt.month
df["year"] = df["date"].dt.year

month_aqi_df = df.groupby(by=["year", "month"], as_index=False)["aqi"].mean()
month_aqi_df['aqi'] = month_aqi_df['aqi'].apply(lambda aqi_val: round(aqi_val, 2))
months_name = ['null', 'Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 
    'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
month_aqi_df['year-month'] = month_aqi_df.apply(lambda row: f'{int(row["year"]) % 2000}/{months_name[int(row["month"])]}', axis = 1)
month_aqi_df['month-name'] = month_aqi_df.apply(lambda row: f'{months_name[int(row["month"])]}', axis = 1)



counts = pd.value_counts(data_air['aqi'])
df2= counts.to_frame()
df3=df2
df3['percent'] = (df2['aqi'] / df2['aqi'].sum()) * 100
df3['index'] = df3.index



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


# ---------- Dashboard ----------

app = Dash(__name__)
app.title = "Calidad del aire"

# Componente 1: Calidad del aire por meses
data1 = dict(
  x=month_aqi_df["year-month"],
  y=month_aqi_df["aqi"],
  name="Calidad del aire por meses",
  marker=dict(
    color="rgb(26, 118, 255)"
  )
)
layout1 = dict(
  #title="Progreso de la calidad del aire por mes",
  showlegend=True,
  xaxis=dict(title="Año/Mes"),
  yaxis=dict(title="AQI (Indice de calidad del aire)"),
  margin=dict(l=40, r=0, t=40, b=30)
)

# Componente 2: Comparación de la calidad del aire a partir de años.

layout2 = dict(
  #title="Comparación de la calidad del aire entre años",
  showlegend=True,
  xaxis=dict(title="Mes"),
  yaxis=dict(title="AQI (Indice de calidad del aire)"),
  margin=dict(l=40, r=0, t=40, b=30)
)

# Componente 3: #Para porcentajes
data3 = dict(
  x=df3["index"],
  y=df3["percent"],
  name="Porcentajes",
  type='bar'
    
)

layout3 = dict(
  #title="Porcentajes del puntaje de calidad del aire",
  xaxis=dict(title="Puntaje calidad del aire"),
  yaxis=dict(title="Porcentaje")
)


#---------------------------------------------------------------------------
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
  html.H1('Dashboard de calidad del aire'),
  dcc.Tabs(
    id="tabs-example-graph",
    value='tab-0-example-graph',
    children=[
      dcc.Tab(label='Tabla de clasificación', value='tab-0-example-graph'),
      dcc.Tab(label='Cancún', value='tab-1-example-graph'),
      dcc.Tab(label='Ciudad de México', value='tab-2-example-graph'),
  ]),
  html.Div(id='tabs-content-example-graph')
])

@app.callback(
  Output('tabs-content-example-graph', 'children'),
  Input('tabs-example-graph', 'value'))
def render_content(tab):
  if tab == 'tab-0-example-graph':
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
          figure=dict(
            data=[data1],
            layout=layout1
          ),
          style={
            'height': 300, 
            #'width': 1300,
            'margin': 'auto'
          }
        ),

        html.H3('Comparación de la calidad del aire entre años'),

        dcc.Graph(
          id='aqi-by-year',
          figure=dict(
            data=[
              dict(
                x=month_aqi_df[month_aqi_df["year"] == 2021]["month-name"],
                y=month_aqi_df[month_aqi_df["year"] == 2021]["aqi"],
                name="Calidad del aire en 2021",
                marker=dict(
                  color="rgb(26, 118, 255)"
                )
              ),
              dict(
                x=month_aqi_df[month_aqi_df["year"] == 2022]["month-name"],
                y=month_aqi_df[month_aqi_df["year"] == 2022]["aqi"],
                name="Calidad del aire en 2022",
                marker=dict(
                  color="red"
                )
              )
            ],
            layout=layout2
          ),
          style={
            'height': 300, 
            #'width': 1300,
            'margin': 'auto'
          }
        ),

        html.H3('Porcentajes del puntaje de calidad del aire'),

        dcc.Graph(
          id='aqi-percent',
          figure=dict(
            data=[data3],
            layout=layout3
          ),
          style={
            'height': 300, 
            'width': 1300,
            'type':'bar'
          }
        )
                 
    ])
  elif tab == 'tab-2-example-graph':
    return html.Div([
      html.H3('Tab content 2'),
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

if __name__ == '__main__':
  app.run_server(debug=True, port = 8000)
