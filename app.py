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

    # Cargar desde fila 4 en adelante (índice 3)
    df = df.iloc[3:, [1, 2, 3, 4, 5]]
    df.columns = ['Fecha', 'Zona', 'Inicio', 'Fin', 'Oficial']
    df = df.dropna(subset=['Zona', 'Inicio', 'Fin', 'Oficial'])

    # Convertir a texto antes de limpiar
    df['Inicio'] = df['Inicio'].astype(str)
    df['Fin'] = df['Fin'].astype(str)

    # Extraer y limpiar los números
    df = df[df['Inicio'].str.extract(r'(\\d+)')[0].notna()]
    df = df[df['Fin'].str.extract(r'(\\d+)')[0].notna()]
    df['Inicio'] = df['Inicio'].str.extract(r'(\\d+)')[0].astype(int)
    df['Fin'] = df['Fin'].str.extract(r'(\\d+)')[0].astype(int)

    return df

def buscar_vale(df, codigo):
    match = re.match(r"([A-Z]{2,4})(\\d+)", codigo.strip().upper())
    if not match:
        return None
    zona = match.group(1)
    numero = int(match.group(2))
    resultado = df[(df['Zona'] == zona) & (df['Inicio'] <= numero) & (df['Fin'] >= numero)]
    return resultado.iloc[0]['Oficial'] if not resultado.empty else None

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
