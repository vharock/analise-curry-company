import streamlit as st
from PIL import Image

st.set_page_config(
    page_title='Home',
    page_icon='🎯'
)

 

#image_path = '/Users\VHAROCK/Documents/Repos/analise de dados - aulas/PYTHON/ciclo5 - restaurantes/'   
#image_path + 
image = Image.open('logo.png')
st.sidebar.image(image,width=120)

st.sidebar.markdown ( '# Cury Company' )
st.sidebar.markdown ( '## Fastest Delivery in Town' )
st.sidebar.markdown ( '---' )

st.write('# Cury Company Growth Dashboard' )

st.markdown(
    '''
    Growth Dashboard foi construído para acompanhar as metricas de crescimento dos entregadores e restaurantes.
    ### Como utilizar esse dashboard?
    - Visão Empresa:
        - Visão Gerencial: Metricas gerais de comportamento
        - Visão Tática: Indicadores semanais de crescimento
        - Visão Geográfica: Insights de geolocalização.
    - Visão Entregador:
        - Acompanhamento dos indicadores semanais de crescimento
    - Visão Restaurante:
        - Indicadores semanais de crescimento dos restaurantes
    ## Ask for help
        - @VictorAndrade
    '''
)