import os
import pandas as pd
import PySAM.Pvwattsv8 as pvwatts
import PySAM.Pvsamv1 as pvsam
import numpy as np

def run_pv_simulation(input_file, output_file, system_size_mw=50, dc_ac_ratio=1.2, losses=14):
    """
    Ejecuta una simulación PV usando PySAM.
    
    Args:
        input_file (str): Ruta al archivo TMY procesado
        output_file (str): Ruta donde guardar los resultados
        system_size_mw (float): Tamaño del sistema en MW DC
        dc_ac_ratio (float): Ratio DC/AC
        losses (float): Pérdidas del sistema en porcentaje
    """
    print(f"\nProcesando archivo: {input_file}")
    
    # Leer latitud y longitud desde la segunda línea del archivo TMY3
    with open(input_file, 'r') as f:
        f.readline()  # Saltar la primera línea
        meta_line = f.readline().strip()  # Leer la segunda línea
    meta_parts = meta_line.split(',')
    lat = float(meta_parts[1])
    lon = float(meta_parts[2])
    
    # Leer el archivo TMY3 ignorando las dos primeras líneas de encabezado
    df = pd.read_csv(input_file, skiprows=2)
    
    # Configurar PySAM
    pv = pvwatts.new()
    
    # Configurar parámetros del sistema
    pv.SystemDesign.system_capacity = system_size_mw * 1000  # Convertir a kW
    pv.SystemDesign.dc_ac_ratio = dc_ac_ratio
    pv.SystemDesign.losses = losses
    pv.SystemDesign.array_type = 0  # Montaje abierto fijo
    pv.SystemDesign.tilt = 25      # Inclinación típica
    pv.SystemDesign.azimuth = 180  # Orientación al norte (hemisferio sur)
    
    # Crear diccionario con el recurso solar
    solar_resource_data = {
        'lat': lat,
        'lon': lon,
        'tz': -4,  # Zona horaria
        'year': df['Year'].tolist(),
        'month': df['Month'].tolist(),
        'day': df['Day'].tolist(),
        'hour': df['Hour'].tolist(),
        'minute': df['Minute'].tolist(),
        'dn': df['DNI'].tolist(),
        'df': df['DHI'].tolist(),
        'gh': df['GHI'].tolist(),
        'wspd': df['WindSpeed'].tolist(),
        'tdry': df['DryBulb'].tolist(),
        'tdew': df['DewPoint'].tolist(),
        'rhum': df['RelativeHumidity'].tolist(),
        'pres': df['Pressure'].tolist(),
        'wdir': df['WindDirection'].tolist()
    }
    
    # Asignar el recurso solar como diccionario
    pv.SolarResource.solar_resource_data = solar_resource_data
    
    # Ejecutar simulación
    pv.execute()
    
    # Obtener resultados
    ac_power = pv.Outputs.ac  # Potencia AC en kW
    
    # Crear DataFrame con resultados
    results_df = pd.DataFrame({
        'Fecha': pd.date_range(start='2014-01-01', periods=8760, freq='H'),
        'Potencia_AC_kW': ac_power
    })
    
    # Guardar resultados
    results_df.to_csv(output_file, index=False)
    print(f"Resultados guardados en: {output_file}")

def main():
    # Directorio base
    base_dir = '/home/josefa_montoya/Josefamontoya/josefamontoya/PRUEBA_2'
    
    # Lista de archivos a procesar
    files_to_process = [
        'salvador_pysam.csv',
        'calama_pysam.csv',
        'Vallenar_pysam.csv'
    ]
    
    # Procesar cada archivo
    for file_name in files_to_process:
        input_path = os.path.join(base_dir, file_name)
        output_path = os.path.join(base_dir, file_name.replace('_pysam.csv', '_pv_results.csv'))
        run_pv_simulation(input_path, output_path)

if __name__ == "__main__":
    main() 