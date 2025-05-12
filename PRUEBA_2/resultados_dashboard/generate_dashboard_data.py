import pandas as pd
import json
import os

def generar_power_y_kpis(localidad, archivo_entrada, potencia_nominal=41666666.67, capex=1000000, opex=20000, lifetime=25):
    # Leer datos
    df = pd.read_csv(archivo_entrada)
    df['timestamp'] = pd.to_datetime(df['Fecha'])
    df['ac_power'] = df['Potencia_AC_kW']
    
    # Guardar archivo de potencia para dashboard
    df_power = df[['timestamp', 'ac_power']]
    df_power.to_csv(f'{localidad}_2014_power.csv', index=False)
    
    # Calcular KPIs
    energia_total_anual = df['ac_power'].sum()  # kWh/año
    energia_diaria = df.groupby(df['timestamp'].dt.date)['ac_power'].sum().mean()  # Promedio diario
    capacity_factor = (energia_total_anual / (potencia_nominal * 8760)) * 100
    lcoe = (capex + opex * lifetime) / (energia_total_anual * lifetime)
    
    kpis = {
        'energia_diaria': round(energia_diaria, 2),
        'lcoe': round(lcoe, 5),
        'capacity_factor': round(capacity_factor, 2)
    }
    with open(f'{localidad}_2014_kpis.json', 'w') as f:
        json.dump(kpis, f, indent=4)
    print(f'Archivos generados para {localidad}')

def main():
    localidades = [
        ('Vallenar', 'Vallenar_pv_results.csv'),
        ('calama', 'calama_pv_results.csv'),
        ('salvador', 'salvador_pv_results.csv')
    ]
    for localidad, archivo in localidades:
        if os.path.exists(archivo):
            generar_power_y_kpis(localidad, archivo)
        else:
            print(f'Archivo no encontrado: {archivo}')

if __name__ == '__main__':
    main() 