import streamlit as st
import pandas as pd
import numpy as np

#st.title(body = ":violet[RECOMENDADOR DE RESTAURANTES DE MADRID]")
st.markdown("<h1 style='text-align: center; color: pink;'>RECOMENDADOR DE RESTAURANTES DE MADRID</h1>", unsafe_allow_html=True)

df_filtrado = pd.read_csv(r"Data/df_filtrado_madrid.csv")
df_filtrado.drop("Unnamed: 0", axis=1, inplace=True)

lista_nombres = set(df_filtrado.Nombre)
lista_puntuacion = [i for i in range(1,11)]

opcion_seleccion = st.selectbox(label = ":violet[SELECCIONA UN RESTAURANTE]", options=lista_nombres)

#puntuacion_seleccion = st.number_input(key="i_1", label=":violet[Puntua el restaurante del 1 al 10:]", step=1, max_value=10, min_value=1)
puntuacion_seleccion = st.selectbox(label = ":violet[SELECCIONA UNA PUNTUACIÓN]", options=lista_puntuacion, key="s_2")


# Utilizar st.session_state para almacenar la lista_puntuados
if 'lista_puntuados' not in st.session_state:
    st.session_state.lista_puntuados = []

def añadir(opcion_seleccion, puntuacion_seleccion):

    nombres_restaurantes = [restaurante["Nombre"] for restaurante in st.session_state.lista_puntuados]
    
    if opcion_seleccion not in nombres_restaurantes:
        diccionario = {"Nombre": opcion_seleccion,
                    "Puntuacion": puntuacion_seleccion}
        st.session_state.lista_puntuados.append(diccionario)

        st.write(":violet[Puntuación añadida exitosamente]")
    else:
        st.write(":violet[La puntuación de este restaurante ya existe]")

def recomendar():

    if len(st.session_state.lista_puntuados) == 0:
        return st.write(":violet[No puntuaste ningún restaurante]")
    
    df_usuario = pd.DataFrame(st.session_state.lista_puntuados)
    # Concatenar los DataFrames basándose en la columna común
    df_usuario = pd.merge(df_filtrado, df_usuario, on='Nombre', how='left')

    # Creando el df de pesos de los restaurantes que visitó el usuario
    df_pesos = df_usuario[df_usuario["Puntuacion"] > 0].copy()

    for columna in df_pesos.columns:
        if columna != "Nombre" and columna != "Puntuacion":
            df_pesos[columna] = df_pesos[columna]*df_pesos["Puntuacion"]

    usuario_pesos = df_pesos.drop(["Nombre", "Puntuacion"], axis=1).sum()
    usuario_pesos = usuario_pesos/usuario_pesos.sum()

    # Creando df de restaurantes que no visitó el usuario
    df_restaurantes = df_usuario[~(df_usuario["Puntuacion"] > 0)].copy()

    # Asignandole el peso correspondientes a cada característica según el usuario de los demás restaurantes
    weighted_movies_matrix = list()

    for punto, restaurant in zip(usuario_pesos.values, df_restaurantes.iloc[:, 1:-1].values):
        weighted_movies_matrix.append(punto*restaurant)

    weighted_movies_matrix = pd.DataFrame(data = weighted_movies_matrix, columns = df_restaurantes.drop(["Nombre", "Puntuacion"], axis=1).columns)

    # Creando df de donde saldrá las recomendaciones
    df_recomendador = pd.concat([df_restaurantes, weighted_movies_matrix.sum(axis = 1)], axis = 1)

    df_recomendador.rename(columns= {0 : "Recomendacion"}, inplace=True)
    # Ordenando los restaurantes de mayor peso a menor
    df_recomendador.sort_values("Recomendacion", ascending = False, inplace=True)

    st.session_state.lista_puntuados.clear()
    # Filtrado de recomendaciones para el usuario
    st.session_state.lista_puntuados = df_recomendador[df_recomendador["Recomendacion"] > 0]["Nombre"].to_list()


st.button(key="c_1", label=":violet[Añadir]", on_click= lambda: añadir(opcion_seleccion, puntuacion_seleccion))

st.button(key="c_2", label=":violet[Iniciar recomendación]", on_click= recomendar)

st.table(st.session_state.lista_puntuados)




    

