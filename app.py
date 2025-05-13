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
    }
    .main {
        background-color: #ffa53a;
    }
    .stApp {
        background-color: #ffa53a;
    }
    .card {
        background-color: white;
        padding: 2em;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        margin: auto;
        width: 100%;
        max-width: 500px;
    }
    .logo {
        display: block;
        margin-left: auto;
        margin-right: auto;
        width: 60%;
        margin-bottom: 2em;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="card">', unsafe_allow_html=True)

st.image("Logo MANTOTAL Facility.png", use_column_width=True)
st.title("Consulta de Vales de Pedido")
st.write("Introduce el código del vale (ej: GA1200, PV 1350, CYL1500)")

codigo_vale = st.text_input("Código del Vale:")
df_vales = cargar_datos()

if codigo_vale:
    resultado = buscar_vale(df_vales, codigo_vale)
    if resultado:
        st.success(f"El vale {codigo_vale.upper()} está asignado a: {resultado}")
    else:
        st.error("Este vale no está registrado en la base de datos.")

st.markdown('</div>', unsafe_allow_html=True)
