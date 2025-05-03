import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def process_tmy_file(input_file, output_file):
    # Leer el archivo TMY, incluyendo las primeras dos líneas que contienen la información de ubicación
    with open(input_file, 'r') as f:
        header_lines = [next(f) for _ in range(2)]
    
    # Extraer latitud y longitud de la segunda línea
    location_data = header_lines[1].split(',')
    lat = float(location_data[5].strip())  # Índice 5 para latitud
    lon = float(location_data[6].strip())  # Índice 6 para longitud
    
    # Leer los datos principales
    df = pd.read_csv(input_file, skiprows=2)
    
    # Verificar y corregir datos
    df['GHI'] = df['GHI'].clip(lower=0)
    df['DHI'] = df['DHI'].clip(lower=0)
    df['DNI'] = df['DNI'].clip(lower=0)
    df['Temperature'] = df['Temperature'].clip(lower=-20, upper=50)
    df['Wind Speed'] = df['Wind Speed'].clip(lower=0, upper=30)
    
    # Solo procesar Solar Zenith Angle si la columna existe
    if 'Solar Zenith Angle' in df.columns:
        df['Solar Zenith Angle'] = df['Solar Zenith Angle'].clip(lower=0, upper=180)
    
    df['Year'] = 2022
    
    # Guardar el archivo con las líneas de encabezado originales
    with open(output_file, 'w') as f:
        f.write(header_lines[0])
        f.write(header_lines[1])
        df.to_csv(f, index=False)
    
    print(f"Archivo procesado y guardado como: {output_file}")
    print(f"Latitud: {lat}, Longitud: {lon}")

# Configuración
TipoData = 2  # 1: Iquique, 2: Sevilla, 3: Jodhpur

if TipoData == 1:
    process_tmy_file('/home/josefa_montoya/Josefamontoya/josefamontoya/Iquique_tmy.csv', 
                    'Iquique_tmy_corregido.csv')
elif TipoData == 2:
    process_tmy_file('/home/josefa_montoya/Josefamontoya/josefamontoya/sevilla_tmy.csv', 
                    'Sevilla_tmy_corregido.csv')
elif TipoData == 3:
    process_tmy_file('/home/josefa_montoya/Josefamontoya/josefamontoya/jodhpur_tmy.csv', 
                    'Jodhpur_tmy_corregido.csv')
else:
    print("Tipo de datos no válido") 