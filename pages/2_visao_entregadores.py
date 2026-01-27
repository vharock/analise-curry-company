import pandas as pd
from datetime import datetime
import streamlit as st
import io
import re
import plotly.express  as px
import plotly.graph_objects as go
import folium
from haversine import haversine
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config(page_title='Visão Entregadores',page_icon='🚚', layout='wide')
#--------------------------------------------------------------------------------------------------------------------
#Funções

def top_delivers(df1, top_asc):
                
        df2 = (df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']]
                .groupby(['City', 'Delivery_person_ID'])
                .mean()
                .sort_values(['City', 'Time_taken(min)'],ascending=top_asc)
                .reset_index())

        df_aux01 =df2.loc[df2['City'] == 'Metropolitian', :].head(10)
        df_aux02 =df2.loc[df2['City'] == 'Urban', :].head(10)
        df_aux03 =df2.loc[df2['City'] == 'Semi-Urban', :].head(10)
        df_aux = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index(drop=True)
               
        return df_aux

def clean_code(df1):
    ''' Esta função tem a responsabilidade de limpar o dataset
        Tipos de limpeza:
        1. Remoção dos NaN
        2. Mudança do tipo do dado da coluna
        3. Remoção dos espaços entre as variáveis
        4. Formatação da coluna data
        5. Limpeza da coluna de tempo
        input: dataframe
        output: dataframe
    '''
      
    # ( Conceitos de seleção condicional )
    linhas_vazias= (df['Delivery_person_Age'] != 'NaN ')
    df1 = df1.loc[linhas_vazias, :].copy()
    
    linhas_vazias= (df['Road_traffic_density'] != 'NaN')
    df1 = df1.loc[linhas_vazias, :].copy()
    
    linhas_vazias= (df['City'] != 'NaN ')
    df1 = df1.loc[linhas_vazias, :].copy()
    
    linhas_vazias= (df['Festival'] != 'NaN ')
    df1 = df1.loc[linhas_vazias, :].copy()
    
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype( int )
    
    # Conversao de texto/categoria/strings para numeros decimais
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype( float )
    
    # Conversao de texto para data
    df1['Order_Date'] = pd.to_datetime( df1['Order_Date'], format='%d-%m-%Y' )
    
    # Retirando vazio e tranformando para inteiro
    linhas_vazias = (df1['multiple_deliveries'] != 'NaN ')
    df1 = df1.loc[linhas_vazias, :].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype( int )
    
    # Retirando espaços vazios
    df1.loc[ :, 'ID'] = df1.loc[:,'ID'].str.strip()
    df1.loc[ :, 'Road_traffic_density'] = df1.loc[:,'Road_traffic_density'].str.strip()
    df1.loc[ :, 'Type_of_order'] = df1.loc[:,'Type_of_order'].str.strip()
    df1.loc[ :, 'Type_of_vehicle'] = df1.loc[:,'Type_of_vehicle'].str.strip()
    df1.loc[ :, 'City'] = df1.loc[:,'City'].str.strip()
    df1.loc[ :, 'Festival'] = df1.loc[:,'Festival'].str.strip()
    # limpando a colouna time taken
    
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.split( '(min) ')[1] )
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype( int )

    return df1

#------------------------------------------------------------------- Inicio da estrutura lógica -------------------------------------------------------------------------
#Import dataset
df= pd.read_csv("dataset/train.csv")
df1= df.copy()

#limpando código
df1 = clean_code(df)

#Visão entregadores

# BARRA LATERAL NO STREAMLIT
#================================================
st.header("Marketplace - Visão Entregadores", divider=True)

image = Image.open('logo.png')
st.sidebar.image(image, width=120)

st.sidebar.markdown ( '# Cury Company' )
st.sidebar.markdown ( '## Fastest Delivery in Town' )
st.sidebar.markdown ( '---' )
st.sidebar.markdown ( '## Selecione uma data limite' )

date_slider = st.sidebar.slider(
        'Até qual valor?' , 
         value=datetime(2022,4,13),
         min_value=datetime(2022,2,11),
         max_value=datetime(2022,4,6),
         format= 'DD-MM-YYYY')
                 
st.sidebar.markdown ( '---' )

traffic_options = st.sidebar.multiselect(
    'Quais as condições de trânsito?',
    ['Low','Medium','High','Jam'],
    default= ['Low','Medium','High','Jam'])
Weatherconditions_options = st.sidebar.multiselect(
    'Quais as condições de clima?',
    ['conditions Sunny','conditions Stormy','conditions Sandstorms','conditions Cloudy','conditions Windy','conditions Fog'],
    default= ['conditions Sunny','conditions Stormy','conditions Sandstorms','conditions Cloudy','conditions Windy','conditions Fog'])


st.sidebar.markdown ( '---' )
st.sidebar.markdown('### Powered by Comunidade DS')
# Filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]
#Filtro de transito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]
#Filtro de condição
linhas_selecionadas = df1['Weatherconditions'].isin(Weatherconditions_options)
df1 = df1.loc[linhas_selecionadas, :]
#================================================
# LAYOUT NO STREAMLIT
#================================================

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', '_', '_'] )

with tab1:
    with st.container():
        st.title('Overall Metrics')
        
        col1,col2,col3,col4 = st.columns(4,gap='large')
        with col1: 
            
            maior_idade = df1.loc[:,'Delivery_person_Age'].max()
            col1.metric ('Maior idade', maior_idade)
            
        with col2: 
            
            menor_idade = df1.loc[:,'Delivery_person_Age'].min()
            col2.metric ('Menor idade', menor_idade) 
            
        with col3: 
            
            melhor_condicao= df1.loc[:,'Vehicle_condition'].max()
            col3.metric ('Maior nota', melhor_condicao) 
            
        with col4: 
           
            pior_condicao = df1.loc[:,'Vehicle_condition'].min()
            col4.metric(' Pior condicao ', pior_condicao)

    with st.container():
        st.markdown('''___''')
        st.title('Avaliações')
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('##### Avaliação media por entregador')
            df_aux = (df1.loc[:,['Delivery_person_ID','Delivery_person_Ratings']]
                      .groupby('Delivery_person_ID')
                      .mean()
                      .reset_index())
            st.dataframe(df_aux)
            
        with col2:
            st.markdown('##### Avaliação media por transito')
            df_aux = (df1.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']]
                      .groupby('Road_traffic_density')
                      .agg({'Delivery_person_Ratings': ['mean', 'std']}))
            df_aux.columns = ['delivery_rating_mean', 'delivery_rating_std']
            df_aux.reset_index()
            st.dataframe(df_aux)
            
            st.markdown('##### Avaliação media por clima')
            df_aux = (df1.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']]
                    .groupby('Weatherconditions')
                    .agg({'Delivery_person_Ratings': ['mean', 'std']}))
            df_aux.columns = ['delivery_mean', 'delivery_std']
            df_aux.reset_index()
            st.dataframe(df_aux)

    with st.container(): 
        st.markdown('''___''')
        st.title('Velocidade de entrega')
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('##### Top entregadores mais rapidos')
            df_aux=top_delivers(df1, top_asc=True)
            st.dataframe(df_aux)

                          
        with col2:
            st.markdown('##### Top entregadores mais lentos')
            df_aux=top_delivers(df1, top_asc=False)
            st.dataframe(df_aux)
            
           
            
            



























        
    





































