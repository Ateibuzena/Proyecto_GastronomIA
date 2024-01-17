import streamlit as st
import pandas as pd
import numpy as np

st.title(body=":violet[Tu recomendador favorito]")
df_filtrado = pd.read_csv(r"Data/Restaurantes_mexico.csv")
df_filtrado.drop("Unnamed: 0", axis=1, inplace=True)
df_filtrado.rename(columns = {"name":"Name"}, inplace=True)


lista_restaurantes = set(df_filtrado.Name)

lista_puntuacion = [i for i in range(1,11)]


opcion_seleccion = st.selectbox(label = ":violet[SELECCIONA UN RESTAURANTE]", options=lista_restaurantes, key="s_1")

opcion_puntuacion = st.selectbox(label = ":violet[SELECCIONA UNA PUNTUACIÓN]", options=lista_puntuacion, key="s_2")

#Utilizamos st.session_state para almacenar la lista_puntuados

if "lista_puntuados" not in st.session_state:
    st.session_state.lista_puntuados = []

#Función añadir

def añadir(opcion_seleccion, opcion_puntuacion):
     
    nombres_restaurantes = [restaurante["Name"] for restaurante in st.session_state.lista_puntuados]

    if opcion_seleccion not in nombres_restaurantes:
        diccionario = {"Name": opcion_seleccion,
                       "Puntuacion": opcion_puntuacion}
        
        st.session_state.lista_puntuados.append(diccionario)
        st.write(":violet[Tu puntuación se ha guardado exitosamente]")

       

    else:

        st.write(":violet[Este restaurante ya está puntuado]")   


# Función recomendar

def recomendar():
    if len(st.session_state.lista_puntuados) == 0:
        return st.write(":violet[No has puntuado ningún restaurante]")
    # Aplicar one-hot encoding a varias columnas
    columnas_a_codificar = ['alcohol', 'smoking_area', 'dress_code', 'accessibility', 'price', 'Rambience', 'area', 'parking_lot']

    df_dummies = pd.get_dummies(df_filtrado, columns=columnas_a_codificar)

    df_dummies.drop(["smoking_area_none", "rating",	"food_rating",	"service_rating",	"Entre Semana",	"Sabado","Domingo"], axis=1, inplace=True)

    # Identificar columnas con tipo de dato booleano
    columnas_booleanas = df_dummies.select_dtypes(include='bool').columns

    # Cambiar el tipo de dato de booleano a entero solo para las columnas booleanas
    df_dummies[columnas_booleanas] = df_dummies[columnas_booleanas].astype(int)

    # Creamos el df del usuario
    df_usuario = pd.DataFrame(data = st.session_state.lista_puntuados)

    # Concatenar los DataFrames basándose en la columna común
    df_usuario = pd.merge(df_dummies, df_usuario, on='Name', how='left') 

    # Aquí nos quedamos sólo con los restaurantes puntuados
    
    df_pesos = df_usuario[df_usuario["Puntuacion"] >0].copy()   

    # Asignandole valor a las caracteristicas de cada restaurante segun la puntuacion que dió el usuario
    for columna in df_pesos.columns:
        if columna != "Name" and columna != "Puntuacion":
            df_pesos[columna] = df_pesos[columna]*df_pesos["Puntuacion"]
    
    # Calculando el peso de cada característica
    usuario_pesos = df_pesos.drop(["Name", "Puntuacion"], axis=1).sum()

    usuario_pesos = usuario_pesos/usuario_pesos.sum()

    # Creando df de restaurantes que no visitó el usuario
    df_restaurantes = df_usuario[~(df_usuario["Puntuacion"] > 0)].copy()

    # Asignandole el peso correspondientes a cada característica según el usuario de los demás restaurantes
    weighted_movies_matrix = list()

    for punto, restaurant in zip(usuario_pesos.values, df_restaurantes.iloc[:, 1:-1].values):
        weighted_movies_matrix.append(punto*restaurant)

    weighted_movies_matrix = pd.DataFrame(data = weighted_movies_matrix, columns = df_restaurantes.drop(["Name", "Puntuacion"], axis=1).columns)

    # Creando df de donde saldrá las recomendaciones
    df_recomendador = pd.concat([df_restaurantes, weighted_movies_matrix.sum(axis = 1)], axis = 1)

    df_recomendador.rename(columns= {0 : "Recomendacion"}, inplace=True)
    # Ordenando los restaurantes de mayor peso a menor
    df_recomendador.sort_values("Recomendacion", ascending = False, inplace=True)

    st.session_state.lista_puntuados.clear()

    alcohol = []
    smoking_area = []
    codigo_vest = []
    accesibilidad = []
    precio = []
    ambiente = []
    area = []
    parking = []
    rating = []

    for nombre in df_recomendador[df_recomendador["Recomendacion"] > 0]["Name"].to_list():

        # Filtra df_filtrado para obtener la fila correspondiente al nombre
        fila = df_filtrado[df_filtrado["Name"] == nombre].iloc[0]  # Se asume que solo hay una fila con ese nombre
        
        # Agrega los valores directamente a las listas
        alcohol.append(fila['alcohol'].replace("_", " ").capitalize())
        smoking_area.append(fila['smoking_area'].replace("_", " ").capitalize())
        codigo_vest.append(fila['dress_code'].replace("_", " ").capitalize())
        accesibilidad.append(fila['accessibility'].replace("_", " ").capitalize())
        precio.append(fila['price'].replace("_", " ").capitalize())
        ambiente.append(fila['Rambience'].replace("_", " ").capitalize())
        area.append(fila['area'].replace("_", " ").capitalize())
        parking.append(fila['parking_lot'].replace("_", " ").capitalize())
        rating.append(fila['rating'].round(2))


    # Filtrado de recomendaciones para el usuario
    st.session_state.lista_puntuados = {"Restaurantes" : df_recomendador[df_recomendador["Recomendacion"] > 0]["Name"].to_list(),
                                        "Alcohol" : alcohol,
                                        "Zona de fumadores": smoking_area,
                                        "Código de vestimenta": codigo_vest,
                                        "Accesibilidad": accesibilidad,
                                        "Precio" : precio,
                                        "Ambiente" : ambiente,
                                        "Área" : area,
                                        "Parking" : parking,
                                        "Rating" : rating}

    
    





st.button(key="c_1", label=":violet[Añadir]", on_click= lambda: añadir(opcion_seleccion, opcion_puntuacion))
st.button(key="c_2", label=":violet[Iniciar recomendación]", on_click= recomendar)
st.table(st.session_state.lista_puntuados) 




