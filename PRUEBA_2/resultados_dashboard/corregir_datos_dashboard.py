import pandas as pd
import json
import os

def calcular_kpis(power_data):
    """
    Calcula los KPIs a partir de los datos de potencia.
    
    Args:
        power_data (pd.DataFrame): DataFrame con los datos de potencia
        
    Returns:
        dict: Diccionario con los KPIs calculados
    """
    # Capacidad instalada (MW)
    capacidad_instalada = 50.0  # Asumimos 50 MW
    
    # Energía anual (MWh)
    energia_anual = power_data['Power (kW)'].sum() / 1000  # Convertir de kWh a MWh
    
    # Factor de capacidad
    horas_anuales = 8760
    energia_maxima = capacidad_instalada * 1000 * horas_anuales  # kWh
    factor_capacidad = energia_anual * 1000 / energia_maxima
    
    # LCOE (USD/MWh) - Cálculo simplificado
    capex = 800  # USD/kW
    opex = 20    # USD/kW/año
    vida_util = 25  # años
    tasa_descuento = 0.07  # 7%
    
    capex_total = capex * capacidad_instalada * 1000  # USD
    opex_anual = opex * capacidad_instalada * 1000    # USD/año
    
    # Factor de recuperación de capital
    frc = tasa_descuento * (1 + tasa_descuento)**vida_util / ((1 + tasa_descuento)**vida_util - 1)
    
    # Costo anual total
    costo_anual = capex_total * frc + opex_anual
    
    # LCOE
    lcoe = costo_anual / energia_anual
    
    return {
        "annual_energy": round(energia_anual, 2),
        "capacity_factor": round(factor_capacidad, 4),
        "lcoe": round(lcoe, 2)
    }

def corregir_archivos_dashboard():
    # Directorio base (mismo directorio donde está el script)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Lista de ubicaciones
    ubicaciones = ['calama', 'Vallenar', 'salvador']
    
    for ubicacion in ubicaciones:
        # Corregir archivo de potencia
        power_file = os.path.join(base_dir, f'{ubicacion}_2014_power.csv')
        if os.path.exists(power_file):
            # Leer el archivo
            df = pd.read_csv(power_file)
            
            # Si la columna se llama 'ac_power', convertirla a kW
            if 'ac_power' in df.columns:
                df['Power (kW)'] = df['ac_power'] / 1000
                df = df.drop('ac_power', axis=1)
            
            # Convertir timestamp a datetime y extraer hora
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['Hour'] = df['timestamp'].dt.hour
            
            # Guardar archivo corregido
            df.to_csv(power_file, index=False)
            print(f'Archivo de potencia corregido: {power_file}')
            
            # Calcular KPIs
            kpis = calcular_kpis(df)
            
            # Guardar KPIs
            kpis_file = os.path.join(base_dir, f'{ubicacion}_2014_kpis.json')
            with open(kpis_file, 'w') as f:
                json.dump(kpis, f, indent=4)
            print(f'Archivo de KPIs corregido: {kpis_file}')

if __name__ == '__main__':
    corregir_archivos_dashboard() 