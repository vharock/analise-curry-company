import pandas as pd
from datetime import datetime
import streamlit as st
import io
import re
import numpy as np
import plotly.express  as px
import plotly.graph_objects as go
import folium
from haversine import haversine
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config(page_title='Visão Restaurantes',page_icon='🧫', layout='wide')
#--------------------------------------------------------------------------------------------------------------------
#Funções
def avg_std_time_on_traffic(df1):
                
            df_aux = (df1.loc[:, ['City', 'Road_traffic_density', 'Time_taken(min)']]
                      .groupby(['City',  'Road_traffic_density'])
                      .agg({'Time_taken(min)': ['mean', 'std']}))
            df_aux.columns = ['time_avg', 'time_std']
            df_aux = df_aux.reset_index()
            fig= px.sunburst(df_aux,path=['City','Road_traffic_density'], values='time_avg',
                             color='time_std',color_continuous_scale='RdBu',
                             color_continuous_midpoint=np.average(df_aux['time_std']))
            return fig
    
def avg_std_time_graph(df1) :
            
               df_aux = df1.loc[:,['City', 'Time_taken(min)']].groupby('City').agg({'Time_taken(min)':['mean','std']})
               df_aux.columns = ['time_mean', 'time_std']
               df_aux = df_aux.reset_index()

               fig= go.Figure()
               fig.add_trace(go.Bar(name='Control', x=df_aux['City'], y=df_aux['time_mean'],error_y=dict(type='data',array=df_aux['time_std'])))
               fig.update_layout(barmode='group')
               
               return fig 

def avg_std_time_delivery(df1,festival,op):
            ''' 
                Esta função calcula o tempo médio e o desvio padrão do tempo de entrega.
                Parâmetros:
                    Input:
                        -df: Dataframe com os dados necessarios para o calculo
                        -op: Tipo de operação que precisa ser calculado
                        'time_mean': calcula o tempo medio
                        'time_std': calcula o desvio padrao do tempo
                        
                    Output:
                        -df: Dataframe com 2 colunas e 1 linha
            '''
            
            df_aux = (df1.loc[:, ['Time_taken(min)', 'Festival']]
                          .groupby('Festival')
                          .agg({'Time_taken(min)': ['mean', 'std']}))
            df_aux.columns = ['time_mean', 'time_std']
            df_aux = df_aux.reset_index()
            df_aux = np.round(df_aux.loc[df_aux['Festival'] == festival, op],2)
            
            return df_aux

def distance(df1,fig):
    if fig == False:
            cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
            df1['distance']= df1.loc[:, cols].apply(lambda x:
                haversine(
                        (x['Restaurant_latitude'], x['Restaurant_longitude']),
                        (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)
            avg_distance = np.round(df1['distance'].mean(),2)
            return avg_distance
    else:
            cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
            df1['distance']= df1.loc[:, cols].apply(lambda x:
                haversine(  (x['Restaurant_latitude'], x['Restaurant_longitude']),
                            (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)
            avg_distance = df1.loc[:,['City', 'distance']].groupby('City').mean().reset_index()
            fig = go.Figure( data= [go.Pie( labels=avg_distance['City'], values=avg_distance['distance'], pull=[0.01,0.01,0.01])])
            
            return fig
    

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

#Visão Restaurantes

# BARRA LATERAL NO STREAMLIT
#================================================
st.header("Marketplace - Visão Restaurantes", divider=True)

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
        
        col1,col2,col3,col4,col5,col6 = st.columns(6)
        with col1: 
            
            qtd_unico = len(df1.loc[:, 'Delivery_person_ID'].unique())
            col1.metric ('Entregadores Únicos', qtd_unico)
            
        with col2:
            avg_distance= distance(df1,fig=False)
            col2.metric ('Distancia media das entregas', avg_distance)
                 
        with col3:
            df_aux=avg_std_time_delivery(df1,'Yes','time_mean')
            col3.metric ('Tempo medio das entregas com festival',  df_aux) 
            
                      
        with col4: 
            df_aux=avg_std_time_delivery(df1,'Yes','time_std')
            col4.metric ('Desvio medio das entregas com festival',  df_aux)
           
                      
        with col5: 
            df_aux=avg_std_time_delivery(df1,'No','time_mean')
            col5.metric ('Tempo medio das entregas sem festival',  df_aux)
            
            
        with col6: 
            df_aux=avg_std_time_delivery(df1,'No','time_std')
            col6.metric ('Desvio medio das entregas sem festival',  df_aux)
           
           
        with st.container():
               st.markdown("""---""")
               col1,col2 = st.columns(2)

        with col1:
               fig= avg_std_time_graph(df1)
               st.plotly_chart(fig)
               
        with col2:
            df_aux = (df1.loc[:, ['City', 'Type_of_order', 'Time_taken(min)']]
                      .groupby(['City', 'Type_of_order'])
                      .agg({'Time_taken(min)': ['mean', 'std']}))
            df_aux.colums = ['time_avg','time_std']
            df_aux = df_aux.reset_index()
            st.dataframe(df_aux)
            
                        
        with st.container():
            st.markdown("""---""")
            st.title('Distribuição do tempo')
            col1,col2 = st.columns(2)

        with col1:
            fig= distance(df1, fig=True)
            st.plotly_chart(fig)
                        
              
        with col2:
            fig=avg_std_time_on_traffic(df1)
            st.plotly_chart(fig)

            
           
                           
                    

























