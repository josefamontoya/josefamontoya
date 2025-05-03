import PySAM.Pvwattsv8 as pv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Configuración de matplotlib
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.alpha'] = 0.3
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12

# Definición de ubicaciones
UBICACIONES = {
    'Sevilla': {
        'archivo': '/home/josefa_montoya/Josefamontoya/josefamontoya/tmy_corregidos/Sevilla_tmy_corregido.csv',
        'lat': 37.37,
        'lon': -5.98,
        'elev': 14,
        'tz': 1
    },
    'Iquique': {
        'archivo': '/home/josefa_montoya/Josefamontoya/josefamontoya/tmy_corregidos/Iquique_tmy_corregido.csv',
        'lat': -20.22,
        'lon': -70.15,
        'elev': 45,
        'tz': -4
    },
    'Jodhpur': {
        'archivo': '/home/josefa_montoya/Josefamontoya/josefamontoya/tmy_corregidos/Jodhpur_tmy_corregido.csv',
        'lat': 26.30,
        'lon': 73.02,
        'elev': 224,
        'tz': 5.5
    }
}

# Capacidades a simular (kW)
CAPACIDADES = [500, 1000, 5000]

def crear_modelo_pv(ubicacion, capacidad):
    """Crea y configura un modelo PV para una ubicación y capacidad específica."""
    # Crear sistema PV
    sistema = pv.default("PVWattsNone")
    
    # Cargar datos meteorológicos
    df = pd.read_csv(ubicacion['archivo'], skiprows=2)  # Saltar las dos primeras filas de metadatos
    
    # Configurar recurso solar
    sistema.SolarResource.solar_resource_data = {
        'lat': ubicacion['lat'],
        'lon': ubicacion['lon'],
        'tz': ubicacion['tz'],
        'elev': ubicacion['elev'],
        'year': df['Year'].values.tolist(),
        'month': df['Month'].values.tolist(),
        'day': df['Day'].values.tolist(),
        'hour': df['Hour'].values.tolist(),
        'minute': df['Minute'].values.tolist(),
        'dn': df['DNI'].values.tolist(),
        'df': df['DHI'].values.tolist(),
        'gh': df['GHI'].values.tolist(),
        'tdry': df['Temperature'].values.tolist(),
        'wspd': df['Wind Speed'].values.tolist()
    }

    # Configurar sistema
    sistema.SystemDesign.system_capacity = capacidad  # kW DC
    sistema.SystemDesign.dc_ac_ratio = 1.2
    sistema.SystemDesign.inv_eff = 96
    sistema.SystemDesign.losses = 14.0
    sistema.SystemDesign.array_type = 0  # Fixed open rack
    sistema.SystemDesign.tilt = abs(ubicacion['lat'])  # Tilt = latitude
    sistema.SystemDesign.azimuth = 180 if ubicacion['lat'] > 0 else 0  # Sur en hemisferio norte, norte en hemisferio sur

    return sistema

def simular_ubicaciones():
    """
    Realiza simulaciones para todas las ubicaciones y capacidades.
    """
    resultados = {}
    
    for nombre, ubicacion in UBICACIONES.items():
        resultados[nombre] = {}
        
        for capacidad in CAPACIDADES:
            # Crear y ejecutar modelo
            sistema = crear_modelo_pv(ubicacion, capacidad)
            sistema.execute()
            
            # Guardar resultados
            resultados[nombre][capacidad] = {
                'energia_anual': sistema.Outputs.annual_energy,
                'energia_mensual': sistema.Outputs.monthly_energy,
                'factor_capacidad': (sistema.Outputs.annual_energy / (capacidad * 8760)) * 100
            }
    
    return resultados

def generar_graficos(resultados):
    """
    Genera gráfico comparativo de la producción anual por ubicación.
    """
    # Gráfico de energía anual por capacidad
    plt.figure(figsize=(12, 6))
    x = np.arange(len(CAPACIDADES))
    width = 0.25
    
    for i, (ubicacion, datos) in enumerate(resultados.items()):
        energias = [datos[cap]['energia_anual'] for cap in CAPACIDADES]
        plt.bar(x + i*width, energias, width, label=ubicacion)
    
    plt.xlabel('Capacidad del Sistema (kW)')
    plt.ylabel('Energía Anual (kWh)')
    plt.title('Comparación de Producción Anual por Ubicación')
    plt.xticks(x + width, CAPACIDADES)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('produccion_anual.png', bbox_inches='tight')
    plt.close()

def guardar_resultados(resultados):
    """
    Guarda los resultados en un archivo CSV.
    """
    filas = []
    for ubicacion, datos_ubicacion in resultados.items():
        for capacidad, datos in datos_ubicacion.items():
            fila = {
                'Ubicación': ubicacion,
                'Capacidad_kW': capacidad,
                'Energía_Anual_kWh': datos['energia_anual'],
                'Factor_Capacidad_%': datos['factor_capacidad']
            }
            filas.append(fila)
    
    df = pd.DataFrame(filas)
    df.to_csv('resultados_simulacion.csv', index=False)
    print("\nResultados guardados en 'resultados_simulacion.csv'")

def main():
    print("Iniciando simulaciones PV...")
    
    # Ejecutar simulaciones
    resultados = simular_ubicaciones()
    
    # Generar gráficos
    print("\nGenerando gráfico de producción anual...")
    generar_graficos(resultados)
    
    # Guardar resultados
    guardar_resultados(resultados)
    
    # Mostrar resumen
    print("\nResumen de Resultados:")
    print("-" * 60)
    for ubicacion, datos in resultados.items():
        print(f"\n{ubicacion}:")
        for capacidad, valores in datos.items():
            print(f"  {capacidad} kW:")
            print(f"    Energía Anual: {valores['energia_anual']:,.0f} kWh")
            print(f"    Factor de Capacidad: {valores['factor_capacidad']:.1f}%")
    
    print("\nGráfico guardado:")
    print("- produccion_anual.png")

if __name__ == "__main__":
    main() 