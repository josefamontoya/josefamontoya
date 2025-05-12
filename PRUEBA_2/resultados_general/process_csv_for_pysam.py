import pandas as pd
import os

def process_csv_for_pysam(input_file, output_file, lat, lon):
    """
    Procesa un archivo CSV para que sea compatible con PySAM en formato TMY3 estándar.
    
    Args:
        input_file (str): Ruta al archivo CSV de entrada
        output_file (str): Ruta donde guardar el archivo procesado
        lat (float): Latitud del sitio
        lon (float): Longitud del sitio
    """
    # Leer el archivo CSV original
    df = pd.read_csv(input_file)
    
    # Seleccionar y renombrar columnas estándar TMY3
    columnas_tmy3 = {
        'Year': 'Year',
        'Month': 'Month',
        'Day': 'Day',
        'Hour': 'Hour',
        'Minute': 'Minute',
        'GHI': 'GHI',
        'DNI': 'DNI',
        'DHI': 'DHI',
        'Tdry': 'DryBulb',
        'Tdew': 'DewPoint',
        'RH': 'RelativeHumidity',
        'Pres': 'Pressure',
        'Wspd': 'WindSpeed',
        'Wdir': 'WindDirection'
    }
    # Filtrar y renombrar
    df_tmy3 = df[list(columnas_tmy3.keys())].rename(columns=columnas_tmy3)
    
    # Crear el encabezado TMY3 estándar
    site_name = os.path.basename(input_file).replace('_processed.csv', '')
    header = f"""TMY3 data for {site_name}\n{site_name}, {lat}, {lon}, -4, 0, TMY3, W/m2, C, %, m/s, deg, mm\n"""
    
    # Guardar el archivo con el nuevo formato
    with open(output_file, 'w') as f:
        f.write(header)
        df_tmy3.to_csv(f, index=False)
    
    print(f"Archivo procesado guardado en: {output_file}")

def main():
    # Directorio base
    base_dir = '/home/josefa_montoya/Josefamontoya/josefamontoya/PRUEBA_2'
    
    # Definir las coordenadas para cada sitio
    sites = {
        'salvador': (-26.25, -69.05),
        'calama': (-22.47, -68.93),
        'Vallenar': (-28.57, -70.76)
    }
    
    # Procesar cada archivo
    for site_name, (lat, lon) in sites.items():
        input_file = os.path.join(base_dir, f'{site_name}_processed.csv')
        output_file = os.path.join(base_dir, f'{site_name}_pysam.csv')
        process_csv_for_pysam(input_file, output_file, lat, lon)

if __name__ == "__main__":
    main() 