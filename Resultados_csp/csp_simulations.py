import os
import pandas as pd
import PySAM.Pvwattsv8 as pv

def load_tmy_data(file_path):
    """Carga datos TMY desde un archivo CSV"""
    # Leer los metadatos de las primeras dos líneas
    with open(file_path, 'r') as f:
        header1 = f.readline().strip().split(',')
        header2 = f.readline().strip().split(',')
    
    # Crear diccionario de metadatos
    metadata = dict(zip(header1, header2))
    
    # Leer los datos
    df = pd.read_csv(file_path, skiprows=2)
    
    return df, metadata

def create_csp_system(config_type='default'):
    """Crea y configura un sistema CSP con diferentes configuraciones"""
    system = pv.default("PVWattsNone")
    
    # Configuración base común
    system.SystemDesign.system_capacity = 100000  # 100 MW
    
    if config_type == 'default':
        # Configuración por defecto (actual)
        system.SystemDesign.dc_ac_ratio = 1.2
        system.SystemDesign.inv_eff = 96
        system.SystemDesign.losses = 14.075
        system.SystemDesign.array_type = 2  # Single axis tracking
        system.SystemDesign.gcr = 0.4
        system.SystemDesign.tilt = 0
        system.SystemDesign.azimuth = 180
    elif config_type == 'high_efficiency':
        # Configuración de alta eficiencia
        system.SystemDesign.dc_ac_ratio = 1.3
        system.SystemDesign.inv_eff = 98
        system.SystemDesign.losses = 10.0
        system.SystemDesign.array_type = 1  # Two axis tracking
        system.SystemDesign.gcr = 0.5
        system.SystemDesign.tilt = 0
        system.SystemDesign.azimuth = 180
    elif config_type == 'optimized_land':
        # Configuración optimizada para uso de terreno
        system.SystemDesign.dc_ac_ratio = 1.1
        system.SystemDesign.inv_eff = 95
        system.SystemDesign.losses = 12.0
        system.SystemDesign.array_type = 2
        system.SystemDesign.gcr = 0.6
        system.SystemDesign.tilt = 0
        system.SystemDesign.azimuth = 180
    
    return system

def calculate_capacity_factor(annual_energy_kwh, capacity_kw):
    """Calcula el factor de capacidad real"""
    hours_per_year = 8760
    return (annual_energy_kwh / (capacity_kw * hours_per_year)) * 100

def run_simulation(tmy_data, metadata, location_name, config_type='default'):
    """Ejecuta la simulación para una ubicación específica con configuración dada"""
    system = create_csp_system(config_type)
    
    # Configurar datos meteorológicos
    weather_data = {
        'year': tmy_data['Year'].tolist(),
        'month': tmy_data['Month'].tolist(),
        'day': tmy_data['Day'].tolist(),
        'hour': tmy_data['Hour'].tolist(),
        'minute': tmy_data['Minute'].tolist(),
        'dn': tmy_data['DNI'].tolist(),
        'df': tmy_data['DHI'].tolist(),
        'gh': tmy_data['GHI'].tolist(),
        'tdry': tmy_data['Temperature'].tolist(),
        'wspd': tmy_data['Wind Speed'].tolist(),
        'lat': float(metadata['Latitude']),
        'lon': float(metadata['Longitude']),
        'tz': float(metadata['Time Zone'])
    }
    
    system.SolarResource.solar_resource_data = weather_data
    
    # Ejecutar simulación
    system.execute()
    
    # Obtener resultados y convertir a GWh
    annual_energy_gwh = system.Outputs.annual_energy / 1e6
    monthly_energy_gwh = [e / 1e6 for e in system.Outputs.monthly_energy]
    
    # Calcular el factor de capacidad real
    capacity_factor = calculate_capacity_factor(system.Outputs.annual_energy, system.SystemDesign.system_capacity)
    
    # Crear DataFrame con los resultados mensuales
    monthly_data = pd.DataFrame({
        'Ubicación': [location_name] * 12,
        'Configuración': [config_type] * 12,
        'Mes': range(1, 13),
        'Energía (GWh)': monthly_energy_gwh
    })
    
    # Crear DataFrame con los resultados anuales
    annual_data = pd.DataFrame({
        'Ubicación': [location_name],
        'Configuración': [config_type],
        'Latitud': [float(metadata['Latitude'])],
        'Longitud': [float(metadata['Longitude'])],
        'Elevación': [float(metadata['Elevation'])],
        'Energía Anual (GWh)': [annual_energy_gwh],
        'Factor de Capacidad (%)': [capacity_factor]
    })
    
    return monthly_data, annual_data

def main():
    # Rutas de los archivos TMY
    locations = {
        'Iquique': 'Iquique_tmy_corregido.csv',
        'Sevilla': 'Sevilla_tmy_corregido.csv',
        'Jodhpur': 'Jodhpur_tmy_corregido.csv'
    }
    
    # Configuraciones a probar
    configs = ['default', 'high_efficiency', 'optimized_land']
    
    # Directorio base
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Listas para almacenar los resultados
    all_monthly_data = []
    all_annual_data = []
    
    # Ejecutar simulaciones para cada ubicación y configuración
    for location, file_name in locations.items():
        print(f"\nProcesando {location}...")
        file_path = os.path.join(base_dir, file_name)
        tmy_data, metadata = load_tmy_data(file_path)
        
        for config in configs:
            print(f"  Configuración: {config}")
            monthly_data, annual_data = run_simulation(tmy_data, metadata, location, config)
            all_monthly_data.append(monthly_data)
            all_annual_data.append(annual_data)
    
    # Combinar todos los resultados
    monthly_results = pd.concat(all_monthly_data, ignore_index=True)
    annual_results = pd.concat(all_annual_data, ignore_index=True)
    
    # Guardar resultados en archivos CSV
    monthly_results.to_csv('resultados_mensuales.csv', index=False)
    annual_results.to_csv('resultados_anuales.csv', index=False)
    
    # Imprimir resultados
    print("\nResultados de las simulaciones:")
    print("-" * 50)
    for _, row in annual_results.iterrows():
        print(f"\nUbicación: {row['Ubicación']}")
        print(f"Configuración: {row['Configuración']}")
        print(f"Coordenadas: {row['Latitud']:.2f}°, {row['Longitud']:.2f}°")
        print(f"Elevación: {row['Elevación']:.0f} m")
        print(f"Energía anual (GWh): {row['Energía Anual (GWh)']:.2f}")
        print(f"Factor de capacidad: {row['Factor de Capacidad (%)']:.2f}%")
        print("Energía mensual (GWh):")
        monthly_data = monthly_results[
            (monthly_results['Ubicación'] == row['Ubicación']) & 
            (monthly_results['Configuración'] == row['Configuración'])
        ]
        for _, month_row in monthly_data.iterrows():
            print(f"  Mes {month_row['Mes']}: {month_row['Energía (GWh)']:.2f}")

if __name__ == "__main__":
    main() 