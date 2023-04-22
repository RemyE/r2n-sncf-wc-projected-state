import streamlit as st # installer avec pip install et doc dans : https://docs.streamlit.io/
import pickle
import pandas as pd

# on récupère notre dico de df
# c'est la seule subtilité de streamlit : on ne veut pas charger le dico
# à chaque fois qu'on interragit avec l'appli : trop long !
# donc on va mettre en cache cette partie qui ne bougera plus de toute l'exécution

@st.cache
def load_data():
    with open('D:/ESTACA/4A/Projet industriel/analyse_des_donnees/dict_df.pkl', 'rb') as file:
        dict_df = pickle.load(file)
    return dict_df

dict_df = load_data()

LIST_RACINE = list(dict_df.keys()) 

# on écrit l'interface

# le titre
st.title("Interface d'accès aux données")

# un premier block : on veut choisir la racine à afficher
# on sélectionne dans une liste déroulante et on extrait du dico
st.subheader("Choisir le périmètre d'affichage")
racine = st.selectbox('Racine : ', LIST_RACINE)
df = dict_df[racine]
df

# maintenant, on veut choisir une colonne et tracer un graphe
st.subheader("Choisir la colonne à tracer :")
col = st.selectbox('Col : ', df.columns[1:])
df_col = df.loc[:, ['x_time',col]]
st.line_chart(df_col, x  = 'x_time', y = col)

st.subheader("Choisir la colonne à tracer :")
col = st.selectbox('Col : ', df.columns[1:], key = 'test')
df_col = df.loc[:, ['x_time',col]]
st.line_chart(df_col, x  = 'x_time', y = col)

# pour lancer l'appli : 
# cd "analyse des données"
# streamlit run interface_simpliste.py