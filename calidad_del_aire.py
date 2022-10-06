import plotly           #(version 4.5.4) pip install plotly==4.5.4
from dash import Dash, dcc, html
import plotly.graph_objs as go
from dash.dependencies import Input, Output
import psycopg2
import pandas as pd
import datetime

# ---------- Conexión a la base de datos ----------
conexion = psycopg2.connect(host= "school-projects.cf1pikxnxsbu.us-east-2.rds.amazonaws.com",
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
    title="Progreso de la calidad del aire por mes",
    showlegend=True,
    xaxis=dict(title="Año/Mes"),
    yaxis=dict(title="AQI (Indice de calidad del aire)"),
    margin=dict(l=40, r=0, t=40, b=30)
)

# Componente 2: Comparación de la calidad del aire a partir de años.

layout2 = dict(
    title="Comparación de la calidad del aire entre años",
    showlegend=True,
    xaxis=dict(title="Mes"),
    yaxis=dict(title="AQI (Indice de calidad del aire)"),
    margin=dict(l=40, r=0, t=40, b=30)
)

# ---------

aqi_table_text = '''
# Informe sobre la calidad del aire en Cancún

| Clasificación | Indice | NO_2       | PM_10       | O_3       | PM_2.5       |
|---------------|--------|------------|-------------|-----------|--------------|
| Buena         | 1      | 0 - 50     | 0 -  25     | 0 - 60    | 0 - 15       |
| Regular       | 2      | 50 - 100   | 25 - 50     | 60 - 120  | 15 - 30      |
| Moderada      | 3      | 100 - 200  | 50 - 90     | 120 - 180 | 40 - 55      |
| Pobre         | 4      | 200 - 400  | 90 - 180    | 180 - 240 | 55 - 110     |
| Muy pobre     | 5      | > 400      | > 180       | > 240     | > 110        |
'''

app.layout = html.Div([
    dcc.Markdown(
        children=aqi_table_text,
        style={
            'font-family': 'Arial'
        }
    ),
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
    )
])

#Sentencias para abrir el servidor al ejecutar este script
if __name__ == '__main__':
    app.run_server(port=8000, debug=True)

# app = dash.Dash(__name__)
#
# df = pd.read_csv('ejemplo.csv')
# #Objetos plotly.graph
# data1 = [go.Scatter(x=df["co"],
#                     y=df["aqi"],
#                     mode="lines")]
#
# layout1 = go.Layout(title="prueba",
#                     xaxis=dict(title="co"),
#                     yaxis=dict(title="aqi"))
#
# data2 = [go.Bar(x=df["aqi"],
#                     y=df["co"])]
#
# layout2 = go.Layout(title="preuba2",
#                     xaxis=dict(title="aqi"),
#                     yaxis=dict(title="co"))
#
# #Definición del layout de la app a partir de componentes HTML y Core
# app.layout = html.Div([
#                     dcc.Graph(id='lineplot', #Creación componente Graph 1
#                     figure = {'data':data1,
#                             'layout':layout1}
#                     ),
#                     dcc.Graph(id='barplot', #Creación componente Graph 2
#                     figure = {'data':data2,
#                             'layout':layout2}
#                                     )])
#
# #Sentencias para abrir el servidor al ejecutar este script
# if __name__ == '__main__':
#     app.run_server(port=8000)


# Mostramos el contenido

# # Se verifica si hay la existencia de valores faltantes
# data_air.isnull().sum().to_frame("Count_null")
#
# # Descripción de los datos
# data_air.describe()
#
# # Información de los datos
# data_air.info()
#
# # Librerías
# import matplotlib.pyplot as plt
# import seaborn as sns
# plt.style.use('ggplot')
#
# #Correlaciones
# print("====== Tabla - Correlación de las variables ======\n")
# print(data_air.iloc[:,1:12].corr(), "\n"*2)
#
# # Matriz de correlación:
# corrmat = data_air.iloc[:,1:12].corr()
#
# # Gráfica
# plt.figure(figsize = (12, 9))
# sns.heatmap(corrmat, vmax=.8, annot=True, square=True)
#
# plt.title("Mapa de calor (Correlación de las variables)", fontsize=16)
# plt.show()
#
# # Tamaño de las gráficas
# plt.figure(figsize = (16, 16))
# cont = 0
#
# # Visualización de boxplots
# for index in data_air:
#
#     if index != "id" and index != 'unix_measurement_dt':
#         plt.subplot(4, 3, cont+1)
#
#         sns.boxplot(data = data_air, y = index, width = 0.2, linewidth = 1)
#         plt.xlabel(index)
#         plt.ylabel("")
#         cont += 1
#
# plt.subplots_adjust(top= 0.96)
# plt.suptitle("Gráficas de caja", fontsize=16)
# plt.show()
#
# # Librería
# import numpy as np
#
# # Dispersión de las variables
# sns.pairplot(data=data_air.iloc[:,1:12], hue='aqi', vars=data_air.select_dtypes(include=np.number).columns[1:12])
# plt.show()
#
# ########################################
# #         ZONA EN CONSTRUCCIÓN         #
# ########################################
#
# #########  HERRAMIENTAS #########
# # División de datos de entrenamiento y de prueba
# from sklearn.model_selection import train_test_split
#
# # Búsqueda de los mejores parámetros
# from sklearn.model_selection import GridSearchCV
#
# ######## Modelos #########
# # Vecinos más cercanos
# from sklearn.neighbors import KNeighborsClassifier
#
# # Regresión logística
# from sklearn.linear_model import LogisticRegression
#
# # Máquinas de soporte vectorial
# from sklearn.svm import SVC
#
# # Árboles de decisión
# from sklearn.tree import DecisionTreeClassifier
#
# # Árboles aleatorios
# from sklearn.ensemble import RandomForestClassifier
#
# # Método de ensamble - AdaBoost
# from sklearn.ensemble import AdaBoostClassifier
