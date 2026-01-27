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

st.set_page_config(page_title='Visão Empresa',page_icon='📈', layout='wide')
#--------------------------------------------------------------------------------------------------------------------
#Funções
def order_metric(df1):
        #1. Quantidade de pedidos por dia.
        df_aux = df1.loc[:, ['ID', 'Order_Date']].groupby( 'Order_Date' ).count().reset_index()
        df_aux.columns = ['order_date', 'qtde_entregas']
        # gráfico
        fig = px.bar( df_aux, x='order_date', y='qtde_entregas' )
        return fig
    
def traffic_order_share(df1):
        #3. Distribuição dos pedidos por tipo de tráfego.
        df_aux = df1.loc[:,['ID', 'Road_traffic_density']].groupby( 'Road_traffic_density' ).count().reset_index()
        df_aux = df_aux.loc[df_aux['Road_traffic_density'] != "NaN", :]
        df_aux['entregas_perc'] = df_aux['ID'] / df_aux['ID'].sum()
        # gráfico
        fig = px.pie( df_aux, values='entregas_perc', names='Road_traffic_density' )
        return fig
    
def traffic_order_city(df1):
        #4. Comparação do volume de pedidos por cidade e tipo de tráfego.
        df_aux = df1.loc[:, ['ID', 'City', 'Road_traffic_density']].groupby( ['City', 'Road_traffic_density'] ).count().reset_index()
        df_aux = df_aux.loc[df_aux['City'] != "NaN", :]
        df_aux = df_aux.loc[df_aux['Road_traffic_density'] != "NaN", :]
        # gráfico
        fig = px.scatter( df_aux, x='City', y='Road_traffic_density', color='City', size='ID')
        return fig
    
def order_by_week(df1):
        #2. Quantidade de pedidos por semana.
        df1['week_of_year'] = df1['Order_Date'].dt.strftime( "%U" )
        df_aux = df1.loc[:, ['ID', 'week_of_year']].groupby( 'week_of_year' ).count().reset_index()
        # gráfico
        fig = px.line( df_aux, x='week_of_year', y='ID' )
        return fig

def order_share_by_week(df1):
        #5. A quantidade de pedidos por entregador por semana
        df_aux1 = df1.loc[:, ['ID', 'week_of_year']].groupby( 'week_of_year' ).count().reset_index()
        df_aux2 = df1.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby( 'week_of_year').nunique().reset_index()
        df_aux = pd.merge( df_aux1, df_aux2, how='inner' )
        df_aux['order_by_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']
        # gráfico
        fig = px.line( df_aux, x='week_of_year', y='order_by_delivery' )
        return fig
    
def country_maps(df1):
        #6. A localização central de cada cidade por tipo de tráfego.
        df_aux=df1.loc[:,['City','Road_traffic_density','Delivery_location_latitude',
        'Delivery_location_longitude']].groupby(['City', 'Road_traffic_density']).median().reset_index()
        df_aux = df_aux.loc[df_aux['City'] != 'NaN']
        df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN']
        # Desenhar o mapa
        map = folium.Map()
        
        for index, location_info in df_aux.iterrows():
            folium.Marker( [location_info['Delivery_location_latitude'],
                    location_info['Delivery_location_longitude']],
                    popup=location_info[['City', 'Road_traffic_density']]).add_to(map)
        folium_static(map, width=1024, height=600)


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

# Visão empresa

#================================================
# BARRA LATERAL NO STREAMLIT
#================================================
st.header("Marketplace - Visão Cliente", divider=True)

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

st.sidebar.markdown ( '---' )
st.sidebar.markdown('### Powered by Comunidade DS')
# Filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]
#Filtro de transito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

#================================================
# LAYOUT NO STREAMLIT
#================================================

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'] )
with tab1:
    fig=order_metric(df1)
    st.markdown('# Orders by Day')
    st.plotly_chart(fig, width='stretch')
    
      
    col1, col2 = st.columns ( 2 )
    
with col1:
    fig = traffic_order_share(df1)
    st.markdown('## Traffic Order Share')
    st.plotly_chart(fig, width='stretch')
    
with col2:
    fig = traffic_order_city(df1)
    st.markdown('## Traffic Order City')
    st.plotly_chart(fig, width='stretch')
    
        
with tab2:
    fig = order_by_week(df1)
    st.markdown ('# Order by Week')
    st.plotly_chart(fig, width='stretch')

   
    fig = order_share_by_week(df1)
    st.markdown ('# Order share by Week')
    st.plotly_chart(fig, width='stretch')

    
with tab3: 
    st.markdown ('# Country Maps')
    country_maps (df1) 
    
        
    







































