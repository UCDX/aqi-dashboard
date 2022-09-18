import plotly           #(version 4.5.4) pip install plotly==4.5.4
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Input, Output
import psycopg2
import pandas as pd

# Conectamos la base de datos
conexion = psycopg2.connect(host= "school-projects.cf1pikxnxsbu.us-east-2.rds.amazonaws.com",
                            database= "aqi_project",
                            user= "aqi_project_user",
                            password= "b58a74a2700d5f2bfaa2")

# Almacenamos los datos en una dataframe
data_air = pd.read_sql("SELECT * FROM air_measurements", conexion)
# Cerramos la conexión
conexion.close()

app = dash.Dash(__name__)

df = data_air
#Objetos plotly.graph
data1 = [go.Scatter(x=df["co"],
                    y=df["aqi"],
                    mode="lines")]

layout1 = go.Layout(title="prueba",
                    xaxis=dict(title="co"),
                    yaxis=dict(title="aqi"))

data2 = [go.Bar(x=df["aqi"],
                    y=df["co"])]

layout2 = go.Layout(title="preuba2",
                    xaxis=dict(title="aqi"),
                    yaxis=dict(title="co"))

#Definición del layout de la app a partir de componentes HTML y Core
app.layout = html.Div([
                    dcc.Graph(id='lineplot', #Creación componente Graph 1
                    figure = {'data':data1,
                            'layout':layout1}
                    ),
                    dcc.Graph(id='barplot', #Creación componente Graph 2
                    figure = {'data':data2,
                            'layout':layout2}
                                    )])

#Sentencias para abrir el servidor al ejecutar este script
if __name__ == '__main__':
    app.run_server(port=8000)
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
