import pandas as pd
import numpy as np
from financial_analysis import calculate_lcoe, calculate_npv

def process_pv_results(file_path):
    """
    Procesa los resultados de la simulación PV y calcula indicadores financieros
    Args:
        file_path (str): Ruta al archivo de resultados PV
    """
    # Parámetros de la planta
    potencia_dc_mw = 50  # MW DC
    dc_ac_ratio = 1.2
    potencia_ac_mw = potencia_dc_mw / dc_ac_ratio  # MW AC
    potencia_ac_kw = potencia_ac_mw * 1000  # kW AC
    perdidas = 0.14  # 14%
    
    # Leer resultados PV
    df = pd.read_csv(file_path)
    
    # Convertir la columna de fecha a datetime
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    df['Año'] = df['Fecha'].dt.year
    primer_ano = df['Año'].iloc[0]
    df = df[df['Año'] == primer_ano]

    # Convertir de W a kW y normalizar a la potencia AC
    df['Potencia_AC_kW'] = df['Potencia_AC_kW'] / 1000  # Convertir de W a kW
    potencia_max = df['Potencia_AC_kW'].max()
    factor_escala = potencia_ac_kw / potencia_max
    df['Potencia_AC_kW'] = df['Potencia_AC_kW'] * factor_escala

    # Aplicar pérdidas
    df['Potencia_AC_kW'] = df['Potencia_AC_kW'] * (1 - perdidas)

    # Calcular energía anual (kWh)
    energia_anual = df['Potencia_AC_kW'].sum()  # Suma de potencia horaria en kWh
    
    # Parámetros financieros
    capex_kw = 650  # USD/kW
    capex_total = capex_kw * potencia_dc_mw * 1000  # USD (basado en potencia DC)
    opex_percent = 0.6  # % del CAPEX
    fcr = 0.08  # 8%
    lifetime = 20  # años
    
    # Calcular LCOE
    lcoe = calculate_lcoe(energia_anual, capex_total, opex_percent, fcr, lifetime)
    
    # Calcular VAN
    spot_price = 60  # USD/MWh
    degradacion = 0.005  # 0.5% anual
    annual_revenue = energia_anual * spot_price / 1000  # USD (kWh a MWh)
    cash_flows = [-capex_total]
    for year in range(lifetime):
        energia_degradada = energia_anual * (1 - degradacion) ** year
        ingreso = energia_degradada * spot_price / 1000
        opex = capex_total * opex_percent / 100
        cash_flows.append(ingreso - opex)
        npv = calculate_npv(cash_flows, fcr)
    
    return {
        'energia_anual': energia_anual,
        'lcoe': lcoe,
        'npv': npv,
        'potencia_ac_mw': potencia_ac_mw
    }

def main():
    locations = {
        'salvador': '/home/josefa_montoya/Josefamontoya/josefamontoya/PRUEBA_2/salvador_pv_results.csv',
        'calama': '/home/josefa_montoya/Josefamontoya/josefamontoya/PRUEBA_2/calama_pv_results.csv',
        'vallenar': '/home/josefa_montoya/Josefamontoya/josefamontoya/PRUEBA_2/Vallenar_pv_results.csv'
    }
    
    for location, file_path in locations.items():
        results = process_pv_results(file_path)
        print(f"\nResultados para {location.upper()}:")
        print(f"Potencia AC: {results['potencia_ac_mw']:.2f} MW")
        print(f"Energía anual: {results['energia_anual']/1e6:.2f} GWh")
        print(f"LCOE: {results['lcoe']:.4f} USD/kWh")
        print(f"VAN: {results['npv']/1e6:.2f} MUSD")

if __name__ == "__main__":
    main() 