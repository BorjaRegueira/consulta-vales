import streamlit as st
import pandas as pd
import re
import requests

# URL del archivo Excel en Dropbox
dropbox_url = "https://www.dropbox.com/scl/fi/1krqq19pflt9enigikm9n/Vales-de-pedido.xlsx?rlkey=qqx033a1jnaenah607oc21ace&raw=1"

@st.cache_data
def cargar_datos():
    file = requests.get(dropbox_url).content
    xls = pd.ExcelFile(file)
    df = xls.parse("NOV18 - VALES DE PEDIDO ")
    df = df.iloc[3:, [1, 2, 3, 4, 5]]
    df.columns = ['Fecha', 'Zona', 'Inicio', 'Fin', 'Oficial']
    df = df.dropna(subset=['Zona', 'Inicio', 'Fin', 'Oficial'])
    df['Inicio'] = df['Inicio'].astype(str)
    df['Fin'] = df['Fin'].astype(str)
    df = df[df['Inicio'].str.extract(r'(\d+)')[0].notna()]
    df = df[df['Fin'].str.extract(r'(\d+)')[0].notna()]
    df['Inicio'] = df['Inicio'].str.extract(r'(\d+)')[0].astype(int)
    df['Fin'] = df['Fin'].str.extract(r'(\d+)')[0].astype(int)
    return df

def buscar_vale(df, codigo):
    match = re.match(r"([A-Z]{2,4})(\d+)", codigo.strip().upper())
    if not match:
        return None
    zona = match.group(1)
    numero = int(match.group(2))
    resultado = df[(df['Zona'] == zona) & (df['Inicio'] <= numero) & (df['Fin'] >= numero)]
    return resultado.iloc[0]['Oficial'] if not resultado.empty else None

# Estilos personalizados
st.markdown("""
    <style>
    body {
        background-color: #ffa53a;
        color: black;
    }
    .main, .stApp {
        background-color: #ffa53a;
        color: black;
    }
    .white-card {
        background-color: white;
        padding: 2em;
        border-radius: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        max-width: 600px;
        margin: 2em auto;
        text-align: center;
    }
    .stTextInput > div > div > input {
        background-color: white;
        border: 2px solid black;
        color: black;
    }
    .stAlert.success {
        border: 2px solid green;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="white-card">', unsafe_allow_html=True)

st.image("Logo MANTOTAL Facility.png", use_container_width=True)

st.markdown("## Consulta de Vales de Pedido")
st.markdown("<p style='margin-bottom: 1em;'>Introduce el código del vale (ej: GA1200, PV1350, CYL1500)</p>", unsafe_allow_html=True)

codigo_vale = st.text_input("Código del Vale:")
df_vales = cargar_datos()

if codigo_vale:
    resultado = buscar_vale(df_vales, codigo_vale)
    if resultado:
        st.success(f"El vale {codigo_vale.upper()} está asignado a: {resultado}")
    else:
        st.error("Este vale no está registrado en la base de datos.")

st.markdown('</div>', unsafe_allow_html=True)
