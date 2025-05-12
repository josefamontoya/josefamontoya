import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

def calculate_lcoe(annual_energy, capex, opex_percent, fcr, lifetime=20):
    """
    Calcula el LCOE (Levelized Cost of Energy)
    
    Args:
        annual_energy (float): Energía anual generada en kWh
        capex (float): Costo de capital inicial en USD
        opex_percent (float): Costos operativos como porcentaje del CAPEX
        fcr (float): Factor de recuperación de capital (Fixed Charge Rate)
        lifetime (int): Vida útil del proyecto en años
    
    Returns:
        float: LCOE en USD/kWh
    """
    opex = capex * (opex_percent / 100)
    total_cost = capex * fcr + opex
    return total_cost / annual_energy

def calculate_npv(cash_flows, discount_rate):
    """
    Calcula el VAN (Valor Actual Neto)
    
    Args:
        cash_flows (list): Lista de flujos de caja anuales
        discount_rate (float): Tasa de descuento
    
    Returns:
        float: VAN
    """
    cash_flows = np.array(cash_flows)
    npv = 0
    for t, cf in enumerate(cash_flows):
        npv += cf / (1 + discount_rate) ** t
    return npv

def run_tornado_analysis(location, base_params, variations):
    """
    Realiza análisis de sensibilidad tipo tornado
    
    Args:
        location (str): Nombre de la ubicación
        base_params (dict): Parámetros base
        variations (dict): Variaciones para cada parámetro
    
    Returns:
        dict: Resultados del análisis
    """
    results = {}
    
    # Calcular LCOE base
    base_lcoe = calculate_lcoe(
        base_params['annual_energy'],
        base_params['capex'],
        base_params['opex_percent'],
        base_params['fcr']
    )
    
    # Calcular VAN base
    spot_price = base_params['spot_price']
    annual_revenue = base_params['annual_energy'] * spot_price / 1000
    cash_flows = [-base_params['capex']]
    for year in range(base_params['lifetime']):
        cash_flow = annual_revenue - (base_params['capex'] * base_params['opex_percent'] / 100)
        cash_flows.append(cash_flow)
    base_npv = calculate_npv(cash_flows, base_params['fcr'])
    
    # Análisis de sensibilidad para cada parámetro
    for param, values in variations.items():
        param_results = []
        for value in values:
            test_params = base_params.copy()
            
            # Ajustar el parámetro según corresponda
            if param == 'FCR':
                test_params['fcr'] = value
            elif param == 'CapEx':
                test_params['capex'] = value * 50000  # Convertir USD/kW a USD total
            elif param == 'Precio Spot':
                test_params['spot_price'] = value
            elif param == 'Vida Inversor':
                test_params['lifetime'] = value
            elif param == 'Pérdidas':
                # Ajustar la energía anual según las pérdidas
                loss_factor = (100 - value) / (100 - base_params.get('losses', 14))
                test_params['annual_energy'] = base_params['annual_energy'] * loss_factor
            
            # Calcular LCOE con parámetros modificados
            lcoe = calculate_lcoe(
                test_params['annual_energy'],
                test_params['capex'],
                test_params['opex_percent'],
                test_params['fcr']
            )
            
            # Calcular VAN con parámetros modificados
            annual_revenue = test_params['annual_energy'] * test_params['spot_price'] / 1000
            cash_flows = [-test_params['capex']]
            for year in range(test_params['lifetime']):
                cash_flow = annual_revenue - (test_params['capex'] * test_params['opex_percent'] / 100)
                cash_flows.append(cash_flow)
            npv = calculate_npv(cash_flows, test_params['fcr'])
            
            param_results.append({
                'lcoe': lcoe,
                'npv': npv
            })
        
        results[param] = param_results
    
    return results, base_lcoe, base_npv

