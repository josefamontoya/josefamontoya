import PySAM.Pvwattsv8 as pv
import PySAM.Lcoefcr as lcoe
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

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

# Parámetros de costos para PV
PV_COSTS = {
    'capital_cost': 1_000_000,  # $/MW
    'fixed_operating_cost': 50_000,  # $/año
    'variable_operating_cost': 0.01  # $/kWh
}

# Parámetros de costos para CSP
CSP_COSTS = {
    'capital_cost': 3_000_000,  # $/MW
    'fixed_operating_cost': 100_000,  # $/año
    'variable_operating_cost': 0.02  # $/kWh
}

def crear_modelo_pv(ubicacion, capacidad):
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

    # Configurar sistema
    sistema.SystemDesign.system_capacity = capacidad
    sistema.SystemDesign.dc_ac_ratio = 1.2
    sistema.SystemDesign.inv_eff = 96
    sistema.SystemDesign.losses = 14.0
    sistema.SystemDesign.array_type = 0
    sistema.SystemDesign.tilt = abs(ubicacion['lat'])
    sistema.SystemDesign.azimuth = 180 if ubicacion['lat'] > 0 else 0

    return sistema

def calcular_lcoe_pv(ubicacion, capacidad, fixed_charge_rate):
    """Calcula el LCOE para un sistema PV."""
    # Crear y ejecutar modelo PV
    sistema = crear_modelo_pv(ubicacion, capacidad)
    sistema.execute()
    annual_energy = sistema.Outputs.annual_energy

    # Calcular LCOE
    lcoe_model = lcoe.default("LCOEFCR")
    lcoe_model.SimpleLCOE.annual_energy = annual_energy
    lcoe_model.SimpleLCOE.capital_cost = PV_COSTS['capital_cost'] * (capacidad / 1000)  # Convertir a $/MW
    lcoe_model.SimpleLCOE.fixed_charge_rate = fixed_charge_rate
    lcoe_model.SimpleLCOE.fixed_operating_cost = PV_COSTS['fixed_operating_cost'] * (capacidad / 1000)
    lcoe_model.SimpleLCOE.variable_operating_cost = PV_COSTS['variable_operating_cost']
    
    lcoe_model.execute()
    return lcoe_model.Outputs.lcoe_fcr

def calcular_lcoe_csp(ubicacion, capacidad, fixed_charge_rate):
    """Calcula el LCOE para un sistema CSP."""
    # Crear y ejecutar modelo CSP (usando PVWatts como aproximación)
    sistema = crear_modelo_pv(ubicacion, capacidad)
    sistema.execute()
    annual_energy = sistema.Outputs.annual_energy

    # Calcular LCOE
    lcoe_model = lcoe.default("LCOEFCR")
    lcoe_model.SimpleLCOE.annual_energy = annual_energy
    lcoe_model.SimpleLCOE.capital_cost = CSP_COSTS['capital_cost'] * (capacidad / 1000)
    lcoe_model.SimpleLCOE.fixed_charge_rate = fixed_charge_rate
    lcoe_model.SimpleLCOE.fixed_operating_cost = CSP_COSTS['fixed_operating_cost'] * (capacidad / 1000)
    lcoe_model.SimpleLCOE.variable_operating_cost = CSP_COSTS['variable_operating_cost']
    
    lcoe_model.execute()
    return lcoe_model.Outputs.lcoe_fcr

def generar_graficos(resultados):
    """Genera gráficos comparativos del LCOE."""
    # Gráfico de LCOE por ubicación y tecnología
    plt.figure(figsize=(12, 6))
    x = np.arange(len(UBICACIONES))
    width = 0.35

    for i, (tecnologia, datos) in enumerate(resultados.items()):
        lcoe_values = [datos[ubicacion] for ubicacion in UBICACIONES.keys()]
        plt.bar(x + i*width, lcoe_values, width, label=tecnologia)

    plt.xlabel('Ubicación')
    plt.ylabel('LCOE ($/kWh)')
    plt.title('Comparación de LCOE entre PV y CSP')
    plt.xticks(x + width/2, UBICACIONES.keys())
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('comparacion_lcoe.png', bbox_inches='tight')
    plt.close()

def main():
    print("Iniciando cálculo de LCOE...")
    
    # Capacidad del sistema en kW
    capacidad = 1000  # 1 MW
    
    # Tasa de carga fija
    fixed_charge_rate = 0.07  # 7%
    
    # Almacenar resultados
    resultados = {
        'PV': {},
        'CSP': {}
    }
    
    # Calcular LCOE para cada ubicación y tecnología
    for ubicacion, datos in UBICACIONES.items():
        print(f"\nCalculando LCOE para {ubicacion}...")
        
        # LCOE para PV
        lcoe_pv = calcular_lcoe_pv(datos, capacidad, fixed_charge_rate)
        resultados['PV'][ubicacion] = lcoe_pv
        print(f"  PV: {lcoe_pv:.4f} $/kWh")
        
        # LCOE para CSP
        lcoe_csp = calcular_lcoe_csp(datos, capacidad, fixed_charge_rate)
        resultados['CSP'][ubicacion] = lcoe_csp
        print(f"  CSP: {lcoe_csp:.4f} $/kWh")
    
    # Generar gráficos
    print("\nGenerando gráficos...")
    generar_graficos(resultados)
    
    # Guardar resultados en CSV
    df = pd.DataFrame(resultados)
    df.to_csv('resultados_lcoe.csv')
    print("\nResultados guardados en 'resultados_lcoe.csv'")
    print("Gráfico guardado como 'comparacion_lcoe.png'")

if __name__ == "__main__":
    main() 