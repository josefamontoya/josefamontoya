import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np

def load_simulation_results():
    """Carga los resultados de las simulaciones desde los archivos CSV"""
    monthly_results = pd.read_csv('resultados_mensuales.csv')
    annual_results = pd.read_csv('resultados_anuales.csv')
    return monthly_results, annual_results

def plot_location_analysis(monthly_results, annual_results, location):
    """Genera un conjunto completo de gráficos para una ubicación específica"""
    plt.figure(figsize=(15, 12))
    sns.set_style("whitegrid")
    
    # 1. Energía mensual
    plt.subplot(3, 1, 1)
    location_monthly = monthly_results[monthly_results['Ubicación'] == location]
    
    colors = sns.color_palette("husl", n_colors=len(location_monthly['Configuración'].unique()))
    
    for i, config in enumerate(location_monthly['Configuración'].unique()):
        config_data = location_monthly[location_monthly['Configuración'] == config]
        plt.plot(config_data['Mes'], config_data['Energía (GWh)'], 
                marker='o', label=config, linewidth=2, color=colors[i])
    
    plt.title(f'Producción Mensual de Energía - {location}', fontsize=12, pad=20)
    plt.xlabel('Mes')
    plt.ylabel('Energía (GWh)')
    plt.xticks(range(1, 13))
    plt.legend(title='Configuración', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    
    # 2. Comparación de energía anual
    plt.subplot(3, 1, 2)
    location_annual = annual_results[annual_results['Ubicación'] == location]
    
    bars = plt.bar(location_annual['Configuración'], 
                  location_annual['Energía Anual (GWh)'],
                  color=colors)
    
    plt.title(f'Energía Anual Total - {location}', fontsize=12, pad=20)
    plt.ylabel('Energía Anual (GWh)')
    
    # Añadir valores sobre las barras
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}',
                ha='center', va='bottom')
    
    plt.grid(True, alpha=0.3, axis='y')
    
    # 3. Comparación de factor de capacidad
    plt.subplot(3, 1, 3)
    bars = plt.bar(location_annual['Configuración'], 
                  location_annual['Factor de Capacidad (%)'],
                  color=colors)
    
    plt.title(f'Factor de Capacidad - {location}', fontsize=12, pad=20)
    plt.ylabel('Factor de Capacidad (%)')
    
    # Añadir valores sobre las barras
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%',
                ha='center', va='bottom')
    
    plt.grid(True, alpha=0.3, axis='y')
    
    # Ajustar el diseño
    plt.tight_layout()
    
    # Guardar el gráfico
    plt.savefig(f'analisis_{location.lower()}.png', 
                bbox_inches='tight', 
                dpi=300)
    plt.close()

def plot_geographic_comparison(annual_results):
    """Genera un gráfico comparativo de todas las ubicaciones"""
    plt.figure(figsize=(12, 8))
    sns.set_style("whitegrid")
    
    # Crear un gráfico de barras agrupadas
    locations = annual_results['Ubicación'].unique()
    configs = annual_results['Configuración'].unique()
    x = np.arange(len(locations))
    width = 0.25
    
    colors = sns.color_palette("husl", n_colors=len(configs))
    
    for i, config in enumerate(configs):
        data = annual_results[annual_results['Configuración'] == config]
        offset = width * (i - 1)
        plt.bar(x + offset, data['Energía Anual (GWh)'], 
               width, label=config, color=colors[i])
    
    plt.xlabel('Ubicación')
    plt.ylabel('Energía Anual (GWh)')
    plt.title('Comparación de Producción entre Ubicaciones')
    plt.xticks(x, locations)
    plt.legend()
    plt.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('comparacion_ubicaciones.png', 
                bbox_inches='tight', 
                dpi=300)
    plt.close()

def main():
    # Cargar resultados
    monthly_results, annual_results = load_simulation_results()
    
    # Generar gráficos para cada ubicación
    for location in monthly_results['Ubicación'].unique():
        plot_location_analysis(monthly_results, annual_results, location)
    
    # Generar gráfico comparativo
    plot_geographic_comparison(annual_results)
    
    print("Gráficos generados exitosamente:")
    print("- analisis_iquique.png")
    print("- analisis_sevilla.png")
    print("- analisis_jodhpur.png")
    print("- comparacion_ubicaciones.png")

if __name__ == "__main__":
    main() 