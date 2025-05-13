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
    df = xls.parse("NOV18 - VALES DE PEDIDO ", dtype=str)

    # Detectar encabezado dinámico
    header_row_idx = df[df.iloc[:, 2] == 'ZONA'].index[0] + 1
    df = df.iloc[header_row_idx:, :]
    df.columns = ['Fecha', 'Zona', 'Inicio', 'Fin', 'Oficial', 'Observaciones'] + list(df.columns[6:])
    
    df = df[['Fecha', 'Zona', 'Inicio', 'Fin', 'Oficial', 'Observaciones']]
    df = df.dropna(subset=['Zona', 'Inicio', 'Fin', 'Oficial'])

    # Limpiar y filtrar entradas no numéricas
    df = df[df['Inicio'].str.match(r'^\\d+$')]
    df = df[df['Fin'].str.match(r'^\\d+$')]
    df['Inicio'] = df['Inicio'].astype(int)
    df['Fin'] = df['Fin'].astype(int)
    return df

# Función para buscar vale
def buscar_vale(df, codigo):
    match = re.match(r"([A-Z]{2,4})(\\d+)", codigo.strip().upper())
    if not match:
        return None, None
    zona = match.group(1)
    numero = int(match.group(2))
    resultado = df[(df['Zona'] == zona) & (df['Inicio'] <= numero) & (df['Fin'] >= numero)]
    if not resultado.empty:
        oficial = resultado.iloc[0]['Oficial']
        observaciones = resultado.iloc[0]['Observaciones'] if pd.notna(resultado.iloc[0]['Observaciones']) else None
        return oficial, observaciones
    return None, None

# Interfaz de la app
st.title("Consulta de Vales de Pedido")
st.write("Introduce el código del vale (ej: GA1200, PV 1350, CYL1500)")

codigo_vale = st.text_input("Código del Vale:")

df_vales = cargar_datos()

if codigo_vale:
    oficial, observaciones = buscar_vale(df_vales, codigo_vale)
    if oficial:
        st.success(f"El vale {codigo_vale.upper()} está asignado a: {oficial}")
        if observaciones:
            st.error(f"Observaciones: {observaciones}")
    else:
        st.error("Este vale no está registrado en la base de datos.")