def plot_tornado(location, results, base_lcoe, base_npv, variations, output_file):
    """
    Genera gráfico tornado para una ubicación
    
    Args:
        location (str): Nombre de la ubicación
        results (dict): Resultados del análisis
        base_lcoe (float): LCOE base
        base_npv (float): VAN base
        variations (dict): Variaciones utilizadas
        output_file (str): Ruta del archivo de salida
    """
    # Preparar datos para el gráfico
    params = list(results.keys())
    lcoe_impacts = []
    npv_impacts = []
    
    for param in params:
        min_lcoe = min(r['lcoe'] for r in results[param])
        max_lcoe = max(r['lcoe'] for r in results[param])
        min_npv = min(r['npv'] for r in results[param])
        max_npv = max(r['npv'] for r in results[param])
        
        lcoe_impact = max(abs(max_lcoe - base_lcoe), abs(min_lcoe - base_lcoe)) / base_lcoe * 100
        npv_impact = max(abs(max_npv - base_npv), abs(min_npv - base_npv)) / abs(base_npv) * 100
        
        lcoe_impacts.append(lcoe_impact)
        npv_impacts.append(npv_impact)
    
    # Ordenar por impacto
    sorted_idx = np.argsort(lcoe_impacts)
    params = [params[i] for i in sorted_idx]
    lcoe_impacts = [lcoe_impacts[i] for i in sorted_idx]
    npv_impacts = [npv_impacts[i] for i in sorted_idx]
    
    # Crear figura con dos subplots
    plt.style.use('default')
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 8))
    
    # Gráfico tornado para LCOE
    y_pos = np.arange(len(params))
    ax1.barh(y_pos, lcoe_impacts, color='skyblue', edgecolor='black')
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(params)
    ax1.set_xlabel('Impacto en LCOE (%)')
    ax1.set_title(f'Análisis de Sensibilidad LCOE - {location.upper()}')
    ax1.grid(True, alpha=0.3)
    
    # Gráfico tornado para VAN
    ax2.barh(y_pos, npv_impacts, color='lightgreen', edgecolor='black')
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(params)
    ax2.set_xlabel('Impacto en VAN (%)')
    ax2.set_title(f'Análisis de Sensibilidad VAN - {location.upper()}')
    ax2.grid(True, alpha=0.3)
    
    # Ajustar layout y guardar
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()

def main():
    # Parámetros base
    base_params = {
        'capex': 800 * 50000,  # USD (50 MW * 800 USD/kW)
        'opex_percent': 1.0,  # % del CAPEX
        'fcr': 0.08,  # 8%
        'lifetime': 20,  # años
        'spot_price': 50,  # USD/MWh
        'annual_energy': 62.54e6,  # kWh (valor base de Salvador)
        'losses': 14  # % de pérdidas base
    }
    
    # Variaciones para análisis de sensibilidad
    variations = {
        'FCR': [0.06, 0.08, 0.10],
        'CapEx': [600, 800, 1000],  # USD/kW
        'Precio Spot': [30, 50, 70],  # USD/MWh
        'Vida Inversor': [10, 15, 20],  # años
        'Pérdidas': [10, 14, 18]  # %
    }
    
    # Ubicaciones con sus respectivas energías anuales
    locations = {
        'salvador': 62.54e6,  # kWh
        'calama': 62.70e6,    # kWh
        'vallenar': 50.98e6   # kWh
    }
    
    for location, annual_energy in locations.items():
        # Actualizar la energía anual para cada ubicación
        base_params['annual_energy'] = annual_energy
        
        # Realizar el análisis de sensibilidad
        results, base_lcoe, base_npv = run_tornado_analysis(location, base_params, variations)
        
        # Generar el gráfico tornado
        plot_tornado(location, results, base_lcoe, base_npv, variations, f'{location}_tornado.png')
        
        # Imprimir resultados base
        print(f"\nResultados base para {location.upper()}:")
        print(f"LCOE base: {base_lcoe:.4f} USD/kWh")
        print(f"VAN base: {base_npv/1e6:.2f} MUSD")
        
        # Imprimir resultados detallados para cada parámetro
        print("\nImpactos por parámetro:")
        for param in results.keys():
            min_lcoe = min(r['lcoe'] for r in results[param])
            max_lcoe = max(r['lcoe'] for r in results[param])
            min_npv = min(r['npv'] for r in results[param])
            max_npv = max(r['npv'] for r in results[param])
            
            print(f"\n{param}:")
            print(f"LCOE: {min_lcoe:.4f} - {max_lcoe:.4f} USD/kWh")
            print(f"VAN: {min_npv/1e6:.2f} - {max_npv/1e6:.2f} MUSD")

if __name__ == "__main__":
    main() 