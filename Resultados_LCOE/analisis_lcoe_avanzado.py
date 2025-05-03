import PySAM.Pvwattsv8 as pv
import PySAM.Lcoefcr as lcoe
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Configuración de matplotlib
plt.style.use('default')
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.alpha'] = 0.3

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

# Parámetros de costos y configuración
PARAMETROS = {
    'PV': {
        'capital_cost': np.linspace(800_000, 1_200_000, 5),  # $/MW
        'fixed_operating_cost': np.linspace(30_000, 70_000, 5),  # $/año
        'variable_operating_cost': np.linspace(0.005, 0.015, 5),  # $/kWh
        'fixed_charge_rate': np.linspace(0.05, 0.09, 5),  # 5% a 9%
        'dc_ac_ratio': np.linspace(1.1, 1.3, 5),
        'losses': np.linspace(10, 18, 5)  # %
    },
    'CSP': {
        'capital_cost': np.linspace(2_500_000, 3_500_000, 5),  # $/MW
        'fixed_operating_cost': np.linspace(80_000, 120_000, 5),  # $/año
        'variable_operating_cost': np.linspace(0.015, 0.025, 5),  # $/kWh
        'fixed_charge_rate': np.linspace(0.05, 0.09, 5),  # 5% a 9%
        'dc_ac_ratio': np.linspace(1.1, 1.3, 5),
        'losses': np.linspace(12, 20, 5)  # %
    }
}

def crear_modelo_pv(ubicacion, capacidad, config):
    """Crea y configura un modelo PV para una ubicación y capacidad específica."""
    sistema = pv.default("PVWattsNone")
    
    # Cargar datos meteorológicos
    df = pd.read_csv(ubicacion['archivo'], skiprows=2)
    
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

    # Configurar sistema con parámetros variables
    sistema.SystemDesign.system_capacity = capacidad
    sistema.SystemDesign.dc_ac_ratio = config['dc_ac_ratio']
    sistema.SystemDesign.inv_eff = 96
    sistema.SystemDesign.losses = config['losses']
    sistema.SystemDesign.array_type = 0
    sistema.SystemDesign.tilt = abs(ubicacion['lat'])
    sistema.SystemDesign.azimuth = 180 if ubicacion['lat'] > 0 else 0

    return sistema

def calcular_lcoe(ubicacion, capacidad, tecnologia, config):
    """Calcula el LCOE para un sistema solar."""
    # Crear y ejecutar modelo
    sistema = crear_modelo_pv(ubicacion, capacidad, config)
    sistema.execute()
    annual_energy = sistema.Outputs.annual_energy

    # Calcular LCOE
    lcoe_model = lcoe.new()
    lcoe_model.SimpleLCOE.annual_energy = annual_energy
    lcoe_model.SimpleLCOE.capital_cost = config['capital_cost'] * (capacidad / 1000)
    lcoe_model.SimpleLCOE.fixed_charge_rate = config['fixed_charge_rate']
    lcoe_model.SimpleLCOE.fixed_operating_cost = config['fixed_operating_cost'] * (capacidad / 1000)
    lcoe_model.SimpleLCOE.variable_operating_cost = config['variable_operating_cost']
    
    lcoe_model.execute()
    return lcoe_model.Outputs.lcoe_fcr

def analisis_sensibilidad(ubicacion, capacidad, tecnologia):
    """Realiza análisis de sensibilidad para diferentes parámetros."""
    resultados = []
    
    # Configuración base
    config_base = {param: np.mean(valores) for param, valores in PARAMETROS[tecnologia].items()}
    
    # Variar cada parámetro individualmente
    for param, valores in PARAMETROS[tecnologia].items():
        for valor in valores:
            config = config_base.copy()
            config[param] = valor
            
            lcoe_valor = calcular_lcoe(ubicacion, capacidad, tecnologia, config)
            resultados.append({
                'Parametro': param,
                'Valor': valor,
                'LCOE': lcoe_valor
            })
    
    return pd.DataFrame(resultados)

def generar_graficos_sensibilidad(df_sensibilidad, tecnologia, ubicacion):
    """Genera gráficos de sensibilidad."""
    plt.figure(figsize=(15, 10))
    
    # Crear subplots para cada parámetro
    parametros = df_sensibilidad['Parametro'].unique()
    n_parametros = len(parametros)
    n_cols = 2
    n_rows = (n_parametros + 1) // n_cols
    
    for i, param in enumerate(parametros, 1):
        plt.subplot(n_rows, n_cols, i)
        datos = df_sensibilidad[df_sensibilidad['Parametro'] == param]
        plt.plot(datos['Valor'], datos['LCOE'], 'o-')
        plt.title(f'Sensibilidad a {param}')
        plt.xlabel('Valor del parámetro')
        plt.ylabel('LCOE ($/kWh)')
        plt.grid(True, alpha=0.3)
    
    plt.suptitle(f'Análisis de Sensibilidad - {tecnologia} en {ubicacion}', y=1.02)
    plt.tight_layout()
    plt.savefig(f'sensibilidad_{tecnologia}_{ubicacion}.png', bbox_inches='tight')
    plt.close()

def main():
    print("Iniciando análisis avanzado de LCOE...")
    
    # Capacidad del sistema en kW
    capacidad = 1000  # 1 MW
    
    # Crear directorio para resultados
    Path('resultados_lcoe').mkdir(exist_ok=True)
    
    # Realizar análisis para cada ubicación y tecnología
    for ubicacion, datos_ubicacion in UBICACIONES.items():
        print(f"\nAnalizando {ubicacion}...")
        
        for tecnologia in ['PV', 'CSP']:
            print(f"  Tecnología: {tecnologia}")
            
            # Análisis de sensibilidad
            df_sensibilidad = analisis_sensibilidad(datos_ubicacion, capacidad, tecnologia)
            
            # Guardar resultados
            df_sensibilidad.to_csv(f'resultados_lcoe/sensibilidad_{tecnologia}_{ubicacion}.csv', index=False)
            
            # Generar gráficos
            generar_graficos_sensibilidad(df_sensibilidad, tecnologia, ubicacion)
            
            # Imprimir resumen
            print(f"    LCOE promedio: {df_sensibilidad['LCOE'].mean():.4f} $/kWh")
            print(f"    LCOE mínimo: {df_sensibilidad['LCOE'].min():.4f} $/kWh")
            print(f"    LCOE máximo: {df_sensibilidad['LCOE'].max():.4f} $/kWh")
    
    print("\nAnálisis completado. Los resultados se han guardado en:")
    print("- Directorio: resultados_lcoe/")
    print("- Archivos CSV con datos de sensibilidad")
    print("- Gráficos de sensibilidad para cada tecnología y ubicación")

if __name__ == "__main__":
    main() 